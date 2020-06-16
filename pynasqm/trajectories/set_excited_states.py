import os
import numpy as np
from functools import singledispatch
from pynasqm.trajectories.qmexcited import QmExcited
from pynasqm.trajectories.qmground import QmGround
from pynasqm.trajectories.fluorescence import Fluorescence
from pynasqm.trajectories.absorption import Absorption
from pynasqm.trajectories.ppump import PPump
from pynasqm.trajectories.utils import snap_indices, traj_indices
from pynasqm.trajectories.get_reference_job import get_reference_job
from pynasqm.trajectories.get_reference_job import get_n_trajs_of_reference
from pynasqm.trajectories.get_reference_job import get_n_ref_runs
from pynasqm.trajectories.initialexcitedstates import get_n_initial_states_w_laser_energy_and_fwhm

@singledispatch
def set_excited_states(job_data, inputceons):
    raise NotImplementedError("set excited states not implemented for this traj type")

@set_excited_states.register(QmGround)
@set_excited_states.register(Absorption)
@set_excited_states.register(PPump)
def _(job_data, inputceons):
    return inputceons

@set_excited_states.register(QmExcited)
def _(job_data, inputceons):
    print("Setting Initial Excited States")
    if job_data.user_input.restart_attempt > 0:
        print("From Restarts")
        r_attempt = job_data.user_input.restart_attempt
        init_state_info = [get_state_from_restart(r_attempt, traj_id)
                           for traj_id in job_data.traj_indices()]
        init_states = [i[0] for i in init_state_info]
        init_coeffs = [i[1] for i in init_state_info]
    elif doing_laser_excitation(job_data):
        init_states = get_n_initial_states_w_laser_energy_and_fwhm(job_data.number_trajectories,
                                                                    'spectra_abs.input',
                                                                    job_data.user_input.laser_energy,
                                                                    job_data.user_input.fwhm)
    elif job_data.user_input.is_pulse_pump:
        init_states = get_sm_states()
    else:
        init_states = [job_data.user_input.exc_state_init_ex_param for _ in range(job_data.number_trajectories)]
    for inputceon, state in zip(inputceons, init_states):
        inputceon.set_excited_state(state, job_data.user_input.n_exc_states_propagate_ex_param)

    print("Finished Setting Initial Excited States")
    return inputceons

def doing_laser_excitation(job_data):
    return job_data.user_input.exc_state_init_ex_param == -1

def get_state_from_restart(self, restart_attempt, traj_id):
    refference_restart = restart_attempt - 1
    coeffn_file = f"qmexcited/traj_{traj_id}/restart_{refference_restart}/coeff-n.out"
    if os.path.isfile(coeffn_file):
        coeffn_data = open(coeffn_file, 'r').readlines()
        return (int(coeffn_data[-1].split()[0]), coeffn_data[-1].split()[2:-1])
    return (-1, None)

def get_sm_states():
    pulse_pump_text = open("pulse_pump_states.txt").readlines()
    state_data = pulse_pump_text[1:]
    init_states = [int(s.split()[1]) for s in state_data]
    return init_states


@set_excited_states.register(Fluorescence)
def _(job_data, inputceons):
    if not os.path.isfile('connect.dat'):
        return inputceons
    print("Setting Initial Excited States using coeff-n data")
    ref_job = get_reference_job(job_data)
    time_step_fs = job_data.user_input.exc_time_step
    ntpx = job_data.user_input.n_steps_print_emcrd
    times_fs = [time_step_fs * x * ntpx for x in snap_indices(job_data)]
    n_frames = len(times_fs)
    # FIXME: should be for all restarts
    for t, traj in enumerate(traj_indices(job_data)):
        coeff_file = f"{ref_job}/traj_{traj}/restart_0/coeff-n.out"
        init_states = None
        if os.path.isfile(coeff_file):
            coeff_data = np.loadtxt(coeff_file)
            init_states = [int(x[0]) for x in coeff_data if x[1] in times_fs]
            for s, init_state in enumerate(init_states):
                inputindex = t * n_frames + s
                (inputceons[inputindex]).set_excited_state(init_state, job_data.user_input.n_flu_exc)
    return inputceons
