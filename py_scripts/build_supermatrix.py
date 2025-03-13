#!/usr/bin/env python

import argparse
from os import listdir, path
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
import sys
import numpy as np
from numba import jit
from concurrent.futures import ProcessPoolExecutor
from functools import partial

@jit(nopython=True)
def concatenate_sequences(seq_array, missing_array, seq_len):
    """Optimized sequence concatenation using Numba."""
    result = np.empty(seq_array.shape[0] + missing_array.shape[0], dtype=np.int8)
    result[:seq_array.shape[0]] = seq_array
    result[seq_array.shape[0]:] = missing_array
    return result

def process_alignment_file(fname, alignment_dir, taxa_dict, missing_char, file_suffix):
    """Process a single alignment file."""
    if not fname.endswith(file_suffix):
        return None
    
    filepath = path.join(alignment_dir, fname)
    local_alignments = taxa_dict.copy()
    
    # Get sequence length and process records
    first_record = next(SeqIO.parse(filepath, "fasta"))
    seq_len = len(first_record.seq)
    
    # Convert sequences to numpy arrays for faster processing
    missing_seq = np.array([ord(missing_char)] * seq_len, dtype=np.int8)
    
    # Process all sequences in the file
    with open(filepath) as f:
        for record in SeqIO.parse(f, "fasta"):
            seq_array = np.array([ord(c) for c in str(record.seq)], dtype=np.int8)
            local_alignments[str(record.id)] = seq_array
    
    # Fill missing sequences
    for taxon in local_alignments:
        if isinstance(local_alignments[taxon], str):
            local_alignments[taxon] = missing_seq
    
    gene_name = fname.replace(file_suffix, "")
    return (gene_name, local_alignments, seq_len)

def build_supermatrix(alignment_dir, taxa_list, missing_char="?", file_suffix=".aln"):
    """Build supermatrix from alignment files using parallel processing."""
    taxa_dict = {taxon: "" for taxon in taxa_list}
    partitions = []
    start = 1

    # Process alignment files in parallel
    with ProcessPoolExecutor() as executor:
        process_func = partial(
            process_alignment_file,
            alignment_dir=alignment_dir,
            taxa_dict=taxa_dict,
            missing_char=missing_char,
            file_suffix=file_suffix
        )
        
        alignment_files = [f for f in listdir(alignment_dir) if f.endswith(file_suffix)]
        results = list(executor.map(process_func, alignment_files))

    # Combine results
    final_alignments = {taxon: [] for taxon in taxa_list}
    
    for result in results:
        if result is None:
            continue
        
        gene_name, local_alignments, seq_len = result
        
        # Update partitions
        partitions.append([gene_name, start, start + seq_len - 1])
        start += seq_len
        
        # Concatenate sequences
        for taxon in taxa_list:
            final_alignments[taxon].append(local_alignments[taxon])

    # Convert final alignments to strings
    for taxon in final_alignments:
        concatenated = np.concatenate(final_alignments[taxon])
        final_alignments[taxon] = ''.join(chr(x) for x in concatenated)

    return final_alignments, partitions

def get_all_taxa(alignment_dir, file_suffix=".aln"):
    """Get all unique taxa names from alignment files."""
    taxa = set()
    for fname in listdir(alignment_dir):
        if fname.endswith(file_suffix):
            for record in SeqIO.parse(path.join(alignment_dir, fname), "fasta"):
                taxa.add(str(record.id))
    return sorted(list(taxa))

def main():
    parser = argparse.ArgumentParser(description="Build supermatrix from alignment files")
    parser.add_argument("-i", "--input", required=True, help="Directory containing alignment files")
    parser.add_argument("-o", "--output", required=True, help="Output prefix for supermatrix files")
    parser.add_argument("-s", "--suffix", default=".aln", help="Alignment file suffix (default: .aln)")
    parser.add_argument("-m", "--missing", default="?", help="Missing data character (default: ?)")
    args = parser.parse_args()

    if not path.isdir(args.input):
        sys.exit(f"Error: Input directory {args.input} not found")

    # Get list of all taxa
    print("Identifying taxa from alignment files...")
    taxa_list = get_all_taxa(args.input, args.suffix)
    print(f"Found {len(taxa_list)} taxa")

    # Build supermatrix
    print("Building supermatrix...")
    alignments, partitions = build_supermatrix(args.input, taxa_list, args.missing, args.suffix)

    # Create SeqRecord objects
    records = []
    for taxon in taxa_list:
        record = SeqRecord(
            Seq(alignments[taxon]),
            id=taxon,
            description=""
        )
        records.append(record)

    # Write outputs
    matrix_length = len(alignments[taxa_list[0]])
    print(f"Supermatrix length: {matrix_length} positions")
    print(f"Number of partitions: {len(partitions)}")

    # Write FASTA
    fasta_out = f"{args.output}"
    SeqIO.write(records, fasta_out, "fasta")
    print(f"Wrote FASTA format: {fasta_out}")

    # Write PHYLIP
    phylip_out = f"{args.output}.phylip"
    SeqIO.write(records, phylip_out, "phylip-relaxed")
    print(f"Wrote PHYLIP format: {phylip_out}")

    # Write partitions
    partition_out = f"{args.output}.partitions"
    with open(partition_out, "w") as f:
        for p in partitions:
            f.write(f"{p[0]} = {p[1]}-{p[2]};\n")
    print(f"Wrote partitions file: {partition_out}")

if __name__ == "__main__":
    main()
