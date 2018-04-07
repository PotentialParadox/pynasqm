class NMRWriter:

    def __init__(self, restricted_atoms, desired_distance):
        self._restricted_atoms = restricted_atoms
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
        file_string += "ixpk={}, nxpk={}, iat={},{},\n".format(self._peak_number,
                                                               self._spectrum_number,
                                                               self._restricted_atoms[0],
                                                               self._restricted_atoms[1])
        file_string += "r1={:.2f}, r2={:.2f}, r3={:.2f}, r4={:.2f},\n".format(self._force_positions[0],
                                                                              self._force_positions[1],
                                                                              self._force_positions[2],
                                                                              self._force_positions[3])
        file_string += "rk2={:.1f}, rk3={:.1f},\n".format(self._force_constants[0],
                                                          self._force_constants[1])
        file_string += "/\n"
        return file_string

    def write_to(self, file_name):
        file_string = self._create_string()
        open(file_name, 'w').write(file_string)
