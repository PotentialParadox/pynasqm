from pynasqm.nmrsinglesingle import NMRSingleSingle
from pynasqm.nmrsinglegroup import NMRSingleGroup
from pynasqm.nmrgroupsingle import NMRGroupSingle
from pynasqm.nmrgroupgroup import NMRGroupGroup

class NMRWriterFactory:

    def __init__(self, restricted_atoms1, restricted_atoms2, desired_distance):
        self._restricted_atoms1 = restricted_atoms1
        self._restricted_atoms2 = restricted_atoms2
        self._desired_distance = desired_distance

    def get_writer(self):
        if self._is_singlesingle():
            return NMRSingleSingle(self._restricted_atoms1, self._restricted_atoms2,
                                   self._desired_distance)
        if self._is_singlegroup():
            return NMRSingleGroup(self._restricted_atoms1, self._restricted_atoms2,
                                  self._desired_distance)
        if self._is_groupsingle():
            return NMRSingleGroup(self._restricted_atoms1, self._restricted_atoms2,
                                  self._desired_distance)
        if self._is_groupgroup():
            return NMRSingleGroup(self._restricted_atoms1, self._restricted_atoms2,
                                  self._desired_distance)

    def _is_singlesingle(self):
        return len(self._restricted_atoms1[0]) == 1 and len(self._restricted_atoms2[0]) == 1

    def _is_singlegroup(self):
        return len(self._restricted_atoms1[0]) == 1 and len(self._restricted_atoms2[0]) > 1

    def _is_groupsingle(self):
        return len(self._restricted_atoms1[0]) > 1 and len(self._restricted_atoms2[0]) == 1

    def _is_groupgroup(self):
        return len(self._restricted_atoms1[0]) > 1 and len(self._restricted_atoms2[0]) > 1
