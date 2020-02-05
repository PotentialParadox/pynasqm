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

    def set_calcxdens(self, set_val):
        if set_val:
            self.qmmm.set_value('calcxdens', '.true.')
        else:
            self.qmmm.set_value('calcxdens', '.false.')

    def set_nexmd_seed(self, seed):
        self.moldyn.set_value('rnd_seed', seed)

    def set_is_tully(self, isTully, qsteps):
        if isTully:
            self.moldyn.set_value('bo_dynamics_flag', 0)
            self.moldyn.set_value('n_quant_steps', qsteps)
        else:
            self.moldyn.set_value('bo_dynamics_flag', 1)
            self.moldyn.set_value('n_quant_steps', 0)

    def set_timestep(self, timestep):
        self.moldyn.set_value('time_step', timestep)

    @staticmethod
    def generate_initial_coeffs(state, states_to_prop):
        A =  np.zeros((states_to_prop, 2), dtype=float)
        if state != 0 and state >= states_to_prop:
            raise ValueError("Initial excited state greater than states_to_prop")
        if state != 0:
            A[state-1,0] = 1
        return A

    def write(self, filename=None):
        if filename is None:
            filename = self._filename
        header = "{}\n{}\n".format(self.qmmm, self.moldyn)
        writer = InputceonWriter(header, self.coords, self.velocities, self.coeffs)
        writer.write(filename)
