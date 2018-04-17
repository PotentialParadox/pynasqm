import re
from pynasqm.closestreader import ClosestReader
from pynasqm.nmrwriterfactory import NMRWriterFactory

class NMRManager:

    def __init__(self, input_ceons, user_input, closest_outputs, dist_files=[]):
        self._input_ceons = input_ceons
        self._user_input = user_input
        self._closest_outputs = closest_outputs
        self._number_trajectories = self._get_number_trajectories()
        self._dist_files = dist_files

    def update(self):
        self.write_dist_files()
        self.update_inputs()

    def write_dist_files(self):
        for trajectory in range(self._get_number_trajectories()):
            closest_output = self._closest_outputs[trajectory]
            restricted_atoms1 = self._get_restricted_solute_atoms()
            restricted_atoms2 = self._get_restricted_solvent_atoms(closest_output)
            desired_distance = self._get_max_distance(closest_output)
            if desired_distance > 12:
                raise ValueError("Desired distance greater than 12, "\
                                 "possibly to many nearest solvent")
            file_name = self._create_dist_file_name(trajectory)
            self._dist_files.append(file_name)
            nmrfactory = NMRWriterFactory(restricted_atoms1, restricted_atoms2, desired_distance)
            nmrwriter = nmrfactory.get_writer()
            nmrwriter.write_to(file_name)

    def update_inputs(self):
        for trajectory in range(self._number_trajectories):
            self._input_ceons[trajectory].set_nmr_directory(self._dist_files[trajectory])

    def _get_restricted_solute_atoms(self):
        atoms_of_interest_mask = self._user_input.mask_for_center
        atoms_of_interest = self._extract_atom_from_mask(atoms_of_interest_mask)
        return [atoms_of_interest] * self._user_input.number_nearest_solvents

    @staticmethod
    def _get_max_distance(closest_output):
        reader = ClosestReader(closest_output)
        distances = reader.distances
        return distances[-1] + 0.2

    @staticmethod
    def _create_dist_file_name(index):
        return "rst_{}.dist".format(index+1)

    @staticmethod
    def _extract_atom_from_mask(mask):
        if mask[0] != '@':
            raise AttributeError("Mask for center must refer to an atom "\
                                 "for restricted dynamics")
        return [mask[1:]]

    @staticmethod
    def _get_restricted_solvent_atoms(closest_output):
        reader = ClosestReader(closest_output)
        residues = reader.residues
        return [[atoms[0]]]


    def _get_number_trajectories(self):
        n_trajs = len(self._input_ceons)
        if len(self._closest_outputs) != n_trajs:
            raise AttributeError("number of input_ceon must equal number of" \
                                 "closest outputs")
        return n_trajs
