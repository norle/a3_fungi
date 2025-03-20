import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.cluster import HDBSCAN
import umap
import multiprocessing as mp
import re  # Import regex module

def run_hdbscan(GENE_NAME):
    # Load embeddings from distance matrix
    distance_matrix = pd.read_csv(f'/work3/s233201/enzyme_out_3/enzyme_trees/{GENE_NAME}/tree_iq_multi_LGI.mldist', 
                                sep=r'\s+',
                                header=None,
                                skiprows=1)
    log_path = f'/work3/s233201/enzyme_out_3/enzyme_trees/{GENE_NAME}/tree_iq_multi_LGI.log'
    log_file = open(log_path, 'r')
    log_lines = log_file.readlines()
    log_file.close()

    accessions = distance_matrix.iloc[:, 0].values
    dm = distance_matrix.iloc[:, 1:].values
    print(dm.shape)

    print('Running UMAP')
    # Perform UMAP dimensionality reduction with precomputed distances
    reducer = umap.UMAP(n_neighbors=100, min_dist=0, n_components=10, metric='precomputed', random_state=42)
    dm_reduced = reducer.fit_transform(dm)

    print('Running HDBSCAN')
    # Initialize and fit HDBSCAN
    clusterer = HDBSCAN(min_cluster_size=5, min_samples=20, metric='l2', cluster_selection_epsilon=0.5, cluster_selection_method='leaf')
    cluster_labels = clusterer.fit_predict(dm_reduced)

    # Print clustering statistics
    n_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
    n_noise = list(cluster_labels).count(-1)

    print(f"Number of clusters: {n_clusters}")
    print(f"Number of noise points: {n_noise}")
    print(f"Total number of points: {len(cluster_labels)}")
    print(f"Percentage of points clustered: {(1 - n_noise/len(cluster_labels))*100:.2f}%")

    # Create 2D UMAP projection for visualization
    reducer_2d = umap.UMAP(n_neighbors=100, min_dist=0.1, n_components=2, metric='precomputed', random_state=42)
    vis_dm = reducer_2d.fit_transform(dm)

    # Create scatter plot with matching style
    plt.figure(figsize=(15, 10))
    plt.scatter(vis_dm[:, 0], vis_dm[:, 1],
               s=30,
               c=cluster_labels, 
               cmap='viridis', 
               alpha=0.6)
    plt.title(f'UMAP visualization of HDBSCAN clusters for {GENE_NAME}')
    plt.xlabel('UMAP1')
    plt.ylabel('UMAP2')
    plt.tight_layout()
    plt.savefig(f'/zhome/85/8/203063/a3_fungi/figures/clusters/5_20_05_leaf/{GENE_NAME}_clusters.png', dpi=300, bbox_inches='tight')
    plt.close()

    # Create cluster DataFrame for original accessions
    cluster_df = pd.DataFrame({
        'sequence_idx': accessions,
        'cluster': cluster_labels
    })

    # Parse log lines to append duplicates with their corresponding clusters
    duplicates = []
    for line in log_lines:
        m = re.search(r"NOTE:\s+(\S+)\s+\(identical to\s+(\S+)\)", line)
        if m:
            dup, orig = m.groups()
            # Lookup cluster from original accession in the original order
            cluster_val = None
            for idx, acc in enumerate(accessions):
                if acc == orig:
                    cluster_val = cluster_labels[idx]
                    break
            if cluster_val is None:
                cluster_val = -1
            duplicates.append({'sequence_idx': dup, 'cluster': cluster_val})
    if duplicates:
        duplicate_df = pd.DataFrame(duplicates)
        cluster_df = pd.concat([cluster_df, duplicate_df], ignore_index=True)
        cluster_df = cluster_df.drop_duplicates(subset=['sequence_idx'], keep='first')
        cluster_df = cluster_df.rename(columns={'sequence_idx': 'accession'})
    # Save cluster assignments
    cluster_df.to_csv(f'/zhome/85/8/203063/a3_fungi/clusters/5_20_05_leaf/{GENE_NAME.lower()}_dm_clusters.csv', index=False)

if __name__ == '__main__':
    gene_names = ['LYS1', 'LYS2', 'LYS4', 'LYS9', 'LYS12', 'LYS20', 'ARO8', 'ACO2']
    
    # Create a process pool with number of CPUs available
    num_cpus = mp.cpu_count()
    print(f"Running with {num_cpus} processes")
    
    with mp.Pool(num_cpus) as pool:
        # Map the run_hdbscan function to all genes in parallel
        pool.map(run_hdbscan, gene_names)

