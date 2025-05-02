from ete3 import Tree
import csv

def modify_tree(input_path, output_path, phylum_map):
    """
    Loads a tree, truncates all node names to 15 characters,
    saves the modified tree, and returns annotations.

    Args:
        input_path (str): Path to the input tree file (Newick format).
        output_path (str): Path to save the modified tree file.
        phylum_map (dict): Dictionary mapping truncated node names to phylum labels.

    Returns:
        list: A list of tuples, where each tuple is (truncated_node_name, phylum_label).
    """
    annotations = [] # List to store annotations
    try:
        # Load the tree
        tree = Tree(input_path, format=1) # Assuming format 1, adjust if needed

        # Iterate through all nodes and truncate names, collect annotations
        for node in tree.traverse():
            if node.name:
                original_name = node.name
                truncated_name = original_name[:15]
                node.name = truncated_name # Apply truncation

                # Check if the truncated name is in the phylum map and collect annotation
                if truncated_name in phylum_map:
                    phylum_label = phylum_map[truncated_name]
                    annotations.append((truncated_name, phylum_label))

        # Write the modified tree (with truncated names only) to the output file
        # format=1 corresponds to the standard Newick format with internal node names
        tree.write(outfile=output_path, format=1)
        print(f"Successfully processed tree and saved truncated version to {output_path}")

    except Exception as e:
        print(f"An error occurred during tree processing: {e}")
        # Optionally re-raise or return empty list depending on desired error handling
        return [] # Return empty list on error

    return annotations

if __name__ == "__main__":
    # Define the input and output file paths here
    input_file_path = "/work3/s233201/enzyme_out_6/tree_LGI.treefile"
    # Output tree file with only truncated names
    output_tree_path = "/work3/s233201/enzyme_out_6/tree_LGI_refactored.treefile"
    phylum_csv_path = "data_out/taxa_clean_0424.csv"
    # Output annotation file path for COLORSTRIP
    output_annotation_path = "/work3/s233201/enzyme_out_6/tree_iq_LGI_phylum_aaa_colorstrip.txt"

    # Create the phylum map by reading the CSV file
    phylum_map = {}
    try:
        with open(phylum_csv_path, mode='r', newline='') as infile:
            reader = csv.reader(infile)
            header = next(reader) # Skip header row
            for row in reader:
                if len(row) >= 2: # Ensure row has at least two columns
                    accession, phylum = row[0], row[1]
                    truncated_accession = accession[:15] # Ensure keys match truncated names
                    # Use a placeholder if phylum is empty or missing
                    phylum_label = phylum if phylum else "Unknown"
                    phylum_map[truncated_accession] = phylum_label
        print(f"Successfully loaded phylum map from {phylum_csv_path}")
    except FileNotFoundError:
        print(f"Error: Phylum CSV file not found at {phylum_csv_path}")
        exit(1) # Exit if the mapping file is crucial and not found
    except Exception as e:
        print(f"An error occurred while reading the phylum CSV: {e}")
        exit(1)

    # Call the function to modify the tree and get annotations
    collected_annotations = modify_tree(input_file_path, output_tree_path, phylum_map)

    # Write the annotations to the iTOL annotation file (DATASET_COLORSTRIP)
    if collected_annotations:
        try:
            # Define the specific colors for known phyla
            PHYLUM_COLORS = {
                'Ascomycota': '#377eb8',        # Blue
                'Basidiomycota': '#e41a1c',     # Red
                'Mucoromycota': '#4daf4a',      # Green
                'Zoopagomycota': '#984ea3',     # Purple
                'Chytridiomycota': '#ff7f00',   # Orange
                'Blastocladiomycota': '#ffff33',# Yellow
                'Cryptomycota': '#a65628',      # Brown
                'Unknown': '#cccccc'           # Default Grey for Unknown/Other
            }

            # Extract unique phylum labels found in the data
            unique_phyla_in_data = list(dict.fromkeys(label for _, label in collected_annotations))

            # Filter PHYLUM_COLORS to only include phyla present in the data, maintaining predefined order if possible
            # Or simply use the predefined list for the legend if that's preferred. Let's use the predefined list for consistency.
            legend_phyla = list(PHYLUM_COLORS.keys())
            legend_colors_list = [PHYLUM_COLORS[phylum] for phylum in legend_phyla]

            # Check if any phyla in data are missing from PHYLUM_COLORS (besides 'Unknown')
            for phylum in unique_phyla_in_data:
                if phylum not in PHYLUM_COLORS:
                    print(f"Warning: Phylum '{phylum}' found in data but not in predefined PHYLUM_COLORS. It will be colored as 'Unknown'.")
                    # Optionally add it to PHYLUM_COLORS with the 'Unknown' color
                    # PHYLUM_COLORS[phylum] = PHYLUM_COLORS['Unknown']


            with open(output_annotation_path, 'w') as outfile:
                # Write iTOL specific header for COLORSTRIP
                outfile.write("DATASET_COLORSTRIP\n")
                outfile.write("SEPARATOR TAB\n")
                outfile.write("DATASET_LABEL\tPhylum Distribution\n") # Label for the dataset
                # Optional: Set default color if a node has no data (already handled by 'Unknown' mapping)
                # outfile.write("COLOR\t#cccccc\n")

                # Write Legend using the predefined PHYLUM_COLORS order
                outfile.write("LEGEND_TITLE\tPhylum\n") # Title for the legend
                legend_shapes = '\t'.join(['1'] * len(legend_phyla)) # 1 is rectangle
                outfile.write(f"LEGEND_SHAPES\t{legend_shapes}\n")
                legend_colors_str = '\t'.join(legend_colors_list)
                outfile.write(f"LEGEND_COLORS\t{legend_colors_str}\n")
                legend_labels_str = '\t'.join(legend_phyla)
                outfile.write(f"LEGEND_LABELS\t{legend_labels_str}\n")

                # Write DATA header
                outfile.write("DATA\n")
                # Write the actual data (Node ID <TAB> Color)
                for node_id, label in collected_annotations:
                    # Get the color from PHYLUM_COLORS, defaulting to 'Unknown' color if not found
                    color = PHYLUM_COLORS.get(label, PHYLUM_COLORS['Unknown'])
                    outfile.write(f"{node_id}\t{color}\n")


            print(f"Successfully wrote COLORSTRIP annotations to {output_annotation_path}")
        except Exception as e:
            print(f"An error occurred while writing the annotation file: {e}")
    else:
        print("No annotations were generated (possibly due to errors or no matching nodes).")
