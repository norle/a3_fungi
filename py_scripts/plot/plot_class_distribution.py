import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec # Import GridSpec
import seaborn as sns
import os
import numpy as np # Import numpy for color mapping if needed

# Define file paths relative to the script or project root if preferred
# Assuming the script is run from a location where these paths are accessible
base_path = '/zhome/85/8/203063/a3_fungi/data_out'
taxa_file = os.path.join(base_path, 'taxa_non_filtered.csv')
class_file = os.path.join(base_path, 'class_non_filtered.csv')
# Update output filename for the new combined plot type
output_plot_file = os.path.join('/zhome/85/8/203063/a3_fungi/figures/combined_phylum_class_distribution.png')

# --- Read the CSV files ---
try:
    taxa_df = pd.read_csv(taxa_file)
    class_df = pd.read_csv(class_file)
except FileNotFoundError as e:
    print(f"Error reading files: {e}")
    exit()

# --- Merge the dataframes on 'Accession' ---
merged_df = pd.merge(taxa_df[['Accession', 'Phylum']], class_df[['Accession', 'Class']], on='Accession', how='inner')

# --- Handle potential missing values ---
merged_df.dropna(subset=['Phylum', 'Class'], inplace=True)
# Optional: Remove entries where Phylum or Class might be placeholders like 'Unknown' or 'Unclassified'
# merged_df = merged_df[~merged_df['Phylum'].str.contains('Unknown|Unclassified', case=False, na=False)]
# merged_df = merged_df[~merged_df['Class'].str.contains('Unknown|Unclassified', case=False, na=False)]

# --- Calculate Data for Stacked Bar Chart ---
distribution = merged_df.groupby(['Phylum', 'Class']).size().unstack(fill_value=0)
# Sort phyla by total count for better visualization in the bar chart
distribution = distribution.loc[distribution.sum(axis=1).sort_values(ascending=False).index]

# --- Calculate Data for Pie Charts ---
phylum_counts = merged_df['Phylum'].value_counts()
top_3_phyla = phylum_counts.nlargest(3).index.tolist()
print(f"Top 3 Phyla for pie charts: {top_3_phyla}")

# --- Plotting ---
print("Generating combined plot...")
custom_params = {"axes.spines.right": False, "axes.spines.top": False}
sns.set_theme(style="ticks", rc=custom_params)

# Create a figure with a GridSpec layout
# Even larger figure size to accommodate larger text
fig = plt.figure(figsize=(30, 24))
# Keep bar chart and pie chart rows equal in height
gs = gridspec.GridSpec(2, 3, figure=fig, height_ratios=[1, 1], hspace=0.5, wspace=0.3)

ax_bar = fig.add_subplot(gs[0, :]) # Top row, span all columns
ax_pie1 = fig.add_subplot(gs[1, 0]) # Bottom row, first column
ax_pie2 = fig.add_subplot(gs[1, 1]) # Bottom row, second column
ax_pie3 = fig.add_subplot(gs[1, 2]) # Bottom row, third column
pie_axes = [ax_pie1, ax_pie2, ax_pie3]

# --- Plot Stacked Bar Chart (Top) ---
distribution.plot(kind='bar', stacked=True, ax=ax_bar, colormap='tab20', legend=False)
ax_bar.set_title('Class Distribution Across All Phyla', fontsize=36) # Doubled font size
ax_bar.set_ylabel('Number of Accessions (Count)', fontsize=32) # Doubled font size
ax_bar.tick_params(axis='x', labelsize=28) # Doubled font size
ax_bar.tick_params(axis='y', labelsize=28) # Doubled font size

# Set rotation and alignment on the actual tick labels
for label in ax_bar.get_xticklabels():
    label.set_rotation(45)
    label.set_ha('right')

# --- Plot Pie Charts (Bottom) ---
for i, phylum in enumerate(top_3_phyla):
    if i >= len(pie_axes): # Safety check if there are fewer than 3 top phyla somehow
        break
    ax = pie_axes[i]
    # Filter data for the current phylum
    phylum_df = merged_df[merged_df['Phylum'] == phylum]
    # Calculate class distribution within this phylum
    class_distribution_in_phylum = phylum_df['Class'].value_counts()

    # Add labels back, adjust distances
    wedges, texts, autotexts = ax.pie(
        class_distribution_in_phylum,
        labels=class_distribution_in_phylum.index,
        autopct='%1.1f%%',
        startangle=90,
        pctdistance=0.80,
        labeldistance=1.1, # Increased slightly to accommodate larger text
        textprops={'fontsize': 20} # Doubled font size for pie chart labels/percentages
    )

    # Hide labels AND percentages for very small slices
    threshold = 3
    for j, pct_label in enumerate(autotexts):
        percentage = float(pct_label.get_text().replace('%',''))
        if percentage < threshold:
            pct_label.set_visible(False)
            texts[j].set_visible(False) # Hide the corresponding class label as well

    ax.set_title(f'Phylum: {phylum}\n(Total: {phylum_counts[phylum]})', fontsize=32) # Doubled font size

# Adjust layout - may need fine-tuning after size changes
plt.tight_layout(rect=[0, 0.03, 1, 0.95]) # Adjust rect if suptitle is added back or needed

# --- Save the plot ---
try:
    plt.savefig(output_plot_file, dpi=300, bbox_inches='tight')
    print(f"Plot successfully saved to {output_plot_file}")
except Exception as e:
    print(f"Error saving plot: {e}")

# --- Show the plot (optional, uncomment if running interactively) ---
# plt.show()

print("Script finished.")
