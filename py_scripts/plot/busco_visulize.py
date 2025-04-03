import pandas as pd
import matplotlib.pyplot as plt

# Load data from CSV
csv_path = '~/a3_fungi/data_out/busco_results.csv'
filtered = '~/a3_fungi/data_out/taxa_no_missing.csv'
df = pd.read_csv(csv_path)

filter_df = pd.read_csv(filtered)

filter_acc = filter_df['Accession'].tolist()

# Create a new column for sorting (1 for GCF, 0 for GCA)
df['is_gcf'] = df['organism'].str.startswith('GCF').astype(int)
# Remove GCA/GCF prefix for grouping
df['clean_name'] = df['organism'].str[:15]

# # Sort by is_gcf (descending) and keep first occurrence
# df = df.sort_values('is_gcf', ascending=False).drop_duplicates(subset='clean_name', keep='first')
# # Clean up temporary columns
# df = df.drop(['is_gcf', 'clean_name'], axis=1)
# print(f"df shape after dropping duplicates: {df.shape}")

# df.to_csv('~/a3_fungi/data_out/busco_results_cleaned.csv', index=False)

# df['organism'].to_csv('~/a3_fungi/data_out/cleaned_genomes.csv', index=False)


# # Filter out entries with >100 missing BUSCOs and >50 fragmented BUSCOs
# df = df[(df['missing_buscos'] <= 100) & (df['fragmented_buscos'] <= 50)]
# print(f"filtered df shape: {df.shape}")

df = df[df['clean_name'].isin(filter_acc)]
print(f"filtered df shape: {df.shape}")

# Save the filtered DataFrame to a new CSV file
output_csv_path = '~/a3_fungi/data_out/filtered_busco_results_enzymes.csv'
df.to_csv(output_csv_path, index=False)
# Save the organism column to a new CSV file
organism_output_csv_path = '~/a3_fungi/data_out/filtered_genomes_enzymes.csv'
df[['organism']].to_csv(organism_output_csv_path, index=False)

# Plotting
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Complete BUSCOs
axes[0, 0].hist(df['complete_buscos'], bins=20, color='blue')
axes[0, 0].set_title('Complete BUSCOs')

# Single Copy BUSCOs
axes[0, 1].hist(df['single_copy_buscos'], bins=20, color='green')
axes[0, 1].set_title('Single Copy BUSCOs')

# Fragmented BUSCOs
axes[1, 0].hist(df['fragmented_buscos'], bins=20, color='orange')
axes[1, 0].set_title('Fragmented BUSCOs')

# Missing BUSCOs
axes[1, 1].hist(df['missing_buscos'], bins=20, color='red')
axes[1, 1].set_title('Missing BUSCOs')

# Adjust layout
plt.tight_layout()
plt.savefig('figures/busco_histograms_enzymes.png')

# Scatter plot of Missing vs Fragmented BUSCOs
plt.figure(figsize=(8, 6))
plt.scatter(df['fragmented_buscos'], df['missing_buscos'], color='purple', s=5) 
plt.title('Scatter plot of Missing vs Fragmented BUSCOs')
plt.xlabel('Fragmented BUSCOs')
plt.ylabel('Missing BUSCOs')
plt.grid(True)
plt.savefig('figures/missing_vs_fragmented_buscos_enzymes.png')


