'''
Interface to Amber
'''
from multiprocessing import Pool
import subprocess
import os


class Amber:
    '''
    A class to control calls to amber
    '''
    def __init__(self, input_roots=None, output_roots=None, coordinate_files=None,
                 prmtop_files=None, restart_files=None, export_roots=None, directories=None):
        self.input_roots = input_roots
        self.output_roots = output_roots
        self.coordinate_files = coordinate_files
        self.prmtop_files = prmtop_files
        self.restart_files = restart_files
        self.export_roots = export_roots
        self.directories = directories

    def run_amber_worker(self, conjoined_list):
        '''
        Explanation for run amber parallel, needs to be private
        '''
        cwd = os.getcwd()
        os.chdir('./{}'.format(conjoined_list[6]))
        print('in directory: {}'.format(os.getcwd()))
        input_root = conjoined_list[0]
        output_root = conjoined_list[1]
        coordinate_file = conjoined_list[2]
        prmtop_file = conjoined_list[3]
        restart_file = conjoined_list[4]
        export_root = conjoined_list[5]
        subprocess.run(['sander', '-O', '-i', "{}.in".format(input_root), '-o',
                        "{}.out".format(output_root), '-c', coordinate_file,
                        '-p', prmtop_file, '-r', "{}".format(restart_file),
                        '-x', "{}.nc".format(export_root)])
        os.chdir(cwd)

    def run_amber(self, number_processors=1, is_ground_state=False):
        '''
        Multithreaded amber run
        '''
        pool = Pool(number_processors)
        conjoined_list = []
        for i in range(len(self.input_roots)):
            conjoined_list.append([self.input_roots[i], self.output_roots[i],
                                   self.coordinate_files[i], self.prmtop_files[i],
                                   self.restart_files[i], self.export_roots[i], self.directories[i]])
        pool.map(self.run_amber_worker, conjoined_list)
        pool.close()
        pool.join()
