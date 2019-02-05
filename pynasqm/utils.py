'''
Commonly used utilities
'''
import re
import numpy as np
import subprocess
import os

def numpy_element(numpy_array, i, j=0):
    try:
        numpy_array.shape[1]
        return numpy_array[i, j]
    except:
        return numpy_array[j]

def numpy_to_txt(numpy_array, form=None):
    n_rows = numpy_array.shape[0]
    n_collumns = None
    output = ""
    prefix = ""
    suffix = ""
    try:
        n_collumns = numpy_array.shape[1]
        suffix = "\n"
    except:
        n_collumns = n_rows
        n_rows = 1
    for i in range(n_rows):
        output += prefix
        for j in range(n_collumns):
            temp_value = numpy_element(numpy_array, i, j)
            if form == "scientific":
                output += "{: 24.14E}".format(temp_value)
            elif isinstance(temp_value, float):
                output += "{: 10.4f}".format(temp_value)
            else:
                output += "{: 8d}".format(temp_value)
        output += suffix
    return output

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise TypeError('Boolean value expected.')

def copy_file(source_path, output_path):
    subprocess.call(['cp', source_path, output_path])

def copy_files(lst, source_directory, output_directory):
    for item in lst:
        source = "{}/{}".format(source_directory, item)
        output = "{}/{}".format(output_directory, item)
        copy_file(source, output)

def mkdir(directory):
    if not os.path.exists(directory):
        os.mkdir(directory)
