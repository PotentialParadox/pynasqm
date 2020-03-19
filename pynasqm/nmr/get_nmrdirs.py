from functools import singledispatch
from pynasqm.trajectories.qmground import QmGround

@singledispatch
def get_nmrdirs(traj_data):
    raise NotImplementedError("No NMR Directories given for this traj type")

@get_nmrdirs.register(QmGround)
def _(traj_data):
    return ["qmground/traj_{}/nmr".format(i) for i in range(1, traj_data.number_trajectories+1)]
