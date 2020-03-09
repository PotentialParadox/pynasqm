from pynasqm.trajectories import Trajectories
from pynasqm.amber import Amber
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
        self._n_snapshots_per_trajectory = self.snaps_per_trajectory()
        self._amber_restart = False

    def snaps_per_trajectory(self):
        n_frames = self._number_frames_in_parent
        run_time = self._user_input.qmground_run_time
        time_delay = self._user_input.absorption_time_delay/1000
        return int(n_frames * ( 1 - time_delay/run_time))

    def _set_initial_input(self):
        input_ceon = self._input_ceons[0]
        user_input = self._user_input
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

    def create_slurm(self, amber):
        if self._user_input.is_hpc:
            job_name = self._user_input.job_name + self._job_suffix
            directory = "{}/traj_${{ID}}/${{i}}".format(self._job_suffix, self._user_input.restart_attempt)
            slurm_file = nasqm_slurm.slurm_trajectory_files(self._user_input, amber,
                                                            job_name, self._job_suffix,
                                                            directory,
                                                            self._n_snapshots_per_trajectory
                                                            )
        else:
            slurm_file = None
        return slurm_file

    def isrestarting(self):
        '''
        Snapshots should never restart
        '''
        return False

    def islastrun(self):
        return not self.isrestarting()

    def start_from_qmground(self):
        combine_trajectories("qmground", self._user_input.n_snapshots_qmground, self._user_input.n_qmground_runs)
        qmground_trajs = [f"qmground/traj_{traj}/nasqm_qmground_{traj}.nc"
                          for traj in range(1, self._number_trajectories+1)]
        outputs = [f"abs/traj_{traj}/qmground_t{traj}_snap" for traj in range(1, self._number_trajectories+1)]
        self._check_trajins(qmground_trajs)
        restart_step = 1
        for trajin, output in zip(qmground_trajs, outputs):
            nasqm_cpptraj.create_restarts(amber_inputfile=trajin, start=self.cpptraj_start_index(),
                                          output=output, step=restart_step)
        self._move_restarts()

    def cpptraj_start_index(self):
        n_frames = self._number_frames_in_parent
        return n_frames - self._n_snapshots_per_trajectory

    def create_restarts_from_parent(self, override=True):
        self._create_directories()
        self.start_from_qmground()
        job = self._job_suffix
        mkdir("{}".format(job))

    def prepareScript(self):
        amber = self.create_amber()
        slurm_files = self.create_slurm(amber)
        return amber, slurm_files

    def create_amber(self):
        amber = Amber()
        roots = None
        restart_attempt = self._user_input.restart_attempt
        if self._user_input.is_hpc:
            roots = [f"nasqm_abs_t${{ID}}_${{i}}"]
            restart_files = [f"snap_${{i}}_for_absorption_t${{ID}}_back.rst"]
            amber.prmtop_files = ["m1.prmtop"]
        else:
            roots = [f"nasqm_abs_t{traj}_{snap_id}"
                     for traj in self.traj_indices()
                     for snap_id in self.snap_indices()]
            restart_files = [f"snap_{snap_id}_for_absorption_t{traj}_back.rst"
                             for traj in self.traj_indices()
                             for snap_id in self.snap_indices()]
            amber.prmtop_files = ["m1.prmtop"] * len(roots)
        amber.input_roots = roots
        amber.output_roots = roots
        amber.restart_files = restart_files
        amber.export_roots = roots
        amber.coordinate_files = self.abs_coordinate_files()
        amber.directories = self._output_directories()
        return amber

    def hpc_abs_coordinate_files(self):
        return [f"snap_${{i}}_for_absorption_t${{ID}}.rst"]

    def abs_coordinate_files(self):
        if self._user_input.is_hpc:
            return self.hpc_abs_coordinate_files()
        return self.pc_abs_coordinate_files()

    def pc_abs_coordinate_files(self):
        return [f"snap_{snap_id}_for_absorption_t{traj}.rst"
                for traj in self.traj_indices()
                for snap_id in self.snap_indices()]

    def _output_directories(self):
        restart = self._user_input.restart_attempt
        job = self._job_suffix
        return [f"abs/traj_{traj}/{snap_id}"
                for traj in self.traj_indices()
                for snap_id in self.snap_indices()]

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

    def create_inputceon_copies(self):
        inputceons = []
        attempt = self._user_input.restart_attempt
        job = self._job_suffix
        directories = [f"abs/traj_{traj}/{snap_id}"
                       for traj in self.traj_indices()
                       for snap_id in self.snap_indices()]
        file_names = [f"nasqm_abs_t{traj}_{snap_id}.in"
                       for traj in self.traj_indices()
                       for snap_id in self.snap_indices()]
        for directory, file_name in zip(directories, file_names):
            mkdir(directory)
            inputceons.append(self._input_ceons[0].copy(directory, file_name))
        inputceons = self.set_nexmd_seed(inputceons)
        inputceons = self.set_excited_states(inputceons)
        self._input_ceons = inputceons

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

    def _update_nmr_info(self):
        pass

