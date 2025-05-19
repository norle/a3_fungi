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
import datashader as ds
from datashader.colors import colormap_select, Greys9
from datashader.utils import export_image
import colorcet as cc
import holoviews as hv
from holoviews.operation.datashader import datashade, shade
hv.extension('bokeh')

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
    # Clean up and standardize accession IDs
    dm1.iloc[:, 0] = dm1.iloc[:, 0].str[:15]
    dm2.iloc[:, 0] = dm2.iloc[:, 0].str[:15]
    
    dm1_order = dm1.iloc[:, 0].tolist()
    dm2_order = dm2.iloc[:, 0].tolist()
    
    # Find common entries between dm1 and dm2
    common_entries = list(set(dm1_order) & set(dm2_order))
    missing_entries = set(dm1_order) - set(dm2_order)
    if missing_entries:
        print(f"Warning: Following entries are missing from {dm2_name}:")
        print(missing_entries)
        print("Removing these entries from both matrices...")
    
    # Filter rows and corresponding columns for both matrices
    keep_indices_dm1 = [i for i, acc in enumerate(dm1_order) if acc in common_entries]
    keep_indices_dm2 = [i for i, acc in enumerate(dm2_order) if acc in common_entries]
    
    # Filter rows
    dm1 = dm1.iloc[keep_indices_dm1].reset_index(drop=True)
    dm2 = dm2.iloc[keep_indices_dm2].reset_index(drop=True)
    
    # Filter columns (excluding first column which contains accessions)
    col_indices_dm1 = [0] + [i + 1 for i in keep_indices_dm1]
    col_indices_dm2 = [0] + [i + 1 for i in keep_indices_dm2]
    
    dm1 = dm1.iloc[:, col_indices_dm1]
    dm2 = dm2.iloc[:, col_indices_dm2]
    
    # Update orders after filtering
    dm1_order = dm1.iloc[:, 0].tolist()
    dm2_order = dm2.iloc[:, 0].tolist()
    
    # Create mapping for reordering dm2
    order_mapping = [dm2_order.index(x) for x in dm1_order]
    
    # Reorder dm2 to match dm1's order
    dm2 = dm2.iloc[order_mapping]
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
    taxa_df = pd.read_csv('/zhome/85/8/203063/a3_fungi/data_out/taxa_no_missing_after_interpro.csv')
    taxa_dict = dict(zip(taxa_df['Accession'].str[:15], taxa_df['Phylum']))
    
    # Map accessions to phyla
    phyla = [taxa_dict.get(acc, "Unknown") for acc in accessions]
    
    # Get unique phylum pairs and assign colors
    unique_phyla = sorted(set(phyla))
    # Only get unique combinations (no duplicates like 'A-B' and 'B-A')
    phyla_pairs = []
    for i, p1 in enumerate(unique_phyla):
        for p2 in unique_phyla[i:]:  # Start from i to avoid duplicates
            phyla_pairs.append((p1, p2))
    
    # Create mapping from phylum name to index for numba
    phylum_to_idx = {phylum: i for i, phylum in enumerate(unique_phyla)}
    phyla_indices = np.array([phylum_to_idx[p] for p in phyla], dtype=np.int64)
    
    # TOL 27 color palette (colorblind-friendly)
    tol_27_colors = [
        '#332288', '#117733', '#44AA99', '#88CCEE', '#DDCC77', '#CC6677', '#AA4499',
        '#882255', '#6699CC', '#661100', '#DD6677', '#AA4466', '#4477AA', '#228833',
        '#CCBB44', '#EE8866', '#BBCC33', '#AAAA00', '#EEDD88', '#FFAABB', '#77AADD',
        '#99DDFF', '#44BB99', '#DDDDDD', '#000000', '#F0E442', '#BBBBBB'
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
    
    # After getting dm1_flat and dm2_flat, create a DataFrame for datashader
    df = pd.DataFrame({
        'x': dm1_flat,
        'y': dm2_flat,
        'phylum_pair': pd.Categorical([
            f"{min(phyla[rows[i]], phyla[cols[i]])}-{max(phyla[rows[i]], phyla[cols[i]])}"
            for i in range(len(rows))
        ])
    })

    # Calculate min and max values for plot ranges
    min_val = min(df['x'].min(), df['y'].min())
    max_val = max(df['x'].max(), df['y'].max())

    # Create color mapping for phylum pairs
    unique_pairs = df['phylum_pair'].unique()
    color_mapping = {pair: tol_27_colors[i % len(tol_27_colors)] 
                    for i, pair in enumerate(unique_pairs)}
    
    # Create both density and phylum-colored plots
    for plot_type in ['density', 'phylum']:
        # Create matplotlib figure and axis
        fig, ax = plt.subplots(figsize=(12, 12))
        
        canvas = ds.Canvas(plot_width=1600, plot_height=1600,
                          x_range=(min_val, max_val),
                          y_range=(min_val, max_val))
        
        if plot_type == 'density':
            agg = canvas.points(df, 'x', 'y')
            img = ds.tf.shade(agg, cmap=cc.fire)
            
            # Create proper matplotlib colormap for the colorbar
            fire_cmap = matplotlib.colors.LinearSegmentedColormap.from_list('fire', cc.fire)
        else:
            # Create a color key array that matches datashader's requirements
            color_key = {str(pair): color_mapping[pair] for pair in unique_pairs}
            
            # Use the same canvas size as density plot
            agg = canvas.points(df, 'x', 'y', agg=ds.count_cat('phylum_pair'))
            img = ds.tf.shade(agg, color_key=color_key, how='eq_hist')
            
        img = ds.tf.set_background(img, 'white')
        
        # Add diagonal line using the same canvas
        diagonal_df = pd.DataFrame({
            'x': [min_val, max_val],
            'y': [min_val, max_val]
        })
        diagonal_agg = canvas.line(diagonal_df, 'x', 'y')
        diagonal_img = ds.tf.shade(diagonal_agg, cmap=['black'])
        
        final_img = ds.transfer_functions.stack(img, diagonal_img)
        
        # Convert datashader image to matplotlib
        ax.imshow(final_img.to_pil(), extent=[min_val, max_val, min_val, max_val])
        
        # Add axes labels and title
        ax.set_xlabel(f'{dm1_name} Distance', fontsize=18)
        ax.set_ylabel(f'{dm2_name} Distance', fontsize=18)
        title = 'Density Plot' if plot_type == 'density' else 'Phylum Pairs Plot'
        ax.set_title(title, fontsize=14)
        
        # Add color bar for density plot
        if plot_type == 'density':
            norm = matplotlib.colors.Normalize(vmin=0, vmax=agg.values.max())
            sm = plt.cm.ScalarMappable(cmap=fire_cmap, norm=norm)
            cbar = plt.colorbar(sm, ax=ax, label='Density')
            # Make colorbar more compact
            cbar.ax.tick_params(labelsize=8)
            
        # Add legend for phylum plot
        elif plot_type == 'phylum':
            legend_elements = [matplotlib.patches.Patch(facecolor=color_mapping[pair],
                                                     label=pair)
                             for pair in unique_pairs]
            # Create vertical legend with small font
            legend = ax.legend(handles=legend_elements, 
                             loc='center left',
                             bbox_to_anchor=(1.02, 0.5),
                             fontsize=12,
                             ncol=1)
            # Adjust spacing between legend entries
            legend.set_draggable(True)
            plt.setp(legend.get_texts(), linespacing=1.2)

        # Save with appropriate suffix
        suffix = '_density' if plot_type == 'density' else '_phylum'
        # For phylum plot, increase right margin to accommodate legend
        if plot_type == 'phylum':
            plt.subplots_adjust(right=0.85)
        plt.savefig(f'figures/dm_comparison_datashader{suffix}.png',
                   dpi=600, bbox_inches='tight')
        plt.close()

    # Create separate plots for each phylum pair
    indiv_plots_dir = 'figures/phylum_pair_plots_datashader'
    os.makedirs(indiv_plots_dir, exist_ok=True)
    
    print('Creating individual plots for each phylum pair...')
    plot_files = []
    
    # For each phylum pair, create a separate plot
    for pair in phyla_pairs:
        # Ensure consistent ordering of pair names
        pair_name = f"{min(pair)}-{max(pair)}"
        pair_data = df[df['phylum_pair'] == pair_name]
        
        if len(pair_data) > 0:
            # Create matplotlib figure and axis
            fig, ax = plt.subplots(figsize=(12, 12))
            
            canvas = ds.Canvas(plot_width=1600, plot_height=1600,
                             x_range=(min_val, max_val),
                             y_range=(min_val, max_val))
            
            agg = canvas.points(pair_data, 'x', 'y')
            img = ds.tf.shade(agg, cmap=cc.fire)
            img = ds.tf.set_background(img, 'white')
            
            # Add diagonal line using the same method as main plot
            diagonal_img = ds.tf.shade(diagonal_agg, cmap=['black'])
            final_img = ds.transfer_functions.stack(img, diagonal_img)
            final_img = ds.tf.dynspread(final_img)
            
            # Convert datashader image to matplotlib
            ax.imshow(final_img.to_pil(), extent=[min_val, max_val, min_val, max_val])
            
            # Add axes labels and title
            ax.set_xlabel(f'{dm1_name} Distance', fontsize=12)
            ax.set_ylabel(f'{dm2_name} Distance', fontsize=12)
            ax.set_title(f'Phylum Pair: {pair_name}', fontsize=14)
            
            # Save individual plot
            plot_filename = f'{indiv_plots_dir}/pair_{min(pair)}_{max(pair)}.png'
            plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
            plt.close()
            plot_files.append(plot_filename)

    print('Plots created successfully!')

if __name__ == '__main__':
    # with open('/zhome/85/8/203063/a3_fungi/data_out/interpro/all_missing.txt', 'r') as file:
    #     to_remove = file.readlines()

    dm1_path = '/zhome/85/8/203063/a3_fungi/full_dist_mats/phyl_busco_4_correct.csv'
    dm1_name = 'AAA Enzyme Phylogenetic'

    dm2_path = '/zhome/85/8/203063/a3_fungi/full_dist_mats/busco_phyl_4.csv'
    dm2_name = 'BUSCO Phylogenetic'
    
    dm1 = pd.read_csv(dm1_path, sep=r'\s+', header=None, skiprows=1)
    dm2 = pd.read_csv(dm2_path, sep=r'\s+', header=None, skiprows=1)

    print(dm1.shape)
    print(dm2.shape)

    plot_dms(dm1, dm2, dm1_name, dm2_name)