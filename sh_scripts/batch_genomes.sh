#!/bin/bash

# Check if the directory is provided as an argument
if [ -z "$1" ]; then
    echo "Usage: $0 <directory>"
    exit 1
fi

# Directory containing the files and to store the batches
DIR="$1"

# Initialize batch counter
batch_num=1
file_count=0

# Create the first batch directory
batch_dir="$DIR/batch_$batch_num"
mkdir -p "$batch_dir"

# Loop through all files in the directory
for file in "$DIR"/*; do
    # Skip directories
    if [ -d "$file" ]; then
        continue
    fi

    # Move the file to the current batch directory
    mv "$file" "$batch_dir"
    ((file_count++))

    # If the batch size is reached, create a new batch directory
    if ((file_count == 100)); then
        ((batch_num++))
        batch_dir="$DIR/batch_$batch_num"
        mkdir -p "$batch_dir"
        file_count=0
    fi
done

echo "Files have been distributed into batches."