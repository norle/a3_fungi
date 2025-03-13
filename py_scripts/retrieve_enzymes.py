import pandas as pd
import os
from tqdm import tqdm

def process_results(result_path, name, gene_dict):

    df = pd.read_csv(result_path, sep='\t', header=None, names=['Gene', 'Accession', 'E', 'Seq'])

    df = df.loc[df.groupby('Gene')['E'].idxmin()]

    genes = df['Gene'].unique()

    for gene in genes:
        fasta_string = f">{name}\n{df.loc[df['Gene'] == gene, 'Seq'].values[0]}\n"
        gene_dict[gene].append(fasta_string)

    return gene_dict

def main():

    PARENT_DIR = '/work3/s233201/fungi_proteins/'
    RESULT_DIR = '/work3/s233201/enzyme_out_1/'
    TAX_FILE = '/zhome/85/8/203063/a3_fungi/data_out/taxa_no_missing.csv'

    # Read valid accessions
    valid_accessions = pd.read_csv(TAX_FILE)['Accession'].tolist()

    if not os.path.exists(RESULT_DIR):
        os.makedirs(RESULT_DIR)

    gene_dict = {gene: [] for gene in ['LYS1', 'LYS20', 'ACO2', 'LYS4','LYS12','ARO8', 'LYS2', 'LYS9']}   

    subdirs = next(os.walk(PARENT_DIR))[1]
    for subdir in tqdm(subdirs, desc="Processing subdirectories"):
        # Only process if the accession is in our valid list
        if subdir not in valid_accessions:
            continue
            
        subdir_path = os.path.join(PARENT_DIR, subdir)
        result_path = os.path.join(subdir_path, 'results.tsv')
        if os.path.exists(result_path):
            name = os.path.basename(subdir_path)
            gene_dict = process_results(result_path, name, gene_dict)
        else:
            print(f'No results for {subdir_path}')

    for gene, sequences in gene_dict.items():
        with open(f'{RESULT_DIR}/{gene}.fasta', 'w') as f:
            f.writelines(sequences)

if __name__ == '__main__':
    main()


