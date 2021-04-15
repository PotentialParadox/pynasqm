#!/bin/bash
# Update the input.ceon files using the AMBER outputs
# First run an Amber singlepoint with NEXD with the AMBER print settings
# set to print after each step. This will generate the coords.xyz
# and velocity.out files for each trajectory. These two files should
# contain the snapshot at time 0 only.
# Place this file in the primary workring directory (the one with pynasqm.in)
dir="qmexcited"
nsteps=10
ndsteps=1
ntrajs=1

for ((i = 1 ; i <= $ntrajs ; i++)); do
    dirpath="${dir}/traj_${i}/restart_0"

    cd $dirpath

    newinput=$(
    coords=$(awk '{
    if (NR > 2){
    gsub(/C/,"6")
    gsub(/H/,"1")
    gsub(/N/,"7")
    gsub(/O/,"8")
    print
    }
    }' coords.xyz)
    tocoords=$(awk -v nsteps="$nsteps" -v ndsteps="$ndsteps" '
    BEGIN {triggered = 1}
    {
	if (triggered) {
	    gsub(/n_class_steps=.*,/, "n_class_steps=" nsteps ",")
	    gsub(/out_data_steps=.*,/, "out_data_steps=" ndsteps ",")
	    gsub(/out_coords_steps=.*,/, "out_coords_steps=" ndsteps ",")
	    print;
	    }
	if ($0 ~ /&coord/) {
	    triggered = 0
	}
    }' input.ceon)
    velocity=$(awk '
    {
    if (triggered) {
	if (!($0 ~ /\$ENDVELOC/)) {
	    print;
	}	
	if ($0 ~ /\$ENDVELOC/) {
	    triggered=0;
	}
    }
    if ($0 ~ /\$VELOC/) {
	triggered=1;
    }
    }' velocity.out)
    aftervelocity=$(awk 'f;/&veloc/{f=1}' input.ceon)

    echo "$tocoords"
    echo "$coords"
    echo "&endcoord"
    echo ""
    echo "&veloc"
    echo "$velocity"
    echo "$aftervelocity")

    echo "$newinput" > input.temp
    mv input.ceon input.old
    mv input.temp input.ceon

    cd ../../..

done

