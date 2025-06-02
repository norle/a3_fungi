from ete3 import Tree
import os

# Define the base directory
base_dir = "/work3/s233201/output_phyl_busco_4"

# Define input and output file paths
tree_file = os.path.join(base_dir, "tree_iq_LGI_refactored.treefile")
outlier_file = "/zhome/85/8/203063/a3_fungi/data/outliers_set.txt"
output_file = os.path.join(base_dir, "tree_iq_LGI_no_outliers.treefile")

# Read outlier names from the file
with open(outlier_file, "r") as f:
    outlier_names = [line.strip() for line in f]

# Load the tree
t = Tree(tree_file)

# Remove outlier nodes from the tree
for outlier in outlier_names:
    try:
        node = t.search_nodes(name=outlier)[0]
        node.delete()
    except IndexError:
        print(f"Warning: Outlier '{outlier}' not found in the tree.")

# Write the modified tree to a new file
t.write(outfile=output_file)

print(f"Tree with outliers removed saved to {output_file}")
