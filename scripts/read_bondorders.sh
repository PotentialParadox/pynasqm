# Reads the bondorders from the Amberout files.

# Expects the directory layout to be of the form
# qmexcited/traj_1/restart_0/nasqm_qmexcited_t$traj_r0.in 

# Returns a csv file with the headings
# "Trajectory, Timefs, Atom1, Atom2, BondOrder"

ntrajs=$1
nbonds=$2
timestep=$3

# The structure of the text block inside the amberout file is
# Bond Order Information for state 9
#  Atom1 Atom2   Elem1 Elem2   Bond Order
#      6     7       C     C      1.0993
#      ....
# We'll need to get the last 
mkdir -p bondorders
echo "Trajectory, Timefs, Atom1, Atom2, BondOrder"

# We iterate through all the trajectories
for ((i=1; i<=$ntrajs; i++))
do
    amber_out=qmexcited/traj_${i}/restart_0/nasqm_qmexcited_t${i}_r0.out
    # echo reading $amber_out
    grep -A $nbonds "Bond Order" $amber_out |
	awk -v "nbonds=$nbonds" -v "traj=$i" -v "dt=$timestep" \
	    'BEGIN{t=0}{
if (NR % (nbonds+3) != 0 && NR % (nbonds+3) != 1 && NR % (nbonds+3) != 2){
    printf "%8d, %10.4f, %8d, %8d, %10.4f\n", traj, t, $1, $2, $5;
}
if (NR % (nbonds+3) == 0) {t += dt;}
}'
done
