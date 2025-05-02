#!/bin/bash
#BSUB -J submit_mafft
#BSUB -o out/submit_mafft_%J.out
#BSUB -e out/submit_mafft_%J.err
#BSUB -q hpc
#BSUB -n 1
#BSUB -R "rusage[mem=1GB]"
#BSUB -W 48:00

BASE_DIR="/work3/s233201/output_phyl_busco_4/supermatrix"

# Create output directories if they don't exist
mkdir -p out_mafft
mkdir -p "${BASE_DIR}/alignments"

# Function to count running jobs
count_running_jobs() {
    bjobs -w | grep "mafft_" | wc -l
}

MAX_CONCURRENT=100

# Process each sequence file
for seq_file in ${BASE_DIR}/sequences/*.faa; do
    # Extract filename without path and extension
    filename=$(basename "$seq_file" .faa)
    
    # Wait if we have reached max concurrent jobs
    while [ $(count_running_jobs) -ge $MAX_CONCURRENT ]; do
        echo "Maximum concurrent jobs reached, waiting..."
        sleep 60
    done
    
    echo "Submitting MAFFT job for ${filename}"
    
    # Submit the MAFFT job
    bsub -J "mafft_${filename}" \
         -o "out_mafft/mafft_${filename}_%J.out" \
         -e "out_mafft/mafft_${filename}_%J.err" \
         -n 2 \
         -R "span[hosts=1] rusage[mem=4GB]" \
         -q hpc \
         -W 12:00 \
         "source ~/miniconda3/etc/profile.d/conda.sh && \
          conda activate mafft && \
          mafft --auto --thread 8 ${seq_file} > ${BASE_DIR}/alignments/${filename}.aln"
done
