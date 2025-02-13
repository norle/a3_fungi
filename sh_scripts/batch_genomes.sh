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

# Initialize batch counters
regular_batch_num=1
large_batch_num=1
regular_file_count=0
large_file_count=0

# Create initial batch directories
regular_batch_dir="$DIR/batch_$regular_batch_num"
large_batch_dir="$DIR/batch_l_$large_batch_num"
mkdir -p "$regular_batch_dir" "$large_batch_dir"

# Create the finished runs directory
finished_runs_dir="$DIR/finished_runs"
mkdir -p "$finished_runs_dir"

# Handle finished runs if file provided
if [ -n "$FINISHED_RUNS_FILE" ]; then
    while IFS= read -r finished_file; do
        if [ -f "$DIR/$finished_file" ]; then
            mv "$DIR/$finished_file" "$finished_runs_dir"
        fi
    done < "$FINISHED_RUNS_FILE"
fi

# Process files
for file in "$DIR"/*; do
    # Skip directories
    if [ -d "$file" ]; then
        continue
    fi

    # Get file size in megabytes
    size_mb=$(du -m "$file" | cut -f1)

    # Determine if file is large (>100MB)
    if [ "$size_mb" -gt 100 ]; then
        # Handle large file
        mv "$file" "$large_batch_dir"
        ((large_file_count++))

        # Create new large batch directory if needed
        if ((large_file_count == BATCH_SIZE)); then
            ((large_batch_num++))
            large_batch_dir="$DIR/batch_l_$large_batch_num"
            mkdir -p "$large_batch_dir"
            large_file_count=0
        fi
    else
        # Handle regular file
        mv "$file" "$regular_batch_dir"
        ((regular_file_count++))

        # Create new regular batch directory if needed
        if ((regular_file_count == BATCH_SIZE)); then
            ((regular_batch_num++))
            regular_batch_dir="$DIR/batch_$regular_batch_num"
            mkdir -p "$regular_batch_dir"
            regular_file_count=0
        fi
    fi
done

echo "Files have been distributed into batches."
echo "Regular batches: $regular_batch_num"
echo "Large genome batches: $large_batch_num"