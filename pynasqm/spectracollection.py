import subprocess
from typing import List
from pynasqm.writespectrabashscript import write_spectra_bash_script

def write_spectra_input(
        user_input,
        suffix: str
    ) -> None:
    n_trajectories = get_n_trajectories(user_input, suffix)
    n_states = get_n_states(user_input, suffix)
    spectra_input, nfailed = accumulate_spectra(
        suffix,
        n_trajectories,
        n_states
    )
    open(f"spectra_{suffix}.input", 'w').write(spectra_input)

def accumulate_spectra(
        suffix: str,
        n_trajectories: int,
        n_states: int
    ) -> (str, int):

    create_spectra_inputs(suffix, n_trajectories, n_states)
    omegas_and_strengths = [open("{}_spectra/traj_{}.out".format(suffix, traj), 'r').read()
                            for traj in range(1, n_trajectories+1)]
    completed, failed_jobs = filter_completed(omegas_and_strengths)
    print_failed(failed_jobs)
    spectra_input = "".join(completed)
    return spectra_input, len(failed_jobs)

def filter_completed(
        data: List[str]
    ) -> (List[str], List[int]):
    nlines = [len(d.splitlines()) for d in data]
    maxlines = max (nlines)
    failed = []
    completed = []
    for i, n in enumerate(nlines):
        if n == maxlines:
            completed.append(data[i])
        else:
            failed.append(i+1)
    return completed, failed

def print_failed(failed_trajs):
    if failed_trajs == []:
        return ""
    failed_string = "Trajectories: "
    for traj in failed_trajs:
        failed_string += "{} ".format(traj)
    failed_string += "failed and are being skipped in the calculation of spectra"
    print(failed_string)

def get_n_trajectories(
        user_input,
        suffix: str
    ) -> int:
    return user_input.n_snapshots_qmground

def get_n_states(
        user_input,
        suffix: str
    ) -> int:
    return user_input.n_abs_exc

def create_spectra_inputs(
        suffix: str,
        n_trajectories: int,
        n_states: int
    ) -> None:
    write_spectra_bash_script(suffix, n_trajectories, n_states)
    subprocess.run("bash spectra.sh", shell=True)

