#!/bin/bash
#SBATCH --job-name=MyJobabs # A name for your job
#SBATCH --qos=roitberg # The queue for your job
#SBATCH --output=MyJobabs-%j.output # Output File
#SBATCH --error=MyJobabs-%j.err #Error File
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
    cd abs/traj_${ID}/restart_0
    $AMBERHOME/bin/sander -O -i nasqm_abs_t${ID}_r0.in -o nasqm_abs_t${ID}_r0.out -c snap_for_abs_t${ID}_r0.rst -p m1.prmtop -r snap_for_abs_t${ID}_r1.rst -x nasqm_abs_t${ID}_r0.nc &
    cd ../../..
done
wait
