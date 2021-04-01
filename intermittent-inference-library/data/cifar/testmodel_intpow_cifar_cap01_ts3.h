/* 
* TestModel_INTPOW_cifar_cap01_ts3.h 
* (Auto-generated)
* Created on: 02/26/21,18:34:59 
* Label : TestModel_INTPOW_cifar_cap01_ts3 
*/

#ifndef TESTMODEL_INTPOW_CIFAR_CAP01_TS3_H_
#define TESTMODEL_INTPOW_CIFAR_CAP01_TS3_H_

#include "../cnn/cnn_types.h"
#include "../cnn/cnn_conv_tiled_std.h"
#include "../cnn/cnn_fc.h"
#include "../cnn/cnn_pool.h"



#pragma PERSISTENT(TestModel_INTPOW_cifar_cap01_ts3)
CNNLayer_t TestModel_INTPOW_cifar_cap01_ts3[7] = {
{
	.lix = 0,
	.fun = CNN_Intermittent_LayerConv_Tiled_Std,
	.weights = (Mat_t){
		.data = 43364,
		.n = 4,
		.ch = 3,
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
		.ch = 3,
		.h = 32,
		.w = 32
	},
	.ofm = (Mat_t){
		.data = 21732,
		.n = 1,
		.ch = 4,
		.h = 28,
		.w = 28
	},
	.parE = (ExeParams_t){
		.Tn = 1,
		.Tm = 4,
		.Tr = 4,
		.Tc = 14,
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
	.lix = 1,
	.fun = CNN_Intermittent_LayerConv_Tiled_Std,
	.weights = (Mat_t){
		.data = 43964,
		.n = 16,
		.ch = 4,
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
		.data = 21732,
		.n = 1,
		.ch = 4,
		.h = 28,
		.w = 28
	},
	.ofm = (Mat_t){
		.data = 100,
		.n = 1,
		.ch = 16,
		.h = 26,
		.w = 26
	},
	.parE = (ExeParams_t){
		.Tn = 4,
		.Tm = 1,
		.Tr = 2,
		.Tc = 26,
		.str = 1,
		.pad = 0,
		.lpOdr = IFM_ORIENTED
	},
	.parP = (PreParams_t){
		.preSz = 8,
	},
	.idxBuf = 0
},
{
	.lix = 2,
	.fun = CNN_Intermittent_LayerConv_Tiled_Std,
	.weights = (Mat_t){
		.data = 45116,
		.n = 16,
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
		.data = 100,
		.n = 1,
		.ch = 16,
		.h = 26,
		.w = 26
	},
	.ofm = (Mat_t){
		.data = 21732,
		.n = 1,
		.ch = 16,
		.h = 20,
		.w = 20
	},
	.parE = (ExeParams_t){
		.Tn = 8,
		.Tm = 1,
		.Tr = 2,
		.Tc = 2,
		.str = 1,
		.pad = 0,
		.lpOdr = WEIGHT_ORIENTED
	},
	.parP = (PreParams_t){
		.preSz = 20,
	},
	.idxBuf = 0
},
{
	.lix = 3,
	.fun = CNN_Intermittent_LayerConv_Tiled_Std,
	.weights = (Mat_t){
		.data = 70204,
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
		.data = 21732,
		.n = 1,
		.ch = 16,
		.h = 20,
		.w = 20
	},
	.ofm = (Mat_t){
		.data = 100,
		.n = 1,
		.ch = 24,
		.h = 14,
		.w = 14
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
		.preSz = 24,
	},
	.idxBuf = 0
},
{
	.lix = 4,
	.fun = CNN_Intermittent_LayerConv_Tiled_Std,
	.weights = (Mat_t){
		.data = 107836,
		.n = 24,
		.ch = 24,
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
		.data = 100,
		.n = 1,
		.ch = 24,
		.h = 14,
		.w = 14
	},
	.ofm = (Mat_t){
		.data = 21732,
		.n = 1,
		.ch = 24,
		.h = 8,
		.w = 8
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
		.preSz = 24,
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
		.data = 21732,
		.n = 1,
		.ch = 24,
		.h = 8,
		.w = 8
	},
	.ofm = (Mat_t){
		.data = 100,
		.n = 1,
		.ch = 24,
		.h = 1,
		.w = 1
	},
	.parE = (ExeParams_t){
		.Tn = 1,
		.Tm = 24,
		.Tr = 1,
		.Tc = 8,
		.str = 1,
		.pad = 0,
		.lpOdr = OFM_ORIENTED
	},
	.parP = (PreParams_t){
		.preSz = 8,
	},
	.idxBuf = 0
},
{
	.lix = 6,
	.fun = CNN_Intermittent_LayerConv_Tiled_Std,
	.weights = (Mat_t){
		.data = 164284,
		.n = 10,
		.ch = 24,
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
		.ch = 24,
		.h = 1,
		.w = 1
	},
	.ofm = (Mat_t){
		.data = 21732,
		.n = 1,
		.ch = 10,
		.h = 1,
		.w = 1
	},
	.parE = (ExeParams_t){
		.Tn = 24,
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
	.Layers       = TestModel_INTPOW_cifar_cap01_ts3,
	.numLayers = 7,
	.name = "TestModel_INTPOW_cifar_cap01_ts3"
};

#endif /* TESTMODEL_INTPOW_CIFAR_CAP01_TS3_H_ */
