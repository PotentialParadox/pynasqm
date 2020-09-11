def write_spectra_bash_script(
        suffix: str,
        ntrajs: int,
        nstates:int
    ) -> None:
    if suffix == "pulse_pump":
        print("Dustin!!!")
    else:
        write_normal_script(suffix, ntrajs, nstates)


def write_normal_script(
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

def write_ppump_script(
        suffix: str,
        ntrajs: int,
        nstates:int
    ) -> None:
    pass
