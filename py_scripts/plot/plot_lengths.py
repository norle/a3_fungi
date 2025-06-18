import os
import csv
from Bio import SeqIO
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches  # new import

# Define phylum colors using ColorBrewer
PHYLUM_COLORS = {
    'Ascomycota': '#377eb8',        # Blue
    'Basidiomycota': '#e41a1c',     # Red
    'Mucoromycota': '#4daf4a',      # Green
    'Zoopagomycota': '#984ea3',     # Purple
    'Chytridiomycota': '#ff7f00',   # Orange
    'Blastocladiomycota': '#ffff33',# Yellow
    'Cryptomycota': '#a65628'       # Brown
}

# Load accession→phylum map
taxa_file = "/zhome/85/8/203063/a3_fungi/data_out/taxa_clean.csv"
acc2phylum = {}
with open(taxa_file) as tf:
    reader = csv.DictReader(tf)
    for row in reader:
        acc2phylum[row['Accession']] = row['Phylum']

# Load outlier accessions
outlier_file = "/zhome/85/8/203063/a3_fungi/data/outliers_set.txt"
with open(outlier_file) as of:
    outlier_accessions = {line.strip() for line in of}

# Path to the folder containing .fasta files
fasta_folder = "/work3/s233201/enzyme_out_6"

# Dictionary to store sequence lengths for each file by phylum
file_sequences = {}

# Collect lengths of sequences for each .fasta file
for file_name in os.listdir(fasta_folder):
    if file_name.endswith(".fasta"):
        gene = file_name[:-6]
        file_sequences[gene] = {}
        with open(os.path.join(fasta_folder, file_name)) as fh:
            for rec in SeqIO.parse(fh, "fasta"):
                if rec.id in outlier_accessions:
                    continue  # Skip outlier sequences
                ph = acc2phylum.get(rec.id, 'Unknown')
                file_sequences[gene].setdefault(ph, []).append(len(rec.seq))

# Define the order of genes for plotting
gene_order = ["LYS20", "ACO2", "LYS4", "LYS12", "ARO8", "LYS2", "LYS9", "LYS1"]

# Create a 3x3 subplot grid
fig, axes = plt.subplots(3, 3, figsize=(12, 12))
axes = axes.flatten()

# Plot histograms for the first 8 genes
for i, gene in enumerate(gene_order):
    ax = axes[i]
    if gene in file_sequences:
        phyla = [p for p in PHYLUM_COLORS if p in file_sequences[gene]]
        data = [file_sequences[gene][p] for p in phyla]
        colors = [PHYLUM_COLORS[p] for p in phyla]
        ax.hist(data, bins=30, stacked=True, color=colors, alpha=0.8)
        ax.set_title(gene, fontweight='bold', fontsize=14)  # Increased fontsize
        ax.set_xlabel("Sequence Length", fontsize=12)  # Increased fontsize
        ax.set_ylabel("Count", fontsize=12)  # Increased fontsize
    else:
        ax.set_title(f"{gene} (No data)", fontweight='bold', fontsize=14)  # Increased fontsize
        ax.set_visible(False)

# 9th subplot reserved for legend
legend_ax = axes[8]
legend_ax.axis('off')
handles = [mpatches.Patch(color=PHYLUM_COLORS[p], label=p) for p in PHYLUM_COLORS]
legend_ax.legend(handles=handles, title='Phylum', loc='center', fontsize=12, title_fontsize=13)  # Increased fontsize

# Final layout and save
plt.tight_layout()
plt.savefig("figures/sequence_length_histograms.png")