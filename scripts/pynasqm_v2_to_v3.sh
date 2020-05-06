##########################
# Convert Abs to qmground
##########################
# Convert the Directories
if [ ! -d "qmground" ];then
    mv abs qmground
fi
# Convert the files
for infile in `ls qmground/traj_*/restart*/*abs*`;do
    if [ -f ${infile} ];then
        mv ${infile} ${infile//abs/qmground}
    fi
done
# Convert the files
for infile in `ls qmground/traj_*/*abs*.nc`;do
    if [ -f ${infile} ];then
        mv ${infile} ${infile//abs/qmground}
    fi
done

##########################
# Convert Flu to qmexcited
##########################
# Convert the Directories
if [ ! -d "qmexcited" ];then
    mv flu qmexcited
fi
# Convert the files
for infile in `ls qmexcited/traj_*/restart*/*flu*`;do
    if [ -f ${infile} ];then
        mv ${infile} ${infile//flu/qmexcited}
    fi
done
# Convert the files
for infile in `ls qmexcited/traj_*/*flu*.nc`;do
    if [ -f ${infile} ];then
        mv ${infile} ${infile//flu/qmexcited}
    fi
done
##########################
# Convert Pynasqm.in File
##########################
sed -i 's/run_absorption_trajectories/run_qmground_trajectories/' pynasqm.in
sed -i 's/n_snapshots_gs/n_snapshots_qmground/' pynasqm.in
sed -i 's/abs_traj_index_file/qmground_traj_index_file/' pynasqm.in
sed -i 's/abs_run_time/qmground_run_time/' pynasqm.in
sed -i 's/abs_time_step/qmground_time_step/' pynasqm.in
sed -i 's/n_abs_runs/n_qmground_runs/' pynasqm.in
sed -i 's/n_steps_to_print_amcrd/n_steps_to_print_qmgmcrd/' pynasqm.in
sed -i 's/n_steps_to_print_abs/n_steps_to_print_qmground/' pynasqm.in
