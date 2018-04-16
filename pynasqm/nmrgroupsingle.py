from pynasqm.nmrwriter import NMRWriter

class NMRGroupSingle(NMRWriter):

    def __init__(self, restricted_atoms1, restricted_atom2, desired_distance):
        self._restricted_atom1 = restricted_atoms1
        self._restricted_atom2 = restricted_atom2[0]
        self._spectrum_number = 0
        self._force_positions = self._default_positions(desired_distance)
        self._force_constants = self._default_constants()

    def _atom_indexes_string(self):
        index_string = "iat=-1,{},\n".format(self._restricted_atom2)
        index_string += "igr1={} igr2=-1,\n".format(self._list_atoms())
        return index_string

    def _list_atoms(self):
        list_string = ""
        for atom in self._restricted_atom1:
            list_string += "{},".format(atom)
        return list_string
