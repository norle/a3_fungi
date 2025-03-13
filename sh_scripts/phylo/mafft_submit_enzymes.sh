#!/bin/bash
#BSUB -J submit_mafft
#BSUB -o out/submit_mafft_%J.out
#BSUB -e out/submit_mafft_%J.err
#BSUB -q hpc
#BSUB -n 1
#BSUB -R "rusage[mem=1GB]"
#BSUB -W 48:00



SEQUENCE_DIR="/work3/s233201/enzyme_out_2"
OUTPUT_DIR="/work3/s233201/enzyme_out_2"

# Create output directories if they don't exist
mkdir -p out_mafft
mkdir -p "${OUTPUT_DIR}/alignments"

# Function to count running jobs
count_running_jobs() {
    bjobs -w | grep "mafft_" | wc -l
}

MAX_CONCURRENT=20

# Process each sequence file
for seq_file in "${SEQUENCE_DIR}"/*.fasta; do
    # Check if files exist
    if [ ! -f "$seq_file" ]; then
        echo "No .faa files found in ${SEQUENCE_DIR}"
        exit 1
    fi
    
    # Extract filename without path and extension
    filename=$(basename "$seq_file" .fasta)
    
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
         -n 8 \
         -R "span[hosts=1] rusage[mem=1GB]" \
         -q hpc \
         -W 12:00 \
         "source ~/miniconda3/etc/profile.d/conda.sh && \
          conda activate mafft && \
          fftnsi --thread 8 ${seq_file} > ${OUTPUT_DIR}/alignments_mafft/${filename}.aln"
done
