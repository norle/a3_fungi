import os
import glob
import json

def main():
    # Define base output directory
    base_output_dir = '/zhome/85/8/203063/a3_fungi/html_molstar_only'
    os.makedirs(base_output_dir, exist_ok=True)

    # Define the desired order of genes
    gene_order = ["LYS20", "ACO2", "LYS4", "LYS12", "ARO8", "LYS2", "LYS9", "LYS1"]
    
    # Source directory for PDB files
    pdb_source_base_path = "/zhome/85/8/203063/a3_fungi/html/to_html/"
    # Source directory for conservation JSON files
    conservation_json_source_base_path = "/zhome/85/8/203063/a3_fungi/html_molstar_only/conservation_data/"

    genes_with_pdb = []
    genes_with_conservation = []
    
    pdb_data_strings = {}
    conservation_data_strings = {}

    # Process PDB files and conservation files
    for gene_name in gene_order:
        # PDB processing
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
        else:
            print(f"PDB file for {gene_name} not found at {pdb_source_path}. It will not be included.")

        # Conservation JSON processing
        conservation_json_file_name = f"{gene_name}_conservation_3dmol.json"
        conservation_json_source_path = os.path.join(conservation_json_source_base_path, conservation_json_file_name)

        if os.path.exists(conservation_json_source_path):
            try:
                with open(conservation_json_source_path, 'r', encoding='utf-8') as f:
                    content = f.read() # Read the content first
                # Ensure content is not None, not empty, and not just whitespace
                if content and content.strip(): 
                    conservation_data_strings[gene_name] = content
                    genes_with_conservation.append(gene_name)
                    print(f"DEBUG: Read and stored non-empty conservation JSON for {gene_name}")
                else:
                    print(f"DEBUG: Conservation JSON for {gene_name} at {conservation_json_source_path} is empty or whitespace only. Skipping.")
            except Exception as e:
                print(f"Error reading conservation JSON {conservation_json_source_path}: {str(e)}")
        else:
            print(f"Conservation JSON for {gene_name} not found at {conservation_json_source_path}. Coloring will not be applied.")

    # Create JSON strings for JavaScript
    pdb_data_json = json.dumps(pdb_data_strings)
    conservation_data_json = json.dumps(conservation_data_strings)
    # genes_with_pdb_json is still useful for quick checks if PDB data was successfully read and embedded
    genes_with_pdb_json = json.dumps(genes_with_pdb)
    # genes_with_conservation_json for quick checks if conservation data was successfully read and embedded
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
        # The Mol* div will be created for all genes in gene_order.
        # JS will check `allGenesWithPDB` before initializing.
        molstar_div_id = f"molstar_{gene_name}"
        # Increased viewer size
        structure_html = f"<div id='{molstar_div_id}' style='width:800px;height:600px;position:relative;margin-top:10px;'></div>"
        if gene_name not in genes_with_pdb: # Check if PDB data was actually loaded
             structure_html = f"<div id='{molstar_div_id}' style='width:800px;height:600px;position:relative;margin-top:10px;'><p>PDB structure not available for {gene_name}</p></div>"

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
  <title>Mol* Structure Viewer</title>
  <link rel="stylesheet" type="text/css" href="https://unpkg.com/molstar@3.0.0/build/viewer/molstar.css" />
  <script type="text/javascript" src="https://unpkg.com/molstar@3.0.0/build/viewer/molstar.js"></script>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 20px; }}
    .tab {{ overflow: hidden; border: 1px solid #ccc; background-color: #f1f1f1; }}
    .tab button {{ background-color: inherit; float: left; border: none; outline: none; cursor: pointer; padding: 14px 16px; transition: 0.3s; font-size: 17px; }}
    .tab button:hover {{ background-color: #ddd; }}
    .tab button.active {{ background-color: #ccc; }}
    .tabcontent {{ display: none; padding: 6px 12px; border: 1px solid #ccc; border-top: none; min-height: 650px; /* Ensure space for larger viewer */ }}
    .tab::after {{ content: ""; clear: both; display: table; }}
  </style>
</head>
<body>
  <h2>Protein Structures (Mol*)</h2>
  <div class="tab">
    {tab_buttons_html}
  </div>

  {tab_content_html}

  <script type="text/javascript">
    const allGenesWithPDB = {genes_with_pdb_json}; // List of genes for which PDB data is available
    const allGenesWithConservation = {genes_with_conservation_json}; // List of genes for which conservation data is available
    const embeddedPDBData = {pdb_data_json};
    const embeddedConservationData = {conservation_data_json};
    // orderedTabGeneNames includes all genes for tab creation purposes
    const orderedTabGeneNames = {ordered_tab_gene_names_json};
    let initializedMolStarViewers = new Set();

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
      initializeMolStarForGene(geneName);
    }}

    async function initializeMolStarForGene(geneName) {{
      if (initializedMolStarViewers.has(geneName)) {{
        // console.log(`Mol* already handled for ${{geneName}}.`);
        return;
      }}

      // Check if PDB data was successfully embedded for this gene
      if (!allGenesWithPDB.includes(geneName) || !embeddedPDBData[geneName]) {{
        console.log(`No PDB data embedded for ${{geneName}}, skipping Mol* initialization.`);
        initializedMolStarViewers.add(geneName); // Mark as handled (no PDB)
        return;
      }}

      const pdbDataString = embeddedPDBData[geneName];
      const viewerElementId = 'molstar_' + geneName;
      const viewerElement = document.getElementById(viewerElementId);

      if (viewerElement) {{
        // Clear "PDB not available" message if it was there
        if (viewerElement.textContent.includes("PDB structure not available")){{
            viewerElement.innerHTML = '';
        }}
        try {{
          console.log(`Initializing Mol* for ${{geneName}} in #${{viewerElementId}} with embedded PDB`);
          if (typeof molstar !== 'undefined' && molstar.Viewer && typeof molstar.Viewer.create === 'function') {{
            const plugin = await molstar.Viewer.create(viewerElement, {{
              layoutIsExpanded: false, // Keep right-hand panel initially collapsed
              layoutShowControls: false, // Hide the bottom controls strip (buttons like "Controls", "Settings")
              layoutShowRemoteState: false, // Hide remote state UI
              viewportShowExpand: true, // Still allow viewport expansion
              viewportShowSelectionMode: false,
              viewportShowAnimation: false,
              // layoutShowLog: false, // Optionally hide log panel by default
              // layoutShowSequence: false, // Optionally hide sequence panel by default
            }});
            // Load structure from embedded string data
            await plugin.loadStructureFromData(pdbDataString, 'pdb');
            initializedMolStarViewers.add(geneName);
            console.log(`Successfully loaded PDB data for ${{geneName}} into #${{viewerElementId}} from embedded string`);

            // Apply conservation coloring if data is available
            if (allGenesWithConservation.includes(geneName) && embeddedConservationData[geneName]) {{
              const conservationJSONString = embeddedConservationData[geneName];
              try {{
                const conservationData = JSON.parse(conservationJSONString);
                const conservationDataMap = new Map();
                for (const resNumStr in conservationData) {{
                  conservationDataMap.set(parseInt(resNumStr), parseFloat(conservationData[resNumStr]));
                }}

                if (conservationDataMap.size > 0) {{
                  console.log(`Applying conservation coloring for ${{geneName}}`);

                  // Wait for structure to be loaded and representation to be ready
                  await new Promise((resolve) => setTimeout(resolve, 100));

                  // Mol* v3: get the structure component
                  const structureEntry = plugin.structureHierarchy.current.structures[0];
                  if (!structureEntry) {{
                    console.error("No structure entry found for coloring.");
                    return;
                  }}
                  // Get all components (usually just one)
                  const components = structureEntry.components;
                  for (const c of components) {{
                    // Update the representations with a custom coloring function
                    // Mol* v3: use updateRepresentationsTheme if available, otherwise fallback
                    if (plugin.managers.structure && plugin.managers.structure.component && plugin.managers.structure.component.updateRepresentationsTheme) {{
                      plugin.managers.structure.component.updateRepresentationsTheme(c, {{
                        color: 'uniform',
                        colorParams: {{
                          value: (location) => {{
                            if (location.kind === 'element-locus' && location.element.unit.model.atomicHierarchy.residues.label_seq_id) {{
                              const seqId = location.element.unit.model.atomicHierarchy.residues.label_seq_id.value(location.element.residueIndex);
                              const score = conservationDataMap.get(seqId);
                              // Use a blue-red gradient: blue (low), white (mid), red (high)
                              if (score !== undefined) {{
                                // Interpolate color: blue (0), white (0.5), red (1)
                                if (score < 0.5) {{
                                  // Blue to white
                                  const t = score / 0.5;
                                  return molstar.Color.fromRgb(Math.round(255 * t), Math.round(255 * t), 255);
                                }} else {{
                                  // White to red
                                  const t = (score - 0.5) / 0.5;
                                  return molstar.Color.fromRgb(255, Math.round(255 * (1 - t)), Math.round(255 * (1 - t)));
                                }}
                              }}
                              return molstar.Color.ColorNames.lightgrey;
                            }}
                            return molstar.Color.ColorNames.lightgrey;
                          }}
                        }}
                      }});
                    }} else if (plugin.representation && plugin.representation.structure && plugin.representation.structure.themes) {{
                      // Fallback for v3: update color theme using the new API
                      plugin.representation.structure.themes.color.set({{
                        name: 'custom',
                        params: {{
                          color: (location) => {{
                            if (location.kind === 'element-locus' && location.element.unit.model.atomicHierarchy.residues.label_seq_id) {{
                              const seqId = location.element.unit.model.atomicHierarchy.residues.label_seq_id.value(location.element.residueIndex);
                              const score = conservationDataMap.get(seqId);
                              if (score !== undefined) {{
                                if (score < 0.5) {{
                                  const t = score / 0.5;
                                  return molstar.Color.fromRgb(Math.round(255 * t), Math.round(255 * t), 255);
                                }} else {{
                                  const t = (score - 0.5) / 0.5;
                                  return molstar.Color.fromRgb(255, Math.round(255 * (1 - t)), Math.round(255 * (1 - t)));
                                }}
                              }}
                              return molstar.Color.ColorNames.lightgrey;
                            }}
                            return molstar.Color.ColorNames.lightgrey;
                          }}
                        }}
                      }});
                    }} else {{
                      console.warn("Could not apply conservation coloring: Mol* API changed.");
                    }}
                  }}
                  console.log(`Applied conservation coloring directly to ${{geneName}}`);
                }} else {{
                  console.log(`No conservation data found in map for ${{geneName}} after parsing embedded JSON.`);
                }}
              }} catch (e) {{
                console.error(`Error parsing or applying conservation data for ${{geneName}}:`, e);
              }}
            }} else {{
              console.log(`No embedded conservation data for ${{geneName}}, skipping coloring.`);
            }}

          }} else {{
            console.error('Mol* Viewer API (molstar.Viewer.create) not found.');
            viewerElement.innerHTML = '<p>Mol* library not loaded.</p>';
          }}
        }} catch (e) {{
          console.error(`Error initializing Mol* or loading PDB for ${{geneName}}:`, e);
          viewerElement.innerHTML = `<p>Error loading PDB: ${{geneName}}. ${{e.message || e}}</p>`;
        }}
      }} else {{
        console.warn(`Mol* viewer element #${{viewerElementId}} not found for ${{geneName}}.`);
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

    output_html_path = os.path.join(base_output_dir, "molstar_only_viewer.html")
    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Mol* only viewer HTML saved to {output_html_path}")
    print(f"PDB and conservation data are embedded directly in the HTML.")

if __name__ == "__main__":
    main()
