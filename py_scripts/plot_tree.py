import os
os.environ['QT_QPA_PLATFORM']='offscreen'
import matplotlib
matplotlib.use('Agg')
import pandas as pd
import ete3
from ete3 import Tree, TreeStyle, NodeStyle

# Read phylum data
phylum_data = pd.read_csv('/zhome/85/8/203063/a3_fungi/data_out/taxa_non_filtered.csv')
phylum_dict = dict(zip(phylum_data['Accession'], phylum_data['Phylum']))

# Define colors for each phylum
phylum_colors = {
    'Ascomycota': '#1f77b4',  # blue
    'Basidiomycota': '#2ca02c',  # green
    'Mucoromycota': '#ff7f0e',  # orange
    'Zoopagomycota': '#d62728',  # red
    'Chytridiomycota': '#9467bd',  # purple
    'Blastocladiomycota': '#8c564b',  # brown
    'Cryptomycota': '#e377c2',  # pink
    'Microsporidia': '#7f7f7f',  # gray
    'Olpidiomycota': '#bcbd22',  # olive
}

# Load the tree
tree = Tree('/work3/s233201/enzyme_out/final_iq_fg.treefile')

# Collapse branches shorter than threshold
MIN_BRANCH_LENGTH = 0.1  # Adjust this threshold as needed
for node in tree.traverse():
    if not node.is_leaf() and node.dist < MIN_BRANCH_LENGTH:
        node.delete()

# Function to get accession from node name
def get_accession(node_name):
    if node_name.startswith('GC'):
        return node_name.split('_')[0] + '_' + node_name.split('_')[1]
    return node_name

# Create TreeStyle
ts = TreeStyle()
ts.show_leaf_name = False  # We'll add custom leaf names
ts.branch_vertical_margin = 2  # Adjust spacing between branches
ts.scale = 500  # Scale branch lengths
ts.show_scale = True
ts.mode = "c"  # circular mode
ts.arc_start = -180  # 0 degrees = 3 o'clock
ts.arc_span = 360  # Total angle to plot the tree

# Iterate through all nodes
for node in tree.traverse():
    if node.is_leaf():
        # Create node style
        nst = NodeStyle()
        nst["size"] = 5
        
        # Get accession and phylum
        accession = get_accession(node.name)
        phylum = phylum_dict.get(accession, "Unknown")
        
        # Set color based on phylum
        nst["fgcolor"] = phylum_colors.get(phylum, "black")
        nst["vt_line_color"] = phylum_colors.get(phylum, "black")
        nst["hz_line_color"] = phylum_colors.get(phylum, "black")
        
        # Apply style without adding text face
        node.set_style(nst)

# Create better formatted legend
legend_position = (20, 20)  # pixels from top-left corner
ts.legend_position = legend_position
ts.legend.clear()

for phylum, color in phylum_colors.items():
    # Create color box
    box_face = ete3.RectFace(20, 20, color, color)
    ts.legend.add_face(box_face, column=0)
    # Add phylum name next to the box
    text_face = ete3.TextFace(f" {phylum}", fsize=10)
    ts.legend.add_face(text_face, column=1)
    # Add a new line
    ts.legend.add_face(ete3.TextFace("", fsize=8), column=0)

# Save the tree as HTML (interactive)
tree.render("/zhome/85/8/203063/a3_fungi/figures/phylogenetic_tree.html", 
            w=1000,  # width can be smaller for HTML as it's zoomable
            tree_style=ts)

# Also keep the PNG version
tree.render("/zhome/85/8/203063/a3_fungi/figures/phylogenetic_tree.png", 
            w=2000, 
            units="px", 
            tree_style=ts)
