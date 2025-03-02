import os
import glob
import pandas as pd
from collections import defaultdict

def get_fasta_accessions(fasta_file):
    accessions = set()
    with open(fasta_file, 'r') as f:
        for line in f:
            if line.startswith('>'):
                accession = line.strip().split()[0][1:]  # Remove '>' and take first part
                accessions.add(accession)
    return accessions

def main():
    # Read all FASTA files
    fasta_files = glob.glob('/work3/s233201/enzyme_out/*.fasta')
    
    # Read taxa_clean.csv
    taxa_df = pd.read_csv('/zhome/85/8/203063/a3_fungi/data_out/taxa_clean.csv')
    taxa_accessions = set(taxa_df['Accession'])
    
    # Create set for all FASTA accessions
    all_fasta_accessions = set()
    
    # Analyze each FASTA file separately
    for fasta_file in fasta_files:
        file_name = os.path.basename(fasta_file)
        print(f"\n=== Analysis for {file_name} ===")
        
        # Get accessions for this file
        file_accessions = get_fasta_accessions(fasta_file)
        all_fasta_accessions.update(file_accessions)  # Add to combined set
        
        # Find missing accessions for this file
        missing_accessions = taxa_accessions - file_accessions
        
        # Count missing by phylum
        phylum_counts = defaultdict(int)
        for acc in missing_accessions:
            phylum = taxa_df[taxa_df['Accession'] == acc]['Phylum'].iloc[0]
            phylum_counts[phylum] += 1
        
        # Print results for this file
        print("\nMissing sequences by phylum:")
        for phylum, count in sorted(phylum_counts.items()):
            print(f"{phylum}: {count}")
        
        print(f"\nTotal missing sequences: {len(missing_accessions)}")
        print(f"Total sequences in taxa_clean: {len(taxa_accessions)}")
        print(f"Total sequences in this FASTA file: {len(file_accessions)}")
        #print("=" * 50)
    
    # Combined analysis for all files
    print("\n=== Combined Analysis for All FASTA Files ===")
    
    # Find missing accessions across all files
    total_missing_accessions = taxa_accessions - all_fasta_accessions
    
    # Count missing by phylum
    total_phylum_counts = defaultdict(int)
    for acc in total_missing_accessions:
        phylum = taxa_df[taxa_df['Accession'] == acc]['Phylum'].iloc[0]
        total_phylum_counts[phylum] += 1
    
    # Print combined results
    print("\nMissing sequences by phylum (across all files):")
    for phylum, count in sorted(total_phylum_counts.items()):
        print(f"{phylum}: {count}")
    
    print(f"\nTotal missing sequences: {len(total_missing_accessions)}")
    print(f"Total sequences in taxa_clean: {len(taxa_accessions)}")
    print(f"Total unique sequences found in all FASTA files: {len(all_fasta_accessions)}")

if __name__ == "__main__":
    main()
