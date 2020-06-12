from functools import singledispatch
from pynasqm.trajectories.fluorescence import Fluorescence
from pynasqm.trajectories.absorption import Absorption

@singledispatch
def get_reference_job(traj_data):
    raise NotImplementedError(f"traj_data type not supported by get_refer\n"\
                              f"{traj_data}")
@get_reference_job.register(Fluorescence)
def _(traj_data):
    return "qmexcited"
@get_reference_job.register(Absorption)
def _(traj_data):
    return "qmground"

@singledispatch
def get_n_trajs_of_reference(traj_data):
    raise NotImplementedError(f"traj_data type not supported by get_ntrajs_of_reference\n"\
                              f"{traj_data}")
@get_n_trajs_of_reference.register(Fluorescence)
def _(traj_data):
    return traj_data.user_input.n_snapshots_ex
@get_n_trajs_of_reference.register(Absorption)
def _(traj_data):
    return traj_data.user_input.n_snapshots_qmground

@singledispatch
def get_n_ref_runs(traj_data):
    raise NotImplementedError(f"traj_data type not supported by get_nref_runs\n"\
                              f"{traj_data}")
@get_n_ref_runs.register(Fluorescence)
def _(traj_data):
    return traj_data.user_input.n_exc_runs
@get_n_ref_runs.register(Absorption)
def _(traj_data):
    return traj_data.user_input.n_qmground_runs
