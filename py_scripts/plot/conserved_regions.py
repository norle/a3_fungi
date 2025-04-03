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

def plot_conservation_heatmap(scores, filename, output_dir):
    """Create a heatmap of conservation scores"""
    plt.figure(figsize=(15, 2))
    scores_array = np.array(scores).reshape(1, -1)
    
    sns.heatmap(scores_array, cmap='RdYlBu_r', 
                xticklabels=50, yticklabels=False,
                cbar_kws={'label': 'Conservation Score'})
    
    plt.title(f'Conservation Analysis: {os.path.basename(filename)}')
    plt.xlabel('Alignment Position')
    
    output_path = os.path.join(output_dir, f'{os.path.basename(filename)}_conservation.png')
    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    plt.close()

def main():
    # Create output directory for plots
    output_dir = '/zhome/85/8/203063/a3_fungi/figures/conservation_plots'
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all alignment files
    alignment_files = glob.glob('/work3/s233201/enzyme_out_1/alignments/*.aln')
    
    for aln_file in tqdm(alignment_files):
        try:
            # Read alignment file as FASTA format
            alignment = AlignIO.read(aln_file, 'fasta')
            
            # Calculate conservation scores
            conservation_scores = calculate_conservation(alignment)
            
            # Create and save heatmap
            plot_conservation_heatmap(conservation_scores, aln_file, output_dir)
            
        except Exception as e:
            print(f"Error processing {aln_file}: {str(e)}")

if __name__ == "__main__":
    main()
