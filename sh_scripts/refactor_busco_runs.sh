#!/bin/bash

# Check if the correct number of arguments is provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <source_directory> <destination_directory>"
    exit 1
fi

# Define the source and destination directories from input arguments
SOURCE_DIR="$1"
DEST_DIR="$2"
LOG_FILE="$DEST_DIR/finished_runs.txt"

# Check if the log file is not empty and echo a message
if [ -s "$LOG_FILE" ]; then
    echo "Warning: The log file is not empty. Appending new entries."
else
    # Ensure the log file is empty
    > "$LOG_FILE"
fi

# Loop through each batch directory in the source directory
for batch_dir in "$SOURCE_DIR"/*; do
    if [ -d "$batch_dir" ]; then
        # Loop through each directory in the batch directory
        for dir in "$batch_dir"/*; do
            if [ -d "$dir" ]; then
                # Count the number of objects in the directory
                object_count=$(ls -1q "$dir" | wc -l)
                
                if [ "$object_count" -eq 4 ]; then
                    # Remove the run_fungi_odb10/metaeuk_output directory if it exists
                    if [ -d "$dir/run_fungi_odb10/metaeuk_output" ]; then
                        rm -rf "$dir/run_fungi_odb10/metaeuk_output"
                    fi
                    
                    # Append the directory name to the log file
                    echo "$(basename "$dir")" >> "$LOG_FILE"
                    
                    # If the destination directory already exists, delete the source directory
                    if [ -d "$DEST_DIR/$(basename "$dir")" ]; then
                        rm -rf "$dir"
                    else
                        # Move the directory to the destination path
                        mv "$dir" "$DEST_DIR"
                    fi
                fi
                # else
                #     # Delete the directory if it doesn't contain exactly 4 objects
                #     rm -rf "$dir"

            fi
        done
    fi
done