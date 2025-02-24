#!/bin/bash

# wasn't necessary in the end, so unused

# Path to the file containing the necessary directory names
necessary_dirs_file="/zhome/85/8/203063/a3_fungi/data_out/busco_results_cleaned.csv"

# Path to the folder containing the directories to check
target_folder="/work3/s233201/fungi_proteins"

# Read the necessary directory names into an array
mapfile -t necessary_dirs < "$necessary_dirs_file"

# Convert the array to a set for quick lookup
declare -A necessary_dirs_set
for dir in "${necessary_dirs[@]}"; do
    short_dir=$(echo "$dir" | cut -c1-15)
    necessary_dirs_set["${short_dir}_proteins.zip"]=1
done

# Iterate over the zip files in the target folder
for file in "$target_folder"/*_proteins.zip; do
    if [ -f "$file" ]; then
        file_name=$(basename "$file")
        # Check if the file is not in the necessary directories set
        if [ -z "${necessary_dirs_set[$file_name]}" ]; then
            echo "Deleting file: $file_name"
            rm -f "$file"
        fi
    fi
done