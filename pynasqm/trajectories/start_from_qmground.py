import os
from functools import singledispatch
from pynasqm.utils import mkdir, copy_files, is_empty_file
from pynasqm.trajectories.utils import traj_indices

def start_from_qmground(traj_data, override):
    copy_restarts_from_qmground(traj_data, override)
    if traj_data.user_input.restrain_solvents:
        copy_nmr_from_qmground(traj_data)

def copy_nmr_from_qmground(traj_data):
    source_files = ["qmground/traj_{}/nmr/rst_{}.dist".format(t, t) for t in traj_indices(traj_data)]
    output_files = [f"{traj_data.job_suffix}/traj_{t}/nmr/rst_{t}.dist" for t in traj_indices(traj_data)]
    copy_files(source_files, output_files)
    source_files = ["qmground/traj_{}/nmr/closest_{}.txt".format(t, t) for t in traj_indices(traj_data)]
    output_files = [f"{traj_data.job_suffix}/traj_{t}/nmr/closest_{t}.txt" for t in traj_indices(traj_data)]
    copy_files(source_files, output_files)

def copy_restarts_from_qmground(traj_data, override):
    test_for_qmground()
    r = traj_data.user_input.n_qmground_runs - 1
    source_files = ["qmground/traj_{}/restart_{}/snap_for_qmground_t{}_r{}.rst".format(t, r, t, r+1)
                    for t in traj_indices(traj_data)]
    output_files = ["{1}/traj_{0}/restart_0/snap_for_{1}_t{0}_r0.rst".format(t, traj_data.job_suffix)
                    for t in traj_indices(traj_data)]
    copy_files(source_files, output_files, force=override)


def test_for_qmground():
    if not os.path.isdir("qmground"):
        raise AssertionError("qmground directory not found.\n"\
                                "Did you run the QM ground-state trajectories?\n")
