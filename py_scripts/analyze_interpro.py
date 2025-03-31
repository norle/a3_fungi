import pandas as pd
import numpy as np
import os

def get_missing(interpro_df, queries, n=1):
    # Convert all strings in DataFrame to lowercase for case-insensitive search
    df_lower = interpro_df.astype(str).apply(lambda x: x.str.lower())
    
    # Convert all queries to lowercase
    queries_lower = [q.lower() for q in queries]
    
    # Check if any of the queries match in any column
    mask = df_lower.apply(lambda row: any(q in ' '.join(row.values) for q in queries_lower), axis=1)
    
    # Use boolean indexing with loc instead of iloc
    querried_accesions = interpro_df.loc[mask, interpro_df.columns[0]].tolist()
    
    # Get unique values and their counts in querried_accesions
    unique_accessions, counts = np.unique(querried_accesions, return_counts=True)
    
    # Filter accessions that appear at least n times
    filtered_accessions = set(unique_accessions[counts >= n])
    
    all_accesions = set(interpro_df.iloc[:, 0].tolist())
    missing_accesions = all_accesions - filtered_accessions
    
    return missing_accesions

if __name__ == "__main__":
    # Create output directory if it doesn't exist
    out_dir = '/zhome/85/8/203063/a3_fungi/data_out/interpro1'
    os.makedirs(out_dir, exist_ok=True)
    
    gene_names = ['ACO2','ARO8','LYS1','LYS2','LYS4','LYS9','LYS12','LYS20']

    queries = {
        'ACO2': ['IPR050926', 'aconitase', 'acnase', 'acoase'],
        'ARO8': ['IPR050859', 'aminotransferase', 'Pyridoxal phosphate-dependent transferase'],
        'LYS1': ['IPR027281', 'saccharopine', 'AlaDh'],
        'LYS2': ['IPR014397', 'Alpha-AR', 'aminoadipate','adenylation domain','sdr','IPR010080','NRPS', 'AMP-binding', 'Nonribosomal peptide' 'IPR014397', 'PTHR44845'],
        'LYS4': ['IPR004418', 'aconitase'],
        'LYS9': ['IPR051168', 'SACCHAROPINE', 'Sacchrp'],
        'LYS12': ['IPR024084', 'Isopropylmalate','Dehydrogenase', 'ISOCITRATE'],
        'LYS20': ['IPR050073', 'HOMOCITRATE','Aldolase'],
    }



    # Set to collect all missing accessions
    all_missing = set()
    
    for gene in gene_names:
        interpro_df = pd.read_csv(f'/zhome/85/8/203063/a3_fungi/interpro/results/{gene}.fasta.tsv', sep='\t')
        
        if gene == 'LYS2':
            missing_accesions = get_missing(interpro_df, queries[gene], n=2)
        else:
            missing_accesions = get_missing(interpro_df, queries[gene], n=1)
            
        print(f"Missing accessions for {gene}: {len(missing_accesions)}")
        
        # Save individual gene missing accessions as text
        with open(os.path.join(out_dir, f'{gene}_missing.txt'), 'w') as f:
            f.write('\n'.join(sorted(missing_accesions)))
        
        # Filter and save DataFrame for missing accessions
        missing_df = interpro_df[interpro_df.iloc[:, 0].isin(missing_accesions)]
        missing_df.to_csv(os.path.join(out_dir, f'{gene}_missing.tsv'), sep='\t', index=False)
        
        all_missing.update(missing_accesions)
        print("\n")
    
    # Report and save all missing accessions
    print(f"Total unique missing accessions across all genes: {len(all_missing)}")
    print(all_missing)
    
    # Save combined missing accessions
    with open(os.path.join(out_dir, 'all_missing.txt'), 'w') as f:
        f.write('\n'.join(sorted(all_missing)))