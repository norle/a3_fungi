#!/bin/bash

# Path to the CSV file
csv_file="/zhome/85/8/203063/a3_fungi/data_out/cleaned_genomes.csv"

# Path to the directory containing the folders
source_dir="/work3/s233201/finished_runs"

# Path to the directory where folders will be moved
destination_dir="/work3/s233201/filtered_runs"

# Create the destination directory if it doesn't exist
mkdir -p "$destination_dir"

# Read the CSV file and store the folder names in an array
mapfile -t folders_to_keep < "$csv_file"

# Loop through all directories in the source directory
for dir in "$source_dir"/*/; do
    dir_name=$(basename "$dir")
    # Check if the directory name is in the folders_to_keep array
    if [[ ! " ${folders_to_keep[@]} " =~ " ${dir_name} " ]]; then
        # Move the directory to the destination directory
        mv "$dir" "$destination_dir"
    fi
done