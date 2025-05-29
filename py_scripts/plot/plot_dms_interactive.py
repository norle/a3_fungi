import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import os

def plot_dms_interactive(dm1, dm2, dm1_name='dm1', dm2_name='dm2', to_remove=None):
    # Clean up and standardize accession IDs
    dm1.iloc[:, 0] = dm1.iloc[:, 0].str[:15]
    dm2.iloc[:, 0] = dm2.iloc[:, 0].str[:15]
    
    dm1_order = dm1.iloc[:, 0].tolist()
    dm2_order = dm2.iloc[:, 0].tolist()
    
    # Find common entries between dm1 and dm2
    common_entries = list(set(dm1_order) & set(dm2_order))
    missing_entries = set(dm1_order) - set(dm2_order)
    if missing_entries:
        print(f"Warning: Following entries are missing from {dm2_name}:")
        print(missing_entries)
        print("Removing these entries from both matrices...")
    
    # Filter rows and corresponding columns for both matrices
    keep_indices_dm1 = [i for i, acc in enumerate(dm1_order) if acc in common_entries]
    keep_indices_dm2 = [i for i, acc in enumerate(dm2_order) if acc in common_entries]
    
    # Filter rows
    dm1 = dm1.iloc[keep_indices_dm1].reset_index(drop=True)
    dm2 = dm2.iloc[keep_indices_dm2].reset_index(drop=True)
    
    # Filter columns (excluding first column which contains accessions)
    col_indices_dm1 = [0] + [i + 1 for i in keep_indices_dm1]
    col_indices_dm2 = [0] + [i + 1 for i in keep_indices_dm2]
    
    dm1 = dm1.iloc[:, col_indices_dm1]
    dm2 = dm2.iloc[:, col_indices_dm2]
    
    # Update orders after filtering
    dm1_order = dm1.iloc[:, 0].tolist()
    dm2_order = dm2.iloc[:, 0].tolist()
    
    # Create mapping for reordering dm2
    order_mapping = [dm2_order.index(x) for x in dm1_order]
    
    # Reorder dm2 to match dm1's order
    dm2 = dm2.iloc[order_mapping]
    dm2_cols = dm2.columns.tolist()
    dm2 = dm2[[dm2_cols[0]] + [dm2_cols[i+1] for i in order_mapping]]

    # Remove specified accessions if to_remove is provided
    if to_remove is not None:
        # Clean up the accessions to remove (remove newlines and whitespace)
        to_remove = [acc.strip() for acc in to_remove]
        
        # Create mask for rows to keep
        keep_mask = ~dm1.iloc[:, 0].isin(to_remove)
        
        # Get integer indices from boolean mask
        keep_indices = np.where(keep_mask)[0]
        
        # Filter both matrices
        dm1 = dm1.iloc[keep_indices].reset_index(drop=True)
        dm2 = dm2.iloc[keep_indices].reset_index(drop=True)
        
        # Filter columns (excluding first column which contains accessions)
        col_indices = [0] + [i + 1 for i in keep_indices]
        dm1 = dm1.iloc[:, col_indices]
        dm2 = dm2.iloc[:, col_indices]

    # Continue with numerical part extraction
    accessions = dm1.iloc[:, 0].tolist()
    dm1 = dm1.iloc[:, 1:]
    dm2 = dm2.iloc[:, 1:]

    # Convert to numpy arrays
    dm1_array = dm1.to_numpy()
    dm2_array = dm2.to_numpy()
    
    # Load taxa information to get phyla
    taxa_df = pd.read_csv('/zhome/85/8/203063/a3_fungi/data_out/taxa_no_missing_after_interpro.csv')
    taxa_dict = dict(zip(taxa_df['Accession'].str[:15], taxa_df['Phylum']))
    
    # Map accessions to phyla
    phyla = [taxa_dict.get(acc, "Unknown") for acc in accessions]
    
    # Get unique phylum pairs and assign colors
    unique_phyla = sorted(set(phyla))
    phyla_pairs = []
    for i, p1 in enumerate(unique_phyla):
        for p2 in unique_phyla[i:]:
            phyla_pairs.append((p1, p2))
    
    # TOL 27 color palette (colorblind-friendly)
    tol_27_colors = [
        '#332288', '#117733', '#44AA99', '#88CCEE', '#DDCC77', '#CC6677', '#AA4499',
        '#882255', '#6699CC', '#661100', '#DD6677', '#AA4466', '#4477AA', '#228833',
        '#CCBB44', '#EE8866', '#BBCC33', '#AAAA00', '#EEDD88', '#FFAABB', '#77AADD',
        '#99DDFF', '#44BB99', '#DDDDDD', '#000000', '#F0E442', '#BBBBBB'
    ]
    
    print(f"Number of unique phyla: {len(unique_phyla)}")
    print(f"Number of possible phylum pairs: {len(phyla_pairs)}")

    # Get upper triangle indices
    rows, cols = np.triu_indices(dm1_array.shape[0], k=1)
    
    # Extract distances using these indices
    dm1_flat = dm1_array[rows, cols]
    dm2_flat = dm2_array[rows, cols]
    
    # Create DataFrame for plotting
    df_data = []
    for i in range(len(rows)):
        phylum_i = phyla[rows[i]]
        phylum_j = phyla[cols[i]]
        pair_name = f"{min(phylum_i, phylum_j)}-{max(phylum_i, phylum_j)}"
        
        df_data.append({
            'x': dm1_flat[i],
            'y': dm2_flat[i],
            'phylum_pair': pair_name,
            'acc_i': accessions[rows[i]],
            'acc_j': accessions[cols[i]]
        })
    
    df = pd.DataFrame(df_data)
    
    # Calculate min and max values for plot ranges
    min_val = min(df['x'].min(), df['y'].min())
    max_val = max(df['x'].max(), df['y'].max())
    
    # Create color mapping for phylum pairs
    unique_pairs = sorted(df['phylum_pair'].unique())
    color_mapping = {pair: tol_27_colors[i % len(tol_27_colors)] 
                    for i, pair in enumerate(unique_pairs)}
    
    # Create the interactive plot
    fig = go.Figure()
    
    # Add traces for each phylum pair
    for pair in unique_pairs:
        pair_data = df[df['phylum_pair'] == pair]
        
        fig.add_trace(go.Scattergl(
            x=pair_data['x'],
            y=pair_data['y'],
            mode='markers',
            name=pair,
            marker=dict(
                color=color_mapping[pair],
                size=3,
                opacity=0.6
            ),
            hovertemplate=f'<b>{pair}</b><br>' +
                         f'{dm1_name}: %{{x:.4f}}<br>' +
                         f'{dm2_name}: %{{y:.4f}}<br>' +
                         'Accession 1: %{customdata[0]}<br>' +
                         'Accession 2: %{customdata[1]}<extra></extra>',
            customdata=list(zip(pair_data['acc_i'], pair_data['acc_j'])),
            visible=True
        ))
    
    # Add diagonal line
    fig.add_trace(go.Scatter(
        x=[min_val, max_val],
        y=[min_val, max_val],
        mode='lines',
        name='Diagonal',
        line=dict(color='black', width=2, dash='dash'),
        hoverinfo='skip',
        showlegend=False
    ))
    
    # Update layout
    fig.update_layout(
        title=f'Interactive Distance Matrix Comparison: {dm1_name} vs {dm2_name}',
        xaxis_title=f'{dm1_name} Distance',
        yaxis_title=f'{dm2_name} Distance',
        width=1000,
        height=800,
        hovermode='closest',
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.01,
            itemsizing='constant'
        ),
        margin=dict(r=200)  # Make room for legend
    )
    
    # Add range slider and buttons for better interactivity
    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                buttons=list([
                    dict(
                        args=[{"visible": [True] * len(fig.data)}],
                        label="Show All",
                        method="restyle"
                    ),
                    dict(
                        args=[{"visible": [False] * (len(fig.data) - 1) + [True]}],
                        label="Hide All",
                        method="restyle"
                    )
                ]),
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.01,
                xanchor="left",
                y=1.02,
                yanchor="top"
            ),
        ]
    )
    
    # Create output directory
    os.makedirs('figures', exist_ok=True)
    
    # Save as HTML
    html_filename = 'figures/dm_comparison_interactive.html'
    fig.write_html(html_filename)
    print(f'Interactive plot saved as {html_filename}')
    
    # Create a second plot with density view
    fig_density = go.Figure()
    
    # Create 2D histogram for density plot
    fig_density.add_trace(go.Histogram2d(
        x=df['x'],
        y=df['y'],
        colorscale='Hot',
        name='Density',
        hovertemplate='X: %{x:.4f}<br>Y: %{y:.4f}<br>Count: %{z}<extra></extra>'
    ))
    
    # Add diagonal line to density plot
    fig_density.add_trace(go.Scatter(
        x=[min_val, max_val],
        y=[min_val, max_val],
        mode='lines',
        name='Diagonal',
        line=dict(color='white', width=3, dash='dash'),
        hoverinfo='skip'
    ))
    
    fig_density.update_layout(
        title=f'Density Plot: {dm1_name} vs {dm2_name}',
        xaxis_title=f'{dm1_name} Distance',
        yaxis_title=f'{dm2_name} Distance',
        width=800,
        height=800
    )
    
    # Save density plot as HTML
    density_html_filename = 'figures/dm_comparison_density_interactive.html'
    fig_density.write_html(density_html_filename)
    print(f'Interactive density plot saved as {density_html_filename}')
    
    # Create combined dashboard with subplots
    fig_combined = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Phylum Pairs', 'Density'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Add phylum pair traces to first subplot
    for i, pair in enumerate(unique_pairs):
        pair_data = df[df['phylum_pair'] == pair]
        
        fig_combined.add_trace(
            go.Scattergl(
                x=pair_data['x'],
                y=pair_data['y'],
                mode='markers',
                name=pair,
                marker=dict(
                    color=color_mapping[pair],
                    size=2,
                    opacity=0.6
                ),
                hovertemplate=f'<b>{pair}</b><br>' +
                             f'{dm1_name}: %{{x:.4f}}<br>' +
                             f'{dm2_name}: %{{y:.4f}}<extra></extra>',
                visible=True,
                legendgroup=pair
            ),
            row=1, col=1
        )
    
    # Add density plot to second subplot
    fig_combined.add_trace(
        go.Histogram2d(
            x=df['x'],
            y=df['y'],
            colorscale='Hot',
            name='Density',
            showlegend=False,
            hovertemplate='X: %{x:.4f}<br>Y: %{y:.4f}<br>Count: %{z}<extra></extra>'
        ),
        row=1, col=2
    )
    
    # Add diagonal lines to both subplots
    for col in [1, 2]:
        fig_combined.add_trace(
            go.Scatter(
                x=[min_val, max_val],
                y=[min_val, max_val],
                mode='lines',
                name='Diagonal' if col == 1 else None,
                line=dict(color='black' if col == 1 else 'white', width=2, dash='dash'),
                hoverinfo='skip',
                showlegend=False if col == 2 else False
            ),
            row=1, col=col
        )
    
    fig_combined.update_layout(
        title=f'Interactive Dashboard: {dm1_name} vs {dm2_name}',
        width=1400,
        height=700,
        hovermode='closest'
    )
    
    fig_combined.update_xaxes(title_text=f'{dm1_name} Distance', row=1, col=1)
    fig_combined.update_yaxes(title_text=f'{dm2_name} Distance', row=1, col=1)
    fig_combined.update_xaxes(title_text=f'{dm1_name} Distance', row=1, col=2)
    fig_combined.update_yaxes(title_text=f'{dm2_name} Distance', row=1, col=2)
    
    # Save combined dashboard
    combined_html_filename = 'figures/dm_comparison_dashboard.html'
    fig_combined.write_html(combined_html_filename)
    print(f'Interactive dashboard saved as {combined_html_filename}')
    
    return fig, fig_density, fig_combined

if __name__ == '__main__':
    # Load data
    dm1_path = '/zhome/85/8/203063/a3_fungi/full_dist_mats/enzyme_phyl_correct_6.csv'
    dm1_name = 'AAA Enzyme Phylogenetic'

    dm2_path = '/zhome/85/8/203063/a3_fungi/full_dist_mats/phyl_busco_4_correct.csv'
    dm2_name = 'BUSCO Phylogenetic'
    
    dm1 = pd.read_csv(dm1_path, sep=r'\s+', header=None, skiprows=1)
    dm2 = pd.read_csv(dm2_path, sep=r'\s+', header=None, skiprows=1)

    print(f"DM1 shape: {dm1.shape}")
    print(f"DM2 shape: {dm2.shape}")

    # Create interactive plots
    fig_main, fig_density, fig_dashboard = plot_dms_interactive(dm1, dm2, dm1_name, dm2_name)
    
    print('Interactive plots created successfully!')
    print('Files created:')
    print('- figures/dm_comparison_interactive.html (main plot with toggleable phylum pairs)')
    print('- figures/dm_comparison_density_interactive.html (density plot)')
    print('- figures/dm_comparison_dashboard.html (combined dashboard)')
