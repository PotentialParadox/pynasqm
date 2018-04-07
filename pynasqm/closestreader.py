import numpy as np
import re
import subprocess

class ClosestReader:
    '''
    Manages the usage of closest commands via cpptraj
    '''

    def __init__(self, closest_output):
        self.closest_output = self._to_stream(closest_output)
        self.atoms = None
        self.residues = None
        self._read_closest()

    @staticmethod
    def _to_stream(possible_string):
        if isinstance(possible_string, str):
            return open(possible_string, 'r')
        return possible_string

    def _read_closest(self):
        '''
        Read the residue ID's of the nearest solvents to
        the molecule of interest
        '''
        closest_array = self._construct_closest_arrary()
        self._update_atoms(closest_array)
        self._update_residues(closest_array)

    def _update_atoms(self, closest_array):
        self.atoms = closest_array[:, 3].astype(int)

    def _update_residues(self, closest_array):
        self.residues = closest_array[:, 1].astype(int)

    def _construct_closest_arrary(self):
        closest_file = self.closest_output.read()
        closest_file = self._remove_first_line(closest_file)
        closest_array = np.fromstring(closest_file, sep=' ')
        return self._reshape_array(closest_array)

    @staticmethod
    def _reshape_array(array):
        length = int(len(array))
        columns = 4
        rows = int(length / columns)
        return np.reshape(array, (rows, columns))

    @staticmethod
    def _remove_first_line(file_string):
        post_string = ""
        for line in file_string.split("\n")[1:]:
            post_string += line + "\n"
        return post_string
