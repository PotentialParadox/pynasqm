from pynasqm.trajectories import Trajectories
from pynasqm.trajectories import combine_trajectories
import pynasqm.cpptraj as nasqm_cpptraj
import pytraj as pt
import pynasqm.nasqmslurm as nasqm_slurm
from pynasqm.utils import mkdir
import os

import subprocess

class AbsorptionSnaps(Trajectories):

    def __init__(self, user_input, input_ceon):
        self._user_input = user_input
        self._input_ceons = [input_ceon]
        self._number_trajectories = user_input.n_snapshots_qmground
        self._child_root = 'nasqm_abs_'
        self._job_suffix = 'abs'
        self._parent_restart_root = 'nasqm_qmground'
        self._number_frames_in_parent = user_input.n_mcrd_frames_per_run_qmground * user_input.n_qmground_runs
        self._n_snapshots_per_trajectory = self._number_frames_in_parent
        self._amber_restart = False

    def _set_initial_input(self):
        input_ceon = self._input_ceons[0]
        user_input = self._user_input
        input_ceon.set_n_steps(user_input.n_steps_abs)
        input_ceon.set_n_steps_to_mcrd(user_input.n_steps_print_qmgmcrd)
        input_ceon.set_quantum(True)
        input_ceon.set_excited_state(0, user_input.n_abs_exc)
        input_ceon.set_n_steps_to_print(user_input.n_steps_to_print_abs)
        input_ceon.set_verbosity(1)
        input_ceon.set_time_step(user_input.time_step)
        input_ceon.set_random_velocities(False)
        input_ceon.calc_transition_dipoles(False)
        input_ceon.set_istully(False, 0)

    def isrestarting(self):
        '''
        Snapshots should never restart
        '''
        return False

    def islastrun(self):
        return not self.isrestarting()

    '''
    FIXME: Should ignore the time to equilibrate and retrieve from qmground
    '''
    def start_from_qmground(self):
        combine_trajectories("qmground", self._user_input.n_snapshots_qmground, self._user_input.n_qmground_runs)
        qmground_trajs = [f"qmground/traj_{traj}/nasqm_qmground_{traj}.nc"
                          for traj in range(1, self._number_trajectories+1)]
        outputs = [f"abs/traj_{traj}/qmground_t{traj}_snap" for traj in range(1, self._number_trajectories+1)]
        self._check_trajins(qmground_trajs)
        restart_step = 1
        for trajin, output in zip(qmground_trajs, outputs):
            nasqm_cpptraj.create_restarts(amber_inputfile=trajin,
                                          output=output, step=restart_step)
        self._move_restarts()

    def create_restarts_from_parent(self, override=True):
        print(self._number_frames_in_parent)
        self._create_directories()
        self.start_from_qmground()
        job = self._job_suffix
        mkdir("{}".format(job))

    def _create_directories(self):
        directories = [f"abs/traj_{traj}" for traj in range(1, self._number_trajectories+1)]
        for directory in directories:
            mkdir(directory)

    def _move_restarts(self):
        directories = [f"abs/traj_{traj}/{snap_id}"
                       for traj in range(1, self._number_trajectories+1)
                       for snap_id in self.snap_indices()]
        for directory in directories:
            mkdir(directory)
        for inputfile, outputfile in zip(self._initial_snaps(), self._final_snaps()):
            subprocess.call(['mv', inputfile, outputfile])

    def _initial_snaps(self):
        if self._n_snapshots_per_trajectory == 1:
            return [f'abs/traj_{traj}/qmground_t{traj}_snap'
                    for traj in self.traj_indices()]
        return [f'abs/traj_{traj}/qmground_t{traj}_snap.{snap_id}'
                for traj in self.traj_indices()
                for snap_id in self.snap_indices()]

    def _final_snaps(self):
        if self._n_snapshots_per_trajectory == 1:
            return [f'abs/traj_{traj}/1/snap_1_for_absorption_t{traj}.rst'
                    for traj in self.traj_indices()]
        return [f'abs/traj_{traj}/{snap_id}/snap_{snap_id}_for_absorption_t{traj}.rst'
                for traj in self.traj_indices()
                for snap_id in self.snap_indices()]

    def snap_indices(self):
        return range(1,self._n_snapshots_per_trajectory+1)

    def _restart_name(self, index):
        if index == -1:
            return self._parent_restart_root
        return "{}.{}".format(self._parent_restart_root, index+1)


    def hpc_coordinate_files(self):
        return ["snap_for_abs_t${{ID}}_r{}.rst".format(self._user_input.restart_attempt)]

    def pc_coordinate_files(self):
        return ["snap_for_abs_t{}_r{}.rst".format(i, self._user_input.restart_attempt)
                for i in range(1, self._number_trajectories+1)]

    def _nmrdirs(self):
        return ["abs/traj_{}/nmr".format(i) for i in range(1, self._number_trajectories+1)]


