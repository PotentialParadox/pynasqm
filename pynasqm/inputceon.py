'''
Class in charge of controling the input files for NASQM
FIXME This should be refactored in oredered to be testable
'''
import re
from pynasqm.sed import sed_inplace, sed_global
from pynasqm.inputceonmanager import InputceonManager
from pynasqm.periodictable import periodic_table

class InputCeon:
    """
    NAESMD always uses the input.ceon file, so that will be used for the naesmd input file.
    AMBER can use any input file name, so we require it.
    """
    def __init__(self, amber_input):
        self.amber_input = amber_input
        self.inputceonmanager = InputceonManager('input.ceon')
        self.path = self.find_path()
        self.input_ceon_path = self.path + "input.ceon"
        self.naesmd_init = open(self.input_ceon_path, 'r').read()
        self.amber_init = open(amber_input, 'r').read()
        self.log = ''

    def set_excited_state(self, state, states_to_prop):
        self.inputceonmanager.set_excited_state(state, states_to_prop)
        self.inputceonmanager.write('input.ceon')

    def find_path(self):
        '''
        Return the full naesmd path
        '''
        a_split = self.amber_input.split('/')
        d_split = a_split[:-1]
        path = ""
        for directory in d_split:
            path += directory + "/"
        return path

    def set_n_steps(self, n_steps):
        '''
        Sets the number of time-steps to do the simulation
        '''
        sed_inplace('input.ceon', r'n_class_steps=\d+', 'n_class_steps=' + str(n_steps))
        sed_inplace(self.amber_input, r'nstlim\s*=\s*\d+\.?\d*', 'nstlim='+str(n_steps))
        if n_steps == 0:
            sed_inplace(self.amber_input, r'irest\s*=\s*\d+', 'irest=0')
            sed_inplace(self.amber_input, r'ntx\s*=\s*\d+', 'ntx=1')

    def set_quantum(self, is_quantum):
        '''
        Set the number of steps between print outs
        '''
        if is_quantum:
            sed_inplace(self.amber_input, r'ifqnt=\s*\d*', 'ifqnt=1')
        else:
            sed_inplace(self.amber_input, r'ifqnt=\s*\d*', 'ifqnt=0')

    def set_n_steps_to_print(self, n_steps_to_print):
        '''
        Set the number of steps between print outs
        '''
        sed_inplace('input.ceon', r'out_data_steps=\d*', 'out_data_steps=' + str(n_steps_to_print))
        sed_inplace(self.amber_input, r'ntpr=\s*\d*', 'ntpr=' + str(n_steps_to_print))

    def set_n_steps_to_mcrd(self, n_steps_to_print):
        '''
        Set the number of steps between print outs
        '''
        sed_inplace(self.amber_input, r'ntwx=\s*\d*', 'ntwx=' + str(n_steps_to_print))

    def write_log(self):
        '''
        Write a log of all our changes
        '''
        open('input_ceon.log', 'w').write(self.log)

    def write_backup(self):
        '''
        Write the backup the original input files overriding any changes we made during the
        process
        '''
        open('input.ceon', 'w').write(self.naesmd_init)
        open(self.amber_input, 'w').write(self.amber_init)


    def set_exc_state_propagate(self, n_exc_states_propagate):
        '''
        Set the number of exciteds states to propagate
        '''
        sed_inplace('input.ceon', 'n_exc_states_propagate=\d*', 'n_exc_states_propagate='
                    + str(n_exc_states_propagate))

    def set_coordinates(self, coordinates):
        '''
        Set the coordinates for input.ceon
        '''
        sed_global('input.ceon', '&coord(.|\s|\n)*?&endcoord', '&coord\n' + coordinates + '&endcoord')

    def set_exc_state_init(self, exc_state_init):
        """
        Set the initial excited state
        """
        sed_inplace('input.ceon', r'exc_state_init=\d*', 'exc_state_init=' + str(exc_state_init))

    def set_verbosity(self, verbosity):
        """
        Set the verbosity for both amber and naesmd
        """
        sed_inplace('input.ceon', r'verbosity=\d*', 'verbosity=' + str(verbosity))
        sed_inplace(self.amber_input, r'verbosity\s*=\s*\d*', 'verbosity=' + str(verbosity))

    def set_printcharges(self, is_printcharges):
        """
        Set the verbosity for both amber and naesmd
        """
        if is_printcharges:
            sed_inplace('input.ceon', r'printcharges=\d*', 'printcharges=1')
        else:
            sed_inplace('input.ceon', r'printcharges=\d*', 'printcharges=0')

    def set_periodic(self, periodic, constant_value):
        '''
        Sets the appropriate boundary condition values for priodic or non-periodic conditions
        '''
        if periodic is True:
            if constant_value == 1:
                sed_inplace(self.amber_input, r'ntb\s*=\s*\d+', 'ntb=1')
                sed_inplace(self.amber_input, r'ntp\s*=\s*\d+', 'ntp=0')
            if constant_value == 2:
                sed_inplace(self.amber_input, r'ntb\s*=\s*\d+', 'ntb=2')
                sed_inplace(self.amber_input, r'ntp\s*=\s*\d+', 'ntp=1')
            sed_inplace(self.amber_input, r'qm_ewald\s*=\s*\d+', 'qm_ewald=1')
            sed_inplace(self.amber_input, r'qm_pme\s*=\s*\d+', 'qm_pme=1')
            sed_inplace(self.amber_input, r'iwrap\s*=\s*\d+', 'iwrap=1')
        if periodic is False:
            sed_inplace(self.amber_input, r'ntb\s*=\s*\d+', 'ntb=0')
            sed_inplace(self.amber_input, r'ntp\s*=\s*\d+', 'ntp=0')
            sed_inplace(self.amber_input, r'qm_ewald\s*=\s*\d+', 'qm_ewald=0')
            sed_inplace(self.amber_input, r'qm_pme\s*=\s*\d+', 'qm_pme=0')
            sed_inplace(self.amber_input, r'iwrap\s*=\s*\d+', 'iwrap=0')

    def set_time_step(self, time_step):
        """
        Sets the timestep of the simulation
        """
        sed_inplace(self.amber_input, r'dt=\s*\d+\.?\d*', 'dt=' +str(time_step/1000))

    def set_random_velocities(self, is_random_velocities):
        '''
        Sets the appropriate values for random velocities
        '''
        if is_random_velocities is False:
            sed_inplace(self.amber_input, r'ntx\s*=\s*\d+\.?\d*', 'ntx=5')
        if is_random_velocities is True:
            sed_inplace(self.amber_input, r'ntx\s*=\s*\d+\.?\d*', 'ntx=1')

    def set_mask(self, mask):
        '''
        Simple setter for the mask
        '''
        sed_inplace(self.amber_input, r"qmmask\s*=\s*'.*'", "qmmask="+mask)

    def get_mask(self):
        '''
        Simple mask getter
        '''
        file_string = open(self.amber_input, 'r').read()
        p_mask = re.compile(r"qmmask\s*=\s*('.*')")
        result = re.findall(p_mask, file_string)
        return result[0]

    def copy(self, file_name):
        '''
        Returns a copy into the new file_name
        '''
        old_file_string = open(self.amber_input, 'r').read()
        open(self.path + file_name, 'w').write(old_file_string)
        return InputCeon(self.path + file_name)

    def log_inputceon(self):
        '''
        log the inputceon file
        '''
        self.log += open('input.ceon', 'r').read()

    def set_nmr_directory(self, nmr_directory):
        p_nmropt = re.compile(r'nmropt\s*=\s*\d+')
        p_ifqnt = re.compile(r"ifqnt\s*=\s*\d*")
        p_disang = re.compile(r'DISANG\s*=*')
        p_dumpave = re.compile(r'DUMPAVE\s*=*')
        p_wt = re.compile(r'\&wt')
        is_nmropt = None
        is_disang = None
        is_dumpave = None
        file_string = None
        with open(self.amber_input, 'r') as file_in:
            file_string = file_in.read()
            is_nmropt = re.search(p_nmropt, file_string)
            is_disang = re.search(p_disang, file_string)
            is_dumpave = re.search(p_dumpave, file_string)
            is_wp = re.search(p_wt, file_string)
        if is_nmropt:
            sed_inplace(self.amber_input, p_nmropt, 'nmropt=1')
        else:
            sed_inplace(self.amber_input, p_ifqnt, 'nmropt=1,\n  ifqnt=1')
        if not is_dumpave:
            file_string = open(self.amber_input, 'r').read()
            file_string = file_string + " &wt\n type='DUMPFREQ', istep1=100,\n /\n"
            open(self.amber_input, 'w').write(file_string)
        if not is_wp:
            file_string = open(self.amber_input, 'r').read()
            file_string = file_string + " &wt\n type='END'\n /\n"
            open(self.amber_input, 'w').write(file_string)
        if is_disang:
            sed_inplace(self.amber_input, p_disang, 'DISANG={}\n'.format(nmr_directory))
            sed_inplace(self.amber_input, p_dumpave, 'DUMPAVE={}.eq\n'.format(nmr_directory[:-5]))
        else:
            file_string = open(self.amber_input, 'r').read()
            file_string = file_string + 'DISANG={}\n'.format(nmr_directory)
            file_string = file_string + 'DUMPAVE={}.eq\n'.format(nmr_directory[:-5])
            open(self.amber_input, 'w').write(file_string)



