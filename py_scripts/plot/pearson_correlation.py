import sys
import pandas as pd
import numpy as np
from scipy.stats import pearsonr, spearmanr

def compute_correlations(df1, df2):
    """Compute both Pearson and Spearman correlations between two DataFrames"""
    # Select only numeric columns from both DataFrames
    df1_numeric = df1.select_dtypes(include=[np.number])
    df2_numeric = df2.select_dtypes(include=[np.number])
    # Flatten the numeric values
    arr1 = df1_numeric.values.flatten()
    arr2 = df2_numeric.values.flatten()
    pearson_corr, pearson_p = pearsonr(arr1, arr2)
    spearman_corr, spearman_p = spearmanr(arr1, arr2)
    return pearson_corr, pearson_p, spearman_corr, spearman_p

if __name__ == '__main__':
    dm1_path = '/zhome/85/8/203063/a3_fungi/full_dist_mats/enzyme_phyl_correct_6.csv'
    dm2_path = '/zhome/85/8/203063/a3_fungi/full_dist_mats/phyl_busco_4_correct.csv'
    # Use same CSV format as in plot_dms_datashader
    dm1 = pd.read_csv(dm1_path, sep=r'\s+', header=None, skiprows=1)
    dm2 = pd.read_csv(dm2_path, sep=r'\s+', header=None, skiprows=1)
    
    # Align dataframes based on accession IDs (first column)
    dm1.iloc[:, 0] = dm1.iloc[:, 0].str[:15]
    dm2.iloc[:, 0] = dm2.iloc[:, 0].str[:15]
    dm1_order = dm1.iloc[:, 0].tolist()
    dm2_order = dm2.iloc[:, 0].tolist()
    common_entries = list(set(dm1_order) & set(dm2_order))
    keep_indices_dm1 = [i for i, acc in enumerate(dm1_order) if acc in common_entries]
    keep_indices_dm2 = [i for i, acc in enumerate(dm2_order) if acc in common_entries]
    dm1 = dm1.iloc[keep_indices_dm1].reset_index(drop=True)
    dm2 = dm2.iloc[keep_indices_dm2].reset_index(drop=True)
    col_indices_dm1 = [0] + [i+1 for i in keep_indices_dm1]
    col_indices_dm2 = [0] + [i+1 for i in keep_indices_dm2]
    dm1 = dm1.iloc[:, col_indices_dm1]
    dm2 = dm2.iloc[:, col_indices_dm2]
    dm1_order = dm1.iloc[:, 0].tolist()
    dm2_order = dm2.iloc[:, 0].tolist()
    order_mapping = [dm2_order.index(x) for x in dm1_order]
    dm2 = dm2.iloc[order_mapping]
    dm2_cols = dm2.columns.tolist()
    dm2 = dm2[[dm2_cols[0]] + [dm2_cols[i+1] for i in order_mapping]]
    
    # Use the numeric part of the matrices (exclude accession column)
    df1_numeric = dm1.iloc[:, 1:]
    df2_numeric = dm2.iloc[:, 1:]
    
    # Read outliers
    with open('/zhome/85/8/203063/a3_fungi/data/outliers_set.txt', 'r') as f:
        to_remove = {line.strip() for line in f}

    # Filter out outliers from common entries
    common_entries = [entry for entry in common_entries if entry not in to_remove]
    
    # Re-filter dataframes based on updated common entries
    keep_indices_dm1 = [i for i, acc in enumerate(dm1_order) if acc in common_entries]
    keep_indices_dm2 = [i for i, acc in enumerate(dm2_order) if acc in common_entries]
    dm1 = dm1.iloc[keep_indices_dm1].reset_index(drop=True)
    dm2 = dm2.iloc[keep_indices_dm2].reset_index(drop=True)
    col_indices_dm1 = [0] + [i+1 for i in keep_indices_dm1]
    col_indices_dm2 = [0] + [i+1 for i in keep_indices_dm2]
    dm1 = dm1.iloc[:, col_indices_dm1]
    dm2 = dm2.iloc[:, col_indices_dm2]
    dm1_order = dm1.iloc[:, 0].tolist()
    dm2_order = dm2.iloc[:, 0].tolist()
    order_mapping = [dm2_order.index(x) for x in dm1_order]
    dm2 = dm2.iloc[order_mapping]
    dm2_cols = dm2.columns.tolist()
    dm2 = dm2[[dm2_cols[0]] + [dm2_cols[i+1] for i in order_mapping]]
    
    # Calculate correlations
    pearson_corr, pearson_p, spearman_corr, spearman_p = compute_correlations(df1_numeric, df2_numeric)
    
    print("=== After removing outliers ===")
    print("Pearson correlation coefficient:", pearson_corr)
    print("Pearson P-value: {:.2e}".format(pearson_p))
    print("Spearman correlation coefficient:", spearman_corr)
    print("Spearman P-value: {:.2e}".format(spearman_p))