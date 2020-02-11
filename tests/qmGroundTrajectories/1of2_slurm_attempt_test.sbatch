ID=${SLURM_ARRAY_TASK_ID}
cd qmground/traj_${ID}/restart_0
if test -f input.ceon; then
    init_state=`grep "exc_state_init.-" input.ceon`
    if [ "$init_state" != "" ];then
        exit
    fi
fi
$AMBERHOME/bin/sander -O -i nasqm_qmground_t${ID}_r0.in -o nasqm_qmground_t${ID}_r0.out -c snap_for_qmground_t${ID}_r0.rst -p m1.prmtop -r snap_for_qmground_t${ID}_r1.rst -x nasqm_qmground_t${ID}_r0.nc
cd ../../..
