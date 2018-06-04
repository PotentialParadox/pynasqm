import numpy as np
from pynasqm.fortran_nml import get_fortran_nml

class InputceonReader:
    def __init__(self, filename):
        self._filename = filename
        self.coords = self._readcoords()
        self.velocities = self._readvelocities()
        self.coeffs = self._readcoeffs()


    def _readcoords(self):
        coord_block = get_fortran_nml(self._filename, 'coord')
        array = []
        for line in coord_block:
            ls = line.split()
            array.append([int(ls[0]), float(ls[1]), float(ls[2]), float(ls[3])])
        return array

    def  _readvelocities(self):
        v_block = get_fortran_nml(self._filename, 'veloc')
        array = []
        for line in v_block:
            ls = line.split()
            array.append([float(x) for x in ls])
        return array

    def _readcoeffs(self):
        c_block = get_fortran_nml(self._filename, 'coeff')
        array = []
        for line in c_block:
            ls = line.split()
            array.append([float(x) for x in ls])
        return array
