#!/bin/bash
# embedded options to bsub - start with #BSUB
# -- our name ---
#BSUB -J iqtree
# -- choose queue --
#BSUB -q hpc

#BSUB -R "rusage[mem=32GB]"
# -- Notify me by email when execution begins --
##BSUB -B
# -- Notify me by email when execution ends   --
##BSUB -N
# -- email address -- 
# please uncomment the following line and put in your e-mail address,
# if you want to receive e-mail notifications on a non-default address
##BSUB -u your_email_address
# -- Output File --
#BSUB -o out/tree_%J.out
# -- Error File --
#BSUB -e out/tree_%J.err
# -- estimated wall clock time (execution time): hh:mm -- 
#BSUB -W 24:00
# -- Number of cores requested -- 
#BSUB -n 1
# -- Specify the distribution of the cores: on a single node --
#BSUB -R "span[hosts=1]"
# -- end of LSF options -- 

source ~/miniconda3/etc/profile.d/conda.sh
conda activate mmseqs

mmseqs createdb /work3/s233201/fungi_proteins/GCA_000002515.1/protein.faa /work3/s233201/fungi_proteins/GCA_000002515.1/db