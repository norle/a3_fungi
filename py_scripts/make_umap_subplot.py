import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from umap import UMAP
from ete3 import Tree

def make_umap_subplot():
    # Configuration
    SHOW_TREE = False  # Set to True to show phylogenetic tree edges
    OUTPUT_PATH = '/zhome/85/8/203063/a3_fungi/figures/busco_aaa_comparison.png'

    # Input files for the two plots
    inputs = [
        {
            'mldist': '/work3/s233201/output_phyl_busco_3/tree_iq_LGI_fast.mldist',
            'tree': '/work3/s233201/output_phyl_busco_3/tree_iq_LGI_fast.treefile',
            'title': 'BUSCO phylogeny'
        },
        {
            'mldist': '/work3/s233201/enzyme_out_4/tree_LGI.mldist',
            'tree': '/work3/s233201/enzyme_out_4/tree_LGI.treefile',
            'title': 'AAA phylogeny'
        }
    ]

    # Create figure with subplots
    fig, axes = plt.subplots(1, 2, figsize=(13, 6))

    # Define phylum colors using ColorBrewer
    PHYLUM_COLORS = {
        'Ascomycota': '#377eb8',
        'Basidiomycota': '#e41a1c',
        'Mucoromycota': '#4daf4a',
        'Zoopagomycota': '#984ea3',
        'Chytridiomycota': '#ff7f00',
        'Blastocladiomycota': '#ffff33',
        'Cryptomycota': '#a65628'
    }

    try:
        taxa_df = pd.read_csv('/zhome/85/8/203063/a3_fungi/data_out/taxa_non_filtered.csv')

        for ax, input_data in zip(axes, inputs):
            # Read and process distance matrix
            distance_matrix = pd.read_csv(input_data['mldist'], sep='\s+', header=None, skiprows=1)
            distance_matrix = distance_matrix.to_numpy()
            accessions = distance_matrix[:, 0]
            distance_matrix = distance_matrix[:, 1:]

            # Process taxa data
            taxa_df['Accession_short'] = taxa_df['Accession'].str[:15]
            accessions_short = np.array([acc[:15] for acc in accessions])
            plot_taxa_df = taxa_df[taxa_df['Accession_short'].isin(accessions_short)].copy()
            plot_taxa_df = plot_taxa_df.set_index('Accession_short').loc[accessions_short].reset_index()

            if distance_matrix.size > 0 and len(plot_taxa_df) == len(accessions):
                # Create UMAP embedding
                reducer = UMAP(n_components=2, metric='precomputed', random_state=42, 
                             min_dist=0.1, n_neighbors=100)
                embedding = reducer.fit_transform(distance_matrix)

                # Plot tree edges if enabled
                if SHOW_TREE:
                    name_to_idx = {acc[:15]: i for i, acc in enumerate(accessions)}
                    tree = Tree(input_data['tree'], format=1)
                    for node in tree.traverse():
                        if not node.is_leaf():
                            leaves = node.get_leaves()
                            for i in range(len(leaves)-1):
                                leaf1 = leaves[i].name[:15]
                                leaf2 = leaves[i+1].name[:15]
                                if leaf1 in name_to_idx and leaf2 in name_to_idx:
                                    idx1, idx2 = name_to_idx[leaf1], name_to_idx[leaf2]
                                    ax.plot([embedding[idx1, 0], embedding[idx2, 0]],
                                          [embedding[idx1, 1], embedding[idx2, 1]],
                                          color='gray', alpha=0.1, linewidth=0.5)

                # Plot points for each phylum
                for phylum in sorted(plot_taxa_df['Phylum'].unique()):
                    mask = plot_taxa_df['Phylum'] == phylum
                    ax.scatter(embedding[mask.values, 0], 
                             embedding[mask.values, 1],
                             s=0.5,
                             label=phylum,
                             color=PHYLUM_COLORS.get(phylum, '#999999'),
                             alpha=0.6,
                             zorder=2)

                # Configure subplot
                ax.set_xticks([])
                ax.set_yticks([])
                ax.set_title(input_data['title'], fontsize=24, pad=10)

        # Add single legend for both plots with larger size
        handles, labels = axes[1].get_legend_handles_labels()
        fig.legend(handles, labels, 
                  bbox_to_anchor=(1.05, 0.5), 
                  loc='center left',
                  prop={'size': 16},  # Increase font size
                  markerscale=2.0)    # Make legend markers larger
        
        plt.tight_layout()
        plt.savefig(OUTPUT_PATH, dpi=300, bbox_inches='tight')
        plt.close()

    except Exception as e:
        print(f"Error processing data: {str(e)}")

if __name__ == '__main__':
    make_umap_subplot()
