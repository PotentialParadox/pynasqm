from pynasqm.nmrwriter import NMRWriter

class NMRGroupGroup(NMRWriter):

    def __init__(self, restricted_atoms1, restricted_atoms2, desired_distance):
        self._restricted_atoms1 = restricted_atoms1
        self._restricted_atoms2 = restricted_atoms2
        self._spectrum_number = 0
        self._force_positions = self._default_positions(desired_distance)
        self._force_constants = self._default_constants()

    def _atom_indexes_string(self):
        index_string = "igr1={} igr2={}\n".format(self._list_atoms(self._restricted_atoms1),
                                                  self._list_atoms(self._restricted_atoms2))
        return index_string

    def _list_atoms(self, atoms):
        list_string = ""
        for atom in atoms:
            list_string += "{},".format(atom)
        return list_string
