#!/bin/bash
# embedded options to bsub - start with #BSUB
# -- our name ---
#BSUB -J get_proteins
# -- choose queue --
#BSUB -q hpc
# -- specify that we need 4GB of memory per core/slot --
# so when asking for 4 cores, we are really asking for 4*4GB=16GB of memory 
# for this job. 
#BSUB -R "rusage[mem=4GB]"
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
#BSUB -n 1 
# -- Specify the distribution of the cores: on a single node --
#BSUB -R "span[hosts=1]"
# -- end of LSF options -- 

# Directory for protein data
PROTEIN_DIR="/work3/s233201/fungi_proteins"
mkdir -p "$PROTEIN_DIR"

# Process the file to get accessions:
# 1. Skip header line
# 2. For each line, keep everything before second underscore
ACCESSIONS=$(tail -n +2 ~/a3_fungi/data_out/filtered_genomes.csv | \
             awk -F '_' '{print $1"_"$2}')

# Download protein data for each accession separately
for ACCESSION in $ACCESSIONS; do
    echo "Downloading proteins for: $ACCESSION"
    
    # Download protein data for the accession
    datasets download genome accession "$ACCESSION" \
        --include protein \
        --filename "${PROTEIN_DIR}/${ACCESSION}_proteins.zip"
done





