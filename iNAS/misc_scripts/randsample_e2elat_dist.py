import sys, os
sys.path.append("..")
from pprint import pprint
import operator
import multiprocessing
import time
from collections import OrderedDict 
import statistics

import numpy as np
import tensorflow as tf

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from NASBase.plat_perf import PlatPerf
from NASBase.model import model_fn_conv2D, model_fn_conv1D, model_fn_fc
from DNNDumper.file_utils import json_dump, json_load, dir_create

from misc_scripts.query_e2elat_minmax import get_latency_for_actions, _action_mult

from run_scripts.run_batch_generic import REHM_TABLE


# script to random sample from solution space and get children to derive TS

SEED = 1234
SAVE_LOC = "misc_scripts/random_sampling/2KBVM/"

SAMPLE_SIZE = 5000
BATCH_SIZE = 30
JOBS_PER_PROCESS = 5

DATASET = "kws"
POW_TYPE_TO_COMPUTE = "INT"
FNAME_PREFIX = "randsample_res_" + DATASET


LOAD_DATA = True


PLATFORM_SETTINGS = {
    'MCU_TYPE' : 'MSP430',   # MSP430   |  MSP432
    'CCAP' : 0.001, # capacitance (F)
    'REHM' : 62.0,  # ehm equivalent resistance (ohm)
    'VON' : 2.99, # (V)
    'VOFF' : 2.8, # (V)
    'VSUP' : 3.0, # (V)
    'EAV_SAFE_MARGIN' : 0.55, # pessimistic safety margin - available energy will be reduced by this ratio
    'VM_CAPACITY' : (4096-2048), 
    'NVM_CAPACITY' : 1000000,
    'DATA_SZ' : 2, # data size in bytes
    'CPU_CLOCK': 16000000, 
    'LAT_E2E_REQ' : 100000000000, # by default no e2e latency req, so set to high
    'POW_TYPE' : 'INT'
}


# ---- for CIFAR 
if DATASET == "cifar":
    NAS_SETTINGS = {
        "CONV_NUM_FILTERS" : [4, 8, 16, 24],    
        "CONV_KERNEL_SIZES" : [1, 3, 5, 7],
        'IMG_SIZE': 32,
        'IMG_CHANNEL': 3,
        'NUM_LAYERS': 5,
        'NUM_CLASS': 10,
        "DATASET" : "CIFAR10",
        'MODEL_FN_TYPE' : 'MODEL_FN_CONV2D',
        'SEED'  : 1, 
        'DETERMINISTIC_FLOW'  : False
    }

# ---- for HAR 
elif DATASET == "har":
    NAS_SETTINGS = {
        "CONV_NUM_FILTERS" : [4, 8, 16, 24],    
        "CONV_KERNEL_SIZES" : [1, 3, 5, 7],
        "IMG_CHANNEL" : 9, 
        "IMG_SIZE" : 128,
        "NUM_LAYERS": 3,
        "NUM_CLASS" : 6,    
        "DATASET" : "HAR",        
        "MODEL_FN_TYPE" : "MODEL_FN_CONV1D",        
        'SEED'  : 1, 
        'DETERMINISTIC_FLOW'  : False
    }

# ---- for KWS
elif DATASET == "kws":
    NAS_SETTINGS = {
        "CONV_NUM_FILTERS" : [48, 64, 96, 128],
        "CONV_KERNEL_SIZES" : [],
        "IMG_CHANNEL" : 1, 
        "IMG_SIZE" : 250,
        "NUM_LAYERS": 4,
        "NUM_CLASS" : 12,
        "DATASET" : "KWS",        
        "MODEL_FN_TYPE" : "MODEL_FN_FC",
        'SEED'  : 1, 
        'DETERMINISTIC_FLOW'  : False
    }
else:
    sys.exit(DATASET + " - not supported yet")





CCAP_LIST = [0.001, 0.005, 0.01]

PERC_RANGES = [0.25, 0.50, 0.75]   # 25%, 50% , 75% of the feasible solutions





#####################################################################
#   HELPERS
#####################################################################
def _action_str_to_list(action_str):
    return [int(a) for a in action_str.split("_")]
def _action_list_to_str(action):
    return "_".join([str(x) for x in action])

def _chunkify(items, chunk_len):
    return [items[i:i+chunk_len] for i in range(0,len(items),chunk_len)]

def _get_model_fn(model_fn_type):
    if model_fn_type == 'MODEL_FN_CONV2D':
        return model_fn_conv2D
    elif model_fn_type == 'MODEL_FN_CONV1D':
        return model_fn_conv1D                            
    elif model_fn_type == 'MODEL_FN_FC':
        return model_fn_fc        
    else:
        sys.exit('unknown model fn type')
    

def get_max_sample_size():
    kernel_sizes = NAS_SETTINGS["CONV_KERNEL_SIZES"]
    filter_sizes = NAS_SETTINGS["CONV_NUM_FILTERS"]
    num_layers = NAS_SETTINGS["NUM_LAYERS"]

    if len(kernel_sizes) > 0:
        maxss= (len(kernel_sizes) * len(filter_sizes))**num_layers  
    else:
        maxss= len(filter_sizes)**num_layers  

    return maxss


def get_children_latency(children, power_type):
    PLATFORM_SETTINGS['POW_TYPE'] = power_type
    performance_model = PlatPerf(NAS_SETTINGS, PLATFORM_SETTINGS)  
    result_latencies = []  
    for each_child in children:
        actions = each_child[0]
        time_performance, exec_design, error = performance_model.get_inference_latency(actions)
        if exec_design != None:
            result_latencies.append(round(time_performance,1))
    return result_latencies

#####################################################################
#   VISUAL
#####################################################################
# population: dic (action: lat)
def plot_lat_dist(population, title, ts_lats=[]):
    print("plot_lat_dist:: enter : ", title)    
    latencies = [v for k,v in population.items()]    
    
    sns.set(style="ticks")
    f, (ax_box, ax_hist) = plt.subplots(2, sharex=True, gridspec_kw={"height_ratios": (.15, .85)})

    sns.boxplot(latencies, ax=ax_box)
    sns.histplot(latencies, ax=ax_hist, bins =100)

    ax_box.set(yticks=[])
    sns.despine(ax=ax_hist)
    sns.despine(ax=ax_box, left=True)
    plt.title(title)

    for ts in ts_lats:
        ax_hist.axvline(ts, color='r', linestyle='--')
    



#####################################################################
#   WHERE IS MY CHILD ?
#####################################################################
# get child position according to pow type model
def get_child_position(children, query_children):
    # sorted according new power type
    sorted_children =  sorted(children.items(), key=lambda kv: kv[1])
    positions = []
    for each_query_child in query_children:
        for pos, each_child in enumerate(sorted_children):
            if each_child[0] == _action_list_to_str(each_query_child):            
                positions.append(pos/len(sorted_children))
                break;
    return positions
            
  


#####################################################################
#   SELECTION
#####################################################################
def select_children(children, perc_ranges):    
    # sort children by latency
    sorted_children =  sorted(children.items(), key=lambda kv: kv[1])
    latencies = [child[1] for child in sorted_children]    
    pop_size = len(sorted_children)
    selected_children = []
    for each_perc in perc_ranges:
        pos = int(np.ceil(each_perc * pop_size)) - 1
        child_action = [int(a) for a in sorted_children[pos][0].split("_")]
        lat = sorted_children[pos][1]
        selected_children.append([child_action, round(lat,2)])
    return selected_children





#####################################################################
#   EVAL FUNCs
#####################################################################

def run_eval_single(count, jobs, model_fn, platform_settings, nas_settings, fout):        
    tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR) # hide deprecated warnings
    results = []
    for actions, actions_str in jobs:        
        model, error = model_fn(actions, plat_settings = platform_settings, nas_settings = nas_settings )  # type: Model, int
        if error == 0:
            performance_model = PlatPerf(nas_settings, platform_settings)
            time_performance, exec_design, error = performance_model.get_inference_latency(actions)
            if exec_design != None:
                #pprint(exec_design)
                results.append((count, actions_str, time_performance))                
                print("Finished child: ", count, actions_str, time_performance) 
            else:
                pass # error
        else:
            pass
    
    fout.put(results) # save result

    return 0

def get_child_best_design(child_actions, platform_settings, nas_settings):
    performance_model = PlatPerf(nas_settings, platform_settings)
    time_performance, exec_design, error = performance_model.get_inference_latency(child_actions)
    return exec_design



#####################################################################
#   BATCHED SAMPLING / FIXED POP
#####################################################################

#count= (len(kernel_sizes) + len(filter_sizes))**num_layers    
def get_randsample_childnet_latency(nas_settings, platform_settings, sample_size = 10000, batchsize=5, jobs_per_process=10):
    print("get_randsample_childnet_latency::Enter")   

    kernel_sizes = nas_settings["CONV_KERNEL_SIZES"]
    filter_sizes = nas_settings["CONV_NUM_FILTERS"]
    num_layers = nas_settings["NUM_LAYERS"]
    model_fn_type = nas_settings["MODEL_FN_TYPE"]
    performance_model = PlatPerf(nas_settings, platform_settings)
    sampled_children = {}
    child_count = 0
    eval_child_count = 0
    batch_count = 0

    model_fn = _get_model_fn(model_fn_type)
    
    while(child_count < sample_size):
        print("Trying another batch [%d] - current count: %d/%d " % (batch_count, child_count, sample_size))
        
        # run batch            
        processes = []
        fout = multiprocessing.Queue() # shared queue
        for i in range(batchsize):
            jobs = []
            for j in range(jobs_per_process):                
                child = []
                # create child
                for l in range(num_layers):

                    if model_fn_type == 'MODEL_FN_CONV2D':                                  
                        ks = int(np.random.choice(kernel_sizes))
                        fs = int(np.random.choice(filter_sizes))
                        child.extend([ks, fs])                         
                    
                    elif model_fn_type == 'MODEL_FN_CONV1D':                                
                        ks = int(np.random.choice(kernel_sizes))
                        fs = int(np.random.choice(filter_sizes))
                        child.extend([ks, fs])        

                    elif model_fn_type == 'MODEL_FN_FC':                                            
                        fs = int(np.random.choice(filter_sizes))
                        child.extend([fs])        
                    else:
                        sys.exit('unknown model fn type')
                            
                child_str = "_".join(str(x) for x in child) # child in str format
                
                if child_str not in sampled_children:
                    jobs.append([child, child_str])

            
            #print("Creating process - ", eval_child_count)
            process = multiprocessing.Process(target=run_eval_single, args=(eval_child_count, jobs, model_fn, platform_settings, nas_settings, fout))
            processes.append(process)
            eval_child_count += jobs_per_process            

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
                    each_actions_str = res[1]; each_time_performance = res[2]                    
                    if each_actions_str not in sampled_children:
                        sampled_children[each_actions_str] = each_time_performance                    
        
        if not fout.empty(): sys.exit("Queue is not empty at the end of batch = " + str(batch_count))            

        fout.close()
        print("------Finished batch = ", batch_count)
                
        child_count = len(sampled_children.keys())
        batch_count+=1          

    return sampled_children





#####################################################################
#   RANDOM SAMPLING MAIN
#####################################################################
def random_sample_population(pow_type, ccap=None):
    print ("\nStarting.....", pow_type, ccap)

    PLATFORM_SETTINGS["POW_TYPE"] = pow_type
    PLATFORM_SETTINGS["CCAP"] = ccap
    PLATFORM_SETTINGS["REHM"] = REHM_TABLE[DATASET][str(ccap)]

    if ccap != None:            
        fname = SAVE_LOC + FNAME_PREFIX + "_" + PLATFORM_SETTINGS["POW_TYPE"] + "_ccap" + str(PLATFORM_SETTINGS['CCAP']) + ".json"
    else:
        fname = SAVE_LOC + FNAME_PREFIX + "_" + PLATFORM_SETTINGS["POW_TYPE"] + ".json"
    
    
    sample_size = min(SAMPLE_SIZE, get_max_sample_size())
    print("SAMPLE SIZE = ", sample_size)
    print("BATCH SIZE = ", BATCH_SIZE)
    print("JHOBS PER PROCESS = ", JOBS_PER_PROCESS)

    child_lat_dist = get_randsample_childnet_latency(NAS_SETTINGS, PLATFORM_SETTINGS, sample_size = sample_size, batchsize=BATCH_SIZE, jobs_per_process=JOBS_PER_PROCESS)                

    
    print ("\n\nEval complete ! Num feasible children evaluated: ", len(child_lat_dist.keys()))            
    print("dumping result : ", fname)    
    json_dump(fname, child_lat_dist)
    print ("-------------------------------------------------\n\n")





def get_fixedpopulation_childnet_latency(children_pop, nas_settings, platform_settings, batchsize=10):
    print("get_fixedpopulation_childnet_latency::Enter - pop size = ", len(children_pop))
    kernel_sizes = nas_settings["CONV_KERNEL_SIZES"]
    filter_sizes = nas_settings["CONV_NUM_FILTERS"]
    num_layers = nas_settings["NUM_LAYERS"]
    model_fn_type = nas_settings["MODEL_FN_TYPE"]
    performance_model = PlatPerf(nas_settings, platform_settings)
    calculated_children = {}
    child_count = 0
    eval_child_count = 0
    batch_count = 0
    result_children = {}

    model_fn = _get_model_fn(model_fn_type)

    # split pop into batches - allocate each batch to a thread
    #pprint(children_pop); sys.exit()
    #chunk_len = len(children_pop) / batchsize
    #batched_children_pop = np.array_split(children_pop, batchsize)

    pop_size = len(children_pop)
    pcount = 0
    while(child_count < pop_size):
        pjobs = []
        fout = multiprocessing.Queue() # shared queue        
        for ix in range(pcount, pcount+batchsize): 
            #print(ix, pcount)
            if ix  < len(children_pop):            
                child_str = children_pop[ix][0]
                child = _action_str_to_list(child_str)
                process = multiprocessing.Process(target=run_eval_single, args=(pcount, child, child_str, model_fn, platform_settings, nas_settings, fout))
                pjobs.append(process)
                pcount +=1        
            else:
                pass
        
        print("Starting jobs..")
        for i, p in enumerate(pjobs):
            p.start()

        # Ensure all of the processes have finished
        print("Joining jobs")
        for i, p in enumerate(pjobs):
            p.join()
        
        time.sleep(1)

        # get results
        print("fout.qsize() : ", fout.qsize())
        for p in pjobs:
            if fout.qsize() > 0: # if not checked, then may hang waiting for a get()
                (count, actions_str, time_performance) = fout.get()
                if actions_str not in result_children:
                    result_children[actions_str] = time_performance
        
        if not fout.empty(): sys.exit("Queue is not empty at the end of batch = " + str(batch_count))            

        fout.close()
        print("------Finished batch = ", batch_count)
        print("------result size = ", len(result_children.keys()))
        
        child_count = len(result_children.keys())
        batch_count+=1          

    if len(result_children.keys()) != len(children_pop):
        print("WARNING: incomplete child population : ", len(result_children.keys()), len(children_pop))            
    
    return result_children



# simply report 3 selected children from the INT and CONT populations
# children at different perc positions
def ts_selection_technique_v2(ccap_lst):
    out_excel_txt = ""
    out_py_txt = ""

    print(PERC_RANGES)
    # ---- report child selection - for INT
    for each_ccap in ccap_lst:
        PLATFORM_SETTINGS["CCAP"] = each_ccap        
    
        PLATFORM_SETTINGS["POW_TYPE"] = "INT"
        fname = SAVE_LOC + FNAME_PREFIX + "_" + PLATFORM_SETTINGS["POW_TYPE"] + "_ccap" + str(PLATFORM_SETTINGS['CCAP']) + ".json"          
        inas_children_pop = json_load(fname)

        print("----- For INT: ccap=", PLATFORM_SETTINGS['CCAP'])
        print(fname)      
        result_children = select_children(inas_children_pop, PERC_RANGES)
        result_children_str = ",".join(["_".join([str(cc) for cc in c[0]]) for c in result_children])

        #print("POP_SIZE: ", len(inas_children_pop))
        
        #print ("selected children: "); print(["_".join([str(cc) for cc in c[0]]) for c in result_children])
        #print ("corresponding latencies: ")
        int_ts_lats = ", ".join([str(c[1]) for c in result_children])

        out_excel_txt += result_children_str + ",," + int_ts_lats + "\n"
        out_py_txt += "\"" + str(each_ccap) + "\"" + " : [" + int_ts_lats + "]," + "\n"


    print()
    print("-- EXCEL format: children actions per TS , TS values:\n")
    print(out_excel_txt)
    print("\n\n-- PYTHON format: cap size, TS values:\n")
    print(out_py_txt)
    print()

    # ---- report child selection - for CONT
    PLATFORM_SETTINGS["POW_TYPE"] = "CONT"
    fname = SAVE_LOC + FNAME_PREFIX + "_" + PLATFORM_SETTINGS["POW_TYPE"] + ".json"  
    print(fname)      
    cont_children_pop = json_load(fname)

    print("\n----- For CONT: ccap=", PLATFORM_SETTINGS['CCAP'])
    result_children = select_children(cont_children_pop, PERC_RANGES)

    print("POP_SIZE: ", len(cont_children_pop))
    print(PERC_RANGES)
    print ("selected children: "); print(["_".join([str(cc) for cc in c[0]]) for c in result_children])
    print ("corresponding latencies: ")
    cont_ts_lats = [c[1] for c in result_children]; pprint(cont_ts_lats)







if __name__ == '__main__':

    np.random.seed(SEED) # set random seed

    if LOAD_DATA == False:
        dir_create(SAVE_LOC)

        # -- intermittent power --
        if (POW_TYPE_TO_COMPUTE == "INT"):
            for each_ccap in CCAP_LIST:
                random_sample_population(POW_TYPE_TO_COMPUTE, ccap=each_ccap)                

        # -- continuous power --            
        elif (POW_TYPE_TO_COMPUTE == "CONT"):
            random_sample_population(POW_TYPE_TO_COMPUTE)

    
    else:
        
        ts_selection_technique_v2(CCAP_LIST)

        
        # ----- [SPECIAL] take children and find baseline latency ------
        # print("------ Child latencies according to CONT: ")
        # FNAME_PREFIX = "fixedsample_res_cifar"
        # PLATFORM_SETTINGS["POW_TYPE"] = "CONT"
        # child_lat_dist = get_fixedpopulation_childnet_latency(list(children_pop.items()), NAS_SETTINGS, PLATFORM_SETTINGS, batchsize=32)
        # fname = SAVE_LOC + FNAME_PREFIX + "_" + PLATFORM_SETTINGS["POW_TYPE"] + ".json"
        # print("dumping result : ", fname)    
        # json_dump(fname, child_lat_dist)
                

        # ----- find position of selected children according to baseline latency model
        # print("------ Child positions according to CONT: ")
        # FNAME_PREFIX = "fixedsample_res_cifar"
        # PLATFORM_SETTINGS["POW_TYPE"] = "CONT"
        # fname = SAVE_LOC + FNAME_PREFIX + "_" + PLATFORM_SETTINGS["POW_TYPE"] + ".json"
        # children_pop = json_load(fname)       
        
        
        # query_children = [child[0] for child in result_children]; print(query_children)
        # child_positions = get_child_position(children_pop, query_children)
        # pprint(child_positions)
        



        
    