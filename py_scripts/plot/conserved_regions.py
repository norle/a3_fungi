import os
import glob
import numpy as np
from Bio import AlignIO
import seaborn as sns
import matplotlib.pyplot as plt
from collections import Counter
from tqdm import tqdm
from numba import jit


@jit(nopython=True)
def calculate_column_conservation(column) -> float:
    """Calculate conservation score for a single column using Numba"""
    counts = np.zeros(26, dtype=np.int32)  # 26 for A-Z plus 1 for gap
    total = 0
    
    # Count occurrences of each amino acid and gaps
    for aa in column:
        if 65 <= aa <= 90:  # ASCII values for A-Z
            counts[aa - 65] += 1
    total = len(column)

    
    # Return frequency of most common character (including gaps)
    return float(np.max(counts)) / total if total > 0 else 0.0

@jit(nopython=True)
def calculate_all_conservation_scores(alignment_array):
    """Calculate conservation scores for all positions using Numba"""
    num_positions = alignment_array.shape[1]
    conservation_scores = np.zeros(num_positions)
    
    for i in range(num_positions):
        conservation_scores[i] = calculate_column_conservation(alignment_array[:, i])
    
    return conservation_scores

def calculate_conservation(alignment):
    """Calculate conservation scores for each position in alignment"""
    # Convert alignment to numpy array of ASCII values
    alignment_array = np.array([[ord(aa) for aa in str(record.seq)] 
                              for record in alignment], dtype=np.int32)
    
    # Calculate conservation using numba-optimized function
    return calculate_all_conservation_scores(alignment_array).tolist()

def plot_conservation_heatmaps(all_scores, all_filenames, output_dir):
    """Create a figure with multiple heatmaps of conservation scores"""
    n_plots = len(all_scores)
    n_cols = 1
    n_rows = n_plots
    
    # Increased figure width to accommodate statistics
    fig = plt.figure(figsize=(20, 1.5*n_rows))  # Increased figure width
    
    # Adjusted grid ratios to give more space for stats
    gs = plt.GridSpec(n_rows, 2, width_ratios=[15, 5])
    
    # Moved colorbar position more to the left
    cbar_ax = fig.add_axes([0.83, 0.1, 0.02, 0.8])  # Changed from 0.89 to 0.86
    
    for idx, (scores, filename) in enumerate(zip(all_scores, all_filenames)):
        # Create subplot for heatmap
        ax_heat = fig.add_subplot(gs[idx, 0])
        scores_array = np.array(scores).reshape(1, -1)
        
        # Show heatmap
        sns.heatmap(scores_array, cmap='RdYlBu_r',
                    xticklabels=50,
                    yticklabels=False,
                    cbar=True if idx == 0 else False,
                    cbar_ax=cbar_ax if idx == 0 else None,
                    cbar_kws={'label': 'Conservation Score'} if idx == 0 else None,
                    vmin=0, vmax=1,
                    ax=ax_heat)
        
        # Remove x-label from all but bottom plot
        if idx != n_plots-1:
            ax_heat.set_xlabel('')
        else:
            ax_heat.set_xlabel('Alignment Position', fontsize=14)
        
        # Move title to left and make vertical
        ax_heat.set_title(f'{os.path.basename(filename).replace(".aln", "")}',
                       rotation='vertical', x=-0.015, y=0.27, fontsize=14)
        
        # Create text subplot for statistics
        ax_stats = fig.add_subplot(gs[idx, 1])
        ax_stats.axis('off')
        
        # Calculate statistics
        mean_score = np.mean(scores)
        median_score = np.median(scores)
        
        # Add statistics with larger font - moved slightly to the left
        stats_text = f'Mean: {mean_score:.2f}\nMedian: {median_score:.2f}'
        ax_stats.text(0, 0.5, stats_text,  # Changed from 0.3 to 0.2
                     transform=ax_stats.transAxes,
                     fontsize=14,
                     verticalalignment='center')
    
    # Set colorbar label fontsize
    cbar_ax.set_ylabel('Conservation Score', fontsize=14)
    
    plt.tight_layout()
    
    output_path = os.path.join(output_dir, 'all_conservation_plots.png')
    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    plt.close()

def main():
    # Create output directory for plots
    output_dir = '/zhome/85/8/203063/a3_fungi/figures/conservation_plots'
    os.makedirs(output_dir, exist_ok=True)
    
    # Define the desired order of genes
    gene_order = ["LYS20", "ACO2", "LYS4", "LYS12", "ARO8", "LYS2", "LYS9", "LYS1"]
    
    # Get all alignment files
    all_files = glob.glob('/work3/s233201/enzyme_out_6/trim/*aln')
    
    # Create a dictionary to map gene names to full file paths
    file_dict = {os.path.basename(f).split('.')[0]: f for f in all_files}
    
    all_scores = []
    all_filenames = []
    
    # Process files in the specified order
    for gene in gene_order:
        if gene in file_dict:
            try:
                alignment = AlignIO.read(file_dict[gene], 'fasta')
                conservation_scores = calculate_conservation(alignment)
                all_scores.append(conservation_scores)
                all_filenames.append(file_dict[gene])
            except Exception as e:
                print(f"Error processing {gene}: {str(e)}")
        else:
            print(f"Warning: {gene} not found in alignment files")
    
    # Create and save combined heatmap
    plot_conservation_heatmaps(all_scores, all_filenames, output_dir)

if __name__ == "__main__":
    main()
