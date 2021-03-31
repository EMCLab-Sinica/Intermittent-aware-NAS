# this code is adapted from : https://github.com/bhimmetoglu/time-series-medicine/blob/master/HAR/HAR-CNN.ipynb

import pandas as pd 
import os, sys
from sklearn.model_selection import train_test_split
import numpy as np

def read_data(data_path, split = "train"):
	""" Read data """

	#print(data_path); sys.exit()

	# Fixed params
	n_class = 6
	n_steps = 128

	# Paths
	path_ = os.path.join(data_path, split)
	path_signals = os.path.join(path_, "Inertial Signals")

	# Read labels and one-hot encode
	label_path = os.path.join(path_, "y_" + split + ".txt")
	labels = pd.read_csv(label_path, header = None)

	# Read time-series data
	channel_files = os.listdir(path_signals)
	channel_files.sort()
	n_channels = len(channel_files)
	posix = len(split) + 5

	#print(channel_files)

	# Initiate array
	list_of_channels = []
	X = np.zeros((len(labels), n_steps, n_channels))	# (7352 rows x 128 cols x 9 channels)
	i_ch = 0
	for fil_ch in channel_files:
		channel_name = fil_ch[:-posix]
		dat_ = pd.read_csv(os.path.join(path_signals,fil_ch), delim_whitespace = True, header = None)	# 7352 rows x 128 cols
	
		#print(dat_); sys.exit()

		# X[:,:,i_ch] = dat_.as_matrix()
		X[:,:,i_ch] = dat_.values		

		# Record names
		list_of_channels.append(channel_name)

		# iterate
		i_ch += 1

	# Return 
	return X, labels[0].values, list_of_channels

def standardize(train, test):
	""" Standardize data """

	# Standardize train and test
	X_train = (train - np.mean(train, axis=0)[None,:,:]) / np.std(train, axis=0)[None,:,:]
	X_test = (test - np.mean(test, axis=0)[None,:,:]) / np.std(test, axis=0)[None,:,:]

	return X_train, X_test

def one_hot(labels, n_class = 6):
	""" One-hot encoding """
	expansion = np.eye(n_class)
	y = expansion[:, labels-1].T
	assert y.shape[1] == n_class, "Wrong number of labels!"

	return y

def get_batches(X, y, batch_size = 100):
	""" Return a generator for batches """
	n_batches = len(X) // batch_size
	X, y = X[:n_batches*batch_size], y[:n_batches*batch_size]

	# Loop over batches and yield
	for b in range(0, len(X), batch_size):
		yield X[b:b+batch_size], y[b:b+batch_size]


# smartphone training data obtained from :
# https://archive.ics.uci.edu/ml/datasets/Human+Activity+Recognition+Using+Smartphones
# data then organized into /UCI/Data/<test/train> folders
def har_getdata():
	dir_path = os.path.dirname(os.path.realpath(__file__))
	X_train, labels_train, list_ch_train = read_data(data_path=dir_path+"/UCI/Data/", split="train") # train
	X_test, labels_test, list_ch_test = read_data(data_path=dir_path+"/UCI/Data/", split="test") # test
	X_train, X_test = standardize(X_train, X_test)

	y_train = one_hot(labels_train)
	y_test = one_hot(labels_test)

	# print(np.shape(X_train))	# (7352, 128, 9)
	# print(np.shape(y_train))	# (7352, 6)
	# print(np.shape(X_test))		# (2947, 128, 9)
	# print(np.shape(y_test))		# (2947, 6)
	# sys.exit()

	return X_train, y_train , X_test ,y_test
