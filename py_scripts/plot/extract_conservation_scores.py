import os
import glob
import numpy as np
from Bio import AlignIO, SeqIO
from collections import defaultdict
import re
import json
import shutil

# Define accession ID and species name as global variables
ACCESSION = "GCF_000146045.2"
SPECIES_NAME = "S. cerevisiae"

# Mapping of accessions to species names (for reference)
# "GCF_000146045.2": "S. cerevisiae"
# "GCA_000230395.2": "A. niger"
# "GCF_000002655.1": "A. fumigatus"
# "GCF_000182895.1": "C. cinerea"
# "GCF_000149305.1": "R. delemar"
# "GCF_028827035.1": "P. chrysogenum"

# Import conservation calculation functions from existing script
from conserved_regions import calculate_conservation

def extract_conservation_scores_for_accession(alignment, accession=ACCESSION):
    """
    Extract conservation scores for a specific accession, excluding gaps
    
    Parameters:
    alignment -- BioPython multiple sequence alignment
    accession -- Accession ID to extract conservation scores for
    
    Returns:
    Dictionary mapping amino acid positions (1-based) to conservation scores
    """
    # Calculate conservation scores for the entire alignment
    conservation_scores = calculate_conservation(alignment)
    
    # Find the sequence with the specified accession
    target_seq = None
    target_idx = -1
    
    for i, record in enumerate(alignment):
        if accession in record.id:
            target_seq = str(record.seq)
            target_idx = i
            break
    
    if target_seq is None:
        raise ValueError(f"Accession {accession} not found in alignment")
    
    # Map alignment positions to sequence positions (excluding gaps)
    position_map = {}  # Maps non-gap positions in target_seq to their alignment positions
    seq_pos = 0
    
    for aln_pos, aa in enumerate(target_seq):
        if aa != "-":  # Skip gaps
            seq_pos += 1
            position_map[seq_pos] = conservation_scores[aln_pos]
    
    return position_map

def main():
    # Create base output directory
    base_output_dir = '/zhome/85/8/203063/a3_fungi/conservation_scores'
    os.makedirs(base_output_dir, exist_ok=True)
    
    # Create organism-specific output directory
    output_dir = os.path.join(base_output_dir, SPECIES_NAME)
    os.makedirs(output_dir, exist_ok=True)
    
    # Directory for Mol* conservation JSON files (keep this at root level)
    molstar_conservation_dir = '/zhome/85/8/203063/a3_fungi/html_molstar_only/conservation_data'
    os.makedirs(molstar_conservation_dir, exist_ok=True)
    
    # Define the gene order (same as in conserved_regions.py)
    gene_order = ["LYS20", "ACO2", "LYS4", "LYS12", "ARO8", "LYS2", "LYS9", "LYS1"]
    
    # Get alignment files for conservation scores
    all_files = glob.glob('/work3/s233201/enzyme_out_6/alignments/*aln')
    file_dict = {os.path.basename(f).split('.')[0]: f for f in all_files}
    
    # Create a FASTA file for the target sequences
    fasta_output = os.path.join(output_dir, f'{ACCESSION}_{SPECIES_NAME}_sequences.fasta')
    with open(fasta_output, 'w') as fasta_file:
        for gene in gene_order:
            input_file = f'/zhome/85/8/203063/a3_fungi/inputs_new/{gene.upper()}.fasta'
            try:
                for record in SeqIO.parse(input_file, 'fasta'):
                    if ACCESSION in record.id:
                        # Get sequence and write to file
                        seq = str(record.seq)
                        fasta_file.write(f">{gene}\n{seq}\n")
                        break
            except Exception as e:
                print(f"Warning: Could not process {gene}: {str(e)}")
                continue
    
    # Process each gene for conservation scores
    for gene in gene_order:
        if gene not in file_dict:
            print(f"Warning: {gene} not found in alignment files")
            continue
            
        try:
            print(f"Processing {gene}...")
            alignment = AlignIO.read(file_dict[gene], 'fasta')
            
            # Extract conservation scores for the target accession
            scores_map = extract_conservation_scores_for_accession(alignment)
            
            # Save to text file (original format)
            output_file = os.path.join(output_dir, f"{gene}_conservation_scores.txt")
            with open(output_file, 'w') as f:
                f.write(f"# Conservation scores for {gene}, accession GCF_000146045.2\n")
                f.write("# Position\tConservation_Score\n")
                
                for pos in sorted(scores_map.keys()):
                    f.write(f"{pos}\t{scores_map[pos]:.4f}\n")
            
            # Create Chimera attribute file (.defattr format)
            chimera_file = os.path.join(output_dir, f"{gene}_conservation.defattr")
            with open(chimera_file, 'w') as f:
                # Header for attribute definition
                f.write(f"# Chimera attribute definition for {gene} conservation scores\n")
                f.write("attribute: conservation\n")
                f.write("match mode: 1-to-1\n")
                f.write("recipient: residues\n")
                
                # Write each residue's conservation score
                for pos in sorted(scores_map.keys()):
                    f.write(f"\t:{pos}\t{scores_map[pos]:.4f}\n")
            
            # Create 3Dmol.js compatible JSON file
            threejs_file = os.path.join(output_dir, f"{gene}_conservation_3dmol.json")
            
            # Format for 3Dmol.js - mapping of residue numbers to conservation scores
            threejs_data = {str(pos): float(scores_map[pos]) for pos in sorted(scores_map.keys())}
            
            with open(threejs_file, 'w') as f:
                json.dump(threejs_data, f, indent=2)
            # Copy JSON file to Mol* conservation directory
            shutil.copy(threejs_file, os.path.join(molstar_conservation_dir, f"{gene}_conservation_3dmol.json"))
            
            print(f"Saved conservation scores for {gene} to {output_file}")
            print(f"Saved Chimera attribute file to {chimera_file}")
            print(f"Saved 3Dmol.js compatible file to {threejs_file}")
            
        except Exception as e:
            print(f"Error processing {gene}: {str(e)}")

if __name__ == "__main__":
    main()
