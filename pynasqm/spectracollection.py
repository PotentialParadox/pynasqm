import subprocess
from typing import List

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

def write_spectra_bash_script(
        suffix: str,
        ntrajs: int,
        nstates:int
    ) -> None:
    spectra_bash_script = "suffix={}\n".format(suffix)
    spectra_bash_script += "ntrajs={}\n".format(ntrajs)
    spectra_bash_script += "nstates={}\n".format(nstates)
    spectra_bash_script += "nlines=$((nstates+1))\n"
    spectra_bash_script += "awklines=$((nstates+3))\n"\
        "mkdir -p ${suffix}_spectra\n"\
        "for ((traj=1;traj<=$ntrajs;++traj)) do\n"\
        "    fileout=${suffix}_spectra/traj_${traj}.out\n"\
        "    > $fileout\n"\
        "    for filename in ${suffix}/traj_${traj}/*/nasqm_*.out;do\n"\
        "        if [ -f $filename ]; then\n"\
        "            grep -A $nlines 'Frequencies (eV) and Oscillator' $filename\\\n"\
        "                | awk -v nlines=\"$awklines\" 'BEGIN{ORS=\"    \"};\n"\
        "{\n"\
        "    if (NR%nlines >2)\n"\
        "    {\n"\
        "      printf \"%24.14E%24.14E\", $2, $6;\n"\
        "    }\n"\
        "    if (NR%nlines ==0)\n"\
        "    {\n"\
        "      printf \"\\n\";\n"\
        "    }\n"\
        "}END{printf \"\\n\"}' >> $fileout \n"\
        "        fi\n"\
        "    done\n"\
        "done\n"
    open('spectra.sh', 'w').write(spectra_bash_script)
