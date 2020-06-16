from functools import singledispatch
from pynasqm.trajectories.qmground import QmGround
from pynasqm.trajectories.qmexcited import QmExcited
from pynasqm.trajectories.fluorescence import Fluorescence
from pynasqm.trajectories.absorption import Absorption
from pynasqm.trajectories.ppump import PPump

@singledispatch
def set_nexmd_seed(job_data, inputceons):
    raise NotImplementedError(f"set nexmd seed not implemented for this traj type\n"
                              f"{job_data}")

@set_nexmd_seed.register(QmGround)
@set_nexmd_seed.register(QmExcited)
@set_nexmd_seed.register(Fluorescence)
@set_nexmd_seed.register(PPump)
@set_nexmd_seed.register(Absorption)
def _(job_data, inputceons):
    return inputceons
