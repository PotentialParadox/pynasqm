import argparse
import sys
from pynasqm.calculatespectra import calculate_spectra, average_spectra, np_to_string

parser = argparse.ArgumentParser()
parser.add_argument("--input_file", "-i", help="The input file", default=None)
parser.add_argument("--output_file", "-o", help="The output file", default=None)
parser.add_argument("--number_states", help="The number of excited states you want to extract",
                    default=1, type=int)
parser.add_argument("--number_gauss", help="The number of gaussians", default=100, type=int)
parser.add_argument("--fwhm", help="Full witdh half max", default=0.05, type=float)
parser.add_argument("--number_bins", help="The number of bins you wish to distribute over",
                    default=1000, type=int)
parser.add_argument("--xmin", help="The minimum energy in eV", default=2.0, type=float)
parser.add_argument("--xmax", help="The maximum energy in eV", default=3.0, type=float)
args = parser.parse_args()

input_file = args.input_file
output_file = args.output_file
spectra = calculate_spectra(args.number_states, args.number_gauss, args.fwhm, args.number_bins,
                            args.xmin, args.xmax, input_file, output_file)

spectra_string = np_to_string(spectra)
open(output_file, 'w').write(spectra_string)
