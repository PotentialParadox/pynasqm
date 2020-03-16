from pynasqm.trajectories.trajectories import Trajectories
from pynasqm.amber import Amber
from pynasqm.trajectories.combine_trajectores import combine_trajectories
from pynasqm.trajectories.utils import check_trajins
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

    def set_initial_input(self):
        input_ceon = self.input_ceons[0]
        user_input = self.user_input
        input_ceon.set_n_steps(0)
        input_ceon.set_n_steps_to_mcrd(0)
        input_ceon.set_quantum(True)
        input_ceon.set_excited_state(0, user_input.n_flu_exc)
        input_ceon.set_n_steps_to_print(1)
        input_ceon.set_verbosity(1)
        input_ceon.set_time_step(user_input.exc_time_step)
        input_ceon.set_random_velocities(False)
        input_ceon.calc_transition_dipoles(True)
        input_ceon.set_istully(False, 0)

    def create_slurm(self, amber):
        if self.user_input.is_hpc:
            job_name = self.user_input.job_name + self.job_suffix
            directory = "{}/traj_${{ID}}/${{i}}".format(self.job_suffix, self.user_input.restart_attempt)
            slurm_file = nasqm_slurm.slurm_trajectory_files(self.user_input, amber,
                                                            job_name, self.job_suffix,
                                                            directory,
                                                            self.n_snapshots_per_trajectory
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

    def start_from_qmexcited(self):
        combine_trajectories("qmexcited", self.user_input.n_snapshots_ex, self.user_input.n_exc_runs)
        qmexcited_trajs = [f"qmexcited/traj_{traj}/nasqm_qmexcited_{traj}.nc"
                          for traj in range(1, self.number_trajectories+1)]
        outputs = [f"flu/traj_{traj}/qmexcited_t{traj}_snap" for traj in range(1, self.number_trajectories+1)]
        check_trajins(qmexcited_trajs)
        restart_step = 1
        for trajin, output in zip(qmexcited_trajs, outputs):
            nasqm_cpptraj.create_restarts(amber_inputfile=trajin, start=self.cpptraj_start_index(),
                                          output=output, step=restart_step)
        self.move_restarts()

    def cpptraj_start_index(self):
        n_frames = self.number_frames_in_parent
        return n_frames - self.n_snapshots_per_trajectory + 1

    def create_restarts_from_parent(self, override=True):
        self.create_directories()
        self.start_from_qmexcited()
        job = self.job_suffix
        mkdir("{}".format(job))

    def prepareScript(self):
        amber = self.create_amber()
        slurm_files = self.create_slurm(amber)
        return amber, slurm_files

    def create_amber(self):
        amber = Amber()
        roots = None
        restart_attempt = self.user_input.restart_attempt
        if self.user_input.is_hpc:
            roots = [f"nasqm_flu_t${{ID}}_${{i}}"]
            restart_files = [f"snap_${{i}}_for_fluorescence_t${{ID}}_back.rst"]
            amber.prmtop_files = ["m1.prmtop"]
        else:
            roots = [f"nasqm_flu_t{traj}_{snap_id}"
                     for traj in self.traj_indices()
                     for snap_id in self.snap_indices()]
            restart_files = [f"snap_{snap_id}_for_fluorescence_t{traj}_back.rst"
                             for traj in self.traj_indices()
                             for snap_id in self.snap_indices()]
            amber.prmtop_files = ["m1.prmtop"] * len(roots)
        amber.input_roots = roots
        amber.output_roots = roots
        amber.restart_files = restart_files
        amber.export_roots = roots
        amber.coordinate_files = self.flu_coordinate_files()
        amber.directories = self.output_directories()
        return amber

    def hpc_flu_coordinate_files(self):
        return [f"snap_${{i}}_for_fluorescence_t${{ID}}.rst"]

    def flu_coordinate_files(self):
        if self.user_input.is_hpc:
            return self.hpc_flu_coordinate_files()
        return self.pc_flu_coordinate_files()

    def pc_flu_coordinate_files(self):
        return [f"snap_{snap_id}_for_fluorescence_t{traj}.rst"
                for traj in self.traj_indices()
                for snap_id in self.snap_indices()]

    def output_directories(self):
        restart = self.user_input.restart_attempt
        job = self.job_suffix
        return [f"flu/traj_{traj}/{snap_id}"
                for traj in self.traj_indices()
                for snap_id in self.snap_indices()]

    def create_directories(self):
        directories = [f"flu/traj_{traj}" for traj in range(1, self.number_trajectories+1)]
        for directory in directories:
            mkdir(directory)

    def move_restarts(self):
        directories = [f"flu/traj_{traj}/{snap_id}"
                       for traj in range(1, self.number_trajectories+1)
                       for snap_id in self.snap_indices()]
        for directory in directories:
            mkdir(directory)
        for inputfile, outputfile in zip(self.initial_snaps(), self.final_snaps()):
            subprocess.call(['mv', inputfile, outputfile])

    def initial_snaps(self):
        if self.n_snapshots_per_trajectory == 1:
            return [f'flu/traj_{traj}/qmexcited_t{traj}_snap'
                    for traj in self.traj_indices()]
        return [f'flu/traj_{traj}/qmexcited_t{traj}_snap.{snap_id}'
                for traj in self.traj_indices()
                for snap_id in self.snap_indices()]

    def final_snaps(self):
        if self.n_snapshots_per_trajectory == 1:
            return [f'flu/traj_{traj}/1/snap_1_for_fluorescence_t{traj}.rst'
                    for traj in self.traj_indices()]
        return [f'flu/traj_{traj}/{snap_id}/snap_{snap_id}_for_fluorescence_t{traj}.rst'
                for traj in self.traj_indices()
                for snap_id in self.snap_indices()]

    def snap_indices(self):
        return range(1,self.n_snapshots_per_trajectory+1)

    def restart_name(self, index):
        if index == -1:
            return self.parent_restart_root
        return "{}.{}".format(self.parent_restart_root, index+1)


    def hpc_coordinate_files(self):
        return ["snap_for_flu_t${{ID}}_r{}.rst".format(self.user_input.restart_attempt)]

    def pc_coordinate_files(self):
        return ["snap_for_flu_t{}_r{}.rst".format(i, self.user_input.restart_attempt)
                for i in range(1, self.number_trajectories+1)]

    def nmrdirs(self):
        return ["flu/traj_{}/nmr".format(i) for i in range(1, self.number_trajectories+1)]

    def _update_nmr_info(self):
        pass

