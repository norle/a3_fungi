import os
from Bio import SeqIO
import matplotlib.pyplot as plt

# Path to the folder containing .fasta files
fasta_folder = "/work3/s233201/enzyme_out_4"

# Dictionary to store sequence lengths for each file
file_sequences = {}

# Collect lengths of sequences for each .fasta file
for file_name in os.listdir(fasta_folder):
    if file_name.endswith(".fasta"):
        file_path = os.path.join(fasta_folder, file_name)
        file_base_name = file_name[:-6]  # Remove .fasta extension
        file_sequences[file_base_name] = []
        
        with open(file_path, "r") as fasta_file:
            for record in SeqIO.parse(fasta_file, "fasta"):
                file_sequences[file_base_name].append(len(record.seq))

# Define the order of genes for plotting
gene_order = ["LYS20", "ACO2", "LYS4", "LYS12", "ARO8", "LYS2", "LYS9", "LYS1"]

# Create a 4x2 subplot for the histograms (one per file)
fig, axes = plt.subplots(4, 2, figsize=(10, 14))
axes = axes.flatten()

# Plot histogram for each file in the specified order
for i, gene_name in enumerate(gene_order):
    if i < len(axes) and gene_name in file_sequences:
        ax = axes[i]
        lengths = file_sequences[gene_name]
        ax.hist(lengths, bins=30, color='blue', alpha=0.7)
        ax.set_title(gene_name)
        ax.set_xlabel("Sequence Length")
        ax.set_ylabel("Frequency")
    elif i < len(axes):
        # Handle the case where a specified gene isn't in the files
        ax = axes[i]
        ax.set_title(f"{gene_name} (No data)")
        ax.set_visible(False)

# Hide any unused subplots
for i in range(len(gene_order), len(axes)):
    axes[i].set_visible(False)

plt.tight_layout()
plt.savefig("figures/sequence_length_histograms.png")