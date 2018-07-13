import re

from pynasqm.fortran_nml import FortranNml

class AmberInputReader:

    def __init__(self, filename):
        self._filename = filename
        self.header = self._header()
        self.cntrl = self._cntrl()
        self.qmmm = self._qmmm()
        self.wt = self._wt()
        # self.disang = self._disang()

    def _header(self):
        return open(self._filename, 'r').readlines()[0]

    def _cntrl(self):
        return self._get_nml('cntrl')

    def _get_nml(self, nml):
        nml = FortranNml(nml)
        nml.get_fortran_nml(self._filename)
        return nml

    def _qmmm(self):
        return self._get_nml('qmmm')

    def _wt(self):
        return self._get_nml('wt')

    def _disang(self):
        p_disang = re.compile(r'DISANG\s*=*')
        search_result = None
        with open(self._filename, 'r') as filein:
            search_result = re.findall(p_disang, filein)
        return search_result[0]

    def _dumpave(self):
        p_dumpave = re.compile(r'DUMPAVE\s*=*')
        search_result = None
        with open(self._filename, 'r') as filein:
            search_result = re.findall(p_dumpave, filein)
        return search_result[0]
