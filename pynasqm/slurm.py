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

    def create_slurm_script(self, command, title=None, slurm_array="1-1"):
        '''
        Return the slurm job script
        '''
        title_used = title
        if title is None:
            title_used = self.header['title']
        job_script = '#!/bin/bash\n' \
                '#SBATCH --job-name='+title_used+' # A name for your job\n' \
                '#SBATCH --qos='+self.header['qos']+' # The queue for your job\n' \
                '#SBATCH --output=./Reports/'+title_used+'-%j.output # Output File\n' \
                '#SBATCH --error=./Reports/'+title_used+'-%j.err #Error File\n' \
                '#SBATCH --partition=hpg2-compute\n' \
                '#SBATCH --constraint=haswell\n' \
                '#SBATCH --mail-user='+self.header['email']+' # Email address\n' \
                '#SBATCH --mail-type='+self.email_preferences+' # What emails you want\n' \
                '#SBATCH --ntasks=1\n' \
                '#SBATCH --mem-per-cpu='+self.header['memory']+\
                ' #Per processor memory requested\n' \
                '#SBATCH --array='+slurm_array+'%'+str(self.header['max_jobs'])+'\n' \
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
    slurm_id = None
    if slurm_script:
        file_name = 'nasqm.sbatch'
        slurm_id = submit_job(file_name, slurm_script)
    wait_for_job(slurm_id)

def wait_for_job(slurm_id):
    print("Waiting for {}".format(slurm_id))
    wait_for_job_finish(slurm_id)
    print("Job: ", slurm_id, "completed")

def submit_job(file_name, slurm_script):
    subprocess.call(['mkdir', '-p', 'Reports'])
    open(file_name, 'w').write(slurm_script)
    print(f"Please modify {file_name} to work on your sytem, then run")
    # p_id = re.compile(r'\d+')
    # try:
    #     proc = subprocess.Popen(['sbatch {}'.format(file_name)], shell=True, stdout=subprocess.PIPE,
    #                             stderr=subprocess.PIPE, universal_newlines=True)
    #     stdout_value, stderr_value = proc.communicate()
    #     slurm_id = str(re.findall(p_id, stdout_value)[0])
    # except IndexError:
    #     raise ValueError("File {} could not be submitted to slurm. Make sure slurm is installed.")
    # if stderr_value == "Error":
    #     raise RuntimeError("Was unable to submit {} to slurm".format(file_name))
    # print("Submitted {} Job: {}".format(file_name, slurm_id))
    # return slurm_id
