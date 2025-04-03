import pandas as pd

def retrieve_taxa(busco_results, taxa_data):

    busco_df = pd.read_csv(busco_results)
    taxa_df = pd.read_csv(taxa_data)

    busco_df['organism'] = busco_df['organism'].str[:15]
    busco_df.rename(columns={'organism': 'Accession'}, inplace=True)

    busco_df = busco_df.merge(taxa_df[['Accession', 'Phylum']], on='Accession', how='left')

    return busco_df

if __name__ == "__main__":

    OUTPUT_PATH = '/zhome/85/8/203063/a3_fungi/data_out/taxa_filtered1.csv'
    BUSCO_RESULTS = '/zhome/85/8/203063/a3_fungi/data_out/filtered_busco_results1.csv'
    TAXA_DATA = '/zhome/85/8/203063/a3_fungi/data_out/taxa_non_filtered.csv'

    from taxa_visualize import visualize_taxa

    busco_df = retrieve_taxa(BUSCO_RESULTS, TAXA_DATA)

    busco_df = busco_df[['Accession', 'Phylum']]
    busco_df.to_csv(OUTPUT_PATH, index=False)

    visualize_taxa(OUTPUT_PATH, '/zhome/85/8/203063/a3_fungi/figures/taxa_histogram_filtered1.png')


