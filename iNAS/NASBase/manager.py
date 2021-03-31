'''
This NASBase module of the iNAS framework is based on the following hardware-aware NAS engine:
Source code: https://github.com/PITT-JZ-COOP/FPGA-implementation-Aware-Neural-Architecture-Search
Paper title: Accuracy vs. efficiency: Achieving both through fpga-implementation aware neural architecture search
Authors: Jiang, W., Zhang, X., Sha, E.H.M., Yang, L., Zhuge, Q., Shi, Y. and Hu, J., 
In Proc. of DAC 2019
pdf: https://arxiv.org/abs/1901.11211
'''

# -- Helper class performing role of DNN Trainer --

import numpy as np
import keras
from keras.models import Model
from keras import backend as K
from keras.callbacks import ModelCheckpoint
import tensorflow as tf
from .plat_perf import PlatPerf
import math
import time


class EpochPrintingCallback(keras.callbacks.Callback):    
    def on_epoch_end(self, epoch, logs=None):
        if (epoch % 10) == 0:
            print(
                "The accuracy and loss for epoch {} is {:7.2f},{:7.2f}".format(
                    epoch, logs["loss"], logs["val_acc"]
                )                
            )

class NetworkManager:
    '''
    Helper class to manage the generation of subnetwork training given a dataset
    '''
    def __init__(self, inas_settings, dataset, epochs=5, child_batchsize=128, acc_beta=0.8, clip_rewards=0.0 ):
        '''
        Manager which is tasked with creating subnetworks, training them on a dataset, and retrieving
        rewards in the term of accuracy, which is passed to the controller RNN.

        Args:
            dataset: a tuple of 4 arrays (X_train, y_train, X_val, y_val)
            epochs: number of epochs to train the subnetworks
            child_batchsize: batchsize of training the subnetworks
            acc_beta: exponential weight for the accuracy
            clip_rewards: float - to clip rewards in [-range, range] to prevent
                large weight updates. Use when training is highly unstable.
        '''
        self.global_suffix = inas_settings.GLOBAL_SETTINGS['EXP_SUFFIX']

        self.dataset = dataset
        self.epochs = epochs
        self.batchsize = child_batchsize
        self.clip_rewards = clip_rewards

        self.beta = acc_beta
        self.beta_bias = acc_beta
        self.moving_acc = 0.0


    def get_rewards(self, model_fn, actions, latency_req, setting, tracked_acc):
        '''
        Creates a subnetwork given the actions predicted by the controller RNN,
        trains it on the provided dataset, and then returns a reward.

        Args:
            model_fn: a function which accepts one argument, a list of
                parsed actions, obtained via an inverse mapping from the
                StateSpace.
            actions: a list of parsed actions obtained via an inverse mapping
                from the StateSpace. It is in a specific order as given below:

                Consider 4 states were added to the StateSpace via the `add_state`
                method. Then the `actions` array will be of length 4, with the
                values of those states in the order that they were added.

                If number of layers is greater than one, then the `actions` array
                will be of length `4 * number of layers` (in the above scenario).
                The index from [0:4] will be for layer 0, from [4:8] for layer 1,
                etc for the number of layers.

                These action values are for direct use in the construction of models.

        Returns:
            a reward for training a model with the given actions
        '''
        with tf.Session(graph=tf.Graph()) as network_sess:
            #tf.random.set_random_seed(setting.NAS_SETTINGS['SEED'])
            K.set_session(network_sess)
            model, error = model_fn(actions,plat_settings = setting.PLATFORM_SETTINGS, nas_settings = setting.NAS_SETTINGS )  # type: Model, int

            if(error != 0):
                print("NASBase::MANAGER:: Build model failed : ERROR: %d"%(error))
                return -0.1 , 0, math.inf , None

            start=time.time()
            performance_model = PlatPerf(setting.NAS_SETTINGS, setting.PLATFORM_SETTINGS)
            time_performance, exec_design, error = performance_model.get_inference_latency(actions)
            end=time.time()

            print("NASBase::MANAGER:: Execution Design E2E Latency = ", time_performance , " ; search time = ", end-start,"\n","\n")


            if (time_performance < 0): # no feasible execution solution (either spatial/atomicity errors)
                print("NASBase::MANAGER:: time_performance failed (exec design not found), abort CNN training ----------------------------------  ", "\n")                
                return -0.1 , 0, math.inf, None 
            
            elif (latency_req < time_performance):
                print("NASBase::MANAGER:: time_performance failed (latency req not met), abort CNN training ----------------------------------  ", "\n")
                performance_reward=((latency_req-time_performance)/10/latency_req)-1
                acc=0
                performance_reward = np.clip(performance_reward, -0.1, 0.1)
                return performance_reward, acc , time_performance, exec_design
            
            else:
                print("NASBase::MANAGER:: time_performance met, doing CNN training now ++++++++++++++++++++++++++++++++++", "\n")
                performance_reward=(time_performance)/latency_req/10    # normalized from 0 to 0.1                
                
                # generate a submodel given predicted actions
                model.compile('adam', 'categorical_crossentropy', metrics=['accuracy'])

                # unpack the dataset
                X_train, y_train, X_val, y_val = self.dataset

                print("NASBase::MANAGER:: ===----",X_train.shape)
                
                h5_fname = 'weights/' + self.global_suffix + '/temp_network_' + self.global_suffix + '.h5'

                # train the model using Keras methods
                model.fit(X_train, y_train, batch_size=self.batchsize, epochs=self.epochs,
                                            verbose=0, validation_data=(X_val, y_val),
                                            callbacks=[ModelCheckpoint(h5_fname,
                                                                        monitor='val_acc', verbose=0,
                                                                        save_best_only=True,
                                                                        save_weights_only=True),
                                                                        EpochPrintingCallback()])

                # load best performance epoch in this training session
                model.load_weights(h5_fname)

                # evaluate the model
                loss, acc = model.evaluate(X_val, y_val, batch_size=self.batchsize)


                print("NASBase::MANAGER:: ++++++++++++Reward Calculation:",acc,self.moving_acc,performance_reward)
                # compute the reward
                reward = (acc - self.moving_acc + performance_reward)

                # if rewards are clipped, clip them in the range -0.05 to 0.05
                if self.clip_rewards:
                    reward = np.clip(reward, -0.05, 0.05)

                # update moving accuracy with bias correction for 1st update
                if self.beta > 0.0 and self.beta < 1.0:
                    self.moving_acc = self.beta * self.moving_acc + (1 - self.beta) * acc
                    self.moving_acc = self.moving_acc / (1 - self.beta_bias)
                    self.beta_bias = 0

                    reward = np.clip(reward, -0.1, 0.1)

                print()
                print("NASBase::MANAGER:: EWA Accuracy = ", self.moving_acc)

            # clean up resources and GPU memory
            network_sess.close()
            return reward, acc, time_performance, exec_design

    def update_moving_acc(self):
        self.moving_acc = (1+0.2)*self.moving_acc
