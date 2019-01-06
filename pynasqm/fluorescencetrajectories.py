from pynasqm.trajectories import Trajectories
import pynasqm.cpptraj as nasqm_cpptraj
from pynasqm.initialexcitedstates import get_n_initial_states_w_laser_energy_and_fwhm

class FluTrajectories(Trajectories):

    def __init__(self, user_input, input_ceon):
        self._user_input = user_input
        self._input_ceons = [input_ceon]
        self._number_trajectories = user_input.n_snapshots_ex
        self._child_root = 'nasqm_flu_'
        self._job_suffix = '_f_'
        self._parent_restart_root = 'nasqm_abs_'
        self._amber_restart = True

    def _restart_name(self, index):
        if index == -1:
            return "{}{}.rst".format(self._parent_restart_root, 1)
        return "{}{}.rst".format(self._parent_restart_root, index+1)

    def _trajins(self):
        trajins = []
        for i in range(1, self._number_trajectories +1):
            trajins.append("{}/{}{}.rst".format(i, self._parent_restart_root, i))
        return trajins

    def doing_laser_excitation(self):
        return self._user_input.exc_state_init_ex_param == -1

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

    def _update_input_files(self):
        n_qm_solvents = self._user_input.number_nearest_solvents
        if n_qm_solvents > 0:
            center_mask = self._user_input.mask_for_center
            trajins = self._trajins()
            self._check_trajins(trajins)
            closest_outputs = ["{}/closest_{}.txt".format(traj, traj)
                               for traj in range(1, self._number_trajectories)]
            mask_updater = SolventMaskUpdater(self._input_ceons, self._user_input, closest_outputs)
            mask_updater.update_masks()
            if self._user_input.restrain_solvents is True:
                trajins = closest_runner.get_trajins()
                parmtop = "m1.prmtop"
                restricted_atoms = self._get_list_restricted_atoms(parmtop, trajins, closest_outputs)
                distances = self._get_distances(parmtop, trajins, closest_outputs, restricted_atoms[0].nresidues)
                NMRManager(self._input_ceons, closest_outputs, restricted_atoms, distances).update()


