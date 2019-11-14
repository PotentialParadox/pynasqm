module load intel/2017
source ~/myapps/load_boost
source /ufrc/roitberg/dtracy/amber/amber.sh

export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK}

ID=${SLURM_ARRAY_TASK_ID}
cd mmground/restart_0
$AMBERHOME/bin/sander -O -i nasqm_ground_r0.in -o nasqm_ground_r0.out -c snap_for_mm_r0.rst -p m1.prmtop -r snap_for_mm_r1.rst -x nasqm_ground_r0.nc
cd ../../..