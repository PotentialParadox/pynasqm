from pynasqm.trajectories import Trajectories
import pynasqm.cpptraj as nasqm_cpptraj
from pynasqm.initialexcitedstates import get_n_initial_states_w_laser_energy_and_fwhm

class FluTrajectories(Trajectories):

    def __init__(self, user_input, input_ceon):
        self._user_input = user_input
        self._input_ceons = [input_ceon]
        self._number_trajectories = user_input.n_snapshots_ex
        self._child_root = 'nasqm_flu_'
        self._job_suffix = 'Flu'
        self._parent_restart_root = 'nasqm_abs_'
        self._amber_restart = True

    def _restart_name(self, index):
        if index == -1:
            return "{}{}.rst".format(self._parent_restart_root, 1)
        return "{}{}.rst".format(self._parent_restart_root, index+1)

    def _trajins(self):
        trajs = self._number_trajectories
        return ["{}/nasqm_abs_{}.rst".format(traj, traj)
                for traj in range(1, trajs+1)]

    def doing_laser_excitation(self):
        return self._user_input.exc_state_init_ex_param == -1

    def _set_initial_input(self):
        input_ceon = self._input_ceons[0]
        user_input = self._user_input
        input_ceon.set_quantum(True)
        input_ceon.set_n_steps(user_input.n_steps_exc)
        input_ceon.set_n_steps_to_mcrd(user_input.n_steps_print_emcrd)
        input_ceon.set_excited_state(user_input.exc_state_init_ex_param,
                                     user_input.n_exc_states_propagate_ex_param)
        input_ceon.set_n_steps_to_print(user_input.n_steps_to_print_exc)
        input_ceon.set_verbosity(1)
        input_ceon.set_time_step(user_input.time_step)
        input_ceon.set_random_velocities(False)
        input_ceon.set_bo(user_input.is_tully, user_input.qsteps)

    def _create_inputceon_copies(self):
        input_ceons = []
        for index in range(1, self._number_trajectories+1):
            file_name = "{}{}.in".format(self._child_root, index)
            input_ceons.append(self._input_ceons[0].copy("{}/".format(index), file_name))
        init_states = None
        if self.doing_laser_excitation():
            init_states = get_n_initial_states_w_laser_energy_and_fwhm(self._number_trajectories,
                                                                       'spectra_abs.input',
                                                                       self._user_input.laser_energy,
                                                                       self._user_input.fwhm)
        else:
            init_states = [self._user_input.exc_state_init_ex_param for _ in range(self._number_trajectories)]
        for inputceon, state in zip(input_ceons, init_states):
            inputceon.set_excited_state(state, self._user_input.n_exc_states_propagate_ex_param)
        self._input_ceons = input_ceons

    def hpc_coordinate_files(self):
        return ["nasqm_abs_${ID}.rst"]

    def pc_coordinate_files(self):
        return ["nasqm_abs_{}.rst".format(traj)
                for traj in range(1, self._number_trajectories+1)]
