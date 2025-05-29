import os
import glob
import numpy as np
import pandas as pd
from Bio import AlignIO, SeqIO
from collections import defaultdict
import matplotlib.pyplot as plt
from tqdm import tqdm
from numba import jit

# Keep only needed Bokeh imports
from bokeh.plotting import figure, save, output_file
from bokeh.layouts import column, row
from bokeh.models import (
    ColumnDataSource, ColorBar, LinearColorMapper, 
    BasicTicker, CheckboxGroup, CustomJS, 
    HoverTool
)
from bokeh.palettes import RdBu11
from bokeh.models import Tabs
from bokeh.models.layouts import TabPanel

@jit(nopython=True)
def calculate_column_conservation(column) -> float:
    """Calculate conservation score for a single column using Numba"""
    counts = np.zeros(26, dtype=np.int32)  # 26 for A-Z
    total = 0
    
    # Count occurrences of each amino acid (excluding gaps)
    for aa in column:
        if 65 <= aa <= 90:  # ASCII values for A-Z
            counts[aa - 65] += 1
            total += 1
    
    # Return frequency of most common character
    return float(np.max(counts)) / total if total > 0 else 0.0

@jit(nopython=True)
def calculate_all_conservation_scores(alignment_array):
    """Calculate conservation scores for all positions using Numba"""
    num_positions = alignment_array.shape[1]
    conservation_scores = np.zeros(num_positions)
    
    for i in range(num_positions):
        conservation_scores[i] = calculate_column_conservation(alignment_array[:, i])
    
    return conservation_scores

def calculate_conservation(alignment):
    """Calculate conservation scores for each position in alignment"""
    # Convert alignment to numpy array of ASCII values
    alignment_array = np.array([[ord(aa) for aa in str(record.seq)] 
                              for record in alignment], dtype=np.int32)
    
    # Calculate conservation using numba-optimized function
    return calculate_all_conservation_scores(alignment_array).tolist()

def load_phylum_data(taxa_file):
    """Load the phylum information for sequences"""
    phylum_data = pd.read_csv(taxa_file)
    # Create a mapping from accession to phylum
    return dict(zip(phylum_data['Accession'], phylum_data['Phylum']))

def get_most_common_aa(alignment, position):
    """Get most common amino acid at a given position"""
    aa_counts = {}
    for record in alignment:
        aa = record.seq[position]
        if aa != '-':  # Skip gaps
            aa_counts[aa] = aa_counts.get(aa, 0) + 1
    return max(aa_counts.items(), key=lambda x: x[1])[0] if aa_counts else '-'

def create_interactive_plot(gene_alignments, gene_scores, accession_to_phylum, output_dir):
    """Create an interactive conservation plot with phylum filtering"""
    
    # Get unique phyla across all sequences
    all_phyla = sorted(set(accession_to_phylum.values()))
    
    # Create tabs for each gene
    tabs = []
    
    for gene_name, alignment in gene_alignments.items():
        # Get accessions and their phyla for this alignment
        seq_accessions = [record.id.split('|')[0] if '|' in record.id else record.id for record in alignment]
        seq_phyla = [accession_to_phylum.get(acc, "Unknown") for acc in seq_accessions]
        
        # Group sequences by phylum
        phylum_indices = defaultdict(list)
        for idx, phylum in enumerate(seq_phyla):
            phylum_indices[phylum].append(idx)
        
        # Prepare data for Bokeh
        alignment_length = len(alignment[0].seq)
        positions = list(range(1, alignment_length + 1))
        
        # Create a color mapper - reverse RdBu11 for blue (0) to red (1)
        color_mapper = LinearColorMapper(
            palette=list(RdBu11), low=0, high=1
        )
        
        # Create figure - modified to show a single row instead of multiple phyla rows
        p = figure(
            width=1200, height=200, 
            x_range=(0, alignment_length),
            y_range=(0, 2),  # Just need space for a single row
            x_axis_label='Alignment Position',
            y_axis_label='',  # No y-axis label needed
            title=f"Conservation scores for {gene_name}",
            tools="pan,wheel_zoom,box_zoom,reset,save"
        )
        
        # Hide y-axis
        p.yaxis.visible = False
        
        # Add color bar
        color_bar = ColorBar(
            color_mapper=color_mapper,
            ticker=BasicTicker(),
            label_standoff=12,
            border_line_color=None,
            location=(0, 0),
            title="Conservation Score"
        )
        p.add_layout(color_bar, 'right')
        
        # Get most common amino acid for each position
        most_common_aas = [get_most_common_aa(alignment, i) for i in range(alignment_length)]
        
        # Create a data source for the combined conservation scores
        combined_data = ColumnDataSource(data=dict(
            x=positions,
            y=[1] * alignment_length,
            conservation=gene_scores[gene_name],
            phylum=['All'] * alignment_length,
            amino_acid=most_common_aas  # Add amino acid information
        ))
        
        # Store phylum-specific data for updating the plot
        phylum_conservation_data = {}
        for phylum in all_phyla:
            if phylum in phylum_indices:
                # Get sequences for this phylum
                phylum_seqs = [alignment[idx] for idx in phylum_indices[phylum]]
                
                # If we have sequences for this phylum, calculate conservation
                if phylum_seqs:
                    # Create a sub-alignment with just these sequences
                    phylum_alignment = [record.seq for record in phylum_seqs]
                    alignment_array = np.array([[ord(aa) for aa in str(seq)] 
                                              for seq in phylum_alignment], dtype=np.int32)
                    phylum_scores = calculate_all_conservation_scores(alignment_array).tolist()
                    
                    # Store the conservation scores for this phylum
                    phylum_conservation_data[phylum] = phylum_scores
        
        # Add hover tool
        hover = HoverTool(
            tooltips=[
                ("Position", "@x"),
                ("Conservation", "@conservation{0.00}"),
                ("Most Common AA", "@amino_acid")
            ]
        )
        p.add_tools(hover)
        
        # Add rectangles for the combined conservation view
        rect_renderer = p.rect(
            x='x', y='y', width=1, height=0.8,
            source=combined_data,
            fill_color={'field': 'conservation', 'transform': color_mapper},
            line_color=None
        )
        
        # Create checkbox group for phyla filtering
        checkbox = CheckboxGroup(labels=all_phyla, active=list(range(len(all_phyla))))
        
        # Create JavaScript callback for checkbox interaction
        callback = CustomJS(
            args=dict(
                source=combined_data,
                phylum_data=phylum_conservation_data,
                checkbox=checkbox,
                phyla=all_phyla,
                positions=positions
            ), 
            code="""
            const active = checkbox.active;
            const selected_phyla = active.map(i => phyla[i]);
            
            if (selected_phyla.length === 0) {
                // If no phyla selected, show empty data
                const empty_data = positions.map(p => 0);
                source.data['conservation'] = empty_data;
                source.data['phylum'] = positions.map(p => 'None');
            } else {
                // Calculate conservation scores for all selected phyla combined
                const combined_scores = Array(positions.length).fill(0);
                
                // For each position, calculate the average conservation across selected phyla
                for (let pos = 0; pos < positions.length; pos++) {
                    let valid_scores = 0;
                    let sum = 0;
                    
                    for (let i of active) {
                        const phylum = phyla[i];
                        if (phylum in phylum_data) {
                            sum += phylum_data[phylum][pos];
                            valid_scores++;
                        }
                    }
                    
                    combined_scores[pos] = valid_scores > 0 ? sum / valid_scores : 0;
                }
                
                source.data['conservation'] = combined_scores;
                source.data['phylum'] = positions.map(p => selected_phyla.join(', '));
            }
            
            source.change.emit();
        """
        )
        
        checkbox.js_on_change('active', callback)
        
        # Create layout with just conservation plot
        controls = column(checkbox, width=200, height=400)
        plot_layout = row(controls, p)
        
        # Add to tabs without structure visualization
        tab = TabPanel(child=plot_layout, title=gene_name)
        tabs.append(tab)
    
    # Create the tabbed layout
    tabs_layout = Tabs(tabs=tabs)
    
    # Save the result
    output_file(os.path.join(output_dir, "interactive_conservation_1.html"))
    save(tabs_layout)
    
    print(f"Interactive plot saved to {os.path.join(output_dir, 'interactive_conservation.html')}")

def main():
    # Define paths
    output_dir = '/zhome/85/8/203063/a3_fungi/html'
    os.makedirs(output_dir, exist_ok=True)
    
    # Taxa data file path
    taxa_file = '/zhome/85/8/203063/a3_fungi/data_out/taxa_clean_0424.csv'
    
    # Define the desired order of genes
    gene_order = ["LYS20", "ACO2", "LYS4", "LYS12", "ARO8", "LYS2", "LYS9", "LYS1"]
    
    # Get all alignment files
    all_files = glob.glob('/work3/s233201/enzyme_out_6/alignments/*aln')
    
    # Create a dictionary to map gene names to full file paths
    file_dict = {os.path.basename(f).split('.')[0]: f for f in all_files}
    
    # Load phylum information
    accession_to_phylum = load_phylum_data(taxa_file)
    
    # Store alignments and conservation scores
    gene_alignments = {}
    gene_scores = {}
    
    # Process files in the specified order
    for gene in gene_order:
        if gene in file_dict:
            try:
                alignment = AlignIO.read(file_dict[gene], 'fasta')
                conservation_scores = calculate_conservation(alignment)
                gene_alignments[gene] = alignment
                gene_scores[gene] = conservation_scores
            except Exception as e:
                print(f"Error processing {gene}: {str(e)}")
        else:
            print(f"Warning: {gene} not found in alignment files")
    
    # Create interactive plot
    create_interactive_plot(gene_alignments, gene_scores, accession_to_phylum, output_dir)
    
    print("Interactive conservation plots created successfully.")

if __name__ == "__main__":
    main()
