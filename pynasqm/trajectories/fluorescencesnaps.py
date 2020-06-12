from pynasqm.trajectories.trajectories import Trajectories
from pynasqm.amber import Amber
from pynasqm.trajectories.combine_trajectores import combine_trajectories
import pynasqm.cpptraj as nasqm_cpptraj
import pytraj as pt
import pynasqm.nasqmslurm as nasqm_slurm
from pynasqm.utils import mkdir
from pynasqm.trajectories.fluorescence import Fluorescence
import os

import subprocess

class FluorescenceSnaps(Trajectories):

    def __init__(self, user_input, input_ceon):
        self.user_input = user_input
        self.input_ceons = [input_ceon]
        self.number_trajectories = user_input.n_snapshots_ex
        self.child_root = 'nasqm_flu_'
        self.job_suffix = 'flu'
        self.parent_restart_root = 'nasqm_qmexcited'
        self.number_frames_in_parent = user_input.n_mcrd_frames_per_run_qmexcited * user_input.n_exc_runs
        self.n_snapshots_per_trajectory = self.snaps_per_trajectory()
        self.amber_restart = False
        self.traj_data = Fluorescence(user_input, input_ceon)

    def snaps_per_trajectory(self):
        n_frames = self.number_frames_in_parent
        run_time = self.user_input.exc_run_time
        time_delay = self.user_input.fluorescence_time_delay/1000
        return int(n_frames * ( 1 - time_delay/run_time))




