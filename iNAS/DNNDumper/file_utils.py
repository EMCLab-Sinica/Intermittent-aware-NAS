import sys, os
import shutil
from pprint import pprint
import json
from pathlib import Path

sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from misc import output_error_msg
import numpy as np

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.int32): 
            return int(obj)  
        return json.JSONEncoder.default(self, obj)



# -- dump json output --
def json_dump(fname, data, indent=4):
    # delete file if exists
    if os.path.exists(fname):
        os.remove(fname)
    
    # write json
    with open(fname, "w") as write_file:
        json.dump(data, write_file, indent=indent, cls=NumpyEncoder)


# -- load data from json file --
def json_load(fname):
    
    if os.path.exists(fname):
        json_data=open(fname)
        file_data = json.load(json_data)
        return file_data
    else:
        sys.exit("ERROR - file does not exist : " + fname)
        return None


def open_file(fname):
    #print ("Opening - "+ fname)
    f = open(fname, 'r', encoding='utf-8') 
    data = f.readlines()
    f.close()
    return data

# def write_json_file(fname, data):                
#         logfile=open(fname, 'w')
#         json_data = json.dumps(data, indent=4)
#         logfile.write(json_data)


def write_file(fname, data):
    f = open(fname, "wt")
    f.write(data)
    f.close()


def delete_file(fname):
    if os.path.exists(fname):
        os.remove(fname)
    else:
        pass

def copy_file(src, dst):
    if os.path.exists(src):
        try:
            shutil.copyfile(src, dst)
        except:
            output_error_msg("File did not copy ! - \n" + dst + "\n" + src)
            sys.exit()
    else:
        output_error_msg('Src file invalid ! - ' + src)
        sys.exit()


def dir_create(dir):
    try:
        Path(dir).mkdir(parents=True, exist_ok=True)
    except:
        sys.exit("dir_create:: Error - " + dir)


def file_exists(fname):
    return os.path.exists(fname)


def get_log_file_list(fname):
    lines = open_file(fname)
    result = []
    for l in lines:
        result.append(LOG_DIR + l)
    return result

# return with full path
def get_dir_filelist(dirname):
    file_names = [f for f in os.listdir(dirname) if os.path.isfile(os.path.join(dirname, f))]
    return file_names