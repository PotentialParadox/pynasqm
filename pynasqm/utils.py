'''
Commonly used utilities
'''
import re
import numpy as np

def numpy_to_txt(numpy_array):
    numpy_to_txt = str(numpy_array)
    numpy_to_txt = re.sub("\[", ' ', numpy_to_txt)
    numpy_to_txt = re.sub("\]", ' ', numpy_to_txt)
    return numpy_to_txt

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise TypeError('Boolean value expected.')
