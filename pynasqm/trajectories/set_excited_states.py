from functools import singledispatch
from pynasqm.trajectories.qmexcited import QmExcited
from pynasqm.trajectories.qmground import QmGround
from pynasqm.trajectories.fluorescence import Fluorescence
from pynasqm.trajectories.absorption import Absorption
from pynasqm.trajectories.ppump import PPump
from pynasqm.trajectories.utils import snap_indices

@singledispatch
def set_excited_states(job_data, inputceons):
    raise NotImplementedError("set excited states not implemented for this traj type")

@set_excited_states.register(QmGround)
@set_excited_states.register(Absorption)
def _(job_data, inputceons):
    return inputceons

@set_excited_states.register(QmExcited)
def _(job_data, inputceons):
    print("Setting Initial Excited States")
    if job_data._user_input.restart_attempt > 0:
        print("From Restarts")
        r_attempt = job_data._user_input.restart_attempt
        init_states = [job_data.get_state_from_restart(r_attempt, traj_id)
                        for traj_id in job_data.traj_indices()]
    elif job_data.doing_laser_excitation():
        init_states = get_n_initial_states_w_laser_energy_and_fwhm(job_data._number_trajectories,
                                                                    'spectra_abs.input',
                                                                    job_data._user_input.laser_energy,
                                                                    job_data._user_input.fwhm)
    elif job_data._user_input.is_pulse_pump:
        init_states = job_data.get_sm_states()
    else:
        init_states = [job_data._user_input.exc_state_init_ex_param for _ in range(job_data._number_trajectories)]
    for inputceon, state in zip(inputceons, init_states):
        inputceon.set_excited_state(state, job_data._user_input.n_exc_states_propagate_ex_param)

    print("Finished Setting Initial Excited States")
    return input_ceons

@set_excited_states.register(Fluorescence)
def _(job_data, inputceons):
    total_time_fs = job_data.user_input.exc_run_time * 1000
    time_step_fs = job_data.user_input.exc_time_step
    ntpx = job_data.user_input.n_steps_print_emcrd
    n_frames = (total_time_fs / time_step_fs) / ntpx
    times_fs = [time_step_fs * x * ntpx for x in snap_indices(job_data)]
    return inputceons
