ID=${SLURM_ARRAY_TASK_ID}
cd abs/traj_${ID}/restart_1
if test -f input.ceon; then
    init_state=`grep "exc_state_init.-" input.ceon`
    if [ "$init_state" != "" ];then
        exit
    fi
fi
$AMBERHOME/bin/sander -O -i nasqm_abs_t${ID}_r1.in -o nasqm_abs_t${ID}_r1.out -c snap_for_abs_t${ID}_r1.rst -p m1.prmtop -r snap_for_abs_t${ID}_r2.rst -x nasqm_abs_t${ID}_r1.nc
cd ../../..
