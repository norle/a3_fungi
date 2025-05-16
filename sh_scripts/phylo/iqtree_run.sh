#!/bin/bash
# embedded options to bsub - start with #BSUB
# -- our name ---
#BSUB -J iqtree
# -- choose queue --
#BSUB -q hpc
# -- specify that we need 4GB of memory per core/slot --
# so when asking for 4 cores, we are really asking for 4*4GB=16GB of memory 
# for this job. 
#BSUB -R "rusage[mem=18GB]"
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
#BSUB -n 20
# -- Specify the distribution of the cores: on a single node --
#BSUB -R "span[hosts=1]"
# -- end of LSF options -- 

source ~/miniconda3/etc/profile.d/conda.sh
conda activate busco_phyl

# iqtree -s /work3/s233201/output_phyl_busco/supermatrix/final.aln -T 20 -mem 300G -m LG+I -B 1000 -pre /work3/s233201/output_phyl_busco/tree_iq_multi_LGI

iqtree -s /work3/s233201/output_phyl_busco_4/supermatrix/final.fasta -T 20 -mem 300G -m LG+I -fast -pre /work3/s233201/output_phyl_busco_4/tree_iq_LGI

# iqtree -s /work3/s233201/enzyme_out_6/final.fasta -T 20 -m LG+I -B 1000 -pre /work3/s233201/enzyme_out_6/tree_LGI