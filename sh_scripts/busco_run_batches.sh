#!/bin/bash
#BSUB -J submit_busco
#BSUB -o out/submit_busco_%J.out
#BSUB -e out/submit_busco_%J.err
#BSUB -q hpc
#BSUB -n 1
#BSUB -R "rusage[mem=0.5GB]"
#BSUB -W 48:00

# Create output directories if they don't exist
mkdir -p out
mkdir -p out_busco

# Define start and end batch numbers
START_BATCH=1
END_BATCH=54
MAX_CONCURRENT=10
echo 'Starting batches'

# Function to count running jobs
count_running_jobs() {
    bjobs -w | grep "busco_" | wc -l
}

# Loop through specified batch range
for batch_num in $(seq $START_BATCH $END_BATCH); do
    batch_dir="/work3/s233201/data/ncbi_dataset/data/batch_${batch_num}"
    out_dir="out_busco/busco_batch_${batch_num}"
    
    if [ -d "$batch_dir" ]; then
        # Wait if we have reached max concurrent jobs
        while [ $(count_running_jobs) -ge $MAX_CONCURRENT ]; do
            echo "Maximum concurrent jobs reached, waiting..."
            sleep 60
        done
        
        echo "Submitting job for batch ${batch_num}"
        
        # Submit a new job for each batch
        bsub -J "busco_${batch_num}" \
             -o "out/Output_${batch_num}.out" \
             -e "out/Error_${batch_num}.err" \
             -n 16 \
             -R "span[hosts=1] rusage[mem=1GB]" \
             -q hpc \
             -W 48:00 \
             -Ne \
             "source ~/miniconda3/etc/profile.d/conda.sh && \
              conda activate busco && \
              busco -i ${batch_dir} \
                -m genome \
                -l fungi_odb10 \
                -f \
                -q \
                -o ${out_dir} \
                -c 16 \
                --metaeuk"
    else
        echo "Batch directory ${batch_num} not found"
    fi
done
