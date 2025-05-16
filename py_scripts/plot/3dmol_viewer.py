import os
import glob
import json

def main():
    # Define base output directory
    base_output_dir = '/zhome/85/8/203063/a3_fungi/html_3dmol'
    os.makedirs(base_output_dir, exist_ok=True)

    # Define the desired order of genes
    gene_order = ["LYS20", "ACO2", "LYS4", "LYS12", "ARO8", "LYS2", "LYS9", "LYS1"]
    
    # Use the same source paths as the Mol* script
    pdb_source_base_path = "/zhome/85/8/203063/a3_fungi/html/to_html/"
    conservation_json_source_base_path = "/zhome/85/8/203063/a3_fungi/html_molstar_only/conservation_data/"

    genes_with_pdb = []
    genes_with_conservation = []
    
    pdb_data_strings = {}
    conservation_data_strings = {}

    # Process PDB files and conservation files using the same logic as before
    for gene_name in gene_order:
        pdb_file_name = f"{gene_name.lower()}.pdb"
        pdb_source_path = os.path.join(pdb_source_base_path, pdb_file_name)
        
        if os.path.exists(pdb_source_path):
            try:
                with open(pdb_source_path, 'r', encoding='utf-8') as f:
                    pdb_data_strings[gene_name] = f.read()
                genes_with_pdb.append(gene_name)
                print(f"DEBUG: Read PDB data for {gene_name}")
            except Exception as e:
                print(f"Error reading PDB file {pdb_source_path}: {str(e)}")

        conservation_json_file_name = f"{gene_name}_conservation_3dmol.json"
        conservation_json_source_path = os.path.join(conservation_json_source_base_path, conservation_json_file_name)

        if os.path.exists(conservation_json_source_path):
            try:
                with open(conservation_json_source_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if content and content.strip():
                    conservation_data_strings[gene_name] = content
                    genes_with_conservation.append(gene_name)
                    print(f"DEBUG: Read conservation JSON for {gene_name}")
            except Exception as e:
                print(f"Error reading conservation JSON {conservation_json_source_path}: {str(e)}")

    # Create JSON strings for JavaScript
    pdb_data_json = json.dumps(pdb_data_strings)
    conservation_data_json = json.dumps(conservation_data_strings)
    genes_with_pdb_json = json.dumps(genes_with_pdb)
    genes_with_conservation_json = json.dumps(genes_with_conservation)
    ordered_tab_gene_names_json = json.dumps(gene_order)

    # Build HTML for tab navigation
    tab_buttons_html = ""
    for i, gene_name in enumerate(gene_order):
        default_open_id = 'id="defaultOpen"' if i == 0 else ''
        tab_buttons_html += f'<button class="tablinks" onclick="openTab(event, \'{gene_name}\')" {default_open_id}>{gene_name}</button>\n'

    # Build HTML for tab content
    tab_content_html = ""
    for gene_name in gene_order:
        viewer_div_id = f"viewer_{gene_name}"
        structure_html = f"<div id='{viewer_div_id}' style='width:800px;height:600px;position:relative;'></div>"
        if gene_name not in genes_with_pdb:
            structure_html = f"<div id='{viewer_div_id}' style='width:800px;height:600px;position:relative;'><p>PDB structure not available for {gene_name}</p></div>"

        tab_content_html += f"""
<div id="{gene_name}_content" class="tabcontent">
    <h3>3D Structure of {gene_name}</h3>
    {structure_html}
</div>
"""

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>3Dmol.js Structure Viewer</title>
    <script src="https://3Dmol.org/build/3Dmol-min.js"></script>
    <script src="https://3Dmol.org/build/3Dmol.ui-min.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .tab {{ overflow: hidden; border: 1px solid #ccc; background-color: #f1f1f1; }}
        .tab button {{ background-color: inherit; float: left; border: none; outline: none; cursor: pointer; padding: 14px 16px; transition: 0.3s; font-size: 17px; }}
        .tab button:hover {{ background-color: #ddd; }}
        .tab button.active {{ background-color: #ccc; }}
        .tabcontent {{ display: none; padding: 6px 12px; border: 1px solid #ccc; border-top: none; min-height: 650px; }}
        .tab::after {{ content: ""; clear: both; display: table; }}
    </style>
</head>
<body>
    <h2>Protein Structures (3Dmol.js)</h2>
    <div class="tab">
        {tab_buttons_html}
    </div>

    {tab_content_html}

    <script type="text/javascript">
        const allGenesWithPDB = {genes_with_pdb_json};
        const allGenesWithConservation = {genes_with_conservation_json};
        const embeddedPDBData = {pdb_data_json};
        const embeddedConservationData = {conservation_data_json};
        const orderedTabGeneNames = {ordered_tab_gene_names_json};
        let initializedViewers = new Set();
        
        function openTab(evt, geneName) {{
            var i, tabcontent, tablinks;
            tabcontent = document.getElementsByClassName("tabcontent");
            for (i = 0; i < tabcontent.length; i++) {{
                tabcontent[i].style.display = "none";
            }}
            tablinks = document.getElementsByClassName("tablinks");
            for (i = 0; i < tablinks.length; i++) {{
                tablinks[i].className = tablinks[i].className.replace(" active", "");
            }}
            document.getElementById(geneName + "_content").style.display = "block";
            if (evt && evt.currentTarget) {{
                evt.currentTarget.className += " active";
            }} else {{
                for (i = 0; i < tablinks.length; i++) {{
                    if (tablinks[i].textContent === geneName) {{
                        tablinks[i].className += " active";
                        break;
                    }}
                }}
            }}
            initialize3DmolForGene(geneName);
        }}

        function initialize3DmolForGene(geneName) {{
            if (initializedViewers.has(geneName)) return;
            
            if (!allGenesWithPDB.includes(geneName) || !embeddedPDBData[geneName]) {{
                console.log(`No PDB data for ${{geneName}}`);
                initializedViewers.add(geneName);
                return;
            }}

            const viewerElementId = `viewer_${{geneName}}`;
            const element = document.getElementById(viewerElementId);
            
            if (element) {{
                if (element.textContent.includes("PDB structure not available")) {{
                    element.innerHTML = '';
                }}

                let viewer = $3Dmol.createViewer(element, {{
                    backgroundColor: "white",
                    antialias: true,
                    shadow: true,
                    shadowIntensity: 0.5  // Reduced shadow intensity
                }});

                const pdbData = embeddedPDBData[geneName];
                viewer.addModel(pdbData, "pdb");
                
                // Set improved cartoon representation
                viewer.setStyle({{}}, {{
                    cartoon: {{
                        style: "smooth",
                        thickness: 0.3,  // Thinner tubes
                        arrows: true,    // Show beta sheets as arrows
                        opacity: 0.95    // Slight transparency
                    }}
                }});
                
                // Set better lighting
                viewer.setLightingPreset("default");
                viewer.setSlab(0, 0);
                
                // Apply conservation coloring if available
                if (allGenesWithConservation.includes(geneName) && embeddedConservationData[geneName]) {{
                    try {{
                        const conservationData = JSON.parse(embeddedConservationData[geneName]);
                        
                        for (const [resNum, score] of Object.entries(conservationData)) {{
                            const color = getColorForScore(parseFloat(score));
                            viewer.setStyle({{resi: parseInt(resNum)}}, {{
                                cartoon: {{color: color}}
                            }});
                        }}
                    }} catch (e) {{
                        console.error(`Error applying conservation data for ${{geneName}}:`, e);
                    }}
                }}

                // Add hover event handling
                viewer.setHoverable({{}}, true, function(atom, viewer, event, container) {{
                    if (!atom.resn || !atom.resi) return;
                    const label = `${{atom.resn}}${{atom.resi}}`;
                    viewer.addLabel(label, {{
                        position: atom,
                        backgroundColor: "black",
                        fontColor: "white",
                        fontSize: 12,
                        showBackground: true
                    }});
                }}, function(atom, viewer) {{
                    // Clear all labels when not hovering
                    viewer.removeAllLabels();
                }});

                viewer.zoomTo();
                viewer.render();
                initializedViewers.add(geneName);
            }}
        }}

        function getColorForScore(score) {{
            if (score < 0.5) {{
                // Blue (0) to white (0.5)
                const t = score / 0.5;
                return `rgb(${{Math.round(255 * t)}}, ${{Math.round(255 * t)}}, 255)`;
            }} else {{
                // White (0.5) to red (1.0)
                const t = (score - 0.5) / 0.5;
                return `rgb(255, ${{Math.round(255 * (1 - t))}}, ${{Math.round(255 * (1 - t))}})`;
            }}
        }}

        document.addEventListener('DOMContentLoaded', function() {{
            const defaultOpenButton = document.getElementById("defaultOpen");
            if (defaultOpenButton) {{
                defaultOpenButton.click();
            }} else if (orderedTabGeneNames.length > 0) {{
                openTab(null, orderedTabGeneNames[0]);
            }}
        }});
    </script>
</body>
</html>"""

    output_html_path = os.path.join(base_output_dir, "3dmol_viewer.html")
    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"3Dmol.js viewer HTML saved to {output_html_path}")
    print(f"PDB and conservation data are embedded directly in the HTML.")

if __name__ == "__main__":
    main()
