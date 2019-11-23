#!/bin/bash
#SBATCH --job-name=Test_r1 # A name for your job
#SBATCH --qos=roitberg # The queue for your job
#SBATCH --output=Test_r1-%j.output # Output File
#SBATCH --error=Test_r1-%j.err #Error File
#SBATCH --partition=hpg2-compute
#SBATCH --constraint=haswell
#SBATCH --mail-user=dtracy.uf@gmail.com # Email address
#SBATCH --mail-type=END # What emails you want
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=2000mb #Per processor memory requested
#SBATCH --array=1-1%4
#SBATCH --time=95:00:00 #Walltime

source ~/myapps/load_exports
module load intel/2017
source /ufrc/roitberg/dtracy/amber/amber.sh

nasqm.py --job 1 --restart 1