import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import itertools
from matplotlib.colors import rgb2hex
import numba as nb
from numba import types
from numba.typed import Dict, List
import matplotlib.colors as mcolors
import os
import matplotlib.animation as animation
from matplotlib.lines import Line2D

matplotlib.use('Agg')

@nb.njit
def get_colors_numba(rows, cols, phyla_indices, pair_to_color_idx):
    """Numba-accelerated function to determine colors based on phylum pairs"""
    n = len(rows)
    color_indices = np.empty(n, dtype=np.int64)
    
    for k in range(n):
        i, j = rows[k], cols[k]
        phylum_i = phyla_indices[i]
        phylum_j = phyla_indices[j]
        
        # Ensure consistent ordering for pair lookup
        if phylum_i > phylum_j:
            pair_key = (phylum_j, phylum_i)
        else:
            pair_key = (phylum_i, phylum_j)
            
        color_indices[k] = pair_to_color_idx[pair_key]
        
    return color_indices


def plot_dms(dm1, dm2, dm1_name='dm1', dm2_name='dm2', to_remove=None):
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

    # Remove specified accessions if to_remove is provided
    if to_remove is not None:
        # Clean up the accessions to remove (remove newlines and whitespace)
        to_remove = [acc.strip() for acc in to_remove]
        
        # Create mask for rows to keep
        keep_mask = ~dm1.iloc[:, 0].isin(to_remove)
        
        # Get integer indices from boolean mask
        keep_indices = np.where(keep_mask)[0]
        
        # Filter both matrices
        dm1 = dm1.iloc[keep_indices].reset_index(drop=True)
        dm2 = dm2.iloc[keep_indices].reset_index(drop=True)
        
        # Filter columns (excluding first column which contains accessions)
        col_indices = [0] + [i + 1 for i in keep_indices]  # +1 because first column is accessions
        dm1 = dm1.iloc[:, col_indices]
        dm2 = dm2.iloc[:, col_indices]

    # Continue with numerical part extraction
    accessions = dm1.iloc[:, 0].tolist()  # Save accessions before removing the column
    dm1 = dm1.iloc[:, 1:]
    dm2 = dm2.iloc[:, 1:]

    # Convert to numpy arrays
    dm1_array = dm1.to_numpy()
    dm2_array = dm2.to_numpy()
    
    # Load taxa information to get phyla
    taxa_df = pd.read_csv('/zhome/85/8/203063/a3_fungi/data_out/taxa_no_missing.csv')
    taxa_dict = dict(zip(taxa_df['Accession'].str[:15], taxa_df['Phylum']))
    
    # Map accessions to phyla
    phyla = [taxa_dict.get(acc, "Unknown") for acc in accessions]
    
    # Get unique phylum pairs and assign colors
    unique_phyla = sorted(set(phyla))
    phyla_pairs = list(itertools.combinations_with_replacement(unique_phyla, 2))
    
    # Create mapping from phylum name to index for numba
    phylum_to_idx = {phylum: i for i, phylum in enumerate(unique_phyla)}
    phyla_indices = np.array([phylum_to_idx[p] for p in phyla], dtype=np.int64)
    
    # TOL 27 color palette (colorblind-friendly)
    tol_27_colors = [
        '#332288', '#117733', '#44AA99', '#88CCEE', '#DDCC77', '#CC6677', '#AA4499',
        '#882255', '#6699CC', '#661100', '#DD6677', '#AA4466', '#4477AA', '#228833',
        '#CCBB44', '#EE8866', '#BBCC33', '#AAAA00', '#EEDD88', '#FFAABB', '#77AADD',
        '#99DDFF', '#44BB99', '#DDDDDD', '#000000', '#FFFFFF', '#BBBBBB'
    ]
    
    # Create color list for phylum pairs, cycling if needed
    color_list = []
    for i in range(len(phyla_pairs)):
        color_idx = i % len(tol_27_colors)
        color_list.append(tol_27_colors[color_idx])
    
    # Create numba-compatible mapping from pair indices to color indices
    pair_to_color_idx = Dict.empty(
        key_type=types.UniTuple(types.int64, 2),
        value_type=types.int64
    )
    
    for i, pair in enumerate(phyla_pairs):
        idx_pair = (phylum_to_idx[pair[0]], phylum_to_idx[pair[1]])
        pair_to_color_idx[idx_pair] = i
    
    print(f"Number of unique phyla: {len(unique_phyla)}")
    print(f"Number of possible phylum pairs: {len(phyla_pairs)}")

    # Get upper triangle indices with the original i, j positions
    rows, cols = np.triu_indices(dm1_array.shape[0], k=1)
    
    # Extract distances using these indices
    dm1_flat = dm1_array[rows, cols]
    dm2_flat = dm2_array[rows, cols]
    
    # Use numba-accelerated function to get color indices
    color_indices = get_colors_numba(rows, cols, phyla_indices, pair_to_color_idx)
    
    # Map color indices back to actual colors
    colors = [color_list[idx] for idx in color_indices]
    
    print(dm1_array.shape)
    print(dm2_array.shape)
    print(dm1_flat.shape)
    print(dm2_flat.shape)
    
    # Create the scatter plot with phylum-based colors
    plt.figure(figsize=(8, 8))
    plt.scatter(dm1_flat, dm2_flat, s=2, c=colors, alpha=0.5, rasterized=True)
    
    # Add diagonal line (y=x)
    min_val = min(dm1_flat.min(), dm2_flat.min())
    max_val = max(dm1_flat.max(), dm2_flat.max())
    plt.plot([min_val, max_val], [min_val, max_val], 'k--', alpha=0.5, label='y=x')
    
    plt.xlabel(dm1_name)
    plt.ylabel(dm2_name)
    plt.title('Distance Matrix Comparison Colored by Phylum Pairs')
    
    print('Adding legend...')
    # Add legend for phylum pairs with fewer marker points
    legend_elements = [plt.Line2D([0], [0], marker='o', color='w', 
                                  label=f"{pair[0]}-{pair[1]}",
                                  markerfacecolor=color_list[i], markersize=5,
                                  markevery=10)  # Use fewer marker points
                       for i, pair in enumerate(phyla_pairs)]
    
    print('Creating legend...')
    plt.legend(handles=legend_elements, title="Phylum Pairs", 
               bbox_to_anchor=(1.05, 1), loc='upper left',
               prop={'size': 6}, title_fontsize=8)
    print('Saving plot...')
    plt.savefig('figures/dm_comparison_by_phyla.png', dpi=150, bbox_inches='tight', format='png')
    
    # Create directory for individual phylum pair plots
    indiv_plots_dir = 'figures/phylum_pair_plots'
    os.makedirs(indiv_plots_dir, exist_ok=True)
    
    print('Creating individual plots for each phylum pair...')
    
    # Dictionary to store plot filenames for animation
    plot_files = []
    
    # For each phylum pair, create a separate plot
    for i, pair in enumerate(phyla_pairs):
        plt.figure(figsize=(6, 6))
        
        # Find indices where this pair occurs
        pair_indices = [j for j, idx in enumerate(color_indices) if idx == i]
        
        # Get data for this pair
        pair_dm1 = dm1_flat[pair_indices]
        pair_dm2 = dm2_flat[pair_indices]
        
        # Plot data for this pair
        plt.scatter(pair_dm1, pair_dm2, s=2, c=color_list[i], alpha=0.5)
        
        # Add diagonal line
        plt.plot([min_val, max_val], [min_val, max_val], 'k--', alpha=0.5)
        
        plt.xlabel(dm1_name)
        plt.ylabel(dm2_name)
        plt.title(f'Distance Matrix Comparison: {pair[0]}-{pair[1]}')
        
        # Save individual plot
        plot_filename = f'{indiv_plots_dir}/pair_{i:02d}_{pair[0]}_{pair[1]}.png'
        plt.savefig(plot_filename, dpi=300)
        plt.close()
        
        plot_files.append(plot_filename)
    
    # Create animation from individual plots
    print('Creating animation...')
    try:
        # Create figure for animation
        fig, ax = plt.subplots(figsize=(6, 6))
        
        def update(frame):
            ax.clear()
            # Load image from file
            img = plt.imread(plot_files[frame])
            # Display image
            ax.imshow(img)
            ax.axis('off')
            return [ax]
        
        # Create animation
        ani = animation.FuncAnimation(fig, update, frames=len(plot_files), 
                                      interval=500, blit=True)
        
        # Save animation
        ani.save('figures/phylum_pairs_animation.gif', writer='pillow', dpi=100)
        plt.close(fig)
        print('Animation saved successfully!')
    except Exception as e:
        print(f"Could not create animation: {e}")
        print("Individual plots are still available in the directory.")
    
    # Also save the original version without the legend for comparison
    plt.figure(figsize=(6, 6))
    plt.scatter(dm1_flat, dm2_flat, s=1, color='black', alpha=0.2, rasterized=True)
    # Add diagonal line
    plt.plot([min_val, max_val], [min_val, max_val], 'k--', alpha=0.5)
    plt.xlabel(dm1_name)
    plt.ylabel(dm2_name)
    plt.title('Distance Matrix Comparison')
    plt.savefig('figures/dm_comparison.png', dpi=150, format='png')

if __name__ == '__main__':

    with open('/zhome/85/8/203063/a3_fungi/data_out/interpro/all_missing.txt', 'r') as file:
        to_remove = file.readlines()

    dm1_path = '/zhome/85/8/203063/a3_fungi/full_dist_mats/enzyme_phyl.csv'
    dm1_name = 'AAA enzyme phyl'

    dm2_path = '/zhome/85/8/203063/a3_fungi/full_dist_mats/busco_phyl.csv'
    dm2_name = 'BUSCO phyl'
    
    dm1 = pd.read_csv(dm1_path, sep=r'\s+', header=None, skiprows=1)
    dm2 = pd.read_csv(dm2_path, sep=r'\s+', header=None, skiprows=1)

    plot_dms(dm1, dm2, dm1_name, dm2_name, to_remove)

