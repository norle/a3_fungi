#!/bin/bash
# embedded options to bsub - start with #BSUB
# -- our name ---
#BSUB -J rf_loop
# -- choose queue --
#BSUB -q hpc
# -- specify that we need 4GB of memory per core/slot --
# so when asking for 4 cores, we are really asking for 4*4GB=16GB of memory 
# for this job. 
#BSUB -R "rusage[mem=1GB]"

# -- email address -- 
# please uncomment the following line and put in your e-mail address,
# if you want to receive e-mail notifications on a non-default address
##BSUB -u your_email_address
# -- Output File --
#BSUB -o out/Output_rf_loop_%J.out
# -- Error File --
#BSUB -e out/Output_rf_loop_%J.err
# -- estimated wall clock time (execution time): hh:mm -- 
#BSUB -W 1:00
# -- Number of cores requested -- 
#BSUB -n 1
# -- Specify the distribution of the cores: on a single node --
#BSUB -R "span[hosts=1]"
# -- end of LSF options -- 

while true; do
    # Check the number of jobs running
    num_jobs=$(bstat | grep -c "RUN")
    if [ "$num_jobs" -lt 2 ]; then
        echo "Less than 2 jobs running. Terminating the loop."
        break
    fi

    bash ~/a3_fungi/sh_scripts/refactor_busco_runs.sh /work3/s233201/out_busco /work3/s233201/finished_runs
    sleep 60  # Sleep for 60 seconds (1 minute)
done

