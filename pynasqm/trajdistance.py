import subprocess

class TrajDistance:

    def __init__(self, parmtop, solute_mask):
        self._parmtop = parmtop
        self._solute_mask = solute_mask

    def __call__(self, trajin, solvent_mask):
        traj_string = self._create_string(trajin, solvent_mask)
        call_file = 'traj_dist.in'
        open(call_file, 'w').write(traj_string)
        subprocess.call(['cpptraj', '-i', call_file, 'distance.dat', '-o', 'distance.log'])
        return self.read_distance()

    def _create_string(self, trajin, solvent_mask):
        traj_string = "parm {}\n".format(self._parmtop)
        traj_string += "trajin {}\n".format(trajin)
        traj_string += "distance {} {} out distance.dat\n".format(self._solute_mask,
                                                                 solvent_mask)
        traj_string += "run\n"
        traj_string += "exit\n"
        return traj_string

    @staticmethod
    def read_distance():
        dist_string = open('distance.dat', 'r').read()
        lines = dist_string.split()
        return float(lines[-1])
