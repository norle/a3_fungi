#!/bin/bash
#BSUB -J submit_iqtree
#BSUB -o out/submit_iqtree_%J.out
#BSUB -e out/submit_iqtree_%J.err
#BSUB -q hpc
#BSUB -n 1
#BSUB -R "rusage[mem=1GB]"
#BSUB -W 48:00

# Create output directories
mkdir -p out_iqtree
mkdir -p /work3/s233201/enzyme_out_6/enzyme_trees

# Function to count running jobs
count_running_jobs() {
    bjobs -w | grep "iqtree_" | wc -l
}

MAX_CONCURRENT=20

# Process each alignment file
for aln in /work3/s233201/enzyme_out_6/trim/*.aln; do
    # Extract enzyme name from filename
    enzyme=$(basename "$aln" .aln)
    
    # Wait if we have reached max concurrent jobs
    while [ $(count_running_jobs) -ge $MAX_CONCURRENT ]; do
        echo "Maximum concurrent jobs reached, waiting..."
        sleep 60
    done
    
    # Create enzyme-specific output directory
    out_dir="/work3/s233201/enzyme_out_6/enzyme_trees/$enzyme"
    mkdir -p "$out_dir"
    
    echo "Submitting IQ-TREE job for ${enzyme}"
    
    # Submit the IQ-TREE job
    bsub -J "iqtree_${enzyme}" \
         -o "out_iqtree/iqtree_${enzyme}_%J.out" \
         -e "out_iqtree/iqtree_${enzyme}_%J.err" \
         -n 4 \
         -R "span[hosts=1] rusage[mem=18GB]" \
         -q hpc \
         -W 72:00 \
         "source ~/miniconda3/etc/profile.d/conda.sh && \
          conda activate busco_phyl && \
          iqtree -s ${aln} -T 4 -m LG+I -B 1000 -pre ${out_dir}/tree_iq_multi_LGI"
done