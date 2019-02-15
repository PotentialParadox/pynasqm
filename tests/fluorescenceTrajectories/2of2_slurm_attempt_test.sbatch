#!/bin/bash
#SBATCH --job-name=MyJobflu # A name for your job
#SBATCH --qos=roitberg # The queue for your job
#SBATCH --output=MyJobflu-%j.output # Output File
#SBATCH --error=MyJobflu-%j.err #Error File
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
    cd flu/traj_${ID}/restart_1
    $AMBERHOME/bin/sander -O -i nasqm_flu_t${ID}_r1.in -o nasqm_flu_t${ID}_r1.out -c snap_for_flu_t${ID}_r1.rst -p m1.prmtop -r snap_for_flu_t${ID}_r2.rst -x nasqm_flu_t${ID}_r1.nc &
    cd ..
done
wait
