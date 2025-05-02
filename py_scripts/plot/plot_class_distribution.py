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
# Further adjust figsize and height_ratios
fig = plt.figure(figsize=(26, 22)) # Slightly larger figure size
# Make bar chart row even shorter relative to pie chart row
gs = gridspec.GridSpec(2, 3, figure=fig, height_ratios=[1, 1], hspace=0.5, wspace=0.3) # Increased hspace slightly

ax_bar = fig.add_subplot(gs[0, :]) # Top row, span all columns
ax_pie1 = fig.add_subplot(gs[1, 0]) # Bottom row, first column
ax_pie2 = fig.add_subplot(gs[1, 1]) # Bottom row, second column
ax_pie3 = fig.add_subplot(gs[1, 2]) # Bottom row, third column
pie_axes = [ax_pie1, ax_pie2, ax_pie3]

# fig.suptitle('Overall and Top 3 Phyla Class Distributions (Non-Filtered Data)', fontsize=24, y=0.98) # Further increased font size

# --- Plot Stacked Bar Chart (Top) ---
distribution.plot(kind='bar', stacked=True, ax=ax_bar, colormap='tab20', legend=False)
ax_bar.set_title('Class Distribution Across All Phyla', fontsize=24) # Increased font size
#ax_bar.set_xlabel('Phylum', fontsize=18) # Increased font size
ax_bar.set_ylabel('Number of Accessions (Count)', fontsize=18) # Increased font size
ax_bar.tick_params(axis='x', labelsize=16) # Increased font size
ax_bar.tick_params(axis='y', labelsize=16) # Increased font size

# Set rotation and alignment on the actual tick labels
for label in ax_bar.get_xticklabels():
    label.set_rotation(45)
    label.set_ha('right')
    # label.set_fontsize(16) # Alternative way to set tick label size

# Optional: Add a legend for the bar chart if feasible
# handles, labels = ax_bar.get_legend_handles_labels()
# ax_bar.legend(handles, labels, title='Class', bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0., fontsize='small', title_fontsize='medium')


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
        labels=class_distribution_in_phylum.index, # Add class labels
        autopct='%1.1f%%',
        startangle=90,
        pctdistance=0.80, # Adjust percentage distance from center
        labeldistance=1.05, # Adjust label distance from center (outside percentage)
        textprops={'fontsize': 14} # Increased base font size for labels/percentages
    )

    # Hide labels AND percentages for very small slices
    threshold = 3
    for j, pct_label in enumerate(autotexts):
        percentage = float(pct_label.get_text().replace('%',''))
        if percentage < threshold:
            pct_label.set_visible(False)
            texts[j].set_visible(False) # Hide the corresponding class label as well
        # else: # Optional: Make percentage bold for visible slices
            # pct_label.set_weight('bold')
            # texts[j].set_fontsize(14) # Increase specific label size


    ax.set_title(f'Phylum: {phylum}\n(Total: {phylum_counts[phylum]})', fontsize=20) # Increased font size
    # Remove legend code as we are using direct labels now
    # # Add a legend to the side of the pie chart if labels are hidden
    # # ax.legend(visible_wedges, visible_labels, title="Classes (%)", loc="center left", bbox_to_anchor=(0.95, 0.5), fontsize='small')


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
