from pynasqm.nmrwriter import NMRWriter

class NMRSingleSingle(NMRWriter):

    def __init__(self, restricted_atom1, restricted_atom2, desired_distance):
        self._restricted_atom1 = restricted_atom1[0]
        self._restricted_atom2 = restricted_atom2[0]
        self._peak_number = 0
        self._spectrum_number = 0
        self._force_positions = self._default_positions(desired_distance)
        self._force_constants = self._default_constants()


    def _atom_indexes_string(self):
        return "iat={},{},\n".format(self._restricted_atom1, self._restricted_atom2)
