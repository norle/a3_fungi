import pandas as pd

# Read BUSCO results and extract accessions
busco_df = pd.read_csv('data_out/busco_results_cleaned.csv')
busco_accessions = set(busco_df['organism'].str[:15])

# Read taxa file
taxa_df = pd.read_csv('data_out/taxa_non_filtered.csv')

# Filter taxa based on BUSCO accessions
filtered_taxa = taxa_df[taxa_df['Accession'].str[:15].isin(busco_accessions)]

# Save filtered results
filtered_taxa.to_csv('data_out/taxa_clean.csv', index=False)

print(f"Original taxa count: {len(taxa_df)}")
print(f"Filtered taxa count: {len(filtered_taxa)}")
