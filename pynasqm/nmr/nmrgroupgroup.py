from pynasqm.nmr.nmrwriter import NMRWriter

class NMRGroupGroup(NMRWriter):

    def __init__(self, restricted_atoms1, restricted_atoms2, desired_distance):
        self._restricted_atoms1 = restricted_atoms1
        self._restricted_atoms2 = restricted_atoms2
        self._spectrum_number = 0
        self._force_constants = self._default_constants(desired_distance)
        self._force_positions = self._default_positions(desired_distance)

    def _atom_indexes_string(self, atoms1, atoms2):
        index_string = "iat=-1,-1,\n".format(atoms2[0])
        index_string += "igr1={} igr2={}\n".format(self._list_atoms(atoms1),
                                                  self._list_atoms(atoms2))
        return index_string
