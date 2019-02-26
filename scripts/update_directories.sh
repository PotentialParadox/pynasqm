trajs=$@
mkdir -p mmground/restart_0
mv nasqm_ground.nc mmground
mv nasqm_ground.in mmground/restart_0/nasqm_ground_r0.in
mv nasqm_ground.out mmground/restart_0/nasqm_ground_r0.out
for traj in $trajs;do
    echo $traj
    abshome=abs/traj_${traj}/restart_0
    mkdir -p $abshome
    mkdir -p abs/traj_${traj}/nmr
    mv ${traj}/nasqm_abs_${traj}.in $abshome/nasqm_abs_t${traj}_r0.in
    mv ${traj}/nasqm_abs_${traj}.rst $abshome/snap_for_abs_t${traj}_r1.rst
    mv ${traj}/nasqm_abs_${traj}.nc $abshome/nasqm_abs_t${traj}_r0.nc
    mv ${traj}/nasqm_abs_${traj}.out $abshome/nasqm_abs_t${traj}_r0.out
    mv ${traj}/rst_${traj}.dist abs/traj_${traj}/nmr
    mv ${traj}/closest_${traj}.txt abs/traj_${traj}/nmr

    fluhome=flu/traj_${traj}/restart_0
    mkdir -p $fluhome
    mkdir -p flu/traj_${traj}/nmr
    mv ${traj}/nasqm_flu_${traj}.in $fluhome/nasqm_flu_t${traj}_r0.in
    mv ${traj}/nasqm_flu_${traj}.rst $fluhome/snap_for_flu_t${traj}_r1.rst
    mv ${traj}/nasqm_flu_${traj}.nc $fluhome/nasqm_flu_t${traj}_r0.nc
    mv ${traj}/nasqm_flu_${traj}.out $fluhome/nasqm_flu_t${traj}_r0.out
    rm -rf ${traj}
done

