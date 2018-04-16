from abc import ABC, abstractmethod

class NMRWriter(ABC):

    def __init__(self, restricted_atoms1, restricted_atoms2, desired_distance):
        self._restricted_atoms1 = restricted_atoms1
        self._restricted_atoms1 = restricted_atoms2
        self._peak_number = 0
        self._spectrum_number = 0
        self._force_positions = self._default_positions(desired_distance)
        self._force_constants = self._default_constants()

    def _default_positions(self, desired_distance):
        return [1, 2, desired_distance, 12]

    def _default_constants(self):
        return [0, 200]

    def _create_string(self):
        file_string = "&rst\n"
        file_string += self._atom_indexes_string()
        file_string += self._postions_string()
        file_string += self._force_constants_string()
        file_string += "/\n"
        return file_string

    def _postions_string(self):
        return "r1={:.2f}, r2={:.2f}, r3={:.2f}, r4={:.2f},\n".format(self._force_positions[0],
                                                                     self._force_positions[1],
                                                                     self._force_positions[2],
                                                                     self._force_positions[3])

    def _force_constants_string(self):
        return "rk2={:.1f}, rk3={:.1f},\n".format(self._force_constants[0], self._force_constants[1])

    @abstractmethod
    def _atom_indexes_string(self):
        pass


    def write_to(self, file_name):
        file_string = self._create_string()
        open(file_name, 'w').write(file_string)
