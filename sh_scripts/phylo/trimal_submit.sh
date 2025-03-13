#!/bin/bash
#BSUB -J submit_trimal
#BSUB -o out/submit_trimal_%J.out
#BSUB -e out/submit_trimal_%J.err
#BSUB -q hpc
#BSUB -n 1
#BSUB -R "rusage[mem=1GB]"
#BSUB -W 24:00

# Define source and output paths
SOURCE_DIR="/work3/s233201/output_phyl_busco_1/supermatrix/alignments"
OUTPUT_DIR="/work3/s233201/output_phyl_busco_1/supermatrix/trim"

# Create output directories if they don't exist
mkdir -p out_trimal
mkdir -p "$OUTPUT_DIR"

# Function to count running jobs
count_running_jobs() {
    bjobs -w | grep "trimal_" | wc -l
}

MAX_CONCURRENT=50

# Process each alignment file
for aln_file in "${SOURCE_DIR}"/*.aln; do
    # Extract filename without path and extension
    filename=$(basename "$aln_file" .aln)
    
    # Wait if we have reached max concurrent jobs
    while [ $(count_running_jobs) -ge $MAX_CONCURRENT ]; do
        echo "Maximum concurrent jobs reached, waiting..."
        sleep 10
    done
    
    echo "Submitting Trimal job for ${filename}"
    
    # Submit the Trimal job
    bsub -J "trimal_${filename}" \
         -o "out_trimal/trimal_${filename}_%J.out" \
         -e "out_trimal/trimal_${filename}_%J.err" \
         -n 1 \
         -R "span[hosts=1] rusage[mem=4GB]" \
         -q hpc \
         -W 1:00 \
         "source ~/miniconda3/etc/profile.d/conda.sh && \
          conda activate busco_phyl && \
          trimal -in ${aln_file} -out ${OUTPUT_DIR}/${filename}.aln -gappyout"
done
