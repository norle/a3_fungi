#!/bin/bash

# Check if the parent directory is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <parent_directory>"
    exit 1
fi

PARENT_DIR="$1"

# Check if the provided argument is a directory
if [ ! -d "$PARENT_DIR" ]; then
    echo "Error: $PARENT_DIR is not a directory"
    exit 1
fi

# Iterate over all directories in the parent directory
for dir in "$PARENT_DIR"/*/; do
    # Check if it is a directory
    if [ -d "$dir" ]; then
        # Move all files from the child directory to the parent directory
        mv "$dir"* "$PARENT_DIR"
        # Remove the child directory
        rmdir "$dir"
    fi
done

echo "All files have been extracted and child directories deleted."