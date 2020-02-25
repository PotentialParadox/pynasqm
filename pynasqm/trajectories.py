from abc import ABC, abstractmethod
import os.path
import subprocess
from os import mkdir
from pynasqm.closestrunner import ClosestRunner
from pynasqm.solventmaskupdater import SolventMaskUpdater
from pynasqm.nmrmanager import NMRManager, create_dist_file_name, toInputPath
from pynasqm.amber import Amber
import pynasqm.nasqmslurm as nasqm_slurm
from pynasqm.restrictedatoms import RestrictedAtoms
from pynasqm.trajdistance import TrajDistance
from pynasqm.closestreader import ClosestReader
from pynasqm.utils import mkdir, copy_file, is_empty_file
from pynasqm.cpptraj import create_restarts
import pytraj as pt

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
        self._set_initial_input()
        self.gen_inputfiles()
        self._print_header("Running {} Dynamics".format(self._job_suffix))
        (amber, slurm) = self.prepareScript()
        self.runDynamics(amber, slurm)

    def gen_inputfiles(self):
        self.create_restarts_from_parent()
        self.create_inputceon_copies()
        if self._user_input.number_nearest_solvents > 0:
            self._update_nmr_info()

    @abstractmethod
    def islastrun(self):
        pass

    @staticmethod
    def _print_header(header):
        print(50*"*")
        print(15 * " " + header)
        print(50*"*")

    def create_restarts_from_parent(self):
        pass

    def create_inputceon_copies(self):
        inputceons = []
        attempt = self._user_input.restart_attempt
        job = self._job_suffix
        mkdir("{}".format(job))
        for index in self.traj_indices():
            file_name = "{}t{}_r{}.in".format(self._child_root, index, attempt)
            mkdir("{}/traj_{}".format(job, index))
            mkdir("{}/traj_{}/restart_{}".format(job, index, attempt))
            directory = "{}/traj_{}/restart_{}".format(job, index, attempt)
            inputceons.append(self._input_ceons[0].copy(directory, file_name))
        inputceons = self.set_nexmd_seed(inputceons)
        inputceons = self.set_excited_states(inputceons)
        self._input_ceons = inputceons

    def set_nexmd_seed(self, inputceons):
        return inputceons

    def set_excited_states(self, inputceons):
        return inputceons

    @abstractmethod
    def _nmrdirs(self):
        pass

    def should_update_nmr(self):
        return (self._user_input.restart_attempt == 0
                and self._job_suffix == "qmground"
                and self._user_input.restrain_solvents is True
                and self._user_input.number_nearest_solvents > 0)

    def _update_nmr_info(self):
        n_qm_solvents = self._user_input.number_nearest_solvents
        nmrdirs = self._nmrdirs()
        center_mask = self._user_input.mask_for_center
        trajins = self._trajins()
        # self._check_trajins(trajins)
        closest_runner = ClosestRunner(n_qm_solvents, self._number_trajectories,
                                        trajins, center_mask, nmrdirs)
        closest_outputs = closest_runner.create_closest_outputs(run=self.should_update_nmr())
        mask_updater = SolventMaskUpdater(self._input_ceons, self._user_input, closest_outputs)
        mask_updater.update_masks()
        trajins = closest_runner.get_trajins()
        parmtop = "m1.prmtop"
        restricted_atoms = None
        if self.should_update_nmr():
            restricted_atoms = self._get_list_restricted_atoms(parmtop, trajins, closest_outputs)
            distances = self._get_distances(parmtop, trajins, closest_outputs, restricted_atoms[0].nresidues)
            NMRManager(self._input_ceons, closest_outputs, restricted_atoms).update(distances, nmrdirs)
        dist_files = [toInputPath(create_dist_file_name(directory, traj))
                      for (directory, traj) in zip(nmrdirs, range(self._number_trajectories))]
        NMRManager(self._input_ceons, closest_outputs, restricted_atoms, dist_files).update_inputs()

    def _get_distances(self, parmtop, trajins, closest_outputs, nresidues):
        center_mask = self._user_input.mask_for_center
        added_buffer = 0.0
        list_distances = []
        for traj, nmrdir in zip(range(self._number_trajectories), self._nmrdirs()):
            residues = [":{}".format(x) for x in ClosestReader(closest_outputs[traj]).residues]
            trajdist = TrajDistance(parmtop, center_mask)
            distances = [trajdist(trajins[traj], residue, traj, nmrdir) + added_buffer for residue in residues]
            maxdistance = max(distances)
            newdistances = [maxdistance for _ in distances]
            distances = newdistances
            far_distances = [-maxdistance for _ in range(nresidues-len(distances)-1)]
            distances = distances + far_distances
            list_distances.append(distances)
        return list_distances

    @staticmethod
    def _check_trajins(trajins):
        for trajin in trajins:
            if not os.path.isfile(trajin):
                raise RuntimeError(f"{trajin} was not found, make sure you ran the previous step: \n"\
                                   f"mm_ground_state ->  qm_ground_state ->  absorption -> excited_state -> fluorescence\n"\
                                   f"                                    -> pulse_pump \n")

    def _get_list_restricted_atoms(self, parmtop, trajins, closest_outputs):
        center_mask = self._user_input.mask_for_center
        list_restricted_atoms = []
        for traj in range(self._number_trajectories):
            print("Generating restricted atoms list for traj {}".format(traj+1))
            list_restricted_atoms.append(RestrictedAtoms(parmtop, trajins[traj], center_mask,
                                                         closest_outputs[traj]))
        return list_restricted_atoms

    def _trajins(self):
        return [self.restart_path(traj, self._user_input.restart_attempt)
                for traj in range(1, self._number_trajectories+1)]

    def _set_initial_input(self):
        pass

    def runDynamics(self, amber, slurm_file):
        if self._user_input.is_hpc:
            nasqm_slurm.run_nasqm_slurm_file(slurm_file)
        else:
            amber.run_amber(number_processors=self._user_input.processors_per_node,
                            is_ground_state=False)

    def hpc_coordinate_files(self):
        return ["snap_for_{}_t${{ID}}_r{}.rst".format(self._job_suffix,
                                                      self._user_input.restart_attempt)]

    def pc_coordinate_files(self):
        return ["snap_for_{}_t{}_r{}.rst".format(self._job_suffix, traj, self._user_input.restart_attempt)
                for traj in range(1, self._number_trajectories+1)]

    def coordinate_files(self):
        if self._user_input.is_hpc:
            return self.hpc_coordinate_files()
        return self.pc_coordinate_files()

    def prmtop_files(self):
        if self._user_input.is_hpc:
            return ["m1.prmtop"]
        return ["m1.prmtop"] * self._number_trajectories

    def traj_indices(self):
        return range(1, self._number_trajectories+1)

    def _output_directories(self):
        restart = self._user_input.restart_attempt
        job = self._job_suffix
        return ["{}/traj_{}/restart_{}".format(job, traj, restart)
                for traj in self.traj_indices()]

    def create_amber(self):
        amber = Amber()
        roots = None
        restart_attempt = self._user_input.restart_attempt
        if self._user_input.is_hpc:
            roots = ["{}t${{ID}}_r{}".format(self._child_root, restart_attempt)]
            restart_files = ["snap_for_{}_t${{ID}}_r{}.rst".format(self._job_suffix, restart_attempt+1)]
            amber.prmtop_files = ["m1.prmtop"]
        else:
            roots = ["{}t{}_r{}".format(self._child_root, i, restart_attempt)
                     for i in range(1, self._number_trajectories+1)]
            restart_files = ["snap_for_{}_t{}_r{}.rst".format(self._job_suffix, i, restart_attempt+1)
                             for i in range(1, self._number_trajectories+1)]
            amber.prmtop_files = ["m1.prmtop"] * self._number_trajectories
        amber.input_roots = roots
        amber.output_roots = roots
        amber.restart_files = restart_files
        amber.export_roots = roots
        amber.coordinate_files = self.coordinate_files()
        amber.prmtop_files = self.prmtop_files()
        amber.directories = self._output_directories()
        return amber

    def create_slurm(self, amber):
        if self._user_input.is_hpc:
            job_name = self._user_input.job_name + self._job_suffix
            directory = "{}/traj_${{ID}}/restart_{}".format(self._job_suffix, self._user_input.restart_attempt)
            slurm_file = nasqm_slurm.slurm_trajectory_files(self._user_input, amber,
                                                             job_name, self._job_suffix, directory)
        else:
            slurm_file = None
        return slurm_file

    def prepareScript(self):
        amber = self.create_amber()
        slurm_files = self.create_slurm(amber)
        return amber, slurm_files

    @abstractmethod
    def _restart_name(self, index):
        pass

    def _trajectory_name(self, index):
        if index == -1:
            index = 0
        return "{}{}".format(self._child_root, index+1)


    def _create_directories(self):
        job = self._job_suffix
        mkdir("{}".format(job))
        for i in range(1, self._number_trajectories + 1):
            directory = "{}/traj_{}".format(job, i)
            restart_directory = "{}/traj_{}/restart_{}".format(job, i,
                                                               self._user_input.restart_attempt)
            nmr_directory = "{}/traj_{}/nmr".format(job, i)
            mkdir(directory)
            mkdir(restart_directory)
            mkdir(nmr_directory)

    def start_from_restart(self, override):
        restart = self._user_input.restart_attempt
        job = self._job_suffix
        for traj in range(1, self._number_trajectories+1):
            source_path = "{}/traj_{}/restart_{}/snap_for_{}_t{}_r{}.rst".format(job, traj,
                                                                                 restart-1,
                                                                                 job,
                                                                                 traj,
                                                                                 restart)
            output_path = "{}/traj_{}/restart_{}/snap_for_{}_t{}_r{}.rst".format(job, traj,
                                                                                 restart,
                                                                                 job,
                                                                                 traj,
                                                                                 restart)
            if os.path.isfile(source_path) and not is_empty_file(source_path):
                create_restarts(source_path, output_path, override=override)
            if os.path.isfile(source_path) and is_empty_file(source_path):
                copy_file(source_path, output_path, override)

    def restart_path(self, trajectory, restart):
        return "{}/traj_{}/restart_{}/snap_for_{}_t{}_r{}.rst".format(self._job_suffix,
                                                                      trajectory, restart,
                                                                      self._job_suffix,
                                                                      trajectory, restart)

def combine_trajectories(suffix, n_trajs, n_runs):
    prmtop = "m1.prmtop"
    print ("-------- Combining Trajectories --------")
    if not os.path.isfile("m1.prmtop"):
        raise RuntimeError("m1.prmtop file not found while attempting to combine trajectories")
    for traj_id in range(1, n_trajs+1):
        combined = "combined" if iscombined(suffix, traj_id) else "uncombined"
        completed = "completed" if iscompleted(suffix, traj_id, n_runs) else "uncompleted"
        print ("Traj {} {} while previously {}".format(traj_id, completed, combined))
        if iscompleted(suffix, traj_id, n_runs):
            print("traj {} is completed".format(traj_id))
        else:
            print("traj {} is not completed".format(traj_id))
        if iscombined(suffix, traj_id):
            print("traj {} is already combined".format(traj_id))
        else:
            print("traj {} is not combined".format(traj_id))
        if iscompleted(suffix, traj_id, n_runs):
            trajs = ["{}/traj_{}/restart_{}/nasqm_{}_t{}_r{}.nc".format(suffix, traj_id, restart,
                                                                        suffix, traj_id, restart)
                     for restart in range(n_runs)]
            traj = pt.load(trajs, top=prmtop)
            pt.io.write_traj("{}/traj_{}/nasqm_{}_{}.nc".format(suffix, traj_id, suffix, traj_id),
                             traj, velocity=True, overwrite=True)
            subprocess.call(['rm'] + trajs)

def iscompleted(suffix, traj_id, n_runs):
    n_restarts = n_runs - 1
    restart_filename = "{}/traj_{}/restart_{}/snap_for_{}_t{}_r{}.rst".format(suffix, traj_id, n_restarts,
                                                                              suffix, traj_id, n_runs)
    traj_filename = "{}/traj_{}/restart_{}/nasqm_{}_t{}_r{}.nc".format(suffix, traj_id, n_restarts,
                                                                          suffix, traj_id, n_restarts)
    return os.path.isfile(restart_filename) and os.path.isfile(traj_filename)


def iscombined(suffix, traj_id):
    return os.path.isfile("{}/traj_{}/nasqm_{}_{}.nc".format(suffix, traj_id, suffix, traj_id))
