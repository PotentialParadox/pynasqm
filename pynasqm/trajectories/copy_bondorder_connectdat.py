import os
from functools import singledispatch
from pynasqm.trajectories.qmground import QmGround
from pynasqm.trajectories.qmexcited import QmExcited
from pynasqm.trajectories.ppump import PPump
from pynasqm.trajectories.fluorescence import Fluorescence
from pynasqm.trajectories.absorption import Absorption
from pynasqm.trajectories.get_reference_job import get_reference_job
from pynasqm.trajectories.get_reference_job import get_n_trajs_of_reference
from pynasqm.trajectories.get_reference_job import get_n_ref_runs
from pynasqm.trajectories.utils import traj_indices, snap_indices
from pynasqm.utils import copy_file

@singledispatch
def copy_bondorder_connectdat(traj_data):
    raise NotImplementedError(f"traj_data type not supported by create_restarts\n"\
                              f"{traj_data}")

@copy_bondorder_connectdat.register(QmGround)
@copy_bondorder_connectdat.register(PPump)
def _(traj_data):
    pass

@copy_bondorder_connectdat.register(QmExcited)
def _(traj_data):
    if not os.path.isfile('connect.dat'):
        return
    directories = [f"qmexcited/traj_{traj}/restart_0"
                   for traj in traj_indices(traj_data)]
    for d in directories:
        copy_file('connect.dat', d, force=True)

@copy_bondorder_connectdat.register(Absorption)
@copy_bondorder_connectdat.register(Fluorescence)
def _(traj_data):
    if not os.path.isfile('connect.dat'):
        return
    ref_job = get_reference_job(traj_data)
    job = traj_data.job_suffix
    n_ref_trajs = get_n_trajs_of_reference(traj_data)
    n_ref_runs = get_n_ref_runs(traj_data)
    directories = [f"{job}/traj_{traj}/{snap_id}"
                   for traj in traj_indices(traj_data)
                   for snap_id in snap_indices(traj_data)]
    for d in directories:
        copy_file('connect.dat', d, force=True)

