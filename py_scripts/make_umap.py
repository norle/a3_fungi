import argparse
from umap import UMAP
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from ete3 import Tree

def make_umap(gene_name):
    # Toggle tree visualization here
    SHOW_TREE = False  # Set to True to show phylogenetic tree edges
    OUTPUT_PATH = f'/zhome/85/8/203063/a3_fungi/figures/enzyme_umaps/{gene_name}.png'


    try:
        # Read taxa data
        taxa_df = pd.read_csv('/zhome/85/8/203063/a3_fungi/data_out/taxa_non_filtered.csv')
        #taxa_df = pd.read_csv('/work3/s233201/enzyme_out/final_iq.mldist')
        
        mldist_name = f'/work3/s233201/enzyme_out_3/enzyme_trees/{gene_name}/tree_iq_multi_LGI.mldist'
        tree_name = f'/work3/s233201/enzyme_out_3/enzyme_trees/{gene_names}tree_iq_multi_LGI.treefile'

        #mldist_name = '/work3/s233201/output_phyl_busco_1/tree_iq_multi_LGI.mldist'
        #tree_name = '/work3/s233201/output_phyl_busco_1/tree_iq_multi_LGI.treefile'
        
        # Read the distance matrix, skipping header
        distance_matrix = pd.read_csv(mldist_name, 
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
            reducer = UMAP(
                n_components=2,
                metric='precomputed',
                random_state=42,
                min_dist=0.1,
                n_neighbors=100
            )
            embedding = reducer.fit_transform(distance_matrix)
                
            # Create a mapping from node names to UMAP coordinates
            name_to_idx = {acc[:15]: i for i, acc in enumerate(accessions)}
            
            # Create plot with larger figure size
            plt.figure(figsize=(15, 10))
            
            # First plot edges from the tree (with low opacity) if enabled
            if SHOW_TREE:
                tree = Tree(tree_name, format=1)
            
                for node in tree.traverse():
                    if not node.is_leaf():
                        leaves = node.get_leaves()
                        for i in range(len(leaves)-1):
                            leaf1 = leaves[i].name[:15]
                            leaf2 = leaves[i+1].name[:15]
                            if leaf1 in name_to_idx and leaf2 in name_to_idx:
                                idx1 = name_to_idx[leaf1]
                                idx2 = name_to_idx[leaf2]
                                plt.plot([embedding[idx1, 0], embedding[idx2, 0]],
                                    [embedding[idx1, 1], embedding[idx2, 1]],
                                    color='gray', alpha=0.1, linewidth=0.5)

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
            
            # Get unique phyla that exist in our data
            phyla = sorted(taxa_df['Phylum'].unique())

            # Plot each phylum separately for legend
            for phylum in phyla:
                mask = taxa_df['Phylum'] == phylum
                plt.scatter(embedding[mask.values, 0], 
                        embedding[mask.values, 1],
                        s=30,
                        label=phylum,
                        color=PHYLUM_COLORS.get(phylum, '#999999'),  # Default to gray if phylum not in dictionary
                        alpha=0.8,
                        zorder=2)
            
            plt.title('UMAP projection with phylogenetic relationships')
            plt.xlabel('UMAP1')
            plt.ylabel('UMAP2')
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.tight_layout()
            
            # Save the plot with appropriate filename
            plt.savefig(OUTPUT_PATH, dpi=300, bbox_inches='tight')
            plt.close()
        else:
            print("Error: Empty distance matrix")
    except Exception as e:
        print(f"Error processing data: {str(e)}")

if __name__ == '__main__':
    gene_names = ['LYS1', 'LYS2', 'LYS4', 'LYS9', 'LYS12', 'LYS20', 'ARO8', 'ACO2']
    for gene_name in gene_names:
        make_umap(gene_name)