#!/bin/bash

# Define directories
input_dir="/work3/s233201/output_phyl_busco_4/supermatrix/sequences"
trashed_dir="/work3/s233201/output_phyl_busco_4/supermatrix/trashed"

# Check if the trashed directory exists, if not, create it
if [ ! -d "$trashed_dir" ]; then
    mkdir -p "$trashed_dir"
fi

# Create trashed directory if it doesn't exist
mkdir -p "$trashed_dir"

# Set the threshold value
threshold=4491  # Change this value as needed

# Initialize counter for kept sequences
kept_count=0

# Loop through all *.fasta files in the input directory
for fasta_file in "$input_dir"/*.faa; do
    # Count the number of '>' characters in the file
    count=$(grep -c ">" "$fasta_file")
    
    # Check if the count is below the threshold
    if (( count < threshold )); then
        # Move the file to the trashed directory
        #mv "$fasta_file" "$trashed_dir"
        echo "Moved $fasta_file to $trashed_dir (count: $count)"
    else
        echo "Kept $fasta_file (count: $count)"
        ((kept_count++))
    fi
done

# Print the total number of sequences kept
echo "Total number of sequences kept: $kept_count"