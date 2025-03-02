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
# 2. Take first 15 characters from each line
ACCESSIONS=$(tail -n +2 ~/a3_fungi/data_out/busco_results_cleaned.csv | \
             cut -c 1-15)

# Get list of existing folders into an array
mapfile -t EXISTING_FOLDERS < <(ls -d ${PROTEIN_DIR}/*/ 2>/dev/null | xargs -n 1 basename)

# Debug print
echo "Found ${#EXISTING_FOLDERS[@]} existing folders"

# Find missing accessions
MISSING_ACCESSIONS=()
for ACCESSION in $ACCESSIONS; do
    FOUND=0
    for FOLDER in "${EXISTING_FOLDERS[@]}"; do
        if [ "$ACCESSION" = "$FOLDER" ]; then
            FOUND=1
            break
        fi
    done
    if [ $FOUND -eq 0 ]; then
        MISSING_ACCESSIONS+=("$ACCESSION")
    fi
done

# Print the number of missing accessions
echo "Total accessions to process: $(echo "$ACCESSIONS" | wc -w)"
echo "Number of missing accessions: ${#MISSING_ACCESSIONS[@]}"

# Download protein data for each missing accession separately
for ACCESSION in "${MISSING_ACCESSIONS[@]}"; do
    echo "Downloading proteins for: $ACCESSION"
    
    # Download protein data for the accession
    if ! datasets download genome accession "$ACCESSION" \
        --include protein \
        --filename "${PROTEIN_DIR}/${ACCESSION}_proteins.zip"; then
        echo "Failed to download proteins for: $ACCESSION"
    fi
done





