import sys, os
from pprint import pprint
import warnings
import numpy as np
import time
import matplotlib.pyplot as plt
import time


import tensorflow as tf

# Importing the required Keras modules containing model and layers\
from tensorflow import keras
from keras.models import Sequential
from keras import backend as K
from keras.callbacks import ModelCheckpoint
from keras.layers import Dense, Conv2D, Dropout, Flatten, MaxPooling2D


# local imports
sys.path.append('.')
import dump_headers_extNVM as dump
from dump_headers_extNVM import _get_text_mat
from file_utils import json_dump, json_load, delete_file, dir_create
from cnn_types import CNNModel, CNNLayer, Mat



########################################################
#   CONSTANTS
########################################################
#from cnn_tf import CHKPOINT_LOC

Q15_SIZE = 2 # bytes per data element (q15)
BASE_ADDR = 100
# BUFF1_ADDRESS = 1000
# BUFF2_ADDRESS = 2000

CHKPOINT_LOC = 'tf_models'
# convolution layer
LAYER_FUNC_NAMES = {
    'CONV' : "CNN_Intermittent_LayerConv_Tiled_Std",
    'GAVGPOOL' : "CNN_Intermittent_GlobalAveragePool",      # global avg pooling       
    'FC' : "CNN_Intermittent_LayerConv_Tiled_Std",
}


########################################################
#   DUMP HEADER FILE
########################################################
def dump_model_header(model_name, num_layers, layer_txt_objs_lst, parent_suffix, output_dir):        
    model =  CNNModel(name = model_name, layers = layer_txt_objs_lst, num_layers=len(layer_txt_objs_lst))
    model_fname = model_name + parent_suffix    
    dump.write_model_header(output_dir, model_fname, model_fname, model)
    return model_fname



########################################################
#   PRIMARY HANDLER
########################################################
# convert tensorflow model to msp430 format
def dump_tf_cnn_handler(model, model_params_exec, model_params_pres, input_shape=[1, 28, 28], dump_dir=""):
    layer_funcs = LAYER_FUNC_NAMES
    layers = model.layers    
    parent_suffix = ""
    output_dir = dump_dir
    dir_create(output_dir) # create if doesn't exit    

    # buffer1_address = BUFF1_ADDRESS
    # buffer2_address = buffer1_address + size of buffer1_address
    ##################Calc buffer size###################
    max_ofm_sz = 0
    for layer in layers:
        layer_name = layer.name.upper()
        if 'INPUT' in layer_name:            
            if len(layer.input_shape) == 4:                                
                ih = layer.input_shape[1]
                iw = layer.input_shape[2]
                ic = layer.input_shape[3]

            elif len(layer.input_shape) == 3:                
                ih = layer.input_shape[1]
                iw = 1
                ic = layer.input_shape[2]

            elif len(layer.input_shape) == 2:
                ih = layer.input_shape[1]
                iw = 1
                ic = 1
            
            
            max_ofm_sz = int(ih) * int(iw) * int(ic) * Q15_SIZE
        elif 'CONV' in layer_name:
            knum = layer.filters
            ih = layer.input_shape[1]
            iw = layer.input_shape[2]
            
            #ksize = layer.kernel_size[0] 

            if len(layer.kernel_size) == 2: # 2d
                ksize_h = layer.kernel_size[0]
                ksize_w = layer.kernel_size[1]
            elif len(layer.kernel_size) == 1: # 1d
                ksize_h = layer.kernel_size[0]
                ksize_w = 1


            stride = 1; pad=0  
            ofm_h = int(((ih-ksize_h + (2*pad))/stride) + 1)  
            ofm_w = int(((iw-ksize_w + (2*pad))/stride) + 1)
            sz = knum * ofm_h * ofm_w * Q15_SIZE 
            if sz > max_ofm_sz:
                max_ofm_sz = sz
        elif ('DENSE' in layer_name) or ('FULLYCONNECTED' in layer_name) or ('FC' in layer_name):
            if layer.units * Q15_SIZE >  max_ofm_sz:
                max_ofm_sz = layer.units * Q15_SIZE


    buffer1_address = BASE_ADDR
    buffer2_address = BASE_ADDR + max_ofm_sz


    curr_buffer = buffer1_address

    
    layer_mat_objs = [] # keep track of layer mat objs

    input_layer_obj = CNNLayer(-1, 'Input', '', 
                                None, None, None, 
                                _get_text_mat(data_loc=curr_buffer, n=1, ch=input_shape[0], h=input_shape[1], w=input_shape[2]))

    layer_mat_objs.append(input_layer_obj)

    mat_bias_txtobj = _get_text_mat(data_loc=0, n=0, ch=0, h=0, w=0) # we assume no bias for now

    

    ignore_layer_flag = False
    ext_nvm_data_offset = BASE_ADDR + max_ofm_sz*2 # <<-- @TODO starts after buffer 2 address size
    lix = 0
    for layer in layers:
        layer_name = layer.name.upper()
        #print("------------------ " + layer_name + " ------------------")
        
        ifm_h = layer_mat_objs[-1].ofm.h
        ifm_w = layer_mat_objs[-1].ofm.w

        if 'INPUT' in layer_name:       # skip input layer       
            continue

        elif 'CONV' in layer_name:              
            layer_func_name = layer_funcs['CONV']  
            knum = layer.filters

            if len(layer.kernel_size) == 2: # 2d
                ksize_h = layer.kernel_size[0]
                ksize_w = layer.kernel_size[1]
            elif len(layer.kernel_size) == 1: # 1d
                ksize_h = layer.kernel_size[0]
                ksize_w = 1

            # print("---------")
            # print(layer.kernel_size)            
            # print("---------")
            # sys.exit()

            stride = 1; pad=0 
            ofm_h = int(((ifm_h-ksize_h + (2*pad))/stride) + 1)  
            ofm_w = int(((ifm_w-ksize_w + (2*pad))/stride) + 1)  
            curr_buffer = buffer2_address if (curr_buffer == buffer1_address) else buffer1_address

            mat_wei_txtobj = _get_text_mat(data_loc=ext_nvm_data_offset, n=knum, ch=layer_mat_objs[-1].ofm.ch, h=ksize_h, w=ksize_w)
            mat_ifm_txtobj = _get_text_mat(data_loc=layer_mat_objs[-1].ofm.data, n=1, ch=layer_mat_objs[-1].ofm.ch, h=layer_mat_objs[-1].ofm.h, w=layer_mat_objs[-1].ofm.w)
            mat_ofm_txtobj = _get_text_mat(data_loc=curr_buffer , n=1, ch=knum, h=ofm_h, w=ofm_w)            
                        
            ext_nvm_data_offset += (knum * layer_mat_objs[-1].ofm.ch * ksize_h * ksize_w) * Q15_SIZE # set the extrnal nvm data offset for next layer params
                                       
        elif ('DENSE' in layer_name) or ('FULLYCONNECTED' in layer_name) or ('FC' in layer_name):            
            layer_func_name = layer_funcs['FC']  
            units = layer.units                        
            stride = 1; pad=0 
            ofm_h = int(((ifm_h-ifm_h + (2*pad))/stride) + 1)  
            ofm_w = int(((ifm_w-ifm_w + (2*pad))/stride) + 1)  
            curr_buffer = buffer2_address if (curr_buffer == buffer1_address) else buffer1_address

            mat_wei_txtobj = _get_text_mat(data_loc=ext_nvm_data_offset, n=units, ch=layer_mat_objs[-1].ofm.ch, h=ifm_h, w=ifm_w)
            mat_ifm_txtobj = _get_text_mat(data_loc=layer_mat_objs[-1].ofm.data, n=1, ch=layer_mat_objs[-1].ofm.ch, h=layer_mat_objs[-1].ofm.h, w=layer_mat_objs[-1].ofm.w)
            mat_ofm_txtobj = _get_text_mat(data_loc=curr_buffer , n=1, ch=units, h=ofm_h, w=ofm_w)            
            
            ext_nvm_data_offset += (units * layer_mat_objs[-1].ofm.ch * ifm_h * ifm_w) * Q15_SIZE # set the extrnal nvm data offset for next layer params

                           
        elif ('GAVGPOOL' in layer_name):     # global avg pooling           
            layer_func_name = layer_funcs['GAVGPOOL']        
            curr_buffer = buffer2_address if (curr_buffer == buffer1_address) else buffer1_address              
            
            mat_wei_txtobj = _get_text_mat(data_loc=0, n=0, ch=0, h=0, w=0)
            mat_ifm_txtobj = _get_text_mat(data_loc=layer_mat_objs[-1].ofm.data, n=1, ch=layer_mat_objs[-1].ofm.ch, h=layer_mat_objs[-1].ofm.h, w=layer_mat_objs[-1].ofm.w)
            mat_ofm_txtobj = _get_text_mat(data_loc=curr_buffer , n=1, ch=layer_mat_objs[-1].ofm.ch, h=1, w=1)            
            
            ext_nvm_data_offset += 0 # no weight params
        
        else:            
            pprint(layer.name)
            pprint(layer)
            sys.exit("ERROR: layer error")
        if (model_params_exec == None) and(model_params_pres == None):
            params_exec={'inter_lo' : 'reuse_O' ,'tile_size' : [1,1,1,1,2,2,2,2]}
            params_pres={'backup_batch_size' : 1}
            layer_txtobj = CNNLayer(lix, layer_name, layer_func_name, 
                                mat_wei_txtobj, mat_bias_txtobj, mat_ifm_txtobj, mat_ofm_txtobj,
                                params_exec= params_exec,
                                params_pres= params_pres) 
        else :
            layer_txtobj = CNNLayer(lix, layer_name, layer_func_name, 
                                mat_wei_txtobj, mat_bias_txtobj, mat_ifm_txtobj, mat_ofm_txtobj,
                                params_exec= model_params_exec[layer.name],
                                params_pres= model_params_pres[layer.name])                                
        layer_mat_objs.append(layer_txtobj)
        
        lix+=1 # increment layer index
        
    num_layers = len(layer_mat_objs)

    # -- dump model definition --    
    #pprint(model_mat_objs_lst)    
    header_fname = dump_model_header(model.name, num_layers, layer_mat_objs[1:], parent_suffix, output_dir)
    
    
  
def _check_mat_type(all_layers):
    for each_layer in all_layers:
        print([each_layer["name"], type(each_layer['ifm']), type(each_layer['ofm'])])

