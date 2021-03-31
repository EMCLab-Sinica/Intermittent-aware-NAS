# run inas for multiple energy buffers and multiple timing specifications
# jobs are batched, pipelined, multithreaded

import sys, os, csv, math
import argparse
import random
import shutil
import time
import subprocess
import itertools
import multiprocessing
import socket
import numpy as np
from pprint import pprint
from itertools import cycle

from DNNDumper.file_utils import open_file, file_exists


# ===== CCAP to TS mapping (obtained by random sampling, get latency of children at TS1, TS2, TS3 ranking) ======

TS_SELECTION_SCHEME = 2 

CCAP_LIST = ["0.001", "0.005", "0.01"]

## -- 2KB VM (children at 25, 50, 75%)
## -- CONTPOW (HW-NAS) : TS found seperately, by sampling the CONTPOW solution space
EXP_CONFIG = {
    # =====================================================================================================    
    "cifar" : {       
        
        "INTPOW" : {                    
            "0.001" : [576.47, 965.05, 1590.98],
            "0.005" : [194.86, 302.37, 477.5],
            "0.01"  : [191.78, 296.2, 457.75],
        },
        "CONTPOW": {        
            "NoEn" : [62.5,	99.8,	158.6],      
        },
        'CONTPOW_EXP_SETTINGS_FILE' : "settings_files/eval_configs/config_inas_cifar_CONT_generic.json",
        'INTPOW_EXP_SETTINGS_FILE' : "settings_files/eval_configs/config_inas_cifar_INT_generic.json",        
    },
    # =====================================================================================================
    "har" : {
            "INTPOW" : {                
                "0.001" : [29.25, 54.17, 138.57],
                "0.005" : [18.7,  28.9, 39.56],
                "0.01"  : [20.45, 31.49, 44.57],             
            },
            "CONTPOW": {             
                "NoEn" : [2.9,	4.7,	8.5],  
            },
            'CONTPOW_EXP_SETTINGS_FILE' : "settings_files/eval_configs/config_inas_har_CONT_generic.json",
            'INTPOW_EXP_SETTINGS_FILE' : "settings_files/eval_configs/config_inas_har_INT_generic.json",            
    },
    # =====================================================================================================
    "kws" : {
            "INTPOW" : {
                "0.001" : [16.33, 21.43, 31.2],                
                "0.005" : [10.35, 16.24, 18.03],
                "0.01" : [10.04, 14.6, 16.28],           
            },
            "CONTPOW": {                
                "NoEn" : [2.0,	2.6,    3.8],  
            },
            'CONTPOW_EXP_SETTINGS_FILE' : "settings_files/eval_configs/config_inas_kws_CONT_generic.json",
            'INTPOW_EXP_SETTINGS_FILE' : "settings_files/eval_configs/config_inas_kws_INT_generic.json",            
    },
}


# caliberated REHM
REHM_TABLE = {
    "cifar" : { "0.001" : 52.0,     "0.005" : 24.0,      "0.01"  : 22.0},
    "har"   : { "0.001" : 62.0,     "0.005" : 41.0,      "0.01"  : 28.0},
    "kws"   : { "0.001" : 62.0,     "0.005" : 44.0,      "0.01"  : 35.0},
}

# ==== dummy ====
SPECIAL_CASE_SUFFIX = ""

#################################################################
# HELPERS
#################################################################
def _chunkify(items, chunk_len):
    return [items[i:i+chunk_len] for i in range(0,len(items),chunk_len)]

def _get_max_gpu_count():
    hostname = socket.gethostname()    
    if   "154" in hostname: return 4    
    else:
        sys.exit("_get_max_gpu_count:: Error - unknown")

def _get_available_gpus():
    hostname = socket.gethostname()    
    if   "154" in hostname: return list(np.arange(4))    
    else:
        sys.exit("_get_available_gpus:: Error - unknown")  


def _is_already_complete(outlog_fname):        
    if (file_exists(outlog_fname)):
        f = open(outlog_fname, 'r')
        lines = f.readlines()
        last_lines = lines[-5:]
        for l in last_lines: 
            if "NASBase::TOP:: Search Complete" in l:
                return True    
        return False
    else:
        return False

# returns false if any one of the logs are still incomplete
def _is_batch_already_complete(outlog_fnames):
    for each_log in outlog_fnames:
        if(_is_already_complete(each_log) == False):
            return False    
    return True


#################################################################
# RUN COMMAND
#################################################################

def worker_thread(wid, cmd_lst):
    print("Worker [%d] :: Enter : has %d jobs " % (wid, len(cmd_lst)))

    for i, each_cmd in enumerate(cmd_lst):
        cmd = each_cmd[0]
        fstdout = each_cmd[1]
        fstderr = each_cmd[2]
        p = subprocess.Popen(cmd, shell=True,
                            stdout=open(fstdout, 'a'), stderr=open(fstderr, 'a'), 
                            start_new_session=True
                        )
        p.wait()
        print("Worker[%d]::Complete [J%d]: %s" % (wid, i, cmd))
        time.sleep(10) 



def _construct_command(dataset, ccap, latreq, gpuid, setting_fname, exp_suffix):
    #print(os.getcwd()); sys.exit()
    if ccap != -1:
        rehm = REHM_TABLE[dataset][str(ccap)]
        c = "python -u main.py" + \
            " --gpuid " + str(gpuid) + \
            " --settings " + setting_fname + \
            " --ccap " + str(ccap) + \
            " --latreq " + str(latreq) + \
            " --rehm " + str(rehm) + \
            " --suffix " + exp_suffix
    else:
        c = "python -u main.py" + \
            " --gpuid " + str(gpuid) + \
            " --settings " + setting_fname + \
            " --latreq " + str(latreq) + \
            " --suffix " + exp_suffix

    fstdout = "out/nohup_eval_" + exp_suffix + ".out"
    fstderr = "out/nohup_eval_" + exp_suffix + ".err"
    return (c, fstdout, fstderr)


def _get_all_commands(run_ids, dataset, pow_types, ccap_lst=CCAP_LIST):
    available_gpus = cycle(_get_available_gpus())
    #available_gpus = cycle([1,3,5])
    
    selected_table = EXP_CONFIG[dataset]
    selected_setting_file_int = selected_table['INTPOW_EXP_SETTINGS_FILE']
    selected_setting_file_cont = selected_table['CONTPOW_EXP_SETTINGS_FILE']

    # generate commands (a batch per gpu)
    cmd_batches = {}
    cnt = 0

    # --- INTPOW has unique TS values per energy budget (energy-aware), CONTPOW has only one set of ts values (energy-unaware)
    for each_run_id in run_ids:
        for each_pow_type in pow_types:
            
            if (each_pow_type == "INTPOW"):
                #for each_ccap in selected_table[each_pow_type].keys():
                for each_ccap in ccap_lst:
                    for each_ts in selected_table[each_pow_type][each_ccap]:                            
                        gpuid = next(available_gpus)
                        if gpuid not in cmd_batches: cmd_batches[gpuid] = []                

                        setting_fname = selected_setting_file_int if "INT" in each_pow_type else selected_setting_file_cont
                        exp_suffix = SPECIAL_CASE_SUFFIX + each_pow_type.lower() + "_" + dataset + "_" + "cap" + str(each_ccap).replace("0.", "") + "_" + "ts" + str(each_ts).replace(".", "") + "_run" + str(each_run_id)
                        #exp_suffix = exp_suffix.replace("0.0", "") # get rid of zeros in 

                        cmd, fstdout, fstderr = _construct_command(dataset, each_ccap, each_ts, gpuid, setting_fname, exp_suffix)

                        if _is_already_complete(fstdout) == False:
                            cmd_batches[gpuid].append([cmd, fstdout, fstderr, gpuid]); cnt+=1
                        else:
                            pass 
            
            elif (each_pow_type == "CONTPOW"):
                for each_ts in selected_table[each_pow_type]["NoEn"]:
                    gpuid = next(available_gpus)
                    if gpuid not in cmd_batches: cmd_batches[gpuid] = []                

                    setting_fname = selected_setting_file_int if "INT" in each_pow_type else selected_setting_file_cont
                    exp_suffix = SPECIAL_CASE_SUFFIX + each_pow_type.lower() + "_" + dataset + "_" + "cap" + "NoEn" + "_" + "ts" + str(each_ts).replace(".", "") + "_run" + str(each_run_id)                        
                    
                    cmd, fstdout, fstderr = _construct_command(dataset, -1, each_ts, gpuid, setting_fname, exp_suffix)

                    if _is_already_complete(fstdout) == False:
                        cmd_batches[gpuid].append([cmd, fstdout, fstderr, gpuid]); cnt+=1
                    else:
                        pass
    
    return cmd_batches



# remapping on full fact params test
def run_main(run_ids, dataset, powtype):    

    cmd_batches = _get_all_commands(run_ids, dataset, powtype)

    #pprint(cmd_batches)      
    #sys.exit()
    
    # allocate to threads - each thread handles a batch on a dedicated GPU
    processes = []
    for gpuid, each_cmd_batch in cmd_batches.items():

        p = multiprocessing.Process(target=worker_thread, args=(gpuid, each_cmd_batch))
        processes.append(p)                
        
    print("Starting processes..")
    for i, p in enumerate(processes):
        p.start()

    # Ensure all of the processes have finished
    print("Joining processes")
    for i, p in enumerate(processes):
        p.join()      

   
def list_incomplete(cmd_list):
    incomplete = []
    count = 0
    for each_cmd in cmd_list:
        cmd = each_cmd[0]
        fstdout = each_cmd[1]
        if _is_already_complete(fstdout) == False:
            incomplete.append(cmd)
            count+=1
        else:
            pass
    
    print("Total incomplete : ", len(incomplete))
    pprint(incomplete)
    print()



def arg_parser():
    setting_selection = {}
    parser = argparse.ArgumentParser('Parser User Input Arguments')
    parser.add_argument('--runids', nargs='+', type=int, default=[],  help="run ids")    
    parser.add_argument('-d', '--dataset', type=str, default=argparse.SUPPRESS,  help="dataset")
    parser.add_argument('-p', '--powtype', type=str, default=argparse.SUPPRESS,  help="power types")
    args = parser.parse_args()

    if 'runids' in args: setting_selection['run_ids'] = args.runids 
    else: sys.exit("Run ids not given")

    if 'dataset' in args: setting_selection['dataset'] = args.dataset
    else: sys.exit("Dataset not given")

    if 'powtype' in args: 
        setting_selection['powtype'] = [args.powtype]
    else:
        setting_selection['powtype'] = ["INTPOW", "CONTPOW"]
    

    return setting_selection



if __name__ == "__main__":

    setting_selection = arg_parser()

    run_main(setting_selection['run_ids'], setting_selection['dataset'], setting_selection['powtype'])
    #list_incomplete(_get_all_commands())

    print("\n------ All jobs complete ------\n\n")

