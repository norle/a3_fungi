import os
import glob
import pandas as pd
from collections import defaultdict

def get_fasta_accessions(fasta_file):
    accessions = set()
    with open(fasta_file, 'r') as f:
        for line in f:
            if line.startswith('>'):
                accession = line.strip().split()[0][1:]
                accessions.add(accession)
    return accessions

def print_distribution(df, title):
    print(f"\n=== {title} ===")
    
    # Distribution by Phylum
    phylum_dist = df['Phylum'].value_counts()
    print("\nPhylum distribution:")
    for phylum, count in phylum_dist.items():
        percentage = (count / len(df)) * 100
        print(f"{phylum}: {count} ({percentage:.2f}%)")
    
    print(f"\nTotal sequences: {len(df)}")

def main():
    # Read taxa_clean.csv
    taxa_df = pd.read_csv('/zhome/85/8/203063/a3_fungi/data_out/taxa_clean.csv')
    
    # Print original distribution
    print_distribution(taxa_df, "Original Distribution")
    
    # Get all FASTA files
    fasta_files = glob.glob('/work3/s233201/enzyme_out/*.fasta')
    
    # Get accessions that appear in ALL FASTA files
    first_file = True
    common_accessions = set()
    
    for fasta_file in fasta_files:
        file_accessions = get_fasta_accessions(fasta_file)
        if first_file:
            common_accessions = file_accessions
            first_file = False
        else:
            common_accessions = common_accessions.intersection(file_accessions)
    
    # Filter dataframe to only include accessions that appear in ALL FASTA files
    filtered_df = taxa_df[taxa_df['Accession'].isin(common_accessions)]
    
    # Print filtered distribution
    print_distribution(filtered_df, "Distribution After Removing Sequences with Missing Data")
    
    # Calculate how many sequences were removed
    removed_count = len(taxa_df) - len(filtered_df)
    print(f"\nNumber of sequences removed: {removed_count}")
    print(f"Percentage of sequences removed: {(removed_count/len(taxa_df))*100:.2f}%")

    taxa_df.to_csv('/zhome/85/8/203063/a3_fungi/data_out/taxa_no_missing.csv', index=False)

if __name__ == "__main__":
    main()
