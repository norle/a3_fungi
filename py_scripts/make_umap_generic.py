from umap import UMAP
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from ete3 import Tree
import multiprocessing


def process_gene_data(gene_name):
    """Process single gene and return UMAP coordinates and taxa information"""
    try:
        taxa_df = pd.read_csv('/zhome/85/8/203063/a3_fungi/data_out/taxa_non_filtered.csv')
        mldist_name = f'/work3/s233201/enzyme_out_3/enzyme_trees/{gene_name}/tree_iq_multi_LGI.mldist'
        
        distance_matrix = pd.read_csv(mldist_name, sep='\s+', header=None, skiprows=1)
        distance_matrix = distance_matrix.to_numpy()
        accessions = distance_matrix[:, 0]
        distance_matrix = distance_matrix[:, 1:]
        
        taxa_df['Accession_short'] = taxa_df['Accession'].str[:15]
        accessions_short = np.array([acc[:15] for acc in accessions])
        taxa_df = taxa_df[taxa_df['Accession_short'].isin(accessions_short)].copy()
        taxa_df = taxa_df.set_index('Accession_short').loc[accessions_short].reset_index()
        
        if distance_matrix.size > 0 and len(taxa_df) == len(accessions):
            reducer = UMAP(n_components=2, metric='precomputed', random_state=42, min_dist=0.1, n_neighbors=100)
            embedding = reducer.fit_transform(distance_matrix)
            return gene_name, embedding, taxa_df['Phylum'].values
    except Exception as e:
        print(f"Error processing {gene_name}: {str(e)}")
        return None

def make_umap(use_subplots=False, ax=None):
    # Toggle tree visualization here
    SHOW_TREE = False  # Set to True to show phylogenetic tree edges
    OUTPUT_PATH = f'/zhome/85/8/203063/a3_fungi/figures/busco_0403.png'


    try:
        # Read taxa data
        taxa_df = pd.read_csv('/zhome/85/8/203063/a3_fungi/data_out/taxa_non_filtered.csv')
        #taxa_df = pd.read_csv('/work3/s233201/enzyme_out/final_iq.mldist')
        
        mldist_name = f'/work3/s233201/output_phyl_busco_3/tree_iq_LGI_fast.mldist'
        tree_name = f'/work3/s233201/output_phyl_busco_3/tree_iq_LGI_fast.treefile'

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

            plt.figure(figsize=(15, 10))
            ax = plt.gca()
            
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
                ax.scatter(embedding[mask.values, 0], 
                        embedding[mask.values, 1],
                        s=12,
                        label=phylum,
                        color=PHYLUM_COLORS.get(phylum, '#999999'),  # Default to gray if phylum not in dictionary
                        alpha=0.8,
                        zorder=2)
            
            # Remove axis scales and ticks
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_xticklabels([])
            ax.set_yticklabels([])
            
            #ax.set_title(f'{gene_name}', fontsize=16, pad=5)
            # ax.set_xlabel('UMAP1')
            # ax.set_ylabel('UMAP2')

            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.tight_layout()
            plt.savefig(OUTPUT_PATH, dpi=300, bbox_inches='tight')
            plt.close()
        else:
            print("Error: Empty distance matrix")
    except Exception as e:
        print(f"Error processing data: {str(e)}")

if __name__ == '__main__':

    make_umap()