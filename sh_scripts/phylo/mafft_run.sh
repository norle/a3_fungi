#!/bin/bash
# embedded options to bsub - start with #BSUB
# -- our name ---
#BSUB -J mafft
# -- choose queue --
#BSUB -q hpc
# -- specify that we need 4GB of memory per core/slot --
# so when asking for 4 cores, we are really asking for 4*4GB=16GB of memory 
# for this job. 
#BSUB -R "rusage[mem=2GB]"
# -- Notify me by email when execution begins --
##BSUB -B
# -- Notify me by email when execution ends   --
##BSUB -N
# -- email address -- 
# please uncomment the following line and put in your e-mail address,
# if you want to receive e-mail notifications on a non-default address
##BSUB -u your_email_address
# -- Output File --
#BSUB -o out/mafft_%J.out
# -- Error File --
#BSUB -e out/mafft_%J.err
# -- estimated wall clock time (execution time): hh:mm -- 
#BSUB -W 12:00
# -- Number of cores requested -- 
#BSUB -n 16
# -- Specify the distribution of the cores: on a single node --
#BSUB -R "span[hosts=1]"
# -- end of LSF options -- 

source ~/miniconda3/etc/profile.d/conda.sh
conda activate mafft

# mafft --auto --thread 16 /work3/s233201/output_phyl/supermatrix/sequences/494at4751.faa > /work3/s233201/output_phyl/supermatrix/alignments/494at4751.faa

fftnsi --thread 16 /work3/s233201/output_phyl/supermatrix/sequences/494at4751.faa > /work3/s233201/output_phyl/supermatrix/alignments/494at4751_test.faa





