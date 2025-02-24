import pandas as pd
import matplotlib.pyplot as plt

def visualize_taxa(csv_path, output_path):
    # Load the CSV file into a DataFrame
    df = pd.read_csv(csv_path)

    # Generate summary statistics
    summary_stats = df['Phylum'].value_counts()
    print("Summary Statistics:")
    print(summary_stats)

    # Create a histogram
    plt.figure(figsize=(10, 6))
    summary_stats.plot(kind='bar')
    plt.title('Histogram of Taxa')
    plt.xlabel('Phylum')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.show()

if __name__ == '__main__':

    csv_path = '/zhome/85/8/203063/a3_fungi/data_out/taxa_non_filtered.csv'
    output_path = '/zhome/85/8/203063/a3_fungi/figures/taxa_histogram_non_filtered.png'
    visualize_taxa(csv_path, output_path)