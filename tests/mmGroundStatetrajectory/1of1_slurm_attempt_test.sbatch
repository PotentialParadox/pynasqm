for i in $(seq 1 1)
do
    MULTIPLIER="$((${SLURM_ARRAY_TASK_ID} - 1))"
    FIRST_COUNT="$((${SLURM_CPUS_ON_NODE} * ${MULTIPLIER}))"
    ID="$((${FIRST_COUNT} + ${i}))"
    cd mmground/restart_0
    $AMBERHOME/bin/sander -O -i nasqm_ground_r0.in -o nasqm_ground_r0.out -c snap_for_mm_r0.rst -p m1.prmtop -r snap_for_mm_r1.rst -x nasqm_ground_r0.nc &
    cd ../../..
done
wait