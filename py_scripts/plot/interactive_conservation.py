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

def calculate_conservation(alignment, outliers):
    """Calculate conservation scores for each position in alignment, excluding outliers"""
    
    # Filter out outlier sequences - check both full ID and accession part
    filtered_alignment = []
    removed_count = 0
    
    for record in alignment:
        # Extract accession (part before | if present)
        accession = record.id.split('|')[0] if '|' in record.id else record.id
        # Keep sequence if neither full ID nor accession is in outliers
        if record.id not in outliers and accession not in outliers:
            filtered_alignment.append(record)
        else:
            removed_count += 1
    
    print(f"Removed {removed_count} outlier sequences out of {len(alignment)} total sequences")
    
    # If all sequences are outliers, return an empty list
    if not filtered_alignment:
        print("Warning: All sequences in alignment are outliers. Returning empty conservation scores.")
        return []
    
    # Convert alignment to numpy array of ASCII values
    alignment_array = np.array([[ord(aa) for aa in str(record.seq)] 
                              for record in filtered_alignment], dtype=np.int32)
    
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
    
    print(f"Creating interactive plot with {len(gene_alignments)} genes...")
    
    # Create tabs for each gene
    tabs = []
    
    for gene_name, alignment in gene_alignments.items():
        print(f"Processing {gene_name} for plot creation...")
        
        # Get accessions and their phyla for this alignment (these are already filtered alignments)
        seq_accessions = [record.id.split('|')[0] if '|' in record.id else record.id for record in alignment]
        seq_phyla = [accession_to_phylum.get(acc, "Unknown") for acc in seq_accessions]
        
        print(f"  - {gene_name}: {len(alignment)} sequences, phyla: {set(seq_phyla)}")
        
        # Group sequences by phylum
        phylum_indices = defaultdict(list)
        for idx, phylum in enumerate(seq_phyla):
            phylum_indices[phylum].append(idx)
        
        # Get unique phyla and prepare sequence data for JavaScript
        valid_phyla = sorted(set(seq_phyla))
        
        # Prepare sequence data for JavaScript - store actual sequences grouped by phylum
        phylum_sequences = {}
        for phylum in valid_phyla:
            if phylum in phylum_indices:
                phylum_seqs = []
                for idx in phylum_indices[phylum]:
                    phylum_seqs.append(str(alignment[idx].seq))
                phylum_sequences[phylum] = phylum_seqs
        
        # Prepare data for Bokeh
        alignment_length = len(alignment[0].seq)
        positions = list(range(1, alignment_length + 1))
        
        print(f"  - {gene_name}: alignment length = {alignment_length}")
        print(f"  - {gene_name}: conservation scores length = {len(gene_scores[gene_name])}")
        
        # Ensure conservation scores match alignment length
        if len(gene_scores[gene_name]) != alignment_length:
            print(f"Warning: Conservation scores length mismatch for {gene_name}")
            continue
        
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
            title=f"Conservation scores for {gene_name} (outliers removed)",
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
            amino_acid=most_common_aas
        ))
        
        # Add hover tool
        hover = HoverTool(
            tooltips=[
                ("Position", "@x"),
                ("Conservation", "@conservation{0.00}"),
                ("Most Common AA", "@amino_acid"),
                ("Phylum", "@phylum")
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
        
        # Create checkbox group for phyla filtering - only include valid phyla
        checkbox = CheckboxGroup(labels=valid_phyla, active=list(range(len(valid_phyla))))
        
        # Simplified JavaScript callback to avoid potential errors
        callback = CustomJS(
            args=dict(
                source=combined_data,
                phylum_sequences=phylum_sequences,
                checkbox=checkbox,
                phyla=valid_phyla,
                positions=positions,
                original_scores=gene_scores[gene_name]
            ), 
            code="""
            // Function to calculate conservation score for a position
            function calculateConservation(sequences, position) {
                if (!sequences || sequences.length === 0) return 0;
                
                const aaCounts = {};
                let total = 0;
                
                for (let seq of sequences) {
                    if (position < seq.length) {
                        const aa = seq[position];
                        if (aa !== '-' && aa !== 'X') {  // Skip gaps and unknown
                            aaCounts[aa] = (aaCounts[aa] || 0) + 1;
                            total++;
                        }
                    }
                }
                
                if (total === 0) return 0;
                
                // Find the most common amino acid
                let maxCount = 0;
                for (let count of Object.values(aaCounts)) {
                    if (count > maxCount) maxCount = count;
                }
                
                return maxCount / total;
            }
            
            const active = checkbox.active;
            const selected_phyla = active.map(i => phyla[i]);
            
            console.log('Selected phyla:', selected_phyla);
            
            if (selected_phyla.length === 0) {
                // If no phyla selected, show empty data
                const empty_data = new Array(positions.length).fill(0);
                source.data['conservation'] = empty_data;
                source.data['phylum'] = new Array(positions.length).fill('None');
            } else if (selected_phyla.length === phyla.length) {
                // If ALL phyla are selected, use the original scores
                source.data['conservation'] = [...original_scores];
                source.data['phylum'] = new Array(positions.length).fill('All');
            } else {
                // Combine sequences from selected phyla
                let combined_sequences = [];
                for (let phylum of selected_phyla) {
                    if (phylum in phylum_sequences) {
                        combined_sequences = combined_sequences.concat(phylum_sequences[phylum]);
                    }
                }
                
                console.log('Combined sequences count:', combined_sequences.length);
                
                // Calculate conservation scores from scratch for the combined sequences
                const conservation_scores = [];
                for (let pos = 0; pos < positions.length; pos++) {
                    conservation_scores.push(calculateConservation(combined_sequences, pos));
                }
                
                source.data['conservation'] = conservation_scores;
                source.data['phylum'] = new Array(positions.length).fill(selected_phyla.join(', '));
            }
            
            source.change.emit();
        """
        )
        
        checkbox.js_on_change('active', callback)
        
        # Create layout with conservation plot and controls
        from bokeh.models import Div
        title_div = Div(text=f"<h3>Phyla in {gene_name}:</h3>", width=200)
        controls = column(title_div, checkbox, width=200, height=400)
        plot_layout = row(controls, p)
        
        # Add to tabs
        tab = TabPanel(child=plot_layout, title=gene_name)
        tabs.append(tab)
        
        print(f"  - Successfully created tab for {gene_name}")
    
    if not tabs:
        print("Error: No tabs were created!")
        return
    
    # Create the tabbed layout
    tabs_layout = Tabs(tabs=tabs)
    
    # Save the result
    output_path = os.path.join(output_dir, "interactive_conservation.html")
    print(f"Saving plot to {output_path}")
    
    try:
        output_file(output_path)
        save(tabs_layout)
        print(f"Interactive plot saved successfully to {output_path}")
    except Exception as e:
        print(f"Error saving plot: {e}")

def main():
    # Define paths
    output_dir = '/zhome/85/8/203063/a3_fungi/html'
    os.makedirs(output_dir, exist_ok=True)
    
    # Taxa data file path
    taxa_file = '/zhome/85/8/203063/a3_fungi/data_out/taxa_clean_0424.csv'
    
    # Define the desired order of genes
    gene_order = ["LYS20", "ACO2", "LYS4", "LYS12", "ARO8", "LYS2", "LYS9", "LYS1"]
    
    # Get all alignment files
    all_files = glob.glob('/work3/s233201/enzyme_out_6/trim/*aln')
    
    # Load outlier gene names from file
    outlier_file = '/zhome/85/8/203063/a3_fungi/data/outliers_set.txt'
    with open(outlier_file, 'r') as f:
        outliers = set(line.strip() for line in f)
    
    print(f"Loaded {len(outliers)} outlier sequences from {outlier_file}")
    
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
                print(f"\nProcessing {gene} with {len(alignment)} sequences...")
                conservation_scores = calculate_conservation(alignment, outliers)
                
                if conservation_scores:
                    # Filter the alignment to remove outliers for the interactive plot
                    filtered_alignment = []
                    for record in alignment:
                        accession = record.id.split('|')[0] if '|' in record.id else record.id
                        if record.id not in outliers and accession not in outliers:
                            filtered_alignment.append(record)
                    
                    gene_alignments[gene] = filtered_alignment
                    gene_scores[gene] = conservation_scores
                    print(f"Successfully processed {gene} with {len(filtered_alignment)} sequences after outlier removal")
                else:
                    print(f"Skipping {gene} due to all sequences being outliers.")
                    continue
            except Exception as e:
                print(f"Error processing {gene}: {str(e)}")
        else:
            print(f"Warning: {gene} not found in alignment files")
    
    # Create interactive plot
    create_interactive_plot(gene_alignments, gene_scores, accession_to_phylum, output_dir)
    
    print("Interactive conservation plots created successfully.")

if __name__ == "__main__":
    main()
