#!/bin/bash
#BSUB -J remove_hmmer
#BSUB -n 8
#BSUB -R "span[hosts=1]"
#BSUB -o remove_hmmer.out
#BSUB -e remove_hmmer.err

# Set default parent directory if not provided
PARENT_DIR=${1:-/work3/s233201/finished_runs}

# Verify the directory exists
if [ ! -d "$PARENT_DIR" ]; then
    echo "Error: Directory $PARENT_DIR does not exist"
    exit 1
fi

# Use find and xargs to process directories in parallel
# -P 8 sets the number of parallel processes to 8
find "$PARENT_DIR" -mindepth 1 -maxdepth 1 -type d -print0 | \
xargs -0 -P 8 -I {} bash -c '
    if [ -d "{}/run_fungi_odb10/hmmer_output" ]; then
        rm -rf "{}/run_fungi_odb10/hmmer_output"
    fi
    if [ -d "{}/logs" ]; then
        rm -rf "{}/logs"
    fi
'