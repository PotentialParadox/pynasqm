from abc import ABC, abstractmethod
import os.path
from pynasqm.closestrunner import ClosestRunner
from pynasqm.solventmaskupdater import SolventMaskUpdater
from pynasqm.nmrmanager import NMRManager
from pynasqm.amber import Amber
import pynasqm.nasqmslurm as nasqm_slurm
from pynasqm.restrictedatoms import RestrictedAtoms
from pynasqm.trajdistance import TrajDistance
from pynasqm.closestreader import ClosestReader

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
        self._print_header("Running Dynamics")
        if self._user_input.is_hpc:
            self._run_on_hpc()
        else:
            self._run_on_pc()

    @staticmethod
    def _print_header(header):
        print(50*"*")
        print(15 * " " + header)
        print(50*"*")

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
            trajins = self._trajins()
            self._check_trajins(trajins)
            closest_runner = ClosestRunner(n_qm_solvents, self._number_trajectories,
                                           trajins, center_mask)
            closest_outputs = closest_runner.create_closest_outputs()
            mask_updater = SolventMaskUpdater(self._input_ceons, self._user_input, closest_outputs)
            mask_updater.update_masks()
            if self._user_input.restrain_solvents is True:
                trajins = closest_runner.get_trajins()
                parmtop = "m1.prmtop"
                restricted_atoms = self._get_list_restricted_atoms(parmtop, trajins, closest_outputs)
                distances = self._get_distances(parmtop, trajins, closest_outputs)
                NMRManager(self._input_ceons, closest_outputs, restricted_atoms, distances).update()

    def _get_distances(self, parmtop, trajins, closest_outputs):
        center_mask = self._user_input.mask_for_center
        added_buffer = 0.2
        list_distances = []
        for traj in range(self._number_trajectories):
            residues = [":{}".format(x) for x in ClosestReader(closest_outputs[traj]).residues]
            trajdist = TrajDistance(parmtop, center_mask)
            distances = [trajdist(trajins[traj], residue, traj) + added_buffer for residue in residues]
            list_distances.append(distances)
        return list_distances

    @staticmethod
    def _check_trajins(trajins):
        for trajin in trajins:
            if not os.path.isfile(trajin):
                raise RuntimeError("{} was not found, make sure you ran the previous step: \n"\
                                   "ground_state->absorption->fluorescence".format(trajin))

    def _get_list_restricted_atoms(self, parmtop, trajins, closest_outputs):
        center_mask = self._user_input.mask_for_center
        list_restricted_atoms = []
        for traj in range(self._number_trajectories):
            list_restricted_atoms.append(RestrictedAtoms(parmtop, trajins[traj], center_mask,
                                                         closest_outputs[traj]))
        return list_restricted_atoms

    @abstractmethod
    def _trajins(self):
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

    @abstractmethod
    def _restart_name(self, index):
        pass

    def _trajectory_name(self, index):
        if index == -1:
            index = 0
        return "{}{}".format(self._child_root, index+1)
