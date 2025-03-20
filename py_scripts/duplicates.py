import numpy as np
import pandas as pd
from tqdm import tqdm
from numba import jit

def clean_sequence(seq):
    """Remove gap characters and X from sequence"""
    return seq.replace('-', '').replace('X', '')


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

def manage_duplicates(in_fasta, unique_fasta, mat_dist):
    """
    Fill in distances for duplicate sequences in the distance matrix.
    
    Args:
        in_fasta (str): Path to original FASTA file with duplicates
        unique_fasta (str): Path to FASTA file with duplicates removed
        mat_dist (numpy.ndarray): Distance matrix for unique sequences
    
    Returns:
        pandas.DataFrame: Updated distance matrix including duplicates
    """
    # Create mapping dictionaries
    orig_seqs = {}
    unique_seqs = {}
    dup_to_unique = {}
    
    # Read original sequences
    with open(in_fasta, 'r') as f:
        header = ""
        for line in f:
            if line.startswith('>'):
                header = line.strip()[1:]
            else:
                orig_seqs[header] = clean_sequence(line.strip())
    
    unique_seqs = pd.read_csv(unique_fasta, sep='\s+', header=None, skiprows=1)
    unique_seqs = {row[0]: clean_sequence(row[1]) for row in unique_seqs.itertuples(index=False)}

    # Create mapping for cleaned sequences
    for orig_header, orig_seq in orig_seqs.items():
        found_match = False
        for unique_header, unique_seq in unique_seqs.items():
            if orig_seq == unique_seq:
                dup_to_unique[orig_header] = unique_header
                found_match = True
                break
        if not found_match:
            print(f"No match found for sequence: {orig_header}")
            print(f"Original sequence: {orig_seq[:50]}...")  # Print first 50 chars
            print("Available unique sequences:")
            for k, v in unique_seqs.items():
                print(f"{k}: {v[:50]}...")
            raise ValueError(f"Could not find unique sequence match for {orig_header}")
    
    # Create new matrix with space for duplicates
    n_total = len(orig_seqs)
    #print(dup_to_unique)
    # Create index mapping
    headers = list(orig_seqs.keys())
    header_to_idx = {h: i for i, h in enumerate(headers)}
    
    # Prepare index mappings for numba
    idx_map_unique1 = np.array([list(unique_seqs.keys()).index(dup_to_unique[h]) for h in headers])
    idx_map_unique2 = np.array([list(unique_seqs.keys()).index(dup_to_unique[h]) for h in headers])
    
    # Use accelerated function
    full_mat = fill_distance_matrix(n_total, idx_map_unique1, idx_map_unique2, mat_dist)
    
    # Create DataFrame with accessions
    df_full = pd.DataFrame(full_mat, index=headers, columns=headers)
    # Reset index to make accessions a column
    df_full.reset_index(inplace=True)
    df_full.rename(columns={'index': ''}, inplace=True)
    
    return df_full

if __name__ == '__main__':
    import pandas as pd
    import numpy as np
    
    in_fasta = '/work3/s233201/enzyme_out_3/ACO2.fasta'
    unique_fasta = '/work3/s233201/enzyme_out_3/enzyme_trees/ACO2/tree_iq_multi_LGI.uniqueseq.phy'
    mat_dist_name = '/work3/s233201/enzyme_out_3/enzyme_trees/ACO2/tree_iq_multi_LGI.mldist'

    mat_dist= pd.read_csv(mat_dist_name, 
                                sep='\s+',
                                header=None,
                                skiprows=1)

    mat_dist = mat_dist.iloc[:, 1:].to_numpy()
    full_mat = manage_duplicates(in_fasta, unique_fasta, mat_dist)

    output_path = '/zhome/85/8/203063/a3_fungi/full_dist_mats/full_mat_ACO2.csv'
    full_mat.to_csv(output_path, sep=' ', index=False)

    print(full_mat.shape)