import re
from pynasqm.closestreader import ClosestReader
from pynasqm.nmrwriter import NMRWriter

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
            restricted_atoms = self._get_restricted_atoms(closest_output)
            desired_distance = self._get_max_distance(closest_output)
            if desired_distance > 12:
                raise ValueError("Desired distance greater than 12, "\
                                 "possibly to many nearest solvent")
            file_name = self._create_dist_file_name(trajectory)
            self._dist_files.append(file_name)
            NMRWriter(restricted_atoms, desired_distance).write_to(file_name)

    def update_inputs(self):
        for trajectory in range(self._number_trajectories):
            self._input_ceons[trajectory].set_nmr_directory(self._dist_files[trajectory])

    @staticmethod
    def _get_max_distance(closest_output):
        reader = ClosestReader(closest_output)
        distances = reader.distances
        return distances[-1] + 0.2

    @staticmethod
    def _create_dist_file_name(index):
        return "rst_{}.dist".format(index+1)

    def _get_restricted_atoms(self, closest_output):
        closest_atom = self._get_closest_atom(closest_output)
        atom_of_interest_mask = self._user_input.mask_for_center
        atom_of_interest = self._extract_atom_from_mask(atom_of_interest_mask)
        return [atom_of_interest, closest_atom]

    @staticmethod
    def _extract_atom_from_mask(mask):
        if mask[0] != '@':
            raise AttributeError("Mask for center must refer to an atom "\
                                 "for restricted dynamics")
        return mask[1:]

    @staticmethod
    def _get_closest_atom(closest_output):
        reader = ClosestReader(closest_output)
        atoms = reader.atoms
        return atoms[0]


    def _get_number_trajectories(self):
        n_trajs = len(self._input_ceons)
        if len(self._closest_outputs) != n_trajs:
            raise AttributeError("number of input_ceon must equal number of" \
                                 "closest outputs")
        return n_trajs
