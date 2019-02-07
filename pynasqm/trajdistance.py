import subprocess

class TrajDistance:

    def __init__(self, parmtop, solute_mask):
        self._parmtop = parmtop
        self._solute_mask = solute_mask

    def __call__(self, trajin, solvent_mask, index=0, directory=None):
        if directory is None:
            directory = index + 1
        file_name = '{}/distance_{}.dat'.format(directory, index+1)
        traj_string = self._create_string(trajin, solvent_mask, file_name)
        call_file = '{}/traj_dist_{}.in'.format(directory, index+1)
        open(call_file, 'w').write(traj_string)
        p1 =subprocess.Popen(['cpptraj', '-i', call_file, file_name, '-o', 'distance.log'], stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
        stdout = p1.communicate()[0]
        return self.read_distance(file_name)

    def _create_string(self, trajin, solvent_mask, outfile_name):
        traj_string = "parm {}\n".format(self._parmtop)
        traj_string += "trajin {}\n".format(trajin)
        traj_string += "distance {} {} out {}\n".format(self._solute_mask,
                                                        solvent_mask,
                                                        outfile_name)
        traj_string += "run\n"
        traj_string += "exit\n"
        return traj_string

    @staticmethod
    def read_distance(file_name):
        dist_string = open(file_name, 'r').read()
        lines = dist_string.split()
        return float(lines[-1])
