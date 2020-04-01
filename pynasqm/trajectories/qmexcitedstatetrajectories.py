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

