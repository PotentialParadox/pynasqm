from functools import singledispatch
from pynasqm.trajectories.qmground import QmGround

@singledispatch
def set_excited_states(job_data, inputceons):
    raise NotImplementedError("set excited states not implemented for this traj type")

@set_excited_states.register(QmGround)
def _(job_data, inputceons):
    return inputceons
