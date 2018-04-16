from pynasqm.nmrwriter import NMRWriter

class NMRSingleSingle(NMRWriter):

    def __init__(self, restricted_atoms1, restricted_atoms2, desired_distance):
        self._restricted_atoms1 = restricted_atoms1
        self._restricted_atoms2 = restricted_atoms2
        self._peak_number = 0
        self._spectrum_number = 0
        self._force_positions = self._default_positions(desired_distance)
        self._force_constants = self._default_constants()


    def _atom_indexes_string(self, atom1, atom2):
        return "iat={},{},\n".format(atom1[0], atom2[0])
