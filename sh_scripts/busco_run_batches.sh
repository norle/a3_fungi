#!/bin/bash
# embedded options to bsub - start with #BSUB
# -- our name ---
#BSUB -J busco_batches 
# -- choose queue --
#BSUB -q hpc
# -- specify that we need 4GB of memory per core/slot --
# so when asking for 4 cores, we are really asking for 4*4GB=16GB of memory 
# for this job. 
#BSUB -R "rusage[mem=1GB]"
# -- Notify me by email when execution begins --
##BSUB -B
# -- Notify me by email when execution ends   --
##BSUB -N
# -- email address -- 
# please uncomment the following line and put in your e-mail address,
# if you want to receive e-mail notifications on a non-default address
##BSUB -u your_email_address
# -- Output File --
#BSUB -o out/Output_%J.out
# -- Error File --
#BSUB -e out/Output_%J.err
# -- estimated wall clock time (execution time): hh:mm -- 
#BSUB -W 24:00 
# -- Number of cores requested -- 
#BSUB -n 32 
# -- Specify the distribution of the cores: on a single node --
#BSUB -R "span[hosts=1]"
# -- end of LSF options -- 

source ~/miniconda3/etc/profile.d/conda.sh
conda activate busco

# Define start and end batch numbers
START_BATCH=11
END_BATCH=20

# Loop through specified batch range
for batch_num in $(seq $START_BATCH $END_BATCH); do
    batch_dir="/work3/s233201/data/ncbi_dataset/data/batch_${batch_num}"
    
    if [ -d "$batch_dir" ]; then
        echo "Processing batch ${batch_num}: $batch_dir"
        
        busco -i "$batch_dir" \
              -m genome \
              -l fungi_odb10 \
              -f \
              -q \
              -o "out_busco/busco_batch_${batch_num}" \
              -c 32 \
              --metaeuk
    else
        echo "Batch directory ${batch_num} not found"
    fi
done

