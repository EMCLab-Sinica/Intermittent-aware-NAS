'''
This NASBase module of the iNAS framework is based on the following hardware-aware NAS engine:
Source code: https://github.com/PITT-JZ-COOP/FPGA-implementation-Aware-Neural-Architecture-Search
Paper title: Accuracy vs. efficiency: Achieving both through fpga-implementation aware neural architecture search
Authors: Jiang, W., Zhang, X., Sha, E.H.M., Yang, L., Zhuge, Q., Shi, Y. and Hu, J., 
In Proc. of DAC 2019
pdf: https://arxiv.org/abs/1901.11211
'''

# -- Top-level NAS handler --

import numpy as np
import csv
import tensorflow as tf
from keras import backend as K
from keras.datasets import cifar10
from keras.datasets import mnist
from keras.utils import to_categorical
from .controller import Controller, StateSpace
from .manager import NetworkManager
#from .model import model_fn_conv2D, model_fn_conv1D, model_fn_fc
from .model import get_model_fn
from .plat_perf import PlatPerf, exec_design_to_string
import math
import networkx as nx
import random
import os
import sys
from math import *
import csv
import time, datetime
import copy 
from pprint import pprint

from DNNDumper.file_utils import dir_create, delete_file
from NASBase.dataset.kws import kws_getdata
from NASBase.dataset.har import har_getdata


################################################################
# HELPERS
################################################################

def _get_training_data(dataset, num_class, img_size, img_ch):    
    if (dataset == 'CIFAR10'):
        (x_train, y_train), (x_test, y_test) = cifar10.load_data()
        x_train = x_train.astype('float16') / 255.
        x_test = x_test.astype('float16') / 255.
        y_train = to_categorical(y_train, num_class)
        y_test = to_categorical(y_test, num_class)
        x_train = x_train.reshape(50000,32,32,3)
        x_test = x_test.reshape(10000,32,32,3)
  
    elif (dataset == 'MNIST'):
        (x_train, y_train), (x_test, y_test) = mnist.load_data()
        x_train = x_train.astype('float16') / 255.
        x_test = x_test.astype('float16') / 255.
        y_train = to_categorical(y_train, num_class)
        y_test = to_categorical(y_test, num_class)
        x_train = x_train.reshape(60000,28,28,1)
        x_test = x_test.reshape(10000,28,28,1)

    elif (dataset == 'HAR'):
        x_train, y_train, x_test, y_test = har_getdata()
        # Train X(7352, 128, 9)
        # Train Y(7352, 6)
        # Test X(2947, 128, 9)
        # Test Y(2947, 6)

    
    elif (dataset == 'KWS'):
        LOAD_PREPROCESSED_DATA = True

        if LOAD_PREPROCESSED_DATA:
            [x_train, y_train, x_test, y_test] = np.load("NASBase/dataset/kws_data_preprosessed.npy", allow_pickle=True)                
        else:
            with tf.Session() as sess_kws_extraction:
                x_train, y_train, x_test, y_test = kws_getdata(sess_kws_extraction)

            np.save("NASBase/dataset/kws_data_preprosessed", [x_train, y_train, x_test, y_test])

        # Train X(36923, 250)
        # Train Y(36923, 12)
        # Test X(4890, 250)
        # Test Y(4890, 12)

        
    else :
        sys.exit("NASBase::TOP:: Error - unspecified dataset - " + dataset)
        pass
    
    return x_train, y_train, x_test, y_test







#tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

################################################################
# NAS Base Entry func
################################################################

def nas_top(test_setting):

    tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR) # hide deprecated warnings

    if isinstance(test_setting.CUDA_SETTINGS['GPUID'], int):
        test_setting.CUDA_SETTINGS['GPUID'] = str(test_setting.CUDA_SETTINGS['GPUID'])  
    os.environ["CUDA_VISIBLE_DEVICES"]=test_setting.CUDA_SETTINGS['GPUID']
    

    # create a shared session between Keras and Tensorflow
    policy_sess = tf.Session()

    K.set_session(policy_sess)

    print("\n\n")
    print("NASBase::TOP:: Dumping run settings -------------------------------------")
    print(test_setting)
    print("NASBase::TOP:: -----------------------------------------------------------\n\n")

    EXP_SUFFIX = test_setting.GLOBAL_SETTINGS['EXP_SUFFIX']    
    SEED = test_setting.NAS_SETTINGS['SEED']    
    MODEL_FN_TYPE = test_setting.NAS_SETTINGS['MODEL_FN_TYPE']
    NUM_LAYERS = test_setting.NAS_SETTINGS['NUM_LAYERS']  
    MAX_TRIALS = test_setting.NAS_SETTINGS['TRIALS'] 
    MAX_EPOCHS = test_setting.NAS_SETTINGS['EPOCH']  
    CHILD_BATCHSIZE = test_setting.NAS_SETTINGS['CHILD_BATCHSIZE']  
    EXPLORATION = test_setting.NAS_SETTINGS['EXPLORATION']  
    REGULARIZATION = test_setting.NAS_SETTINGS['REGULARIZATION']  
    CONTROLLER_CELLS = test_setting.NAS_SETTINGS['CONTROLLER_CELLS']  
    EMBEDDING_DIM = test_setting.NAS_SETTINGS['EMBEDDING_DIM']  
    ACCURACY_BETA = test_setting.NAS_SETTINGS['ACCURACY_BETA']  
    CLIP_REWARDS = test_setting.NAS_SETTINGS['CLIP_REWARDS']  
    RESTORE_CONTROLLER = test_setting.NAS_SETTINGS['RESTORE_CONTROLLER'] 
    DATASET = test_setting.NAS_SETTINGS['DATASET']
    IMG_CHANNEL = test_setting.NAS_SETTINGS['IMG_CHANNEL']
    IMG_SIZE = test_setting.NAS_SETTINGS['IMG_SIZE']
    NUM_CLASS = test_setting.NAS_SETTINGS['NUM_CLASS']
    MODEL_FN_TYPE = test_setting.NAS_SETTINGS['MODEL_FN_TYPE']    

    LATENCY_REQ = test_setting.PLATFORM_SETTINGS['LAT_E2E_REQ']  # set the inference timing requirement 

    TRIAL_LOG_DIR = test_setting.LOG_SETTINGS["TRIAL_LOG_DIR"]        
    fname, ext = os.path.splitext(test_setting.LOG_SETTINGS["TRIAL_LOG_FNAME"])
    TRIAL_LOG_FNAME = fname + "_" + EXP_SUFFIX + ext

    if( test_setting.NAS_SETTINGS['DETERMINISTIC_FLOW']  ):
        random.seed(SEED)
        np.random.seed(SEED)
        tf.compat.v1.set_random_seed(SEED)


    # delete files    
    files = ['tmp_buffers/buffers' + EXP_SUFFIX +'.txt']    
    for f in files:
        if os.path.exists(f):
            os.remove(f)

    # prepare misc output folders
    if not os.path.exists('weights/' + EXP_SUFFIX + "/"):
        os.makedirs('weights/' + EXP_SUFFIX + "/")
    if not os.path.exists('tmp_buffers/'):
        os.makedirs('tmp_buffers/')


    # prepare log    
    dir_create(TRIAL_LOG_DIR)

    # put start timestamp on log (start time)
    with open(TRIAL_LOG_DIR + "/" + TRIAL_LOG_FNAME, mode='a+') as f:                
        ts = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        writer = csv.writer(f, delimiter=';')
        writer.writerow([ts])
        

    #====================--------================#
   
    # construct a state space
    state_space = StateSpace()    
    
    # add states
    if (len(test_setting.NAS_SETTINGS['CONV_KERNEL_SIZES']) == 0) and (len(test_setting.NAS_SETTINGS['CONV_NUM_FILTERS']) == 0):
        sys.exit("NASBase::TOP:: Error - invalid state space")

    # set state space, ignore empty parameters
    if len(test_setting.NAS_SETTINGS['CONV_KERNEL_SIZES']) > 0:
        state_space.add_state(name='kernel', values=test_setting.NAS_SETTINGS['CONV_KERNEL_SIZES'])
    if len(test_setting.NAS_SETTINGS['CONV_NUM_FILTERS']) > 0:
        state_space.add_state(name='filters', values=test_setting.NAS_SETTINGS['CONV_NUM_FILTERS'])
        
    # print the state space being searched
    state_space.print_state_space()

    # prepare the training data for the NetworkManager
    x_train, y_train, x_test, y_test = _get_training_data(DATASET, NUM_CLASS, IMG_SIZE, IMG_CHANNEL)    
    data_loader = [x_train, y_train, x_test, y_test]  # pack the dataset for the NetworkManager

    previous_acc = 0.0
    total_reward = 0.0

    with policy_sess.as_default():
        # create the Controller and build the internal policy network
        controller = Controller(test_setting, policy_sess, NUM_LAYERS, state_space,
                                reg_param=REGULARIZATION,
                                exploration=EXPLORATION,
                                controller_cells=CONTROLLER_CELLS,
                                embedding_dim=EMBEDDING_DIM,
                                restore_controller=RESTORE_CONTROLLER)

    # create the Network Manager
    manager = NetworkManager(test_setting, data_loader, epochs=MAX_EPOCHS, child_batchsize=CHILD_BATCHSIZE, clip_rewards=CLIP_REWARDS,
                             acc_beta=ACCURACY_BETA)

    # get an initial random state space if controller needs to predict an
    # action from the initial state
    state = state_space.get_random_state_space(NUM_LAYERS)
    print("NASBase::TOP:: Initial Random State : ", state_space.parse_state_space_list(state))
    print()

    # clear the previous files
    #controller.remove_files()
    tracked_acc = {}
    old_acc = 0.7
    ite_count=0
    acc_list = []
    per_list = []
    rew_list = []
    loss_list = []
    old_action=[]
    old_action_cnt=0
    
    # train for number of trails
    for trial in range(MAX_TRIALS):
        
        ite_count+=1
        print("NASBase::TOP:: ===================This is TRIAL:", ite_count,"Let's go====================")
        with policy_sess.as_default():
            K.set_session(policy_sess)
            actions = controller.get_action(state)  # get an action for the previous state

            action_list = state_space.parse_state_space_list(actions)
            if (tuple(old_action)==tuple(action_list)) and old_action_cnt<1:
                print("[Warning]: Find the same action as previous", old_action_cnt)
                manager.update_moving_acc()
                old_action_cnt+=1
            elif (tuple(old_action)==tuple(action_list)) and old_action_cnt==1:
                print("[Warning]: Find the same action as previous reaching maximum, generate randomly")
                manager.update_moving_acc()
                actions = controller.get_rand_action(state)
                old_action_cnt=0
            elif (tuple(old_action)!=tuple(action_list)):
                old_action_cnt=0
            old_action = state_space.parse_state_space_list(actions)
            

        # print the action probabilities
        #state_space.print_actions(actions)
        print("NASBase::TOP:: ######## Predicted actions : ", state_space.parse_state_space_list(actions)) # generate CNN architecture parameters
       
        action_to_simulator=state_space.parse_state_space_list(actions)

        # build a model, train and get reward and accuracy from the network manager
        model_fn = get_model_fn(MODEL_FN_TYPE)
        start=time.time()
        reward, previous_acc, time_performance, exec_design = manager.get_rewards(model_fn, state_space.parse_state_space_list(actions), LATENCY_REQ , test_setting, tracked_acc)  # CNN train and return the best accuracy
        end=time.time()
        per_list.append(time_performance)
        print("NASBase::TOP:: time taken to derive reward", end-start,"\n")

        action_tuple = tuple(state_space.parse_state_space_list(actions))
        tracked_acc[action_tuple] = previous_acc


        print("NASBase::TOP:: Rewards : ", reward, "Accuracy : ", previous_acc)
        acc_list.append(previous_acc)
        rew_list.append(reward)

        old_acc = previous_acc 

        with policy_sess.as_default():
            K.set_session(policy_sess)

            total_reward += reward
            print("NASBase::TOP:: Total reward : ", total_reward)

            # actions and states are equivalent, save the state and reward
            state = actions
            controller.store_rollout(state, reward)

            # train the controller on the saved state and the discounted rewards
            loss = controller.train_step()
            print("NASBase::TOP:: Trial %d: Controller loss : %0.6f" % (trial + 1, loss))
            loss_list.append(loss)

            print("NASBase::TOP:: ===============+WWW+=================")
            print("Acc =",acc_list)
            print("Lat =",per_list)
            print("Rew =",rew_list)
            print("Los =",loss_list)            
            print("NASBase::TOP:: =====================================")

            # write the results of this trial into a file
            with open(TRIAL_LOG_DIR + "/" + TRIAL_LOG_FNAME, mode='a+') as f:                
                ts = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
                data = [ts, ite_count, previous_acc, reward, loss]
                lst_state_space = state_space.parse_state_space_list(state) # network arch params
                data.extend([str(lst_state_space)])  # log the network architecture
                data.extend([exec_design_to_string(exec_design)]) # log the execution design details
                writer = csv.writer(f, delimiter=';')
                writer.writerow(data)
        print()

    print("NASBase::TOP:: Total Reward : ", total_reward)
    print("NASBase::TOP:: Search Complete ")

