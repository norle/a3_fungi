import os
import glob
import json
from accession_map import accession_to_species

def main():
    # Define base output directory
    base_output_dir = '/zhome/85/8/203063/a3_fungi/html_3dmol'
    os.makedirs(base_output_dir, exist_ok=True)

    # Define the desired order of genes
    gene_order = ["Info", "LYS20", "ACO2", "LYS4", "LYS12", "ARO8", "LYS2", "LYS9", "LYS1"]
    
    # Update base paths for both organisms
    base_path = "/zhome/85/8/203063/a3_fungi/conservation_scores"
    organisms = {
        'S_cerevisiae': {'pdb_suffix': '.pdb'},
        'A_niger': {'pdb_suffix': '_a_niger.pdb'},
        'C_cinerea': {'pdb_suffix': '_c_cinerea.pdb'},
    }

    # Add full‐name map and accession holder
    full_name_map = {
        'S_cerevisiae': 'Saccharomyces cerevisiae',
        'A_niger': 'Aspergillus niger',
        'C_cinerea': 'Coprinopsis cinerea',
    }
    accession_data_strings = {org: {} for org in organisms}
    
    # Initialize data structures for both organisms
    genes_with_pdb = {org: [] for org in organisms}
    genes_with_conservation = {org: [] for org in organisms}
    pdb_data_strings = {org: {} for org in organisms}
    conservation_data_strings = {org: {} for org in organisms}

    # Process files for each organism
    for org in organisms:
        for gene_name in gene_order:
            # PDB files
            pdb_file_name = f"{gene_name.lower()}{organisms[org]['pdb_suffix']}"
            pdb_source_path = os.path.join(base_path, org, pdb_file_name)
            
            if os.path.exists(pdb_source_path):
                try:
                    with open(pdb_source_path, 'r', encoding='utf-8') as f:
                        pdb_data_strings[org][gene_name] = f.read()
                    genes_with_pdb[org].append(gene_name)
                    print(f"DEBUG: Read PDB data for {gene_name} ({org})")
                except Exception as e:
                    print(f"Error reading PDB file {pdb_source_path}: {str(e)}")

            # Conservation files: extract accession
            conservation_json_file_name = f"{gene_name}_conservation_3dmol.json"
            conservation_json_source_path = os.path.join(base_path, org, conservation_json_file_name)

            if os.path.exists(conservation_json_source_path):
                try:
                    with open(conservation_json_source_path, 'r', encoding='utf-8') as f:
                        raw = f.read().strip()
                    if raw:
                        data = json.loads(raw)
                        accession_data_strings[org][gene_name] = data.get('accession', 'N/A')
                        data.pop('accession', None)
                        conservation_data_strings[org][gene_name] = json.dumps(data)
                        genes_with_conservation[org].append(gene_name)
                        print(f"DEBUG: Read conservation JSON for {gene_name} ({org})")
                except Exception as e:
                    print(f"Error reading conservation JSON {conservation_json_source_path}: {str(e)}")

    # After all file reads, override accession per organism for every gene
    genome_accessions = {
        'S_cerevisiae': 'GCF_000146045.2',
        'A_niger':     'GCF_000002855.4',
        'C_cinerea':   'GCF_000182895.1',
    }
    for org, acc in genome_accessions.items():
        for gene_name in gene_order:
            accession_data_strings[org][gene_name] = acc

    # Create JSON strings for JavaScript
    data_for_js = {
        'pdbData': pdb_data_strings,
        'conservationData': conservation_data_strings,
        'genesWithPdb': genes_with_pdb,
        'genesWithConservation': genes_with_conservation,
        'orderedTabGeneNames': gene_order,
        'accessionData': accession_data_strings,
        'fullNameMap': full_name_map,
        'accessionToSpecies': accession_to_species
    }
    json_data = {key: json.dumps(value) for key, value in data_for_js.items()}

    # Build HTML for tab navigation
    tab_buttons_html = ""
    for i, gene_name in enumerate(gene_order):
        default_open_id = 'id="defaultOpen"' if i == 0 else ''
        tab_buttons_html += f'<button class="tablinks" onclick="openTab(event, \'{gene_name}\')" {default_open_id}>{gene_name}</button>\n'

    # Build responsive tab content HTML with placeholders for species & accession
    info_tab_content = f"""
<div id="Info_content" class="tabcontent">
    <div style="max-width: 800px; margin: auto; text-align: left;">
        <h3 style="text-align: left;">About this page</h3>
        <p>
            Representative structures are displayed for the AAA pathway enzymes with coloring based on conservation scores. For each of the AAA pathway enzymes, enzyme sequences were retrieved and aligned from 4634 fungal genomes. The conservation score for each of the representative sequences was calculated - conservation score is the frequency of that amino acid at the specific alignment position. Red shows that the amino acid is more conserved, blue shows less conserved, white shows medium conservation.
        </p>
    </div>
</div>
"""

    tab_content_html = info_tab_content
    for gene_name in gene_order[1:]:
        viewers_html = ""
        for org in organisms:
            viewer_div_id = f"viewer_{gene_name}_{org}"
            acc_span_id = f"accession_{gene_name}_{org}"
            species_span_id = f"species_{gene_name}_{org}"
            structure_html = (
                f"<div id='{viewer_div_id}' "
                "style='width:100%;height:400px;max-width:600px;position:relative;'></div>"
            )
            viewers_html += f"""
            <div style="flex:1 1 300px;margin:10px;">
                <h4><span id="{species_span_id}">{full_name_map[org]}</span></h4>
                <p>Accession: <span id="{acc_span_id}">–</span></p>
                {structure_html}
            </div>"""

        tab_content_html += f"""
<div id="{gene_name}_content" class="tabcontent">
    <h3>3D Structure of {gene_name}</h3>
    <div style="display:flex;flex-wrap:wrap;justify-content:center;">
        {viewers_html}
    </div>
</div>
"""

    # Update the JavaScript to handle both organisms
    js_viewer_init = """
        function initialize3DmolForGene(geneName) {
            if (geneName === "Info") return;
            if (initializedViewers.has(geneName)) return;
            
            const organisms = Object.keys(embeddedPDBData);
            
            organisms.forEach(org => {
                if (!embeddedPDBData[org][geneName]) {
                    console.log(`No PDB data for ${geneName} (${org})`);
                    return;
                }

                const viewerElementId = `viewer_${geneName}_${org}`;
                const element = document.getElementById(viewerElementId);
                
                if (element) {
                    if (element.textContent.includes("PDB structure not available")) {
                        element.innerHTML = '';
                    }

                    let viewer = $3Dmol.createViewer(element, {
                        backgroundColor: "white"
                    });

                    viewer.addStyle({
                        line: {},
                        stick: {},
                        sphere: {},
                        cartoon: {}
                    });

                    viewer.addModel(embeddedPDBData[org][geneName], "pdb");
                    viewer.setStyle({}, {cartoon: {}});
                    
                    if (embeddedConservationData[org][geneName]) {
                        try {
                            const conservationData = JSON.parse(embeddedConservationData[org][geneName]);
                            
                            for (const [resNum, score] of Object.entries(conservationData)) {
                                const color = getColorForScore(parseFloat(score));
                                viewer.setStyle({resi: parseInt(resNum)}, {
                                    cartoon: {color: color}
                                });
                            }
                        } catch (e) {
                            console.error(`Error applying conservation data for ${geneName} (${org}):`, e);
                        }
                    }

                    viewer.addResLabels({
                        sele: {},
                        showBackground: true,
                        backgroundOpacity: 0.8,
                        alignment: "center"
                    });

                    viewer.setHoverable({}, true,
                        function(atom, viewer, event, container) {
                            if (!atom.resn || !atom.resi) return;
                            const label = `${atom.resn}${atom.resi}`;
                            viewer.addLabel(label, {
                                position: atom,
                                backgroundColor: "black",
                                fontColor: "white",
                                fontSize: 12,
                                showBackground: true
                            });
                        },
                        function(atom, viewer) {
                            viewer.removeAllLabels();
                        }
                    );

                    viewer.zoomTo();
                    viewer.render();

                    // Set accession text if available
                    const acc = embeddedAccessionData[org][geneName];
                    if (acc) {
                        const span = document.getElementById(`accession_${geneName}_${org}`);
                        if (span) span.innerText = acc;
                        // override species name if mapping exists
                        const speciesSpan = document.getElementById(`species_${geneName}_${org}`);
                        if (embeddedAccessionToSpecies[acc] && speciesSpan) {
                            speciesSpan.innerText = embeddedAccessionToSpecies[acc];
                        }
                    }
                }
            });
            
            initializedViewers.add(geneName);
        }
    """

    # Update the HTML content with the new JavaScript
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
    <h2>Protein Structure Comparison (3Dmol.js)</h2>
    <div class="tab">
        {tab_buttons_html}
    </div>

    {tab_content_html}

    <script type="text/javascript">
        const embeddedPDBData = {json_data['pdbData']};
        const embeddedConservationData = {json_data['conservationData']};
        const embeddedAccessionData = {json_data['accessionData']};
        const embeddedAccessionToSpecies = {json_data['accessionToSpecies']};
        const fullNameMap = {json_data['fullNameMap']};
        const genesWithPDB = {json_data['genesWithPdb']};
        const genesWithConservation = {json_data['genesWithConservation']};
        const orderedTabGeneNames = {json_data['orderedTabGeneNames']};
        let initializedViewers = new Set();
        
        {js_viewer_init}
        
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
