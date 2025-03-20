#!/bin/bash
# embedded options to bsub - start with #BSUB
# -- our name ---
#BSUB -J hdbscan
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
#BSUB -o out/hdb_%J.out
# -- Error File --
#BSUB -e out/hdb_%J.err
# -- estimated wall clock time (execution time): hh:mm -- 
#BSUB -W 1:00
# -- Number of cores requested -- 
#BSUB -n 8
# -- Specify the distribution of the cores: on a single node --
#BSUB -R "span[hosts=1]"
# -- end of LSF options -- 

source ~/miniconda3/etc/profile.d/conda.sh
conda activate busco_phyl

python -u ~/a3_fungi/py_scripts/cluster_hdbscan.py

