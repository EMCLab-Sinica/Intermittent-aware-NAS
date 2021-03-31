'''
This NASBase module of the iNAS framework is based on the following hardware-aware NAS engine:
Source code: https://github.com/PITT-JZ-COOP/FPGA-implementation-Aware-Neural-Architecture-Search
Paper title: Accuracy vs. efficiency: Achieving both through fpga-implementation aware neural architecture search
Authors: Jiang, W., Zhang, X., Sha, E.H.M., Yang, L., Zhuge, Q., Shi, Y. and Hu, J., 
In Proc. of DAC 2019
pdf: https://arxiv.org/abs/1901.11211
'''

# -- helper class to interface with the iNAS platform performance model --

import math
import sys
import random
import os
import sys
import math
from math import *
import csv
import time
import copy
import json 
from IEExplorer.handler import find_best_solution, get_layer_data_access_cost
from CostModel.plat_energy_costs import PlatformCostModel
from DNNDumper.cnn_types import Mat

from DNNDumper.file_utils import NumpyEncoder

class PlatPerf:
    def __init__(self, NAS_SETTINGS, PLAT_SETTINGS):
        self.PLAT_SETTINGS = PLAT_SETTINGS        
        self.NAS_SETTINGS = NAS_SETTINGS
        self.PLAT_COST_PROFILE = self.get_cost_model()  # this points to the platform specific cost model, derived from micro-benchmark based profiling

    
    # get cost profile per platform (using the benchmark measurements)                
    def get_cost_model(self):
        if self.PLAT_SETTINGS['MCU_TYPE'] == "MSP430":
            plat_cost_profile = PlatformCostModel.PLAT_MSP430_EXTNVM                
        else:
            sys.exit("NASBase::PlatPerf: ERROR - unsupported platform cost model")        
        return plat_cost_profile


    # network definition (using custom data structs) for different model types
    def get_network(self, predic_actions, model_fn_type='MODEL_FN_CONV2D'):
        network = []
        ifm_h = self.NAS_SETTINGS['IMG_SIZE']
        ifm_w = self.NAS_SETTINGS['IMG_SIZE']
        ifm_ch= self.NAS_SETTINGS['IMG_CHANNEL']
        ofm_ch= 0
        layers= self.NAS_SETTINGS['NUM_LAYERS']
        num_classes= self.NAS_SETTINGS['NUM_CLASS']

        # -- get network depending on model function type
        if model_fn_type == "MODEL_FN_CONV2D":
            # CONV layers
            for i in range(layers):
                kernel_h = predic_actions[i*2]; kernel_w = predic_actions[i*2]
                filter_size = predic_actions[i*2+1]
                ofm_ch = filter_size
                ofm_h = ifm_h - kernel_h + 1; ofm_w = ifm_w - kernel_w + 1
                item = {
                    'name' : "CONV_"+str(i), 'type' : "CONV", 'stride' : 1,
                    'K' : Mat(None, filter_size, ifm_ch, kernel_h, kernel_w), # n, ch, h, w
                    'IFM' : Mat(None, 1, ifm_ch, ifm_h, ifm_w), 'OFM' : Mat(None, 1, filter_size, ofm_h, ofm_w),
                }
                network.append(item)
                ifm_h = ofm_h; ifm_w = ofm_w
                ifm_ch= filter_size

            # append GLOBAL AVG POOLING layer
            item={
                'name' : "GAVGPOOL_0", 'type' : "GAVGPOOL", 'stride' : 1,
                'K' : Mat(None, ifm_ch, ifm_ch, ifm_h, ifm_w),
                'IFM' : Mat(None, 1, ifm_ch, ifm_h, ifm_w), 'OFM' : Mat(None, 1, ifm_ch, 1, 1),
            }
            network.append(item)
        
        elif model_fn_type == "MODEL_FN_CONV1D":            
            ifm_w = 1
            # CONV layers
            for i in range(layers):
                kernel_h = predic_actions[i*2]; kernel_w = 1
                filter_size = predic_actions[i*2+1]
                ofm_ch = filter_size
                ofm_h = ifm_h - kernel_h + 1; ofm_w = 1
                item = {
                    'name' : "CONV_"+str(i), 'type' : "CONV", 'stride' : 1,
                    'K' : Mat(None, filter_size, ifm_ch, kernel_h, kernel_w), # n, ch, h, w
                    'IFM' : Mat(None, 1, ifm_ch, ifm_h, ifm_w), 'OFM' : Mat(None, 1, filter_size, ofm_h, ofm_w),
                }
                network.append(item)
                ifm_h = ofm_h; ifm_w = ofm_w
                ifm_ch= filter_size

            # append GLOBAL AVG POOLING layer
            item={
                'name' : "GAVGPOOL_0", 'type' : "GAVGPOOL", 'stride' : 1,
                'K' : Mat(None, ifm_ch, ifm_ch, ifm_h, ifm_w),
                'IFM' : Mat(None, 1, ifm_ch, ifm_h, ifm_w), 'OFM' : Mat(None, 1, ifm_ch, 1, 1),
            }
            network.append(item)

        elif model_fn_type == "MODEL_FN_FC":    
            ifm_w = 1        
            # FC layers
            for i in range(layers):
                kernel_h = ifm_h; kernel_w = 1
                filter_size = predic_actions[i]
                ofm_ch = filter_size
                ofm_h = 1; ofm_w = 1
                item = {
                    'name' : "FC_"+str(i), 'type' : "FC", 'stride' : 1,
                    'K' : Mat(None, filter_size, ifm_ch, kernel_h, kernel_w), # n, ch, h, w
                    'IFM' : Mat(None, 1, ifm_ch, ifm_h, ifm_w), 'OFM' : Mat(None, 1, filter_size, ofm_h, ofm_w),
                }
                network.append(item)
                ifm_h = ofm_h; ifm_w = ofm_w
                ifm_ch= filter_size        
        else:
            sys.exit("get_network:: unknown")
        
        # -- append last FC layer
        item={
            'name' : "FC_END", 'type' : "FC", 'stride' : 1,
            'K' : Mat(None, num_classes, ifm_ch, 1, 1),
            'IFM' : Mat(None, 1, ifm_ch, 1, 1), 'OFM' : Mat(None, 1, num_classes, 1, 1),
        }
        network.append(item)

        return network
        

    # use intermittent-aware perf cost model and derive E2E inference latency
    def get_inference_latency(self, predic_actions):
        network = self.get_network(predic_actions, model_fn_type=self.NAS_SETTINGS['MODEL_FN_TYPE']) 
        error = None
        latency = 0
        network_exec_design = []
        sols = find_best_solution(network, self.PLAT_SETTINGS, self.PLAT_COST_PROFILE, power_type=self.PLAT_SETTINGS['POW_TYPE'])
        for each_layer in network: 
            
            # if any one of the layers do not have a best solution, then return -1
            if sols[each_layer['name']]['best_sol'] == None: # cannot find a feasible execution design
                return -1, None, sols[each_layer['name']]['error_code']
            else:
                latency = latency + sols[each_layer['name']]['best_sol'][0]['Le2e']
                network_exec_design.append({'layer' : each_layer['name'], 
                                            'params': sols[each_layer['name']]['best_sol'][0]['params'],
                                            'Epc' : sols[each_layer['name']]['best_sol'][0]['Epc'],
                                            'Eu' : sols[each_layer['name']]['best_sol'][0]['Eu'],
                                            'Le2e' : sols[each_layer['name']]['best_sol'][0]['Le2e'],
                                            'npc' : sols[each_layer['name']]['best_sol'][0]['npc'][0],
                                            'vm' : sols[each_layer['name']]['best_sol'][0]['vm'],                                            
                                            })        
        return latency, network_exec_design, error

    
    def get_network_data_access_cost(self, predic_actions, network_exec_design):
        network = self.get_network(predic_actions, model_fn_type=self.NAS_SETTINGS['MODEL_FN_TYPE']) 
        error = None
        latency = 0 
        
        net_cost = []
        for lix, each_layer in enumerate(network):
            exec_design = network_exec_design[lix]
            [rd_cost_L, wr_cost_L, rd_cost_E, wr_cost_E] = get_layer_data_access_cost(each_layer, exec_design, self.PLAT_SETTINGS, self.PLAT_COST_PROFILE, power_type='INT')
            net_cost.append([rd_cost_L, wr_cost_L, rd_cost_E, wr_cost_E])
        return net_cost


# convert exec design into string
def exec_design_to_string(exec_design):
    if exec_design != None:        
        s = ""
        for each_layer in exec_design:        
            #s += ','.join(['='.join(i) for i in each_layer.items()])
            s += str(each_layer)
            s += ","
        return s
    else:
        return ""

