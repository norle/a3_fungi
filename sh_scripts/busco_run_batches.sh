#!/bin/bash

# Define start and end batch numbers
START_BATCH=6
END_BATCH=60
echo 'Starting batches'

# Loop through specified batch range
for batch_num in $(seq $START_BATCH $END_BATCH); do
    batch_dir="/work3/s233201/data/ncbi_dataset/data/batch_${batch_num}"
    out_dir="out_busco/busco_batch_${batch_num}"
    
    if [ -d "$batch_dir" ]; then
        echo "Submitting job for batch ${batch_num}"
        
        # Submit a new job for each batch
        bsub -J "busco_${batch_num}" \
             -o "out/Output_${batch_num}.out" \
             -e "out/Error_${batch_num}.err" \
             -n 4 \
             -R "span[hosts=1] rusage[mem=1GB]" \
             -q hpc \
             -W 48:00 \
             -B \
             -N \
             "source ~/miniconda3/etc/profile.d/conda.sh && \
              conda activate busco && \
              busco -i ${batch_dir} \
                -m genome \
                -l fungi_odb10 \
                -f \
                -q \
                -o ${out_dir} \
                -c 4 \
                --metaeuk"
    else
        echo "Batch directory ${batch_num} not found"
    fi
done