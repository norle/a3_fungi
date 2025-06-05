import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read the CSV file
df1 = pd.read_csv('/zhome/85/8/203063/a3_fungi/data_out/taxa_clean.csv')
df2 = pd.read_csv('/zhome/85/8/203063/a3_fungi/data_out/taxa_clean_0424.csv')

# Read outliers file and filter df2
with open('/zhome/85/8/203063/a3_fungi/data/outliers_set.txt', 'r') as f:
    outliers = {line.strip() for line in f}
df2 = df2[~df2['Accession'].isin(outliers)]

# Count the occurrences of each phylum in both datasets
phylum_counts1 = df1['Phylum'].value_counts()
phylum_counts2_before = pd.read_csv('/zhome/85/8/203063/a3_fungi/data_out/taxa_clean_0424.csv')['Phylum'].value_counts()
phylum_counts2_after = df2['Phylum'].value_counts()

# Get all unique phyla from all datasets
all_phyla = sorted(set(phylum_counts1.index) | set(phylum_counts2_before.index) | set(phylum_counts2_after.index))

# Create a dictionary with combined counts for sorting
combined_counts = {}
for phylum in all_phyla:
    combined_counts[phylum] = phylum_counts1.get(phylum, 0) + phylum_counts2_before.get(phylum, 0)

# Sort phyla by combined counts (most common to least common)
all_phyla = sorted(all_phyla, key=lambda x: combined_counts[x], reverse=True)

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

# Create a figure and axis
fig, ax = plt.subplots(figsize=(8, 5))

# Set the positions of the bars
x = np.arange(len(all_phyla))
width = 0.3  # increased width from 0.25 to 0.3

# Create bars for each dataset
for i, phylum in enumerate(all_phyla):
    count1 = phylum_counts1.get(phylum, 0)
    count2 = phylum_counts2_before.get(phylum, 0)
    count3 = phylum_counts2_after.get(phylum, 0)
    
    # Create bars with phylum-specific colors
    color = PHYLUM_COLORS.get(phylum, '#999999')
    bar1 = ax.bar(x[i] - width, count1, width, color=color, alpha=0.7, label="")
    bar2 = ax.bar(x[i], count2, width, color=color, alpha=0.4, hatch='//', label="")
    bar3 = ax.bar(x[i] + width, count3, width, color=color, alpha=0.4, hatch='\\\\', label="")
    

    offset = -.1  # Offset for value labels
    # Add value labels on top of each bar with reduced font size and rotation
    ax.text(x[i] - width + offset, count1, f'{int(count1)}', ha='left', va='bottom', fontsize=8, rotation=45)
    ax.text(x[i] - 0 + offset, count2, f'{int(count2)}', ha='left', va='bottom', fontsize=8, rotation=45)
    ax.text(x[i] + width + offset, count3, f'{int(count3)}', ha='left', va='bottom', fontsize=8, rotation=45)

# Update legend
ax.bar(0, 0, color='gray', alpha=0.7, label='Annotated genomes')
ax.bar(0, 0, color='gray', alpha=0.4, hatch='//', label='After INTERPRO')
ax.bar(0, 0, color='gray', alpha=0.4, hatch='\\\\', label='After outliers')

# Remove top and right spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Customize the plot
ax.set_title('Comparison of Fungi Phyla Distributions')
ax.set_xlabel('Phylum')
ax.set_ylabel('Count')
ax.set_xticks(x)
ax.set_xticklabels(all_phyla, rotation=45, ha='right')
ax.legend()

# Adjust layout to prevent label cutoff
plt.tight_layout()

# Save the plot
plt.savefig('/zhome/85/8/203063/a3_fungi/figures/phyla_distribution_comparison.png', dpi=300)
plt.close()
