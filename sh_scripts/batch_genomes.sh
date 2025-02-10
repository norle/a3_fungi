#!/bin/bash

# Check if the directory is provided as an argument
if [ -z "$1" ]; then
    echo "Usage: $0 <directory> [finished_runs_file] [batch_size]"
    exit 1
fi

# Directory containing the files and to store the batches
DIR="$1"

# Optional file with finished runs
FINISHED_RUNS_FILE="$2"

# Batch size (default to 100 if not provided)
BATCH_SIZE="${3:-100}"

echo "Batch size of $BATCH_SIZE"

# Initialize batch counter
batch_num=1
file_count=0

# Create the first batch directory
batch_dir="$DIR/batch_$batch_num"
mkdir -p "$batch_dir"

# Create the finished runs directory
finished_runs_dir="$DIR/finished_runs"
mkdir -p "$finished_runs_dir"

# If the finished runs file is provided, move the corresponding files
if [ -n "$FINISHED_RUNS_FILE" ]; then
    while IFS= read -r finished_file; do
        if [ -f "$DIR/$finished_file" ]; then
            mv "$DIR/$finished_file" "$finished_runs_dir"
        fi
    done < "$FINISHED_RUNS_FILE"
fi

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
    if ((file_count == BATCH_SIZE)); then
        ((batch_num++))
        batch_dir="$DIR/batch_$batch_num"
        mkdir -p "$batch_dir"
        file_count=0
    fi
done

echo "Files have been distributed into batches."