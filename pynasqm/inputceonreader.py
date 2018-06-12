import re
import numpy as np
from pynasqm.fortran_nml import FortranNml

class InputceonReader:
    def __init__(self, filename):
        self._filename = filename
        self.qmmm = self._readqmmm()
        self.moldyn = self._readmoldyn()
        self.coords = self._readcoords()
        self.velocities = self._readvelocities()
        self.coeffs = self._readcoeffs()

    def _readqmmm(self):
        nml = FortranNml('qmmm')
        nml.get_fortran_nml(self._filename)
        return nml

    def _readmoldyn(self):
        nml = FortranNml('moldyn')
        nml.get_fortran_nml(self._filename)
        return nml

    def _readcoords(self):
        coord_block = FortranNml('coord').get_block_string(self._filename)
        array = []
        for line in coord_block:
            ls = line.split()
            array.append([int(ls[0]), float(ls[1]), float(ls[2]), float(ls[3])])
        return array

    def  _readvelocities(self):
        v_block = FortranNml('veloc').get_block_string(self._filename)
        array = []
        for line in v_block:
            ls = line.split()
            array.append([float(x) for x in ls])
        return array

    def _readcoeffs(self):
        c_block = FortranNml('coeff').get_block_string(self._filename)
        array = []
        for line in c_block:
            ls = line.split()
            array.append([float(x) for x in ls])
        return array
