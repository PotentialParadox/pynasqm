from functools import singledispatch
from pynasqm.trajectories.qmground import QmGround
from pynasqm.trajectories.qmexcited import QmExcited
from pynasqm.trajectories.ppump import PPump

@singledispatch
def get_nmrdirs(traj_data):
    raise NotImplementedError(f"No NMR Directories given for this traj type: {traj_data}")

@get_nmrdirs.register(QmGround)
@get_nmrdirs.register(QmExcited)
@get_nmrdirs.register(PPump)
def _(traj_data):
    return [f"{traj_data.job_suffix}/traj_{traj}/nmr" for traj in range(1, traj_data.number_trajectories+1)]

