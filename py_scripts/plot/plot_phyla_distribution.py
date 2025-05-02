import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read the CSV file
df1 = pd.read_csv('/zhome/85/8/203063/a3_fungi/data_out/taxa_clean.csv')
df2 = pd.read_csv('/zhome/85/8/203063/a3_fungi/data_out/taxa_clean_0424.csv')


# Count the occurrences of each phylum in both datasets
phylum_counts1 = df1['Phylum'].value_counts()
phylum_counts2 = df2['Phylum'].value_counts()

# Get all unique phyla from both datasets
all_phyla = sorted(set(phylum_counts1.index) | set(phylum_counts2.index))

# Create a dictionary with combined counts for sorting
combined_counts = {}
for phylum in all_phyla:
    combined_counts[phylum] = phylum_counts1.get(phylum, 0) + phylum_counts2.get(phylum, 0)

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
width = 0.35  # width of the bars

# Create bars for each dataset
for i, phylum in enumerate(all_phyla):
    # Get count from each dataset, default to 0 if phylum doesn't exist
    count1 = phylum_counts1.get(phylum, 0)
    count2 = phylum_counts2.get(phylum, 0)
    
    # Create bars with phylum-specific colors
    color = PHYLUM_COLORS.get(phylum, '#999999')
    bar1 = ax.bar(x[i] - width/2, count1, width, color=color, alpha=0.7, label="")
    bar2 = ax.bar(x[i] + width/2, count2, width, color=color, alpha=0.4, hatch='//', label="")
    
    # Add value labels on top of each bar with reduced font size
    ax.text(x[i] - width/2, count1, f'{int(count1)}', ha='center', va='bottom', fontsize=8)
    ax.text(x[i] + width/2, count2, f'{int(count2)}', ha='center', va='bottom', fontsize=8)

# Add dataset legend (only dataset information)
ax.bar(0, 0, color='gray', alpha=0.7, label='Annotated genomes')
ax.bar(0, 0, color='gray', alpha=0.4, hatch='//', label='Full AAA pathway')

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
