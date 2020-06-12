from functools import singledispatch
from pynasqm.trajectories.qmground import QmGround
from pynasqm.trajectories.qmexcited import QmExcited
from pynasqm.trajectories.fluorescence import Fluorescence
from pynasqm.trajectories.absorption import Absorption
from pynasqm.trajectories.utils import traj_indices, snap_indices

@singledispatch
def amber_pc_restart_files(traj_data, restart_attempt):
    raise NotImplementedError(f"traj_data type not supported by amber_pc_restart_files\n"\
                              f"{traj_data}")
@amber_pc_restart_files.register(QmGround)
@amber_pc_restart_files.register(QmExcited)
def _(traj_data, restart_attempt):
    return ["snap_for_{}_t{}_r{}.rst".format(traj_data.job_suffix, i, restart_attempt+1)
            for i in traj_indices(traj_data)]
@amber_pc_restart_files.register(Absorption)
@amber_pc_restart_files.register(Fluorescence)
def _(traj_data, restart_attempt):
    return [f"snap_{snap_id}_for_{traj_data.job_suffix}_t{traj}.rst"
            for traj in traj_indices(traj_data)
            for snap_id in snap_indices(traj_data)]

@singledispatch
def amber_hpc_restart_files(traj_data, restart_attempt):
    raise NotImplementedError(f"traj_data type not supported by amber_hpc_restart_files\n"\
                              f"{traj_data}")
@amber_hpc_restart_files.register(QmGround)
@amber_hpc_restart_files.register(QmExcited)
def _(traj_data, restart_attempt):
    return ["snap_for_{}_t${{ID}}_r{}.rst".format(traj_data.job_suffix, restart_attempt+1)]
@amber_hpc_restart_files.register(Absorption)
@amber_hpc_restart_files.register(Fluorescence)
def _(traj_data, restart_attempt):
    return [f"snap_${{i}}_for_fluorescence_t${{ID}}.rst"]
