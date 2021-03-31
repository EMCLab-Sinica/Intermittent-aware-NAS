import sys, os
from pprint import pprint
import operator
import multiprocessing
import time
from collections import OrderedDict 

import json

import numpy as np
import tensorflow as tf

import pandas as pd


sys.path.append("..")
from NASBase.plat_perf import PlatPerf
from NASBase.model import get_model_fn_by_dataset
from DNNDumper.file_utils import json_dump, json_load, dir_create
from settings import _update_settings, Settings
from misc_scripts.query_e2elat_minmax import get_latency_for_actions, _action_mult


from run_scripts.run_batch_generic import EXP_CONFIG as RUN_EXP_CONFIG
from run_scripts.run_batch_generic import REHM_TABLE

BASE_CCAP = "0.01"
BASE_TS = "ts3" # TS1=0, TS2=1, TS3=2

EVAL_DATASETS = ['cifar', 'har', 'kws']
SINGLE_EVAL_DATASET = 'cifar'

# range of capacitors and vm sizes
CCAP_LIST = np.arange(0.0002, 0.03+0.0002, 0.0002)
VM_CAPACITY_LIST = [128,256,512]+list(np.arange(1024, 16384+512, 512))

#CCAP_LIST = [0.001, 0.005, 0.01]
#VM_CAPACITY_LIST = [512, 1024, 2048, 4096]

BATCH_SIZE = 30
JOBS_PER_PROCESS = 2

DATA_SOL_DIR = "solution_dump/eval/"
DSE_RES_DIR = "solution_dump/dse/"



#####################################################################
#   HELPER
#####################################################################
def _net_exec_design_to_str(net_exec_design):        
    s = "|".join([l['params'] for l in net_exec_design])
    return s


# get best sols from primary experiments
def get_best_sol_network(dataset, dataset_sols_fname):
    data = json_load(dataset_sols_fname)    
    
    # find and return correct case
    action = data[dataset]["INTPOW"][BASE_CCAP][BASE_TS]["action"]

    # construct network
    exp_settings_obj = construct_full_settings_obj(RUN_EXP_CONFIG[dataset]['INTPOW_EXP_SETTINGS_FILE'])           
    pp = PlatPerf(exp_settings_obj.NAS_SETTINGS, exp_settings_obj.PLATFORM_SETTINGS)        
    model_fn_type = get_model_fn_by_dataset(dataset)

    network_layers = pp.get_network(action, model_fn_type=exp_settings_obj.NAS_SETTINGS['MODEL_FN_TYPE'])

    return network_layers, action


def construct_full_settings_obj(exp_settings_file, ccap=None, latreq=None):
    # load json
    if os.path.exists(exp_settings_file):
        json_data=open(exp_settings_file)
        settings_json = json.load(json_data)        
    else:
        sys.exit("ERROR - file does not exist : " + exp_settings_file)
        
    exp_settings = Settings() # get default settings

    # update default settings
    if 'GLOBAL_SETTINGS' in settings_json:
        exp_settings.GLOBAL_SETTINGS = _update_settings(exp_settings.GLOBAL_SETTINGS, settings_json['GLOBAL_SETTINGS'])
    if 'CUDA_SETTINGS' in settings_json:
        exp_settings.CUDA_SETTINGS = _update_settings(exp_settings.CUDA_SETTINGS, settings_json['CUDA_SETTINGS'])
    if 'PLATFORM_SETTINGS' in settings_json:
        exp_settings.PLATFORM_SETTINGS = _update_settings(exp_settings.PLATFORM_SETTINGS, settings_json['PLATFORM_SETTINGS'])
    if 'NAS_SETTINGS' in settings_json:
        exp_settings.NAS_SETTINGS = _update_settings(exp_settings.NAS_SETTINGS, settings_json['NAS_SETTINGS'])
    if 'DUMPER_SETTINGS' in settings_json:
        exp_settings.DUMPER_SETTINGS = _update_settings(exp_settings.DUMPER_SETTINGS, settings_json['DUMPER_SETTINGS'])
    if 'DUMPER_SETTINGS' in settings_json:
        exp_settings.LOG_SETTINGS = _update_settings(exp_settings.LOG_SETTINGS, settings_json['LOG_SETTINGS'])

    # override experiment cmd settings
    if ccap != None:    
        exp_settings.PLATFORM_SETTINGS['CCAP'] = ccap
    if latreq != None:        
        exp_settings.PLATFORM_SETTINGS['LAT_E2E_REQ'] = latreq
            
    return exp_settings


#####################################################################
#   WORKER THREAD
#####################################################################
# find latenc and data access cost for the param combo
def run_eval_single(dataset, action, jobs, platform_settings, nas_settings, fout):           
    results = []
    for j_ix, j_pccap, j_vmsize in jobs: 
        jix = int(j_ix)
        ccap = j_pccap
        vmsize = int(j_vmsize)
        
        platform_settings['CCAP'] = ccap
        platform_settings['VM_CAPACITY'] = vmsize
        platform_settings['REHM'] =  0.50
                       
        performance_model = PlatPerf(nas_settings, platform_settings)        
        net_late2e, net_exec_design, error = performance_model.get_inference_latency(action)
        
        if error == None:
            net_data_access_cost = performance_model.get_network_data_access_cost(action, net_exec_design)            
            results.append({
                'perm' : [jix, ccap, vmsize],                 
                'sol':  _net_exec_design_to_str(net_exec_design),
                'late2e' : net_late2e,
                'dcost' : net_data_access_cost
            })                
            print("Finished child: ", jix, ccap, vmsize, net_late2e, _net_exec_design_to_str(net_exec_design))
        else:
            print("Finished child - INFEASIBLE: ", jix, ccap, vmsize, action, None)
            results.append({
                'perm' : [jix, ccap, vmsize],
                'sol': None,                
            })              
        
    fout.put(results) # save result

    return 0


#####################################################################
#   CREATE AND SPAWN THREADS
#####################################################################
def launch_dse_jobs(dataset, dataset_sols_fname, batchsize=2, jobs_per_process=4):
    print("launch_dse_jobs::Enter")   

    # prep nas/plat settings
    exp_settings_obj = construct_full_settings_obj(RUN_EXP_CONFIG[dataset]['INTPOW_EXP_SETTINGS_FILE'])      
    nas_settings = exp_settings_obj.NAS_SETTINGS
    platform_settings = exp_settings_obj.PLATFORM_SETTINGS
   
    # find best solution actions
    network_layers, action = get_best_sol_network(dataset, dataset_sols_fname)
    
    # ---- for all permutations of capacitors and vm size
    all_jobs = []
    jix = 0
    for each_ccap in CCAP_LIST:
        for each_vmsize in VM_CAPACITY_LIST:
            all_jobs.append((jix, each_ccap, each_vmsize))
            jix +=1
 
    # ---- split into batches
    print("total permutations: ", np.shape(all_jobs))    
    all_jobs = np.array(all_jobs)
    
    batched_all_jobs = all_jobs.reshape((int(all_jobs.size/(batchsize*jobs_per_process*3)), batchsize, jobs_per_process,3))

    pprint(batched_all_jobs); 
    
    # dispatch batched jobs
    all_results = []
    for bix, each_batch in enumerate(batched_all_jobs):
        processes = []
        fout = multiprocessing.Queue() # shared queue
        for each_process_jobs in each_batch:

            process = multiprocessing.Process(target=run_eval_single, args=(dataset, action, each_process_jobs, platform_settings, nas_settings, fout))
            processes.append(process)

        print("Starting jobs..")
        for i, p in enumerate(processes):            
            p.start()

        # Ensure all of the processes have finished
        print("Joining jobs")        
        for i, p in enumerate(processes):
            p.join()
        
        time.sleep(1)

        # get results
        print("fout.qsize() : ", fout.qsize())
        for p in processes:
            if fout.qsize() > 0: # if not checked, then may hang waiting for a get()
                results_lst = fout.get()
                for res in results_lst:
                    all_results.append(res)                                        
        
        if not fout.empty(): sys.exit("Queue is not empty at the end of batch = " + str(bix))            

        fout.close()
        print("------Finished batch = ", bix, " : all_results length = ", len(all_results))

    return all_results


if __name__ == '__main__':

    for dataset in EVAL_DATASETS:
    
        dataset_sols_fname = DATA_SOL_DIR + dataset + "/" + "all_data_" + dataset + ".json"
        all_results = launch_dse_jobs(dataset, dataset_sols_fname, batchsize=BATCH_SIZE, jobs_per_process=JOBS_PER_PROCESS)

        # save results    
        fname = DSE_RES_DIR + "dse_result_" + dataset + ".json"
        json_dump(fname, all_results)