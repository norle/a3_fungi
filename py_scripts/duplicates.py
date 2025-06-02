import numpy as np
import pandas as pd
from tqdm import tqdm
from numba import jit
import re

@jit(nopython=True)
def fill_distance_matrix(n_total, idx_map_unique1, idx_map_unique2, mat_dist):
    """Fill distance matrix using numba acceleration"""
    full_mat = np.zeros((n_total, n_total))
    for i in range(n_total):
        for j in range(i):  # Only fill lower triangle
            idx1 = idx_map_unique1[i]
            idx2 = idx_map_unique2[j]
            dist = mat_dist[idx1, idx2]
            full_mat[i, j] = dist
            full_mat[j, i] = dist  # Mirror
    return full_mat

def manage_duplicates(in_fasta, unique_fasta, mat_dist, log_file):
    """
    Fill in distances for duplicate sequences in the distance matrix.
    
    Args:
        in_fasta (str): Path to original FASTA file with duplicates
        unique_fasta (str): Path to FASTA file with duplicates removed
        mat_dist (numpy.ndarray): Distance matrix for unique sequences
        log_file (str): Path to IQ-TREE log file containing duplicate information
    
    Returns:
        pandas.DataFrame: Updated distance matrix including duplicates
    """
    # Read the unique sequences to get the base mapping
    unique_seqs = pd.read_csv(unique_fasta, sep='\s+', header=None, skiprows=1)
    unique_headers = unique_seqs[0].tolist()
    
    # Create duplicate mapping from log file
    dup_to_unique = {}
    with open(log_file, 'r') as f:
        for line in f:
            m = re.search(r"NOTE:\s+(\S+)\s+\(identical to\s+(\S+)\)", line)
            if m:
                dup, orig = m.groups()
                dup_to_unique[dup] = orig
    
    # Add non-duplicate sequences to the mapping
    for header in unique_headers:
        dup_to_unique[header] = header
    
    # Read original headers from FASTA
    headers = []
    with open(in_fasta, 'r') as f:
        for line in f:
            if line.startswith('>'):
                headers.append(line.strip()[1:])
    
    # Create index mappings for numba
    unique_header_to_idx = {h: i for i, h in enumerate(unique_headers)}
    idx_map_unique1 = np.array([unique_header_to_idx[dup_to_unique[h]] for h in headers])
    idx_map_unique2 = np.array([unique_header_to_idx[dup_to_unique[h]] for h in headers])
    
    # Generate full matrix
    n_total = len(headers)
    full_mat = fill_distance_matrix(n_total, idx_map_unique1, idx_map_unique2, mat_dist)
    
    # Create DataFrame with accessions
    df_full = pd.DataFrame(full_mat, index=headers, columns=headers)
    df_full.reset_index(inplace=True)
    df_full.rename(columns={'index': ''}, inplace=True)
    
    return df_full

def enzyme_matrices():

    gene_names = ["LYS20", "ACO2", "LYS4", "LYS12", "ARO8", "LYS2", "LYS9", "LYS1"]
    for gene_name in gene_names:
        base_dir = '/work3/s233201/enzyme_out_7/enzyme_trees'
        in_fasta = f'/work3/s233201/enzyme_out_7/{gene_name}.fasta'
        unique_fasta = f'{base_dir}/{gene_name}/tree_iq_multi_LGI.uniqueseq.phy'
        mat_dist_name = f'{base_dir}/{gene_name}/tree_iq_multi_LGI.mldist'
        log_file = f'{base_dir}/{gene_name}/tree_iq_multi_LGI.log'

        mat_dist = pd.read_csv(mat_dist_name, sep=r'\s+', header=None, skiprows=1)
        mat_dist = mat_dist.iloc[:, 1:].to_numpy()
        
        full_mat = manage_duplicates(in_fasta, unique_fasta, mat_dist, log_file)
        output_path = f'/zhome/85/8/203063/a3_fungi/full_dist_mats/fast/full_mat_{gene_name}.csv'
        full_mat.to_csv(output_path, sep=' ', index=False)
        print(full_mat.shape)

def single_matrix():

    main_dir = '/work3/s233201/output_phyl_busco_4'
    in_fasta = f'{main_dir}/supermatrix/final.fasta'
    
    
    unique_fasta = f'{main_dir}/tree_iq_LGI.uniqueseq.phy'
    mat_dist_name = f'{main_dir}/tree_iq_LGI.mldist'
    log_file = f'{main_dir}/tree_iq_LGI.log'

    output_path = f'/zhome/85/8/203063/a3_fungi/full_dist_mats/phyl_busco_4_correct.csv'

    # main_dir = '/work3/s233201/output_phyl_busco_4'
    # in_fasta = f'{main_dir}/final.fasta'
    
    
    # unique_fasta = f'{main_dir}/tree_iq_LGI.uniqueseq.phy'
    # mat_dist_name = f'{main_dir}/tree_iq_LGI.mldist'
    # log_file = f'{main_dir}/tree_iq_LGI.log'

    # output_path = f'/zhome/85/8/203063/a3_fungi/full_dist_mats/busco_phyl_4.csv'

    mat_dist = pd.read_csv(mat_dist_name, sep=r'\s+', header=None, skiprows=1)
    mat_dist = mat_dist.iloc[:, 1:].to_numpy()

    full_mat = manage_duplicates(in_fasta, unique_fasta, mat_dist, log_file)
    
    full_mat.to_csv(output_path, sep=' ', index=False)
    print(full_mat.shape)

if __name__ == '__main__':

    #single_matrix()
    enzyme_matrices()