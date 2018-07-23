class ClosestWriter:

    def __init__(self, trajins, number_nearest, focus_mask=":1"):
        self.trajins = self._list(trajins)
        self.number_nearest = number_nearest
        self.prmtop = "m1.prmtop"
        self.solvent_mask = "!:1"
        self.focus_mask = focus_mask
        self.trajouts = self._default_trajout()
        self.script_files = []

    @staticmethod
    def _list(trajins):
        if isinstance(trajins, str):
            return [trajins]
        return trajins

    def _default_trajout(self):
        closest_outputs = []
        for trajectory in range(1, self._number_trajectories() + 1):
            closest_outputs.append("{}/closest_{}.txt".format(trajectory,trajectory))
        return closest_outputs

    def _number_trajectories(self):
        return len(self.trajins)

    def write(self):
        for i in range(self._number_trajectories()):
            script_filename = "{}/closest_{}.traj".format(i+1,i+1)
            self.script_files.append(script_filename)
            script = self._closest_script(self.trajins[i], self.trajouts[i])
            open(script_filename, 'w').write(script)

    def _closest_script(self, trajin, trajout):
        '''
        Creates a script to identify near solvents to later
        be included in the QM calculation
        '''
        script = "parm {}\n".format(self.prmtop)
        script += "solvent !:1\n"
        script += "trajin {}\n".format(trajin)
        script += "closest {} {} closestout {}\n".format(self.number_nearest,
                                                                     self.focus_mask,
                                                                     trajout)
        script += "run\n" \
                  "quit\n"
        return script
