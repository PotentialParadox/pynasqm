from functools import singledispatch
from pynasqm.trajectories.qmground import QmGround
from pynasqm.trajectories.qmexcited import QmExcited

@singledispatch
def get_nmrdirs(traj_data):
    raise NotImplementedError("No NMR Directories given for this traj type: {traj_data}")

@get_nmrdirs.register(QmGround)
@get_nmrdirs.register(QmExcited)
def _(traj_data):
    return [f"{traj_data.job_suffix}/traj_{traj}/nmr" for traj in range(1, traj_data.number_trajectories+1)]

