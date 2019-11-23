module load intel/2017
source ~/myapps/load_boost
source /ufrc/roitberg/dtracy/amber/amber.sh

export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK}

ID=${SLURM_ARRAY_TASK_ID}
cd abs/traj_${ID}/restart_1
$AMBERHOME/bin/sander -O -i nasqm_abs_t${ID}_r1.in -o nasqm_abs_t${ID}_r1.out -c snap_for_abs_t${ID}_r1.rst -p m1.prmtop -r snap_for_abs_t${ID}_r2.rst -x nasqm_abs_t${ID}_r1.nc
cd ../../..
