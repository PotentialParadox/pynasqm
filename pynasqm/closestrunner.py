from pynasqm.closestwriter import ClosestWriter
import subprocess

class ClosestRunner:

    def __init__(self, number_nearest_solvents, number_trajectories):
        self._n_solvents = number_nearest_solvents
        self._n_trajectories = number_trajectories
        self._trajins = self._default_trajins()

    def _default_trajins(self):
        trajins = []
        for i in range(1, self._n_trajectories+1):
            trajins.append("ground_snap.{}".format(i))
        return trajins

    def create_closest_outputs(self):
        writer = ClosestWriter(self._trajins, self._n_solvents)
        writer.write()
        self._run_closest_scripts(writer.script_files)
        return writer.trajouts

    @staticmethod
    def _run_closest_scripts(file_names):
        for script in file_names:
            subprocess.call(['cpptraj', '-i', script, '-o', 'cpptraj.out'])
