for i in $(seq 1 1)
do
    MULTIPLIER="$((${SLURM_ARRAY_TASK_ID} - 1))"
    FIRST_COUNT="$((${SLURM_CPUS_ON_NODE} * ${MULTIPLIER}))"
    ID="$((${FIRST_COUNT} + ${i}))"
    cd ${ID}
    $AMBERHOME/bin/sander -O -i nasqm_ground_r1.in -o nasqm_ground_r1.out -c nasqm_ground_r0.rst -p m1.prmtop -r nasqm_ground_r1.rst -x nasqm_ground_r1.nc &
    cd ..
done
wait
