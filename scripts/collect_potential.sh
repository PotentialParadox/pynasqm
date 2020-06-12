# Collect Potentials
# Expects a trajectory layout of the form
# ${directory}/traj_${traj}/restart_${res}/energy-ev.out
#
# Returns a csv of the form
# | trajectory | time (fs) | energy (eV) |

#User Inputs
directory=qmexcited
ntrajs=1024
nrestarts=0

echo 'Traj,Time-fs,Potential-Ev'
for ((traj=1;traj<=$ntrajs;++traj)) do
    for ((res=0;res<=$nrestarts;++res)) do
        infile=${directory}/traj_${traj}/restart_${res}/energy-ev.out
        [ -f $infile ] && \
        cat $infile | awk -v traj="$traj"  '
{
if (NR > 1){
   printf "%8d,%14.8f,%14.8f\n", traj, $1, $4;
}
}
'
    done
done
