from abc import ABC, abstractmethod
from pynasqm.closestrunner import ClosestRunner
from pynasqm.solventmaskupdater import SolventMaskUpdater
from pynasqm.nmrmanager import NMRManager
from pynasqm.amber import Amber
import pynasqm.nasqmslurm as nasqm_slurm

class Trajectories(ABC):

    def __init__(self, user_input, input_ceon, number_trajectories=1):
        self._user_input = user_input
        self._input_ceons = [input_ceon]
        self._number_trajectories = number_trajectories
        self._child_root = "undefined_root"
        self._job_suffix = "undefined_job_suffix"
        self._parent_restart_root = "undefined_parent_root"
        self._amber_restart = True

    def run(self):
        self._create_restarts_from_parent()
        self._create_inputceon_copies()
        self._update_input_files()
        if self._user_input.is_hpc:
            self._run_on_hpc()
        else:
            self._run_on_pc()

    @abstractmethod
    def _create_restarts_from_parent(self):
        pass

    def _create_inputceon_copies(self):
        input_ceons = []
        for index in range(1, self._number_trajectories+1):
            file_name = "{}{}.in".format(self._child_root, index)
            input_ceons.append(self._input_ceons[0].copy(file_name))
        self._input_ceons = input_ceons

    def _update_input_files(self):
        n_qm_solvents = self._user_input.number_nearest_solvents
        if n_qm_solvents > 0:
            center_mask = self._user_input.mask_for_center
            closest_runner = ClosestRunner(n_qm_solvents, self._number_trajectories,
                                           center_mask)
            self._update_trajins(closest_runner)
            closest_outputs = closest_runner.create_closest_outputs()
            mask_updater = SolventMaskUpdater(self._input_ceons, self._user_input, closest_outputs)
            mask_updater.update_masks()
            if self._user_input.restrain_solvents is True:
                trajins = closest_runner.get_trajins()
                parmtop = 'm1.prmtop'
                NMRManager(self._input_ceons, self._user_input, closest_outputs).update()

    def _update_trajins(self, closest_runner):
        pass

    def _run_on_hpc(self):
        amber = Amber()
        amber.input_roots = [self._child_root]
        amber.output_roots = [self._child_root]
        amber.coordinate_files = [self._parent_restart_root]
        amber.from_restart = self._amber_restart
        job_name = self._user_input.job_name + self._job_suffix
        slurm_files = nasqm_slurm.slurm_trajectory_files(self._user_input, amber,
                                                         job_name, self._number_trajectories)
        nasqm_slurm.run_nasqm_slurm_files(slurm_files)

    def _run_on_pc(self):
        (snap_restarts, trajectory_roots) = self._create_restarts_and_trajectories()
        amber = Amber()
        amber.input_roots = trajectory_roots
        amber.output_roots = trajectory_roots
        amber.coordinate_files = snap_restarts
        amber.prmtop_files = ["m1.prmtop"]*len(trajectory_roots)
        amber.restart_roots = trajectory_roots
        amber.export_roots = trajectory_roots
        amber.run_amber(self._user_input.processors_per_node)

    def _create_restarts_and_trajectories(self):
        snap_restarts = []
        trajectory_roots = []
        if self._number_trajectories == 1:
            snap_restarts.append(self._restart_name(-1))
            trajectory_roots.append(self._trajectory_name(-1))
        else:
            for i in range(self._number_trajectories):
                snap_restarts.append(self._restart_name(i))
                trajectory_roots.append(self._trajectory_name(i))
        return snap_restarts, trajectory_roots

    def _restart_name(self, index):
        if index == -1:
            index = 1
        return "{}{}.rst".format(self._parent_restart_root, index+1)

    def _trajectory_name(self, index):
        if index == -1:
            index = 1
        return "{}{}".format(self._child_root, index+1)
