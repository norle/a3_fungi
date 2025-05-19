import os
import json

def main():
    # Define base output directory
    base_output_dir = '/zhome/85/8/203063/a3_fungi/html_molstar' # Changed output directory slightly
    os.makedirs(base_output_dir, exist_ok=True)

    # Define the desired order of genes
    gene_order = ["LYS20", "ACO2", "LYS4", "LYS12", "ARO8", "LYS2", "LYS9", "LYS1"]
    
    # Use the same source paths as the Mol* script (and 3Dmol script)
    pdb_source_base_path = "/zhome/85/8/203063/a3_fungi/html/to_html/"
    # Assuming conservation JSON for Mol* is the same as for 3Dmol, or adjust path if different
    # For Mol*, the JSON format should be: { "residue_number": score, ... }
    conservation_json_source_base_path = "/zhome/85/8/203063/a3_fungi/html_molstar_only/conservation_data/" # Same as 3dmol script

    genes_with_pdb = []
    genes_with_conservation = []
    
    pdb_data_strings = {}
    conservation_data_strings = {}

    # Process PDB files and conservation files
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

        # Using the same _conservation_3dmol.json files, assuming format is compatible
        # or can be adapted in JS. Format: {"1": 0.5, "2": 0.8, ...} (residue number as string key)
        conservation_json_file_name = f"{gene_name}_conservation_3dmol.json"
        conservation_json_source_path = os.path.join(conservation_json_source_base_path, conservation_json_file_name)

        if os.path.exists(conservation_json_source_path):
            try:
                with open(conservation_json_source_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if content and content.strip():
                    # Validate JSON content slightly
                    try:
                        json.loads(content)
                        conservation_data_strings[gene_name] = content
                        genes_with_conservation.append(gene_name)
                        print(f"DEBUG: Read conservation JSON for {gene_name}")
                    except json.JSONDecodeError as je:
                        print(f"Error decoding conservation JSON {conservation_json_source_path}: {str(je)}")
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
        viewer_div_id = f"molstar_viewer_{gene_name}" # Changed ID prefix
        structure_html = f"<div id='{viewer_div_id}' style='width:800px;height:600px;position:relative;'></div>"
        if gene_name not in genes_with_pdb:
            structure_html = f"<div id='{viewer_div_id}' style='width:800px;height:600px;position:relative;'><p>PDB structure not available for {gene_name}</p></div>"

        tab_content_html += f"""
<div id="{gene_name}_content" class="tabcontent">
    <h3>3D Structure of {gene_name} (Mol*)</h3>
    {structure_html}
</div>
"""

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Mol* Structure Viewer</title>
    <!-- PDBe-Molstar plugin CSS/JS (AlphaFold-style) -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/pdbe-molstar@3.3.0/build/pdbe-molstar-light.css" />
    <script defer src="https://cdn.jsdelivr.net/npm/pdbe-molstar@3.3.0/build/pdbe-molstar-plugin.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .tab {{ overflow: hidden; border: 1px solid #ccc; background-color: #f1f1f1; }}
        .tab button {{ background-color: inherit; float: left; border: none; outline: none; cursor: pointer; padding: 14px 16px; transition: 0.3s; font-size: 17px; }}
        .tab button:hover {{ background-color: #ddd; }}
        .tab button.active {{ background-color: #ccc; }}
        .tabcontent {{ display: none; padding: 6px 12px; border: 1px solid #ccc; border-top: none; min-height: 650px; }}
        .tab::after {{ content: ""; clear: both; display: table; }}
        .molstar-viewer-instance {{ /* Styles for individual viewer divs if needed */ }}
    </style>
</head>
<body>
    <h2>Protein Structures (Mol* via PDBe-Molstar)</h2>
    <div class="tab">
        {tab_buttons_html}
    </div>

    <!-- Replace each tab content with the PDBe-Molstar web component -->
    {''.join(f'''
    <div id="{g}_content" class="tabcontent">
      <h3>3D Structure of {g} (Mol*)</h3>
      <pdbe-molstar-plugin
        id="viewer_{g}"
        class="molstar-viewer-instance"
        structure-data="{pdb_data_strings[g].replace('"', '&quot;')}"
        structure-format="pdb"
        theme="light"
        style="width:800px;height:600px;">
      </pdbe-molstar-plugin>
    </div>
    ''' for g in gene_order)}

    <!-- Add tab-switching logic -->
    <script>
      function openTab(evt, geneName) {{
        var i, tabcontent, tablinks;
        tabcontent = document.getElementsByClassName("tabcontent");
        for (i = 0; i < tabcontent.length; i++) tabcontent[i].style.display = "none";
        tablinks = document.getElementsByClassName("tablinks");
        for (i = 0; i < tablinks.length; i++) tablinks[i].className = tablinks[i].className.replace(" active", "");
        document.getElementById(geneName + "_content").style.display = "block";
        if (evt && evt.currentTarget) evt.currentTarget.className += " active";
      }}
      document.addEventListener('DOMContentLoaded', function() {{
        var btn = document.getElementById("defaultOpen");
        if (btn) btn.click();
      }});
    </script>
</body>
</html>"""

    output_html_path = os.path.join(base_output_dir, "molstar_viewer.html")
    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Mol* viewer HTML saved to {output_html_path}")
    print(f"PDB and conservation data are embedded directly in the HTML.")

if __name__ == "__main__":
    main()
