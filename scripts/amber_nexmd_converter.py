import argparse
import numpy as np
from pynasqm.inputceonreader import InputceonReader
from pynasqm.inputceonwriter import InputceonWriter
from pynasqm.amberrestartwriter import AmberRestartWriter
from pynasqm.amberrestartreader import AmberRestartReader
from pynasqm.conversions import amber_to_angstrom_ps, angstrom_ps_to_amber

def amber_to_nexmd(amber, nexmd):
    a_veloc = amber.velocities
    veloc = [[b * amber_to_angstrom_ps for b in a] for a in a_veloc]
    a_coords = amber.coordinates
    n_coords = [x[1:] for x in nexmd.coords]
    atom_ids = [x[0] for x in nexmd.coords]
    coords = []
    for index in range(len(n_coords)):
        coord_element = [atom_ids[index]]
        coord_element.extend(a_coords[index])
        coords.append(coord_element)
    header = "{}\n{}\n".format(nexmd.qmmm, nexmd.moldyn)
    coeffs = nexmd.coeffs
    return InputceonWriter(header, coords, veloc, coeffs)

def nexmd_to_amber(nexmd, amber):
    n_veloc = nexmd.velocities
    header = amber.header
    veloc = [[b * angstrom_ps_to_amber for b in a] for a in n_veloc]
    coords = [x[1:] for x in nexmd.coords]
    return AmberRestartWriter(header, coords, veloc)

def main(args):
    inputceonfile = ""
    amberrestartfile = ""
    if args.file1[-5:] == ".ceon":
        inputceonfile = args.file1
        amberrestartfile = args.file2
    else:
        amberrestartfile = args.file1
        inputceonfile = args.file2
    amberreader = AmberRestartReader(amberrestartfile)
    ceonreader = InputceonReader(inputceonfile)
    if args.outputfile[-5:] == ".ceon":
        print("Converting from amber restart {} to inputceon {}".format(amberrestartfile, args.outputfile))
        ceonwriter = amber_to_nexmd(amberreader, ceonreader)
        ceonwriter.write(args.outputfile)
    else:
        print("Converting from inputceon {} to amber restart {}".format(inputceonfile, args.outputfile))
        amberwriter = nexmd_to_amber(ceonreader, amberreader)
        amberwriter.write(args.outputfile)

parser = argparse.ArgumentParser()
parser.add_argument("file1", help="Either an inputceon file or amber restart file")
parser.add_argument("file2", help="If file 1 is and inputceon file then amber restart file else flip")
parser.add_argument("outputfile", help="outputfile, either an inputceon file or restart file")
args = parser.parse_args()
main (args)
