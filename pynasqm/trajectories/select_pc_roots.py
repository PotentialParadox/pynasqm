from functools import singledispatch
from pynasqm.trajectories.qmground import QmGround
from pynasqm.trajectories.qmexcited import QmExcited
from pynasqm.trajectories.ppump import PPump
from pynasqm.trajectories.fluorescence import Fluorescence
from pynasqm.trajectories.absorption import Absorption
from pynasqm.trajectories.utils import traj_indices, snap_indices

@singledispatch
def select_pc_roots(traj_data, restart_attempt):
    raise NotImplementedError(f"traj_data type not supported by select_pc_roots\n"\
                              f"{traj_data}")

@select_pc_roots.register(QmGround)
@select_pc_roots.register(QmExcited)
@select_pc_roots.register(PPump)
def _(traj_data, restart_attempt):
    return ["{}t{}_r{}".format(traj_data.child_root, i, restart_attempt)
            for i in traj_indices(traj_data)]

@select_pc_roots.register(Fluorescence)
@select_pc_roots.register(Absorption)
def _(traj_data, restart_attempt):
    return [f"{traj_data.child_root}t{traj_id}_{snap_id}"
            for traj_id in traj_indices(traj_data)
            for snap_id in snap_indices(traj_data)]
