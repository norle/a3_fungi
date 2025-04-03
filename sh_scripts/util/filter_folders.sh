#!/bin/bash

# Path to the CSV file
csv_file="/zhome/85/8/203063/a3_fungi/data_out/taxa_no_missing_after_interpro.csv"

# Path to the directory containing the folders
source_dir="/work3/s233201/finished_runs"

# Path to the directory where folders will be moved
destination_dir="/work3/s233201/filtered_runs"

# Create the destination directory if it doesn't exist
mkdir -p "$destination_dir"

# Read the CSV file and store the first 15 chars of folder names in an array
while IFS= read -r line; do
    folders_to_keep+=("${line:0:15}")
done < "$csv_file"

# Loop through all directories in the source directory
for dir in "$source_dir"/*/; do
    dir_name=$(basename "$dir")
    dir_name_prefix=${dir_name:0:15}
    # Check if the first 15 characters of the directory name is in the folders_to_keep array
    if [[ ! " ${folders_to_keep[@]} " =~ " ${dir_name_prefix} " ]]; then
        # Move the directory to the destination directory
        mv "$dir" "$destination_dir"
    fi
done