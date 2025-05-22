import pandas as pd
import numpy as np

def filter_dm_pairs(dm1, dm2, dm1_range=(0.5, 1.0), dm2_range=(1.0, 1.5), outfile='filtered_pairs.txt'):
    """
    Filter pairs of accessions based on their distances in two distance matrices.
    
    Args:
        dm1, dm2: pandas DataFrames containing distance matrices
        dm1_range: tuple of (min, max) distance for first matrix
        dm2_range: tuple of (min, max) distance for second matrix
        outfile: path to output file
    """
    # Clean up and standardize accession IDs
    dm1.iloc[:, 0] = dm1.iloc[:, 0].str[:15]
    dm2.iloc[:, 0] = dm2.iloc[:, 0].str[:15]
    
    # Get common entries
    dm1_order = dm1.iloc[:, 0].tolist()
    dm2_order = dm2.iloc[:, 0].tolist()
    common_entries = list(set(dm1_order) & set(dm2_order))
    
    # Filter and reorder matrices
    keep_indices_dm1 = [i for i, acc in enumerate(dm1_order) if acc in common_entries]
    keep_indices_dm2 = [i for i, acc in enumerate(dm2_order) if acc in common_entries]
    
    dm1 = dm1.iloc[keep_indices_dm1].reset_index(drop=True)
    dm2 = dm2.iloc[keep_indices_dm2].reset_index(drop=True)
    
    # Get accessions and numerical matrices
    accessions = dm1.iloc[:, 0].tolist()
    dm1_array = dm1.iloc[:, 1:].to_numpy()
    dm2_array = dm2.iloc[:, 1:].to_numpy()
    
    # Get upper triangle indices
    rows, cols = np.triu_indices(dm1_array.shape[0], k=1)
    
    # Extract distances
    dm1_flat = dm1_array[rows, cols]
    dm2_flat = dm2_array[rows, cols]
    
    # Apply distance constraints
    mask = ((dm1_flat >= dm1_range[0]) & (dm1_flat <= dm1_range[1]) &
           (dm2_flat >= dm2_range[0]) & (dm2_flat <= dm2_range[1]))
    
    # Get filtered pairs
    filtered_pairs = []
    for idx in np.where(mask)[0]:
        acc1 = accessions[rows[idx]]
        acc2 = accessions[cols[idx]]
        d1 = dm1_flat[idx]
        d2 = dm2_flat[idx]
        filtered_pairs.append((acc1, acc2, d1, d2))
    
    # Write to file
    with open(outfile, 'w') as f:
        f.write("Acc1\tAcc2\tDM1_dist\tDM2_dist\n")
        for acc1, acc2, d1, d2 in filtered_pairs:
            f.write(f"{acc1}\t{acc2}\t{d1:.4f}\t{d2:.4f}\n")
    
    print(f"Found {len(filtered_pairs)} pairs matching the criteria")
    print(f"Results written to {outfile}")
    
    return filtered_pairs

if __name__ == '__main__':
    # Example usage
    dm1_path = '/zhome/85/8/203063/a3_fungi/full_dist_mats/enzyme_phyl_correct_6.csv'
    dm2_path = '/zhome/85/8/203063/a3_fungi/full_dist_mats/phyl_busco_4_correct.csv'    
    dm1 = pd.read_csv(dm1_path, sep=r'\s+', header=None, skiprows=1)
    dm2 = pd.read_csv(dm2_path, sep=r'\s+', header=None, skiprows=1)
    
    # Example: find pairs where dm1 distance is between 0.5 and 1.0
    # and dm2 distance is between 1.0 and 1.5
    filter_dm_pairs(dm1, dm2, 
                   dm1_range=(1, 1.2),
                   dm2_range=(0.5, 0.7),
                   outfile='/zhome/85/8/203063/a3_fungi/data/filtered_pairs.txt')
