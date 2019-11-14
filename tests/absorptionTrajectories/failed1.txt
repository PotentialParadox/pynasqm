for i in $(seq 1 2)
do
    MULTIPLIER="$((${SLURM_ARRAY_TASK_ID} - 1))"
    FIRST_COUNT="$((${SLURM_CPUS_ON_NODE} * ${MULTIPLIER}))"
    ID="$((${FIRST_COUNT} + ${i}))"
    cd abs/traj_${ID}/restart_1
    $AMBERHOME/bin/sander -O -i nasqm_abs_t${ID}_r1.in -o nasqm_abs_t${ID}_r1.out -c snap_for_abs_t${ID}_r1.rst -p m1.prmtop -r snap_for_abs_t${ID}_r2.rst -x nasqm_abs_t${ID}_r1.nc &
    cd ../../..
done
wait
