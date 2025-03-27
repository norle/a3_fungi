import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def plot_dms(dm1, dm2, dm1_name='dm1', dm2_name='dm2'):
    # Align both dms
    dm1.iloc[:, 0] = dm1.iloc[:, 0].str[:15]
    dm2.iloc[:, 0] = dm2.iloc[:, 0].str[:15]
    
    dm1_order = dm1.iloc[:, 0].tolist()
    
    # Create mapping for reordering dm2
    dm2_order = dm2.iloc[:, 0].tolist()
    order_mapping = [dm2_order.index(x) for x in dm1_order]
    
    # Reorder rows of dm2
    dm2 = dm2.iloc[order_mapping]
    
    # Reorder columns of dm2 (excluding first column)
    dm2_cols = dm2.columns.tolist()
    dm2 = dm2[[dm2_cols[0]] + [dm2_cols[i+1] for i in order_mapping]]

    # Continue with numerical part extraction
    dm1 = dm1.iloc[:, 1:]
    dm2 = dm2.iloc[:, 1:]

    # Convert to numpy arrays
    dm1_array = dm1.to_numpy()
    dm2_array = dm2.to_numpy()

    print(dm1_array.shape)
    print(dm2_array.shape)

    # Plot the matrices
    # Flatten the upper triangle of the distance matrices
    triu_indices = np.triu_indices(dm1_array.shape[0], k=1)
    dm1_flat = dm1_array[triu_indices]
    dm2_flat = dm2_array[triu_indices]
    
    print(dm1_flat.shape)
    print(dm2_flat.shape)
    print(dm1_flat[:10])
    print(dm2_flat[:10])
    # Create the scatter plot
    plt.figure(figsize=(6, 6))
    plt.scatter(dm1_flat, dm2_flat, s=1, color='black', alpha=0.2)
    plt.xlabel(dm1_name)
    plt.ylabel(dm2_name)
    plt.title('Distance Matrix Comparison')
    plt.savefig('figures/dm_comparison.png', dpi=300)

if __name__ == '__main__':

    dm1_path = '/zhome/85/8/203063/a3_fungi/full_dist_mats/enzyme_phyl.csv'
    dm1_name = 'AAA enzyme phyl'

    dm2_path = '/zhome/85/8/203063/a3_fungi/full_dist_mats/busco_phyl.csv'
    dm2_name = 'BUSCO phyl'
    
    dm1 = pd.read_csv(dm1_path, sep=r'\s+', header=None, skiprows=1)
    dm2 = pd.read_csv(dm2_path, sep=r'\s+', header=None, skiprows=1)

    plot_dms(dm1, dm2, dm1_name, dm2_name)

