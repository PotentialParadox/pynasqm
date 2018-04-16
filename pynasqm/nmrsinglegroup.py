from pynasqm.nmrwriter import NMRWriter

class NMRSingleGroup(NMRWriter):

    def __init__(self, restricted_atom1, restricted_atoms2, desired_distance):
        self._restricted_atom1 = restricted_atom1[0]
        self._restricted_atom2 = restricted_atoms2
        self._spectrum_number = 0
        self._force_positions = self._default_positions(desired_distance)
        self._force_constants = self._default_constants()

    def _atom_indexes_string(self):
        index_string = "iat={},-1,\n".format(self._restricted_atom1)
        index_string += "igr1=-1, igr2={}\n".format(self._list_atoms())
        return index_string

    def _list_atoms(self):
        list_string = ""
        for atom in self._restricted_atom2:
            list_string += "{},".format(atom)
        return list_string
