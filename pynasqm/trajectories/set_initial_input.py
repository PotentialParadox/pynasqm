from functools import singledispatch
from pynasqm.trajectories.qmground import QmGround
from pynasqm.trajectories.qmexcited import QmExcited
from pynasqm.trajectories.absorption import Absorption
from pynasqm.trajectories.fluorescence import Fluorescence
from pynasqm.trajectories.ppump import PPump

@singledispatch
def set_initial_input(traj_data):
    raise NotImplementedError(f"Initial Input not Defined for Traj Type\n"\
                              f"{traj_data}")

@set_initial_input.register(QmGround)
def _(traj_data):
    input_ceon = traj_data.input_ceons[0]
    user_input = traj_data.user_input
    input_ceon.set_n_steps(user_input.n_steps_per_run_qmground)
    input_ceon.set_n_steps_to_mcrd(user_input.n_steps_print_qmgmcrd)
    input_ceon.set_quantum(True)
    input_ceon.set_excited_state(0, user_input.n_qmground_exc)
    input_ceon.set_n_steps_to_print(user_input.n_steps_to_print_qmground)
    input_ceon.set_verbosity(1)
    input_ceon.set_time_step(user_input.qmground_time_step)
    input_ceon.set_random_velocities(False)
    input_ceon.calc_transition_dipoles(False)
    input_ceon.set_istully(False, 0)

@set_initial_input.register(QmExcited)
def _(traj_data):
    input_ceon = traj_data.input_ceons[0]
    user_input = traj_data.user_input
    input_ceon.set_quantum(True)
    input_ceon.set_n_steps(user_input.n_steps_per_run_exc)
    input_ceon.set_n_steps_to_mcrd(user_input.n_steps_print_emcrd)
    input_ceon.set_excited_state(user_input.exc_state_init_ex_param,
                                 user_input.n_exc_states_propagate_ex_param)
    input_ceon.set_n_steps_to_print(user_input.n_steps_to_print_exc)
    input_ceon.set_verbosity(1)
    input_ceon.set_time_step(user_input.exc_time_step)
    input_ceon.set_random_velocities(False)
    input_ceon.calc_transition_dipoles(False)
    input_ceon.set_istully(user_input.is_tully, user_input.qsteps)

@set_initial_input.register(Absorption)
def _(traj_data):
    input_ceon = traj_data.input_ceons[0]
    user_input = traj_data.user_input
    input_ceon.set_n_steps(0)
    input_ceon.set_n_steps_to_mcrd(0)
    input_ceon.set_quantum(True)
    input_ceon.set_excited_state(0, user_input.n_abs_exc)
    input_ceon.set_n_steps_to_print(1)
    input_ceon.set_verbosity(1)
    input_ceon.set_time_step(user_input.qmground_time_step)
    input_ceon.set_random_velocities(False)
    input_ceon.calc_transition_dipoles(False)
    input_ceon.set_istully(False, 0)

@set_initial_input.register(Fluorescence)
def _(traj_data):
    input_ceon = traj_data.input_ceons[0]
    user_input = traj_data.user_input
    input_ceon.set_n_steps(0)
    input_ceon.set_n_steps_to_mcrd(0)
    input_ceon.set_quantum(True)
    input_ceon.set_excited_state(1, user_input.n_flu_exc)
    input_ceon.set_n_steps_to_print(1)
    input_ceon.set_verbosity(1)
    input_ceon.set_time_step(user_input.exc_time_step)
    input_ceon.set_random_velocities(False)
    input_ceon.calc_transition_dipoles(False)
    input_ceon.set_istully(False, 0)

@set_initial_input.register(PPump)
def _(traj_data):
    input_ceon = traj_data.input_ceons[0]
    user_input = traj_data.user_input
    input_ceon.set_quantum(True)
    input_ceon.set_n_steps(0)
    input_ceon.set_n_steps_to_mcrd(user_input.n_steps_print_emcrd)
    n_states_to_prop = user_input.n_pulsepump_excited_states
    input_ceon.set_excited_state(1, n_states_to_prop)
    input_ceon.set_n_steps_to_print(user_input.n_steps_to_print_exc)
    input_ceon.set_verbosity(1)
    input_ceon.set_time_step(user_input.qmground_time_step)
    input_ceon.set_random_velocities(False)
    input_ceon.set_istully(False, user_input.qsteps)
    input_ceon.calc_transition_dipoles(True)
    user_input.walltime="01:00:00" # This calculation does not take a lot of time
