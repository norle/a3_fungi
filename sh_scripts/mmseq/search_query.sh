#!/bin/bash
#BSUB -J mmseqs_search
#BSUB -q hpc
#BSUB -R "rusage[mem=16GB]"
#BSUB -o out/mmseqs_search_%J.out
#BSUB -e out/mmseqs_search_%J.err
#BSUB -W 24:00
#BSUB -n 16
#BSUB -R "span[hosts=1]"


source ~/miniconda3/etc/profile.d/conda.sh
conda activate mmseqs

# Function to process single protein file
process_file() {
    protein_file="$1"
    dir_path=$(dirname "$protein_file")
    base_name=$(basename "$dir_path")
    
    # Check if results.tsv already exists
    if [ -f "${dir_path}/results.tsv" ]; then
        #echo "Results file already exists for: $protein_file - Skipping"
        return 0
    fi
    
    mkdir -p "${dir_path}/mmseqs_results"
    
    echo "Searching against: $protein_file"
    mmseqs easy-search \
        /zhome/85/8/203063/a3_fungi/data/s_cer_query.fasta \
        "$protein_file" \
        "${dir_path}/results.tsv" \
        "${dir_path}/tmp" \
        --format-output "query,target,evalue,tseq" \
        -s 7.5 \
        -e 1e-5 \
        --threads 1

    rm -rf "${dir_path}/mmseqs_results/tmp"
}

export -f process_file

# Parent directory containing all fungi protein directories
PARENT_DIR="/work3/s233201/fungi_proteins"

# Run searches in parallel using xargs
find "$PARENT_DIR" -name "protein.faa" -print0 | xargs -0 -I {} -P 16 bash -c 'process_file "{}"'

echo "All searches completed successfully"
