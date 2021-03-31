'''
This NASBase module of the iNAS framework is based on the following hardware-aware NAS engine:
Source code: https://github.com/PITT-JZ-COOP/FPGA-implementation-Aware-Neural-Architecture-Search
Paper title: Accuracy vs. efficiency: Achieving both through fpga-implementation aware neural architecture search
Authors: Jiang, W., Zhang, X., Sha, E.H.M., Yang, L., Zhuge, Q., Shi, Y. and Hu, J., 
In Proc. of DAC 2019
pdf: https://arxiv.org/abs/1901.11211
'''

# -- model type definitions --

from keras.models import Model
from keras.layers import Input, Dense, Conv2D, Conv1D, GlobalAveragePooling2D, GlobalAveragePooling1D, Flatten

import sys
import inspect
from pprint import pprint

class ModelErrorCodes():
    MCODE_INSUFFICIENT_NVM_SPACE = 1
    MCODE_ILLEGAL_ACTIONS = 2


################################################################
#   HELPERS
################################################################

def _get_model_common_settings(nas_settings):
    input_size = nas_settings['IMG_SIZE']
    input_ch   = nas_settings['IMG_CHANNEL']
    layers     = nas_settings['NUM_LAYERS']
    num_classes= nas_settings['NUM_CLASS']  
    return input_size, input_ch, layers, num_classes

def get_model_fn(model_fn_type):
    if (model_fn_type == 'MODEL_FN_CONV2D'):
        return model_fn_conv2D                
    elif (model_fn_type == 'MODEL_FN_CONV1D'):
        return model_fn_conv1D    
    elif (model_fn_type == 'MODEL_FN_FC'):
        return model_fn_fc
    else:
        sys.exit("NASBase::TOP:: Error - unspecified model_fn_type - " + model_fn_type)

def get_model_fn_by_dataset(dataset):
    if 'cifar' in dataset:
        return model_fn_conv2D                
    elif 'har' in dataset:
        return model_fn_conv1D    
    elif 'kws' in dataset:
        return model_fn_fc
    else:
        sys.exit("NASBase::TOP:: Error - unspecified dataset - " + dataset)


################################################################
#   MODEL_FN_CONV2D
#   2D CONV layers + GPOOL + DENSE
################################################################
def model_fn_conv2D(actions, nas_settings = None, plat_settings = None):
    if (nas_settings == None): sys.exit(inspect.currentframe().f_code.co_name+"::Error - nas settings missing")
    if (plat_settings == None): sys.exit(inspect.currentframe().f_code.co_name+"::Error - plat settings missing")

    if ( nas_settings['DETERMINISTIC_FLOW'] ):
        kernel_init = "zeros"
    else:
        kernel_init = "glorot_uniform"
        
    # unpack the actions from the list
    # kernel_1, filters_1, kernel_2, filters_2, kernel_3, filters_3, kernel_4, filters_4 = actions
    input_size, input_ch, layers, num_classes = _get_model_common_settings(nas_settings)    
    
    max_ofm = input_size * input_size * input_ch
    error_code=buffer_size=ofm_size=weight_size=nvm_reserved=0
    #model_params_size=0
    
    ip = Input(shape=( input_size, input_size, input_ch), name="INPUT")   # 2D input with multiple channels (H,W,N)
    for i in range(layers):
        kernel_h = actions[i*2]
        kernel_w = actions[i*2]
        filter_size = actions[i*2 +1]
        ofm_h = input_size - kernel_h + 1
        ofm_w = input_size - kernel_w + 1
        ofm_size = ofm_h * ofm_w * filter_size
        weight_size =weight_size + kernel_h * kernel_w * filter_size * input_ch
        
        if ofm_size > max_ofm:
            max_ofm = ofm_size

        # validate
        if(input_size < actions[i*2]):
            return Model(), ModelErrorCodes.MCODE_ILLEGAL_ACTIONS
        nvm_usage = nvm_reserved + (2 * max_ofm + weight_size) * plat_settings['DATA_SZ']   
        if(nvm_usage > plat_settings['NVM_CAPACITY']):
            return Model(), ModelErrorCodes.MCODE_INSUFFICIENT_NVM_SPACE

        input_size = input_size - kernel_h + 1
        input_ch   = filter_size
        if (i==0): 
            x = Conv2D(filter_size, (kernel_h, kernel_w),kernel_initializer=kernel_init, strides=(1, 1),use_bias=False, padding='valid', activation='relu', name="CONV_"+str(i))(ip)            
        else:
            x = Conv2D(filter_size, (kernel_h, kernel_w),kernel_initializer=kernel_init, strides=(1, 1),use_bias=False, padding='valid', activation='relu', name="CONV_"+str(i))(x)
        
        # model_params_size += (kernel_w *  kernel_h * filter_size)
        
    x = GlobalAveragePooling2D(name="GAVGPOOL_0")(x)
    weight_size =weight_size + num_classes * input_ch
    nvm_usage = nvm_reserved + (2 * max_ofm + weight_size) * plat_settings['DATA_SZ']   
    if(nvm_usage > plat_settings['NVM_CAPACITY']):
        return Model(), ModelErrorCodes.MCODE_INSUFFICIENT_NVM_SPACE

    x = Dense(num_classes,kernel_initializer=kernel_init, use_bias=False, activation='softmax', name="FC_END")(x)
    # model_params_size +=  num_classes
 
    model = Model(ip, x)
    return model, 0



################################################################
#   MODEL_FN_CONV1D
#   1D CONV layers + GPOOL + DENSE
################################################################
def model_fn_conv1D(actions, nas_settings = None, plat_settings = None):
    if (nas_settings == None): sys.exit(inspect.currentframe().f_code.co_name+"::Error - nas settings missing")
    if (plat_settings == None): sys.exit(inspect.currentframe().f_code.co_name+"::Error - plat settings missing")
    if ( nas_settings['DETERMINISTIC_FLOW'] ):
        kernel_init = 'zeros'
    else : 
        kernel_init = 'glorot_uniform'
    
    # unpack the actions from the list    
    input_size, input_ch, layers, num_classes = _get_model_common_settings(nas_settings)    
    
    max_ofm = input_size * input_ch
    error_code=buffer_size=ofm_size=weight_size=nvm_reserved=0    
    #model_params_size=0

    ip = Input(shape=( input_size, input_ch), name="INPUT") # 1D input with multiple channels (H,N)
    for i in range(layers):
        kernel_h = actions[i*2]
        kernel_w = 1
        filter_size = actions[i*2 +1]
        ofm_h = input_size - kernel_h + 1
        ofm_w = 1
        ofm_size = ofm_h * ofm_w * filter_size
        weight_size =weight_size + kernel_h * kernel_w * filter_size * input_ch
        
        if ofm_size > max_ofm:
            max_ofm = ofm_size

        # validate
        if(input_size < actions[i*2]):
            return Model(), ModelErrorCodes.MCODE_ILLEGAL_ACTIONS
        nvm_usage = nvm_reserved + (2 * max_ofm + weight_size) * plat_settings['DATA_SZ']   
        if(nvm_usage > plat_settings['NVM_CAPACITY']):
            return Model(), ModelErrorCodes.MCODE_INSUFFICIENT_NVM_SPACE

        input_size = input_size - kernel_h + 1
        input_ch   = filter_size
        if (i==0):             
            x = Conv1D(filter_size, kernel_h,kernel_initializer=kernel_init, strides=1, use_bias=False, padding='valid', activation='relu', name="CONV_"+str(i))(ip)            
        else:
            x = Conv1D(filter_size, kernel_h,kernel_initializer=kernel_init, strides=1, use_bias=False, padding='valid', activation='relu', name="CONV_"+str(i))(x)
        
        # model_params_size += (kernel_w *  kernel_h * filter_size)
        
    x = GlobalAveragePooling1D(name="GAVGPOOL_0")(x)
    weight_size =weight_size + num_classes * input_ch
    nvm_usage = nvm_reserved + (2 * max_ofm + weight_size) * plat_settings['DATA_SZ']   
    if(nvm_usage > plat_settings['NVM_CAPACITY']):
        return Model(), ModelErrorCodes.MCODE_INSUFFICIENT_NVM_SPACE

    x = Dense(num_classes,kernel_initializer=kernel_init, use_bias=False, activation='softmax', name="FC_END")(x)
    # model_params_size +=  num_classes
 
    model = Model(ip, x)
    return model, 0


################################################################
#   MODEL_FN_CONV1D
#   DENSE layers
################################################################
def model_fn_fc(actions, nas_settings = None, plat_settings = None):
    if (nas_settings == None): sys.exit(inspect.currentframe().f_code.co_name+"::Error - nas settings missing")
    if (plat_settings == None): sys.exit(inspect.currentframe().f_code.co_name+"::Error - plat settings missing")
    if ( nas_settings['DETERMINISTIC_FLOW'] ):
        kernel_init = 'zeros'
    else : 
        kernel_init = 'glorot_uniform'

    # unpack the actions from the list    
    input_size, input_ch, layers, num_classes = _get_model_common_settings(nas_settings)    
    
    max_ofm = input_size * input_ch
    error_code=buffer_size=ofm_size=weight_size=nvm_reserved=0    
    #model_params_size=0

    if (len(actions) != layers):
        sys.exit(inspect.currentframe().f_code.co_name+"::Error - number of actions invalid = " + str(len(actions)))

    ip = Input(shape=(input_size,), name="INPUT") # 1D input with multiple channels (H,N)
    for i in range(layers):
        kernel_h = input_size
        kernel_w = 1
        filter_size = actions[i]
        ofm_h = 1
        ofm_w = 1
        ofm_size = ofm_h * ofm_w * filter_size
        weight_size =weight_size + filter_size * input_ch
        
        if ofm_size > max_ofm:
            max_ofm = ofm_size

        # validate        
        nvm_usage = nvm_reserved + (2 * max_ofm + weight_size) * plat_settings['DATA_SZ']   
        if(nvm_usage > plat_settings['NVM_CAPACITY']):
            return Model(), ModelErrorCodes.MCODE_INSUFFICIENT_NVM_SPACE

        #input_size = filter_size
        input_ch   = filter_size
        if (i==0):             
            x = Dense(filter_size,kernel_initializer=kernel_init, use_bias=False, activation='relu', name="FC_"+str(i))(ip)
        else:            
            x = Dense(filter_size,kernel_initializer=kernel_init, use_bias=False, activation='relu', name="FC_"+str(i))(x)
        
        # model_params_size += (kernel_w *  kernel_h * filter_size)
        
    #x = GlobalAveragePooling1D()(x)

    weight_size =weight_size + num_classes * input_ch
    nvm_usage = nvm_reserved + (2 * max_ofm + weight_size) * plat_settings['DATA_SZ']   
    if(nvm_usage > plat_settings['NVM_CAPACITY']):
        return Model(), ModelErrorCodes.MCODE_INSUFFICIENT_NVM_SPACE
    
    x = Dense(num_classes,kernel_initializer=kernel_init, use_bias=False, activation='softmax', name="FC_END")(x)
    # model_params_size +=  num_classes
 
    model = Model(ip, x)
    return model, 0

