from functools import singledispatch
from pynasqm.trajectories.qmground import QmGround
from pynasqm.trajectories.fluorescence import Fluorescence
from pynasqm.trajectories.absorption import Absorption
from pynasqm.trajectories.ppump import PPump

@singledispatch
def set_excited_states(job_data, inputceons):
    raise NotImplementedError("set excited states not implemented for this traj type")

@set_excited_states.register(QmGround)
@set_excited_states.register(Fluorescence)
@set_excited_states.register(Absorption)
def _(job_data, inputceons):
    return inputceons
