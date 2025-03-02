from umap.umap_ import UMAP
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

try:
    # Read taxa data
    taxa_df = pd.read_csv('/zhome/85/8/203063/a3_fungi/data_out/taxa_non_filtered.csv')
       
    # Read the distance matrix, skipping header
    distance_matrix = pd.read_csv('/work3/s233201/enzyme_out/final_iq.mldist', 
                                sep='\s+',
                                header=None,
                                skiprows=1)
    
    # Convert to numpy array and drop first column (which contains accessions)
    distance_matrix = distance_matrix.to_numpy()
    accessions = distance_matrix[:, 0]
    distance_matrix = distance_matrix[:, 1:]
    
    # Filter and align taxa_df with distance matrix accessions
    taxa_df = taxa_df[taxa_df['Accession'].isin(accessions)].copy()
    taxa_df = taxa_df.set_index('Accession').loc[accessions].reset_index()
    
    print(f"Matrix shape: {distance_matrix.shape}")
    print(f"Number of matching taxa: {len(taxa_df)}")
    
    if distance_matrix.size > 0 and len(taxa_df) == len(accessions):
        # Create 3D UMAP
        reducer = UMAP(n_components=3, metric='precomputed')
        embedding = reducer.fit_transform(distance_matrix)
        
        # Create dataframe for plotting
        plot_df = pd.DataFrame({
            'UMAP1': embedding[:, 0],
            'UMAP2': embedding[:, 1],
            'UMAP3': embedding[:, 2],
            'Phylum': taxa_df['Phylum'],
            'Accession': accessions
        })
        
        # Create 3D scatter plot
        fig = px.scatter_3d(plot_df, 
                           x='UMAP1', 
                           y='UMAP2', 
                           z='UMAP3',
                           color='Phylum',
                           hover_data=['Accession'],
                           title='3D UMAP projection of enzyme data')
        
        # Update layout for better visualization
        fig.update_traces(marker=dict(size=5))
        fig.update_layout(
            scene=dict(
                xaxis_title='UMAP1',
                yaxis_title='UMAP2',
                zaxis_title='UMAP3',
                xaxis=dict(backgroundcolor="white"),
                yaxis=dict(backgroundcolor="white"),
                zaxis=dict(backgroundcolor="white"),
                bgcolor='white'
            ),
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.85,
                font=dict(size=16)
            )
        )
        
        # Save as interactive HTML file
        fig.write_html('/zhome/85/8/203063/a3_fungi/figures/umap_3d.html')
        
    else:
        print("Error: Empty distance matrix")
except Exception as e:
    print(f"Error processing data: {str(e)}")
