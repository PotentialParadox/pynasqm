from functools import singledispatch
from pynasqm.trajectories.qmground import QmGround

@singledispatch
def set_nexmd_seed(job_data, inputceons):
    raise NotImplementedError("set nexmd seed not implemented for this traj type")

@set_nexmd_seed.register(QmGround)
def _(job_data, inputceons):
    return inputceons
