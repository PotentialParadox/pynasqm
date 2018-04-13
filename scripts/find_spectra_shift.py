'''
Print the spectra shift between two
spectra given the filename of the
file containing both spectra
and the units you prefer it to be in
'''
import argparse
import pynasqm.findshift
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("--file1", help="The first file you want read the first state from")
parser.add_argument("--file2", help="The second file you want read the first state from")
parser.add_argument("--unit", help="0-ev, 1-nm", type=int, default=0)
args = parser.parse_args()

UNIT = "ev" if args.unit == 0 else "nm"
print(pynasqm.findshift.find_shift(args.file1, args.file2, UNIT), UNIT)
