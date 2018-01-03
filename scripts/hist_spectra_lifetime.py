import argparse
import sys
from pynasqm.calculatespectra import calculate_spectra, average_spectra, np_to_string

parser = argparse.ArgumentParser()
parser.add_argument("--spectra", "-s", help="Absorbance-0 Fluorescence-1", default=0, type=int)
parser.add_argument("--number_trajectories", "-t", help="The number of trajectories to average over",
                    default=1, type=int)
parser.add_argument("--number_states", help="The number of excited states you want to extract",
                    default=1, type=int)
parser.add_argument("--number_gauss", help="The number of gaussians", default=100, type=int)
parser.add_argument("--fwhm", help="Full witdh half max", default=0.05, type=float)
parser.add_argument("--number_bins", help="The number of bins you wish to distribute over",
                    default=1000, type=int)
parser.add_argument("--xmin", help="The minimum energy in eV", default=2.0, type=float)
parser.add_argument("--xmax", help="The maximum energy in eV", default=3.0, type=float)
args = parser.parse_args()



for traj in range(args.number_trajectories):
    input_file = None
    output_file = None
    if args.spectra == 0:
        input_file = "spectra_abs_{}.input".format(traj)
        output_file = "spectra_abs_{}.output".format(traj)
    elif args.spectra == 1:
        input_file = "spectra_flu_{}.input".format(traj)
        output_file = "spectra_flu_{}.output".format(traj)
    else:
        sys.exit("Spectra must be either 0-Absorbance or 1-Fluorescence")
    calculate_spectra(args.number_states, args.number_gauss, args.fwhm, args.number_bins,
                      args.xmin, args.xmax, input_file, output_file)

spectra_average = average_spectra(args.spectra, args.number_trajectories)
spectra_string = np_to_string(spectra_average)
output_file = ""
if args.spectra == 0:
    output_file = "spectra_abs.output"
elif args.spectra == 1:
    output_file = "spectra_flu.output"
open(output_file, 'w').write(spectra_string)
