#!/bin/bash
#BSUB -J delete_dbs
#BSUB -q hpc
#BSUB -R "rusage[mem=4GB]"
#BSUB -o out/delete_dbs_%J.out
#BSUB -e out/delete_dbs_%J.err
#BSUB -W 4:00
#BSUB -n 1
#BSUB -R "span[hosts=1]"

# Parent directory containing all fungi protein directories
PARENT_DIR="/work3/s233201/fungi_proteins"

# Find and remove all MMseqs2 database files
find "$PARENT_DIR" -type f -name "db*" -delete

# Find and remove temporary directories
find "$PARENT_DIR" -type d -name "tmp" -exec rm -rf {} +

echo "All database files have been removed"
