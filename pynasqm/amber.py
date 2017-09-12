'''
Interface to Amber
'''
from multiprocessing import Pool
import subprocess


class Amber:
    '''
    A class to control calls to amber
    '''
    def __init__(self, input_roots=None, output_roots=None, coordinate_files=None,
                 prmtop_files=None, restart_roots=None, export_roots=None):
        self.input_roots = input_roots
        self.output_roots = output_roots
        self.coordinate_files = coordinate_files
        self.prmtop_files = prmtop_files
        self.restart_roots = restart_roots
        self.export_roots = export_roots

    def run_amber_worker(self, conjoined_list):
        '''
        Explanation for run amber parallel, needs to be private
        '''
        input_root = conjoined_list[0]
        output_root = conjoined_list[1]
        coordinate_file = conjoined_list[2]
        prmtop_file = conjoined_list[3]
        restart_root = conjoined_list[4]
        export_root = conjoined_list[5]
        subprocess.run(['sander', '-O', '-i', "{}.in".format(input_root), '-o',
                        "{}.out".format(output_root), '-c', coordinate_file,
                        '-p', prmtop_file, '-r', "{}.rst".format(restart_root),
                        '-x', "{}.nc".format(export_root)])

    def run_amber(self, number_processors=1):
        '''
        Multithreaded amber run
        '''
        pool = Pool(number_processors)
        conjoined_list = []
        for i in range(len(self.input_roots)):
            conjoined_list.append([self.input_roots[i], self.output_roots[i],
                                   self.coordinate_files[i], self.prmtop_files[i],
                                   self.restart_roots[i], self.export_roots[i]])
        pool.map(self.run_amber_worker, conjoined_list)
        pool.close()
        pool.join()
