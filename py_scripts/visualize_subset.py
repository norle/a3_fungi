from retrieve_taxa import retrieve_taxa
import matplotlib.pyplot as plt

OUTPUT_PATH = '/zhome/85/8/203063/a3_fungi/data_out/taxa_filtered1.csv'
BUSCO_RESULTS = '/zhome/85/8/203063/a3_fungi/data_out/busco_results.csv'
TAXA_DATA = '/zhome/85/8/203063/a3_fungi/data_out/taxa_non_filtered.csv'

df = retrieve_taxa(BUSCO_RESULTS, TAXA_DATA)

filtered_df = df[df['Phylum'] == 'Microsporidia']

# Plotting
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Complete BUSCOs
axes[0, 0].hist(filtered_df['complete_buscos'], bins=20, color='blue')
axes[0, 0].set_title('Complete BUSCOs')

# Single Copy BUSCOs
axes[0, 1].hist(filtered_df['single_copy_buscos'], bins=20, color='green')
axes[0, 1].set_title('Single Copy BUSCOs')

# Fragmented BUSCOs
axes[1, 0].hist(filtered_df['fragmented_buscos'], bins=20, color='orange')
axes[1, 0].set_title('Fragmented BUSCOs')

# Missing BUSCOs
axes[1, 1].hist(filtered_df['missing_buscos'], bins=20, color='red')
axes[1, 1].set_title('Missing BUSCOs')

# Adjust layout
plt.tight_layout()
plt.savefig('figures/microsporidia_histograms.png')