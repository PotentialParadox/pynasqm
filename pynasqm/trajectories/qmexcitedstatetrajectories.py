import os
from random import randint
from pynasqm.utils import copy_files, mkdir
from pynasqm.trajectories.trajectories import Trajectories
import pynasqm.cpptraj as nasqm_cpptraj
from pynasqm.initialexcitedstates import get_n_initial_states_w_laser_energy_and_fwhm
from pynasqm.inputceon import InputCeon
from pynasqm.trajectories.qmexcited import QmExcited

class QmExcitedStateTrajectories(Trajectories):

    def __init__(self, user_input, input_ceon):
        self.user_input = user_input
        self.input_ceons = [input_ceon]
        self.number_trajectories = user_input.n_snapshots_ex
        self.child_root = 'nasqm_qmexcited_'
        self.job_suffix = 'qmexcited'
        self.parent_restart_root = 'nasqm_qmground_'
        self.amber_restart = True
        self.traj_data = QmExcited(user_input, input_ceon)

    def restart_name(self, index):
        if index == -1:
            return "{}{}.rst".format(self.parent_restart_root, 1)
        return "{}{}.rst".format(self.parent_restart_root, index+1)

    def doing_laser_excitation(self):
        return self.user_input.exc_state_init_ex_param == -1

    def isrestarting(self):
        return self.user_input.restart_attempt < self.user_input.n_exc_runs - 1

    def islastrun(self):
        return not self.isrestarting()


    def set_excited_states(self, input_ceons):
        print("Setting Initial Excited States")
        if self.doing_laser_excitation():
            init_states = get_n_initial_states_w_laser_energy_and_fwhm(self.number_trajectories,
                                                                       'spectra_abs.input',
                                                                       self.user_input.laser_energy,
                                                                       self.user_input.fwhm)
        elif self.user_input.is_pulse_pump:
            init_states = self.get_sm_states()
        else:
            init_states = [self.user_input.exc_state_init_ex_param for _ in range(self.number_trajectories)]
        for inputceon, state in zip(input_ceons, init_states):
            inputceon.set_excited_state(state, self.user_input.n_exc_states_propagate_ex_param)

        print("Finished Setting Initial Excited States")
        return input_ceons

    def get_sm_states(self):
        pulse_pump_text = open("pulse_pump_states.txt").readlines()
        state_data = pulse_pump_text[1:]
        init_states = [int(s.split()[1]) for s in state_data]
        return init_states

    def set_nexmd_seed(self, inputceons):
        print("Setting NEXMD Random Seeds")
        random_seeds = [randint(1,10000) for i in range(len(inputceons))]
        for inputceon, seed in zip(inputceons, random_seeds):
            inputceon.set_nexmd_seed(seed)
        return inputceons

    def nmrdirs(self):
        return ["qmexcited/traj_{}/nmr".format(i) for i in range(1, self.number_trajectories+1)]

    @staticmethod
    def is_atleast(min_value, test):
        if min_value is None:
            return True
        return test >= min_value

    @staticmethod
    def is_atmost(max_value, test):
        if max_value is None:
            return True
        return test >= max_value

    def satisfies_pulse_pump(self, restraints, muab_for_sm):
        return is_atleast(restraints.min_energy, muab_for_sm.energy) \
            and is_atmost(restraints.max_energy, muab_for_sm.energy) \
            and is_atleast(restraints.min_strength, muab_for_sm.strength)
