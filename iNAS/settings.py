import argparse
import json
import os, sys

## default settintgs & description
class Settings: 
    
    GLOBAL_SETTINGS = {
        'EXP_SUFFIX' : ""   # experiment name suffix
    }    
    
    # ----------------------------------------------------
    # CUDA SETTINGS
    # ----------------------------------------------------
    CUDA_SETTINGS = {
        'GPUID' : "0", # GPU card
    }   
    # ----------------------------------------------------
    # PLATFORM SPECIFIC SETTINGS
    # ----------------------------------------------------
    PLATFORM_SETTINGS = {
        'MCU_TYPE' : 'MSP430',   # MSP430   |  MSP432
        'CCAP' : 0.005, # capacitance (F)
        'REHM' : 300.0,  # ehm equivalent resistance (ohm)
        'VON' : 2.99, # (V)
        'VOFF' : 2.8, # (V)
        'VSUP' : 3.0, # (V)
        'EAV_SAFE_MARGIN' : 0.55, # energy budget safety margin
        'VM_CAPACITY' : (4096-2048),         
        'NVM_CAPACITY' : 1000000,
        'DATA_SZ' : 2, # data size in bytes
        'CPU_CLOCK': 16000000, 
        'LAT_E2E_REQ' : 100000, # by default no e2e latency req, so set to high
        'POW_TYPE' : 'INT'
    }

    # ----------------------------------------------------
    # NAS TOOL SETTINGS 
    # ----------------------------------------------------
    NAS_SETTINGS = {        
        'SEED'  : 1,    # seed used to initialize the randomizers
        'DETERMINISTIC_FLOW'  : False,
        'CONV_NUM_FILTERS' : [4, 8, 16, 24],    
        'CONV_KERNEL_SIZES' : [1, 3, 5, 7],
        'NUM_LAYERS': 5,    # number of layers of the state space
        'NUM_CLASS' : 10,
        'EPOCH': 25,    # maximum number of epochs to train the DNN Trainer
        'TRIALS': 100,  # maximum number of child networks generated
        'CHILD_BATCHSIZE' : 256, # batchsize of the child models
        'EXPLORATION' : 0.1,  # high exploration
        'REGULARIZATION' : 1e-3,  # regularization strength
        'CONTROLLER_CELLS' : 32,  # number of cells in RNN controller
        'EMBEDDING_DIM' : 20,  # dimension of the embeddings for each state
        'ACCURACY_BETA' : 0.8,  # beta value for the moving average of the accuracy
        'CLIP_REWARDS' : 0.0,  # clip rewards in the [-0.05, 0.05] range
        'RESTORE_CONTROLLER' : False,  # restore controller to continue training
        'DATASET' : 'CIFAR10',
        'IMG_CHANNEL' : 3, 
        'IMG_SIZE' : 32,
        'MODEL_FN_TYPE' : 'MODEL_FN_CONV2D',      # [MODEL_FN_CONV2D | MODEL_FN_CONV1D | MODEL_FN_FC]
    }

    # ----------------------------------------------------
    # DNN DUMPER SETTINGS
    # ----------------------------------------------------
    DUMPER_SETTINGS = {
        'DUMP_DIR' : '' #<where to store the solutions (*.h5 model, *.h model)
    }

    # ----------------------------------------------------
    # DNN DUMPER SETTINGS
    # ----------------------------------------------------
    LOG_SETTINGS = {    
        'TRIAL_LOG_DIR' : "trial_log",
        'TRIAL_LOG_FNAME' : "trial_info.csv", 
        'LOG_LEVEL' : 1    
    }

    def __str__(self):
        return  "GLOBAL_SETTINGS:=" + "\n" + str(self.GLOBAL_SETTINGS) + "\n" + \
                "CUDA_SETTINGS:=" + "\n" + str(self.CUDA_SETTINGS) + "\n" + \
                "PLATFORM_SETTINGS:=" + "\n" + str(self.PLATFORM_SETTINGS)+ "\n" + \
                "NAS_SETTINGS:=" + "\n" + str(self.NAS_SETTINGS)+ "\n" + \
                "DUMPER_SETTINGS:=" + "\n" + str(self.DUMPER_SETTINGS)+ "\n" + \
                "LOG_SETTINGS:=" + "\n" + str(self.LOG_SETTINGS)+ "\n" 



def load_settings(fname):
    # load json
    if os.path.exists(fname):
        json_data=open(fname)
        file_data = json.load(json_data)
        return file_data
    else:
        sys.exit("ERROR - file does not exist : " + fname)
        return None


def _update_settings(default_settings, new_settings):
    for k, v in new_settings.items():
        default_settings[k] = v # adds new items, overwrites existing items    
    return default_settings


def arg_parser(test_settings):
    parser = argparse.ArgumentParser('Parser User Input Arguments')
    parser.add_argument('-g', '--gpuid',    type=int, default=argparse.SUPPRESS,  help="GPU selection")
    #parser.add_argument('-d', '--dataset',  type=str,  default=argparse.SUPPRESS,  help="supported dataset including : 1. MNIST, 2. CIFAR10 (default). 3 TinyIMAGENET")
    #parser.add_argument('-l', '--layers',   type=int, default=argparse.SUPPRESS, help="the number of child network layers, default is 6")
    #parser.add_argument('-e', '--epochs',   type=int, default=argparse.SUPPRESS, help="the total epochs for model fitting, default is 30")
    #parser.add_argument('-t', '--trial',    type=int, default=argparse.SUPPRESS, help="the maximum number of models generated, default is 10")
    #parser.add_argument('-b', '--batch_size', type=int, default=argparse.SUPPRESS, help="the batch size used to train the child CNN, default is 128")
    
    parser.add_argument('-c', '--ccap',    type=float, default=argparse.SUPPRESS,   help="capacitor size")
    parser.add_argument('-l', '--latreq',    type=float, default=argparse.SUPPRESS,   help="end-to-end latency requirement")
    parser.add_argument('--rehm',   type=float, default=argparse.SUPPRESS,   help="EHM equivalent resistance")


    
    parser.add_argument('-d', '--seed',    type=int, default=argparse.SUPPRESS,   help="seed for randomness, default is 123")
    parser.add_argument('-f', '--suffix',   type=str, default=argparse.SUPPRESS,   help="experiment run name suffix")
    parser.add_argument('-s',  '--settings', type=str, default=argparse.SUPPRESS, help="settings file to load")
    parser.add_argument('-r', '--fixed',    type=bool, default=argparse.SUPPRESS,   help="fixed flow for run to run")

    args = parser.parse_args()

    
    # first apply settings file
    if 'settings' in args:
        print('ARG_IMPORT_SETTINGS : %s'%(args.settings))
        settings_json = load_settings(args.settings)
    
        if 'GLOBAL_SETTINGS' in settings_json:
            test_settings.GLOBAL_SETTINGS = _update_settings(test_settings.GLOBAL_SETTINGS, settings_json['GLOBAL_SETTINGS'])
        if 'CUDA_SETTINGS' in settings_json:
            test_settings.CUDA_SETTINGS = _update_settings(test_settings.CUDA_SETTINGS, settings_json['CUDA_SETTINGS'])
        if 'PLATFORM_SETTINGS' in settings_json:
            test_settings.PLATFORM_SETTINGS = _update_settings(test_settings.PLATFORM_SETTINGS, settings_json['PLATFORM_SETTINGS'])
        if 'NAS_SETTINGS' in settings_json:
            test_settings.NAS_SETTINGS = _update_settings(test_settings.NAS_SETTINGS, settings_json['NAS_SETTINGS'])
        if 'DUMPER_SETTINGS' in settings_json:
            test_settings.DUMPER_SETTINGS = _update_settings(test_settings.DUMPER_SETTINGS, settings_json['DUMPER_SETTINGS'])
        if 'DUMPER_SETTINGS' in settings_json:
            test_settings.LOG_SETTINGS = _update_settings(test_settings.LOG_SETTINGS, settings_json['LOG_SETTINGS'])
        
    # then apply custom fine-grain settings
    if 'gpuid' in args:
        print('ARG_SET_GPUID : ', args.gpuid)
        test_settings.CUDA_SETTINGS['GPUID'] = args.gpuid
    if 'dataset' in args:
        print('ARG_SET_DATASET : ', args.dataset)
        test_settings.NAS_SETTINGS['DATASET'] = args.dataset
    if 'layers'  in args: 
        print('ARG_SET_LAYSER : ', args.layers)
        test_settings.NAS_SETTINGS['NUM_LAYERS'] = args.layers
    if 'epochs'  in args:
        print('ARG_SET_EPOCHS : ', args.epochs)
        test_settings.NAS_SETTINGS['EPOCH'] = args.epochs
    if 'trial'   in args:
        print('ARG_SET_TRIAL : ', args.trial)
        test_settings.NAS_SETTINGS['TRIALS'] = args.trial
    if 'batch_size' in args:
        print('ARG_SET_BATCH_SIZE : ', args.batch_size)
        test_settings.NAS_SETTINGS['CHILD_BATCHSIZE'] = args.batch_size
    if 'seed' in args:
        print('ARG_SET_SEED : ', args.seed)
        test_settings.NAS_SETTINGS['SEED'] = args.seed
    if 'suffix' in args:
        print('ARG_SET_SUFFIX : ', args.suffix)
        test_settings.GLOBAL_SETTINGS['EXP_SUFFIX'] = args.suffix
    if 'ccap' in args:
        print('ARG_SET_CCAP : ', args.ccap)
        test_settings.PLATFORM_SETTINGS['CCAP'] = args.ccap
    if 'latreq' in args:
        print('ARG_SET_LATREQ : ', args.latreq)
        test_settings.PLATFORM_SETTINGS['LAT_E2E_REQ'] = args.latreq
    if 'rehm' in args:
        print('ARG_SET_REHM : ', args.rehm)
        test_settings.PLATFORM_SETTINGS['REHM'] = args.rehm
    if 'fixed' in args:
        print('ARG_SET_DETERMINISTIC_FLOW : ', args.fixed)
        test_settings.NAS_SETTINGS['DETERMINISTIC_FLOW'] = args.fixed

    return test_settings

