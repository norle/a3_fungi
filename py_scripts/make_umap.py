from umap.umap_ import UMAP
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

try:
    # Read taxa data
    taxa_df = pd.read_csv('/zhome/85/8/203063/a3_fungi/data_out/taxa_non_filtered.csv')
    #taxa_df = pd.read_csv('/work3/s233201/enzyme_out/final_iq.mldist')
       
    # Read the distance matrix, skipping header
    distance_matrix = pd.read_csv('/work3/s233201/enzyme_out_1/tree_iq_multi_LGI.mldist', 
                                sep='\s+',
                                header=None,
                                skiprows=1)
    
    # Convert to numpy array and drop first column (which contains accessions)
    distance_matrix = distance_matrix.to_numpy()
    accessions = distance_matrix[:, 0]
    distance_matrix = distance_matrix[:, 1:]
    
    # Filter and align taxa_df with distance matrix accessions using first 15 characters
    taxa_df['Accession_short'] = taxa_df['Accession'].str[:15]
    accessions_short = np.array([acc[:15] for acc in accessions])
    taxa_df = taxa_df[taxa_df['Accession_short'].isin(accessions_short)].copy()
    taxa_df = taxa_df.set_index('Accession_short').loc[accessions_short].reset_index()
    
    print(f"Matrix shape: {distance_matrix.shape}")
    print(f"Number of matching taxa: {len(taxa_df)}")
    
    if distance_matrix.size > 0 and len(taxa_df) == len(accessions):
        # Create UMAP object
        reducer = UMAP(metric='precomputed')
        embedding = reducer.fit_transform(distance_matrix)

        # Create color mapping
        phyla = taxa_df['Phylum'].unique()
        colors = plt.cm.tab10(np.linspace(0, 1, len(phyla)))
        phylum_to_color = dict(zip(phyla, colors))
        
        # Create plot
        plt.figure(figsize=(12, 8))
        
        # Plot each phylum separately for legend
        for phylum in phyla:
            mask = taxa_df['Phylum'] == phylum
            points = plt.scatter(embedding[mask.values, 0], 
                       embedding[mask.values, 1],
                       s=10,  # Reduced point size
                       label=phylum,
                       color=phylum_to_color[phylum],
                       alpha=0.6)
        
        plt.title('UMAP projection of the enzyme data')
        plt.xlabel('UMAP1')
        plt.ylabel('UMAP2')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        
        # Save the plot
        plt.savefig('/zhome/85/8/203063/a3_fungi/figures/umap.png', 
                    dpi=300, 
                    bbox_inches='tight')
        plt.close()
    else:
        print("Error: Empty distance matrix")
except Exception as e:
    print(f"Error processing data: {str(e)}")
