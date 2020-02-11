class ClosestWriter:

    def __init__(self, trajins, number_nearest, focus_mask=":1", directories=None):
        self.trajins = self._list(trajins)
        self.number_nearest = number_nearest
        self.prmtop = "m1.prmtop"
        self.solvent_mask = "!:1"
        self.focus_mask = focus_mask
        self.directories = self._default_directories(directories)
        self.closeouts = self._default_trajout()
        self.script_files = self._default_scriptfiles()

    @staticmethod
    def _list(trajins):
        if isinstance(trajins, str):
            return [trajins]
        return trajins

    def _default_directories(self, directories):
        if directories is None:
            return ["{}".format(i) for i in range(1, self._number_trajectories() + 1)]
        return directories

    def _default_trajout(self):
        return ["{}/closest_{}.txt".format(directory, traj)
                for traj, directory in zip(range(1, self._number_trajectories()+1), self.directories)]

    def _default_scriptfiles(self):
        return ["{}/closest_{}.traj".format(directory, traj)
                for traj, directory in zip(range(1, self._number_trajectories()+1), self.directories)]

    def _number_trajectories(self):
        return len(self.trajins)

    def write(self):
        for i, script_filename in enumerate(self.script_files):
            script = self._closest_script(self.trajins[i], self.closeouts[i])
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
