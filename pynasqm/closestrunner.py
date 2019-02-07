from pynasqm.closestwriter import ClosestWriter
import subprocess

class ClosestRunner:

    def __init__(self, number_nearest_solvents, number_trajectories, trajins, focus_mask=":1",
                 directories=None):
        self._n_solvents = number_nearest_solvents
        self._n_trajectories = number_trajectories
        self._trajins = trajins
        self._focus_mask = focus_mask
        self._directories = directories

    def set_trajins(self, trajins):
        self._trajins = trajins

    def get_trajins(self):
        return self._trajins

    def create_closest_outputs(self):
        writer = ClosestWriter(self._trajins, self._n_solvents, self._focus_mask, self._directories)
        writer.write()
        self._run_closest_scripts(writer.script_files)
        return writer.closeouts

    @staticmethod
    def _run_closest_scripts(file_names):
        for script in file_names:
            p1 =subprocess.Popen(['cpptraj', '-i', script, '-o', 'cpptraj.out'], stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
            stdout = p1.communicate()
