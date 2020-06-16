from functools import singledispatch
from pynasqm.trajectories.qmground import QmGround
from pynasqm.trajectories.qmexcited import QmExcited
from pynasqm.trajectories.fluorescence import Fluorescence
from pynasqm.trajectories.absorption import Absorption
from pynasqm.trajectories.ppump import PPump
from pynasqm.trajectories.utils import traj_indices, snap_indices

def get_coordinate_files(traj_data):
    if traj_data.user_input.is_hpc:
        return hpc_coordinate_files(traj_data)
    return pc_coordinate_files(traj_data)


@singledispatch
def hpc_coordinate_files(traj_data):
    raise NotImplementedError(f"traj_data type not supported by getambercoordinatefiles\n"\
                              f"{traj_data}")

@hpc_coordinate_files.register(QmGround)
@hpc_coordinate_files.register(QmExcited)
@hpc_coordinate_files.register(PPump)
def _(traj_data):
    return ["snap_for_{}_t${{ID}}_r{}.rst".format(traj_data.job_suffix,
                                                  traj_data.user_input.restart_attempt)]

@hpc_coordinate_files.register(Absorption)
@hpc_coordinate_files.register(Fluorescence)
def _(traj_data):
    return [f"snap_${{i}}_for_{traj_data.job_suffix}_t${{ID}}.rst"]

@singledispatch
def pc_coordinate_files(traj_data):
    raise NotImplementedError(f"traj_data type not supported by getambercoordinatefiles\n"\
                              f"{traj_data}")

@pc_coordinate_files.register(QmGround)
@pc_coordinate_files.register(QmExcited)
@pc_coordinate_files.register(PPump)
def _(traj_data):
    return ["snap_for_{}_t{}_r{}.rst".format(traj_data.job_suffix, traj, traj_data.user_input.restart_attempt)
            for traj in traj_indices(traj_data)]

@pc_coordinate_files.register(Absorption)
@pc_coordinate_files.register(Fluorescence)
def _(traj_data):
    return [f"snap_{snap_id}_for_{traj_data.job_suffix}_t{traj}.rst"
            for traj in traj_indices(traj_data)
            for snap_id in snap_indices(traj_data)]
