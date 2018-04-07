from pynasqm.closestwriter import ClosestWriter
import subprocess

class ClosestRunner:

    def __init__(self, user_input):
        self._user_input = user_input

    def create_closest_outputs(self, trajins):
        number_solvents = self._user_input.number_nearest_solvents
        writer = ClosestWriter(trajins, number_solvents)
        writer.write()
        self._run_closest_scripts(writer.script_files)
        return writer.trajouts

    @staticmethod
    def _run_closest_scripts(file_names):
        for script in file_names:
            subprocess.call(['cpptraj', '-i', script, '-o', 'cpptraj.out'])
