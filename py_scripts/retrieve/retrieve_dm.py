from ete3 import Tree
import pandas as pd
import numpy as np
import gzip
import pickle
from tqdm import tqdm

def get_distance_matrix(tree_file):
    """
    Extract pairwise distances from an IQ-TREE generated tree file.
    Can handle both plain and gzipped tree files.
    
    Args:
        tree_file (str): Path to the tree file in Newick format (plain or gzipped)
    
    Returns:
        pd.DataFrame: Distance matrix with species names as index and columns
    """
    # Handle gzipped tree files
    if tree_file.endswith('.gz'):
        with gzip.open(tree_file, 'rt') as f:  # 'rt' mode for text reading
            newick_str = f.read()
        tree = Tree(newick_str)
    else:
        tree = Tree(tree_file)
    
    # Get all leaf names
    leaves = tree.get_leaf_names()
    
    # Initialize distance matrix
    n_species = len(leaves)
    dist_matrix = np.zeros((n_species, n_species))
    
    # Calculate pairwise distances
    for i, sp1 in enumerate(tqdm(leaves, desc="Calculating distances")):
        for j, sp2 in enumerate(leaves):
            if i != j:
                dist_matrix[i, j] = tree.get_distance(sp1, sp2)
    
    # Create DataFrame with species names
    dm_df = pd.DataFrame(dist_matrix, index=leaves, columns=leaves)
    
    return dm_df

def load_pickled_matrix(pickle_file):
    """
    Load a distance matrix from a pickled gzip file.
    
    Args:
        pickle_file (str): Path to the .gzp file
    
    Returns:
        pd.DataFrame: Distance matrix
    """
    with gzip.open(pickle_file, 'rb') as f:
        data = pickle.load(f)
    return data['D_out'] if isinstance(data, dict) else data

def load_model_gz(model_file):
    """
    Load a distance matrix from an IQ-TREE model file.
    
    Args:
        model_file (str): Path to the .model.gz file
    
    Returns:
        pd.DataFrame: Distance matrix
"""
    with gzip.open(model_file, 'rb') as f:
        data = pickle.load(f)
        if isinstance(data, dict) and 'dist_matrix' in data:
            return pd.DataFrame(data['dist_matrix'])
        elif isinstance(data, dict) and 'D_out' in data:
            return data['D_out']
        else:
            print("Available keys in data:", data.keys() if isinstance(data, dict) else "Not a dictionary")
    # Save the distance matrix to a compressed CSV file
    distance_matrix.to_csv("data/distance_matrix.csv.gz", compression="gzip")

# Example usage
tree_file = "/work3/s233201/enzyme_out/final_iq_fg.treefile"
distance_matrix = get_distance_matrix(tree_file)

