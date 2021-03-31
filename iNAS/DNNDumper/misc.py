import sys, os
from pprint import pprint
import numpy as np
import warnings
import re





####################################################
# DATA MANIPULATION
####################################################      
'''
matrix dimension transposing
'''
def _np_dim_transpose_HWC_to_CHW(x):
    return np.transpose(x, (2, 0, 1))
def _np_dim_transpose_CHW_to_HWC(x):
    return np.transpose(x, (1, 2, 0))


'''
Get dimensions of input/weights
'''
def _get_dims(x, k, layout='NCHW'):
    if layout=='NCHW':
        x_c = np.shape(x)[0]
        x_h = np.shape(x)[1]
        x_w = np.shape(x)[2]
        k_n = np.shape(k)[0]
        k_c = np.shape(k)[1]
        k_h = np.shape(k)[2]
        k_w = np.shape(k)[3]    
    
    elif layout=='HWNC':
        x_h = np.shape(x)[0]
        x_w = np.shape(x)[1]
        x_c = np.shape(x)[2]        
        k_h = np.shape(k)[0]
        k_w = np.shape(k)[1]    
        k_n = np.shape(k)[2]
        k_c = np.shape(k)[3]

    else:
        sys.exit("_get_dims: layout unrecognized")

    return x_c, x_h, x_w, k_n, k_c, k_h, k_w

def _get_dim_ifm(x, layout='NCHW'):
    if layout=="NCHW":
        x_c = np.shape(x)[0]
        x_h = np.shape(x)[1]
        x_w = np.shape(x)[2]
    elif layout == "HWNC":
        x_c = np.shape(x)[2]
        x_h = np.shape(x)[0]
        x_w = np.shape(x)[1]
    else:
        sys.exit("_get_dim_ifm: layout unrecognized")
    
    return x_c, x_h, x_w

def _get_dim_k(k, layout='NCHW'):
    if layout=="NCHW":
        k_n = np.shape(k)[0]
        k_c = np.shape(k)[1]
        k_h = np.shape(k)[2]
        k_w = np.shape(k)[3]    
    elif layout=="HWNC":
        k_n = np.shape(k)[2]
        k_c = np.shape(k)[3]
        k_h = np.shape(k)[0]
        k_w = np.shape(k)[1]    
    else:
        sys.exit("_get_dim_ifm: layout unrecognized")

    return k_n, k_c, k_h, k_w


'''
Convert between Q15 and float
'''
def _q15_to_float(q):
    return (q * (2**-15))  # 2^-15

def _float_to_q15(f):
    return (f * (2**15))  # 2^15


'''
saturate/truncate
'''
def _saturate(n, nmin, nmax):
    if n<nmin:
        return nmin
    else:
        if n>nmax:
            return nmax
        else:
            return n
        
'''
x: [ch, h, w]
'''
def _sum_channels(x):
    result = []
    for each_ch in x:
        s = np.sum(each_ch)
        result.append(s)
    return np.array(result)


####################################################
# STRING MANIPULATION
####################################################   
def get_substring(target, sub1, sub2, empty=None, integer=True):
    try:
        result = re.search(sub1+'(.*?)'+sub2, target)         
        result = result.group(1)
        if (integer):
            result = int(result)        
    except:                
        result = empty
    return result


####################################################
# DEBUG
####################################################   
def _debug_show_numlist(numlist, pause=True):
    print("---------------")
    for each_num in numlist:
        pprint(each_num)    
    print("---------------")
    if(pause==True):
        input("")

####################################################
# ERROR HANDLING
####################################################  
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m' 
 
def output_error_msg(s):
    print (bcolors.WARNING + s + bcolors.ENDC)
