from functools import singledispatch
from pynasqm.trajectories.qmground import QmGround
from pynasqm.trajectories.qmexcited import QmExcited

@singledispatch
def set_initial_input(job_data):
    raise NotImplementedError("Initial Input not Defined for Traj Type")

@set_initial_input.register(QmGround)
def _(job_data):
    input_ceon = job_data.input_ceons[0]
    user_input = job_data.user_input
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
def _(job_data):
    input_ceon = self.input_ceons[0]
    user_input = self.user_input
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
