#!/bin/bash

# Check if the parent directory is provided as an argument
if [ -z "$1" ]; then
    echo "Usage: $0 <parent_directory>"
    exit 1
fi

# Parent directory
PARENT_DIR="$1"

# Loop through directories in the parent directory
for dir in "$PARENT_DIR"/*/; do
    # Check if hmmer_output directory exists and remove it
    if [ -d "$dir/run_fungi_odb10/hmmer_output" ]; then
        rm -rf "$dir/run_fungi_odb10/hmmer_output"
        #echo "Removed $dir/hmmer_output"
    fi

    # Check if logs directory exists and remove it
    if [ -d "$dir/logs" ]; then
        rm -rf "$dir/logs"
        #echo "Removed $dir/logs"
    fi
done