'''
A wrapper to slurm
'''
import subprocess
import time
import re

class Slurm:
    '''
    A class used to manage slurm scripts. slurm_header is a dictionary that holds
    these necessary items. In the NASQM automation routine this will be user_input.
    '''
    def __init__(self, slurm_header):
        self.header = slurm_header # Dictionary
        self.email_options()

    def email_options(self):
        '''
        Choose and email option based the numeric code below
        '''
        switcher = {
            1: "BEGIN",
            2: "END",
            3: "BEGIN,END",
            4: "FAIL",
            5: "BEGIN,FAIL",
            6: "END,FAIL",
            7: "BEGIN,END,FAIL"
        }
        self.email_preferences = switcher.get(self.header['email_options'])

    def create_slurm_script(self, command, title=None, n_arrays=1):
        '''
        Return the slurm job script
        '''
        title_used = title
        if title is None:
            title_used = self.header['title']
        job_script = '#!/bin/bash\n' \
                '#SBATCH --job-name='+title_used+' # A name for your job\n' \
                '#SBATCH --qos='+self.header['qos']+' # The queue for your job\n' \
                '#SBATCH --output='+title_used+'-%j.output # Output File\n' \
                '#SBATCH --error='+title_used+'-%j.err #Error File\n' \
                '#SBATCH --mail-user='+self.header['email']+' # Email address\n' \
                '#SBATCH --mail-type='+self.email_preferences+' # What emails you want\n' \
                '#SBATCH --nodes='+str(self.header['n_nodes'])+' #No. computers requested\n' \
                '#SBATCH --tasks-per-node='+str(self.header['ppn'])+\
                ' # No. processors per node\n' \
                '#SBATCH --mem-per-cpu='+self.header['memory']+\
                ' #Per processor memory requested\n' \
                '#SBATCH --array=1-'+str(n_arrays)+'%'+str(self.header['max_jobs'])+'\n' \
                '#SBATCH --time='+self.header['walltime']+' #Walltime\n' \
                '\n' + command
        return job_script

def wait_for_job_finish(slurm_id):
    '''
    Loop until job finishes
    '''
    p_id = re.compile(slurm_id)
    condition = True
    while condition:
        time.sleep(10)
        command = "squeue -j " + slurm_id
        proc = subprocess.Popen([command], shell=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, universal_newlines=True)
        stdout_value, stderr_value = proc.communicate()
        if stderr_value == "Error":
            return None
        if not re.search(p_id, stdout_value):
            condition = False

def run_slurm(slurm_script):
    '''
    Run the slurm script
    '''
    open('nasqm.sbatch', 'w').write(slurm_script)
    p_id = re.compile(r'\d+')
    proc = subprocess.Popen(['sbatch nasqm.sbatch'], shell=True, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, universal_newlines=True)
    stdout_value, stderr_value = proc.communicate()
    slurm_id = str(re.findall(p_id, stdout_value)[0])
    if stderr_value == "Error":
        return None
    print("Submitted Job: ", slurm_id)
    wait_for_job_finish(slurm_id)
    print("Job: ", slurm_id, "completed")
