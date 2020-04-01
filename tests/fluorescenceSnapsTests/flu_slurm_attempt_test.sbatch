#!/bin/bash
#SBATCH --job-name=MyJobfluorescence # A name for your job
#SBATCH --qos=roitberg # The queue for your job
#SBATCH --output=./Reports/MyJobfluorescence-%j.output # Output File
#SBATCH --error=./Reports/MyJobfluorescence-%j.err #Error File
#SBATCH --partition=hpg2-compute
#SBATCH --constraint=haswell
#SBATCH --mail-user=dtracy.uf@gmail.com # Email address
#SBATCH --mail-type=END # What emails you want
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=2000mb #Per processor memory requested
#SBATCH --array=1-4%4
#SBATCH --time=00:01:00 #Walltime

source ~/myapps/load_exports
module load intel/2017
source ~/myapps/load_boost
source /ufrc/roitberg/dtracy/amber/amber.sh

export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK}

ID=${SLURM_ARRAY_TASK_ID}
for i in {1..8};do
    cd fluorescence/traj_${ID}/${i}
    if test -f input.ceon; then
        init_state=`grep "exc_state_init.-" input.ceon`
        if [ "$init_state" != "" ];then
            exit
        fi
    fi

    $AMBERHOME/bin/sander -O\
    -i nasqm_fluorescence_t${ID}_r0.in\
    -o nasqm_fluorescence_t${ID}_r0.out\
    -c snap_${i}_for_fluorescence_t${ID}.rst\
    -p m1.prmtop

    cd ../../..
done
