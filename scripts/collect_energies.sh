# Collect Energies
# Expects a trajectory layout of the form
# ${directory}/traj_${traj}/restart_${res}/nasqm_${directory}_t${traj}_r${res}.out
#
# Returns a csv of the form
# | trajectory | time (fs) | state | energy (eV) | energy (AU) |

#User Inputs
directory=qmexcited
ntrajs=1024
nrestarts=1
nstates=30
timestep=0.5
totaltime=1000

#Derived Values
timeinrestart=`echo "${totaltime} / (${nrestarts} + 1)" | bc -l`
appendsize=$((nstates+2))
blocksize=$((nstates+4))

echo 'Trajectory,Time(fs),State,Energy(eV),Energy(AU)'
for ((traj=1;traj<=$ntrajs;++traj)) do
    for ((res=0;res<=$nrestarts;++res)) do
        infile=${directory}/traj_${traj}/restart_${res}/nasqm_${directory}_t${traj}_r${res}.out
        [ -f $infile ] && \
            starttime=`echo "${res} * ${timeinrestart}" | bc -l` && \
            grep -A $appendsize "Total energy of the ground state" $infile \
                | awk -v starttime="$starttime", -v traj="$traj" -v blocksize="$blocksize" -v timestep="$timestep" '
{if (NR%blocksize != 0 && NR%blocksize != 1 && NR%blocksize != 3){
    t=int(NR/blocksize)*timestep+starttime
    printf "%4.2d,%10.2f,%4d,%18.11f,%18.11f\n", traj, t, $1, $2, $3;
}
}'
    done
done
