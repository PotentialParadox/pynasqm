ID=${SLURM_ARRAY_TASK_ID}
cd mmground/restart_0
if test -f input.ceon; then
    init_state=`grep "exc_state_init.-" input.ceon`
    if [ "$init_state" != "" ];then
        exit
    fi
fi
$AMBERHOME/bin/sander -O -i nasqm_ground_r0.in -o nasqm_ground_r0.out -c snap_for_mm_r0.rst -p m1.prmtop -r snap_for_mm_r1.rst -x nasqm_ground_r0.nc
cd ../../..