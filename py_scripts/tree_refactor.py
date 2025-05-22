from ete3 import Tree
import csv
import colorsys
from collections import Counter

def modify_tree(input_path, output_path, taxon_map):
    """
    Loads a tree, truncates all node names to 15 characters,
    saves the modified tree, and returns annotations.

    Args:
        input_path (str): Path to the input tree file (Newick format).
        output_path (str): Path to save the modified tree file.
        taxon_map (dict): Dictionary mapping truncated node names to taxon labels.

    Returns:
        list: A list of tuples, where each tuple is (truncated_node_name, taxon_label).
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

                # Check if the truncated name is in the taxon map and collect annotation
                if truncated_name in taxon_map:
                    taxon_label = taxon_map[truncated_name]
                    annotations.append((truncated_name, taxon_label))

        # Write the modified tree (with truncated names only) to the output file
        # format=1 corresponds to the standard Newick format with internal node names
        tree.write(outfile=output_path, format=1)
        print(f"Successfully processed tree and saved truncated version to {output_path}")

    except Exception as e:
        print(f"An error occurred during tree processing: {e}")
        # Optionally re-raise or return empty list depending on desired error handling
        return [] # Return empty list on error

    return annotations

def generate_distinct_colors(n):
    """Generate n distinct colors using HSV color space."""
    colors = []
    for i in range(n):
        hue = i / n
        saturation = 0.7 + (i % 3) * 0.1  # Vary saturation slightly
        value = 0.9
        rgb = colorsys.hsv_to_rgb(hue, saturation, value)
        # Convert to hex
        hex_color = '#{:02x}{:02x}{:02x}'.format(
            int(rgb[0] * 255),
            int(rgb[1] * 255),
            int(rgb[2] * 255)
        )
        colors.append(hex_color)
    return colors

def get_top_classes(class_map, n=15):
    """Get the n most common classes from the class map."""
    class_counts = Counter(class_map.values())
    # Get the n most common classes, excluding 'Other'
    if 'Other' in class_counts:
        del class_counts['Other']
    top_classes = [class_name for class_name, count in class_counts.most_common(n)]
    return top_classes

if __name__ == "__main__":
    # Define the input and output file paths here
    input_file_path = "/work3/s233201/output_phyl_busco_4/tree_iq_LGI.treefile"
    output_tree_path = "/work3/s233201/output_phyl_busco_4/tree_iq_LGI_refactored.treefile"
    phylum_csv_path = "data_out/taxa_clean_0424.csv"
    class_csv_path = "data_out/class_non_filtered.csv"
    output_phylum_path = "/work3/s233201/enzyme_out_6/tree_iq_LGI_phylum_aaa_colorstrip.txt"
    output_class_path = "data/tree_iq_LGI_class_aaa_colorstrip.txt"

    # Create both phylum and class maps
    phylum_map = {}
    class_map = {}
    
    # Load phylum map
    try:
        with open(phylum_csv_path, mode='r', newline='') as infile:
            reader = csv.reader(infile)
            header = next(reader) # Skip header row
            for row in reader:
                if len(row) >= 2: # Ensure row has at least two columns
                    accession, phylum = row[0], row[1]
                    truncated_accession = accession[:15] # Ensure keys match truncated names
                    # Use "Other" instead of "Unknown"
                    phylum_label = phylum if phylum else "Other"
                    phylum_map[truncated_accession] = phylum_label
        print(f"Successfully loaded phylum map from {phylum_csv_path}")
    except FileNotFoundError:
        print(f"Error: Phylum CSV file not found at {phylum_csv_path}")
        exit(1) # Exit if the mapping file is crucial and not found
    except Exception as e:
        print(f"An error occurred while reading the phylum CSV: {e}")
        exit(1)

    # Load class map
    try:
        with open(class_csv_path, mode='r', newline='') as infile:
            reader = csv.reader(infile)
            header = next(reader)  # Skip header row
            for row in reader:
                if len(row) >= 2:
                    accession, class_name = row[0], row[1]
                    truncated_accession = accession[:15]
                    # Use "Other" instead of "Unknown"
                    class_label = class_name if class_name else "Other"
                    class_map[truncated_accession] = class_label
        print(f"Successfully loaded class map from {class_csv_path}")
    except FileNotFoundError:
        print(f"Error: Class CSV file not found at {class_csv_path}")
        exit(1)
    except Exception as e:
        print(f"An error occurred while reading the class CSV: {e}")
        exit(1)

    # Call the function to modify the tree and get annotations
    collected_phylum_annotations = modify_tree(input_file_path, output_tree_path, phylum_map)
    collected_class_annotations = modify_tree(input_file_path, output_tree_path, class_map)

    # Define colors for phyla
    PHYLUM_COLORS = {
        'Ascomycota': '#377eb8',        # Blue
        'Basidiomycota': '#e41a1c',     # Red
        'Mucoromycota': '#4daf4a',      # Green
        'Zoopagomycota': '#984ea3',     # Purple
        'Chytridiomycota': '#ff7f00',   # Orange
        'Blastocladiomycota': '#ffff33',# Yellow
        'Cryptomycota': '#a65628',      # Brown
        'Other': '#cccccc'              # Default Grey for Other
    }

    # Write phylum annotations to iTOL COLORSTRIP file
    if collected_phylum_annotations:
        try:
            with open(output_phylum_path, 'w') as outfile:
                # Write iTOL specific header for COLORSTRIP
                outfile.write("DATASET_COLORSTRIP\n")
                outfile.write("SEPARATOR TAB\n")
                outfile.write("DATASET_LABEL\tPhylum Distribution\n") # Label for the dataset

                # Write Legend using the predefined PHYLUM_COLORS order
                outfile.write("LEGEND_TITLE\tPhylum\n") # Title for the legend
                legend_shapes = '\t'.join(['1'] * len(PHYLUM_COLORS)) # 1 is rectangle
                outfile.write(f"LEGEND_SHAPES\t{legend_shapes}\n")
                legend_colors_str = '\t'.join(PHYLUM_COLORS.values())
                outfile.write(f"LEGEND_COLORS\t{legend_colors_str}\n")
                legend_labels_str = '\t'.join(PHYLUM_COLORS.keys())
                outfile.write(f"LEGEND_LABELS\t{legend_labels_str}\n")

                # Write DATA header
                outfile.write("DATA\n")
                # Write the actual data (Node ID <TAB> Color)
                for node_id, label in collected_phylum_annotations:
                    # Get the color from PHYLUM_COLORS, defaulting to 'Other' color if not found
                    color = PHYLUM_COLORS.get(label, PHYLUM_COLORS['Other'])
                    outfile.write(f"{node_id}\t{color}\n")


            print(f"Successfully wrote phylum COLORSTRIP annotations to {output_phylum_path}")
        except Exception as e:
            print(f"An error occurred while writing the phylum annotation file: {e}")
    else:
        print("No phylum annotations were generated (possibly due to errors or no matching nodes).")

    # Instead of using all classes, get the top 15
    top_classes = get_top_classes(class_map, n=15)
    
    # Generate colors for the top classes
    class_colors = generate_distinct_colors(len(top_classes))
    
    # Create the color map for top classes
    CLASS_COLORS = dict(zip(top_classes, class_colors))
    CLASS_COLORS['Other'] = '#cccccc'  # Add Other with grey color

    # Modify class map to replace rare classes with 'Other'
    for acc in class_map:
        if class_map[acc] not in CLASS_COLORS:
            class_map[acc] = 'Other'

    # Write class annotations to iTOL COLORSTRIP file
    if collected_class_annotations:
        try:
            with open(output_class_path, 'w') as outfile:
                outfile.write("DATASET_COLORSTRIP\n")
                outfile.write("SEPARATOR TAB\n")
                outfile.write("DATASET_LABEL\tClass Distribution\n")

                # Write Legend using the predefined CLASS_COLORS order
                outfile.write("LEGEND_TITLE\tClass\n") # Title for the legend
                legend_shapes = '\t'.join(['1'] * len(CLASS_COLORS)) # 1 is rectangle
                outfile.write(f"LEGEND_SHAPES\t{legend_shapes}\n")
                outfile.write(f"LEGEND_COLORS\t{'\t'.join(CLASS_COLORS.values())}\n")
                outfile.write(f"LEGEND_LABELS\t{'\t'.join(CLASS_COLORS.keys())}\n")

                # Write DATA header
                outfile.write("DATA\n")
                # Write the actual data (Node ID <TAB> Color)
                for node_id, label in collected_class_annotations:
                    # Get the color from CLASS_COLORS, defaulting to 'Other' color if not found
                    color = CLASS_COLORS.get(label, CLASS_COLORS['Other'])
                    outfile.write(f"{node_id}\t{color}\n")

            print(f"Successfully wrote class COLORSTRIP annotations to {output_class_path}")
        except Exception as e:
            print(f"An error occurred while writing the class annotation file: {e}")
    else:
        print("No class annotations were generated (possibly due to errors or no matching nodes).")
