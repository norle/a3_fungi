import os
import glob
import base64

def generate_html(image_dir):
    """Generates an HTML file to display plots with scrolling and a menu."""

    image_files = sorted([f for f in glob.glob(os.path.join(image_dir, "*.png")) if os.path.isfile(f)])
    if not image_files:
        return "<p>No images found in the specified directory.</p>"

    image_names = [os.path.basename(f) for f in image_files]
    image_data_uris = []
    for f in image_files:
        with open(f, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
            image_data_uris.append(f"data:image/png;base64,{encoded_string}")

    # Shorten image names for the menu
    short_image_names = [name.replace("pair_", "").replace(".png", "").replace("_", "-") for name in image_names]

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Pair Comparison Plots</title>
        <style>
            body {{
                font-family: sans-serif;
                display: flex;
                flex-direction: column;
                align-items: center;
                margin: 0;
                padding: 20px;
            }}
            #container {{
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 20px;  /* Space between elements */
                width: 100%;
                max-width: 1400px;
                margin: 0 auto;
            }}
            #scroll-instruction {{
                display: flex;
                flex-direction: column;
                align-items: center;
                color: #666;
                min-width: 50px;
            }}
            #image-container {{
                width: 800px;
            }}
            #plot-image {{
                width: 100%;
                border: 1px solid #ccc;
            }}
            #menu {{
                width: 300px;
                max-height: 80vh;
                overflow-y: auto;
                border: 1px solid #ddd;
                padding: 10px;
                box-sizing: border-box;
            }}
            .menu-item {{
                padding: 5px 10px;
                margin: 5px 0;
                border: 1px solid #ddd;
                cursor: pointer;
                background-color: #f9f9f9;
                white-space: nowrap; /* Prevent text wrapping */
                overflow: hidden;
                text-overflow: ellipsis; /* Show ... for overflow text */
                box-sizing: border-box;
            }}
            .menu-item:hover {{
                background-color: #eee;
            }}
            .menu-item.active {{
                background-color: #ccffcc; /* Highlighted color */
            }}
        </style>
    </head>
    <body>
        <h1>Pair Comparison Plots</h1>
        <div id="container">
            <div id="scroll-instruction">
                <div id="scroll-arrow">⬆️<br>⬇️</div>
                <small>Scroll<br>to browse</small>
            </div>
            <div id="image-container">
                <img id="plot-image" src="{image_data_uris[0]}" alt="{image_names[0]}">
            </div>
            <div id="menu">
                {''.join(f'<div class="menu-item" data-image-uri="{image_data_uris[i]}" onclick="window.displayImage(\'{image_data_uris[i]}\')">{short_image_names[i]}</div>' for i in range(len(image_names)))}
            </div>
        </div>

        <script>
            let images = {str(image_data_uris).replace("'", '"')};
            let currentImageIndex = 0;
            let imgElement = document.getElementById('plot-image');
            let menuItems = document.querySelectorAll('.menu-item');

            window.displayImage = function(imageDataUri) {{
                imgElement.src = imageDataUri;
                currentImageIndex = images.indexOf(imageDataUri);
                updateActiveMenuItem(imageDataUri);
            }};

            function updateActiveMenuItem(imageDataUri) {{
                menuItems.forEach(item => item.classList.remove('active'));
                menuItems.forEach(item => {{
                    if (item.dataset.imageUri === imageDataUri) {{
                        item.classList.add('active');
                    }}
                }});
            }}

            window.addEventListener('wheel', function(e) {{
                if (e.deltaY > 0) {{
                    currentImageIndex = (currentImageIndex + 1) % images.length;
                }} else {{
                    currentImageIndex = (currentImageIndex - 1 + images.length) % images.length;
                }}
                imgElement.src = images[currentImageIndex];
                updateActiveMenuItem(images[currentImageIndex]);
            }});

            // Initialize active menu item on page load
            updateActiveMenuItem(images[0]);
        </script>
    </body>
    </html>
    """

    return html_content

if __name__ == "__main__":
    image_directory = "/zhome/85/8/203063/a3_fungi/figures/phylum_pair_plots_datashader/"  # Replace with your directory
    output_html_file = "/zhome/85/8/203063/a3_fungi/html/plot_viewer.html"  # Replace with your desired output path

    html = generate_html(image_directory)

    with open(output_html_file, "w") as f:
        f.write(html)

    print(f"HTML file generated at: {output_html_file}")
