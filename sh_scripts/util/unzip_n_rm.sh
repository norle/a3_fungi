#!/bin/bash

# Check if the directory argument is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <directory>"
    exit 1
fi

# Change to the specified directory
cd "$1" || exit

# Loop through all zip files in the specified directory
for zip_file in *.zip; do
    # Check if there are any zip files
    if [ -e "$zip_file" ]; then
        echo "Unzipping: $zip_file"
        # Unzip the file without overwriting existing files
        unzip -n "$zip_file"
        # Remove the zip file
        rm "$zip_file"
    fi
done