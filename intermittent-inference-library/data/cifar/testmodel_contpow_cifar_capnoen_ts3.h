/* 
* TestModel_CONTPOW_cifar_capNoEn_ts3.h 
* (Auto-generated)
* Created on: 02/26/21,18:34:58 
* Label : TestModel_CONTPOW_cifar_capNoEn_ts3 
*/

#ifndef TESTMODEL_CONTPOW_CIFAR_CAPNOEN_TS3_H_
#define TESTMODEL_CONTPOW_CIFAR_CAPNOEN_TS3_H_

#include "../cnn/cnn_types.h"
#include "../cnn/cnn_conv_tiled_std.h"
#include "../cnn/cnn_fc.h"
#include "../cnn/cnn_pool.h"



#pragma PERSISTENT(TestModel_CONTPOW_cifar_capNoEn_ts3)
CNNLayer_t TestModel_CONTPOW_cifar_capNoEn_ts3[7] = {
{
	.lix = 0,
	.fun = CNN_Intermittent_LayerConv_Tiled_Std,
	.weights = (Mat_t){
		.data = 86500,
		.n = 24,
		.ch = 3,
		.h = 3,
		.w = 3
	},
	.bias = (Mat_t){
		.data = 0,
		.n = 0,
		.ch = 0,
		.h = 0,
		.w = 0
	},
	.ifm = (Mat_t){
		.data = 100,
		.n = 1,
		.ch = 3,
		.h = 32,
		.w = 32
	},
	.ofm = (Mat_t){
		.data = 43300,
		.n = 1,
		.ch = 24,
		.h = 30,
		.w = 30
	},
	.parE = (ExeParams_t){
		.Tn = 1,
		.Tm = 24,
		.Tr = 5,
		.Tc = 6,
		.str = 1,
		.pad = 0,
		.lpOdr = WEIGHT_ORIENTED
	},
	.parP = (PreParams_t){
		.preSz = 1,
	},
	.idxBuf = 0
},
{
	.lix = 1,
	.fun = CNN_Intermittent_LayerConv_Tiled_Std,
	.weights = (Mat_t){
		.data = 87796,
		.n = 4,
		.ch = 24,
		.h = 5,
		.w = 5
	},
	.bias = (Mat_t){
		.data = 0,
		.n = 0,
		.ch = 0,
		.h = 0,
		.w = 0
	},
	.ifm = (Mat_t){
		.data = 43300,
		.n = 1,
		.ch = 24,
		.h = 30,
		.w = 30
	},
	.ofm = (Mat_t){
		.data = 100,
		.n = 1,
		.ch = 4,
		.h = 26,
		.w = 26
	},
	.parE = (ExeParams_t){
		.Tn = 12,
		.Tm = 2,
		.Tr = 1,
		.Tc = 2,
		.str = 1,
		.pad = 0,
		.lpOdr = WEIGHT_ORIENTED
	},
	.parP = (PreParams_t){
		.preSz = 1,
	},
	.idxBuf = 0
},
{
	.lix = 2,
	.fun = CNN_Intermittent_LayerConv_Tiled_Std,
	.weights = (Mat_t){
		.data = 92596,
		.n = 16,
		.ch = 4,
		.h = 5,
		.w = 5
	},
	.bias = (Mat_t){
		.data = 0,
		.n = 0,
		.ch = 0,
		.h = 0,
		.w = 0
	},
	.ifm = (Mat_t){
		.data = 100,
		.n = 1,
		.ch = 4,
		.h = 26,
		.w = 26
	},
	.ofm = (Mat_t){
		.data = 43300,
		.n = 1,
		.ch = 16,
		.h = 22,
		.w = 22
	},
	.parE = (ExeParams_t){
		.Tn = 4,
		.Tm = 2,
		.Tr = 2,
		.Tc = 22,
		.str = 1,
		.pad = 0,
		.lpOdr = IFM_ORIENTED
	},
	.parP = (PreParams_t){
		.preSz = 1,
	},
	.idxBuf = 0
},
{
	.lix = 3,
	.fun = CNN_Intermittent_LayerConv_Tiled_Std,
	.weights = (Mat_t){
		.data = 95796,
		.n = 24,
		.ch = 16,
		.h = 7,
		.w = 7
	},
	.bias = (Mat_t){
		.data = 0,
		.n = 0,
		.ch = 0,
		.h = 0,
		.w = 0
	},
	.ifm = (Mat_t){
		.data = 43300,
		.n = 1,
		.ch = 16,
		.h = 22,
		.w = 22
	},
	.ofm = (Mat_t){
		.data = 100,
		.n = 1,
		.ch = 24,
		.h = 16,
		.w = 16
	},
	.parE = (ExeParams_t){
		.Tn = 8,
		.Tm = 1,
		.Tr = 2,
		.Tc = 2,
		.str = 1,
		.pad = 0,
		.lpOdr = IFM_ORIENTED
	},
	.parP = (PreParams_t){
		.preSz = 1,
	},
	.idxBuf = 0
},
{
	.lix = 4,
	.fun = CNN_Intermittent_LayerConv_Tiled_Std,
	.weights = (Mat_t){
		.data = 133428,
		.n = 8,
		.ch = 24,
		.h = 5,
		.w = 5
	},
	.bias = (Mat_t){
		.data = 0,
		.n = 0,
		.ch = 0,
		.h = 0,
		.w = 0
	},
	.ifm = (Mat_t){
		.data = 100,
		.n = 1,
		.ch = 24,
		.h = 16,
		.w = 16
	},
	.ofm = (Mat_t){
		.data = 43300,
		.n = 1,
		.ch = 8,
		.h = 12,
		.w = 12
	},
	.parE = (ExeParams_t){
		.Tn = 12,
		.Tm = 1,
		.Tr = 3,
		.Tc = 4,
		.str = 1,
		.pad = 0,
		.lpOdr = IFM_ORIENTED
	},
	.parP = (PreParams_t){
		.preSz = 1,
	},
	.idxBuf = 0
},
{
	.lix = 5,
	.fun = CNN_Intermittent_GlobalAveragePool,
	.weights = (Mat_t){
		.data = 0,
		.n = 0,
		.ch = 0,
		.h = 0,
		.w = 0
	},
	.bias = (Mat_t){
		.data = 0,
		.n = 0,
		.ch = 0,
		.h = 0,
		.w = 0
	},
	.ifm = (Mat_t){
		.data = 43300,
		.n = 1,
		.ch = 8,
		.h = 12,
		.w = 12
	},
	.ofm = (Mat_t){
		.data = 100,
		.n = 1,
		.ch = 8,
		.h = 1,
		.w = 1
	},
	.parE = (ExeParams_t){
		.Tn = 1,
		.Tm = 8,
		.Tr = 6,
		.Tc = 12,
		.str = 1,
		.pad = 0,
		.lpOdr = OFM_ORIENTED
	},
	.parP = (PreParams_t){
		.preSz = 1,
	},
	.idxBuf = 0
},
{
	.lix = 6,
	.fun = CNN_Intermittent_LayerConv_Tiled_Std,
	.weights = (Mat_t){
		.data = 143028,
		.n = 10,
		.ch = 8,
		.h = 1,
		.w = 1
	},
	.bias = (Mat_t){
		.data = 0,
		.n = 0,
		.ch = 0,
		.h = 0,
		.w = 0
	},
	.ifm = (Mat_t){
		.data = 100,
		.n = 1,
		.ch = 8,
		.h = 1,
		.w = 1
	},
	.ofm = (Mat_t){
		.data = 43300,
		.n = 1,
		.ch = 10,
		.h = 1,
		.w = 1
	},
	.parE = (ExeParams_t){
		.Tn = 8,
		.Tm = 10,
		.Tr = 1,
		.Tc = 1,
		.str = 1,
		.pad = 0,
		.lpOdr = OFM_ORIENTED
	},
	.parP = (PreParams_t){
		.preSz = 1,
	},
	.idxBuf = 0
}
};

#pragma PERSISTENT(network)
CNNModel_t network={
	.Layers       = TestModel_CONTPOW_cifar_capNoEn_ts3,
	.numLayers = 7,
	.name = "TestModel_CONTPOW_cifar_capNoEn_ts3"
};

#endif /* TESTMODEL_CONTPOW_CIFAR_CAPNOEN_TS3_H_ */
