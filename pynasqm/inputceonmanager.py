import numpy as np
from pynasqm.inputceonreader import InputceonReader
from pynasqm.inputceonwriter import InputceonWriter

class InputceonManager:

    def __init__(self, filename):
        self._filename = filename
        self._reader = InputceonReader(filename)
        self.qmmm = self._reader.qmmm
        self.moldyn = self._reader.moldyn
        self.coords = self._reader.coords
        self.velocities = self._reader.velocities
        self.coeffs = self._reader.coeffs

    def set_excited_state(self, state, states_to_prop):
        self.moldyn.set_value('exc_state_init', state)
        self.moldyn.set_value('n_exc_states_propagate', states_to_prop)
        self.coeffs = self.generate_initial_coeffs(state, states_to_prop)

    def set_timestep(self, timestep):
        self.moldyn.set_value('time_step', timestep)

    @staticmethod
    def generate_initial_coeffs(state, states_to_prop):
        A =  np.zeros((states_to_prop, 2), dtype=float)
        if state != 0:
            A[state-1,0] = 1
        return A

    def write(self, filename=None):
        if filename is None:
            filename = self._filename
        header = "{}\n{}\n".format(self.qmmm, self.moldyn)
        writer = InputceonWriter(header, self.coords, self.velocities, self.coeffs)
        writer.write(filename)
