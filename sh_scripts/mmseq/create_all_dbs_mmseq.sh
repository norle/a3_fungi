#!/bin/bash
#BSUB -J mmseqs_dbs
#BSUB -q hpc
#BSUB -R "rusage[mem=32GB]"
#BSUB -o out/mmseqs_dbs_%J.out
#BSUB -e out/mmseqs_dbs_%J.err
#BSUB -W 24:00
#BSUB -n 1
#BSUB -R "span[hosts=1]"

source ~/miniconda3/etc/profile.d/conda.sh
conda activate mmseqs

# Parent directory containing all fungi protein directories
PARENT_DIR="/work3/s233201/fungi_proteins"

# Find all protein.faa files and create databases
find "$PARENT_DIR" -name "protein.faa" | while read -r protein_file; do
    # Get the directory containing the protein file
    dir_path=$(dirname "$protein_file")
    
    # Create the database in the same directory
    echo "Creating database for: $protein_file"
    mmseqs createdb "$protein_file" "$dir_path/db"
    mmseqs createindex "$dir_path/db" "$dir_path/tmp"
done

echo "All databases created successfully"
