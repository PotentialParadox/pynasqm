#!/bin/bash
#SBATCH --job-name=MyJobAbs # A name for your job
#SBATCH --qos=roitberg # The queue for your job
#SBATCH --output=MyJobAbs-%j.output # Output File
#SBATCH --error=MyJobAbs-%j.err #Error File
#SBATCH --mail-user=dtracy.uf@gmail.com # Email address
#SBATCH --mail-type=END # What emails you want
#SBATCH --nodes=1 #No. computers requested
#SBATCH --tasks-per-node=16 # No. processors per node
#SBATCH --mem-per-cpu=2000mb #Per processor memory requested
#SBATCH --array=1-1%4
#SBATCH --time=00:01:00 #Walltime

module load intel/2017

for i in $(seq 1 2)
do
    MULTIPLIER="$((${SLURM_ARRAY_TASK_ID} - 1))"
    FIRST_COUNT="$((${SLURM_CPUS_ON_NODE} * ${MULTIPLIER}))"
    ID="$((${FIRST_COUNT} + ${i}))"
    cd ${ID}
    $AMBERHOME/bin/sander -O -i nasqm_abs_r0_t${ID}.in -o nasqm_abs_r0_t${ID}.out -c ground_snap.${ID} -p m1.prmtop -r nasqm_abs_r0_t${ID}.rst -x nasqm_abs_r0_t${ID}.nc &
    cd ..
done
wait
