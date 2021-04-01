/* 
* TestModel_INTPOW_kws_cap01_ts3.h 
* (Auto-generated)
* Created on: 03/02/21,20:38:13 
* Label : TestModel_INTPOW_kws_cap01_ts3 
*/

#ifndef TESTMODEL_INTPOW_KWS_CAP01_TS3_H_
#define TESTMODEL_INTPOW_KWS_CAP01_TS3_H_

#include "../cnn/cnn_types.h"
#include "../cnn/cnn_conv_tiled_std.h"
#include "../cnn/cnn_fc.h"
#include "../cnn/cnn_pool.h"



#pragma PERSISTENT(TestModel_INTPOW_kws_cap01_ts3)
CNNLayer_t TestModel_INTPOW_kws_cap01_ts3[5] = {
{
	.lix = 0,
	.fun = CNN_Intermittent_LayerConv_Tiled_Std,
	.weights = (Mat_t){
		.data = 1100,
		.n = 96,
		.ch = 1,
		.h = 250,
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
		.ch = 1,
		.h = 250,
		.w = 1
	},
	.ofm = (Mat_t){
		.data = 600,
		.n = 1,
		.ch = 96,
		.h = 1,
		.w = 1
	},
	.parE = (ExeParams_t){
		.Tn = 1,
		.Tm = 1,
		.Tr = 1,
		.Tc = 1,
		.str = 1,
		.pad = 0,
		.lpOdr = IFM_ORIENTED
	},
	.parP = (PreParams_t){
		.preSz = 12,
	},
	.idxBuf = 0
},
{
	.lix = 1,
	.fun = CNN_Intermittent_LayerConv_Tiled_Std,
	.weights = (Mat_t){
		.data = 49100,
		.n = 128,
		.ch = 96,
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
		.data = 600,
		.n = 1,
		.ch = 96,
		.h = 1,
		.w = 1
	},
	.ofm = (Mat_t){
		.data = 100,
		.n = 1,
		.ch = 128,
		.h = 1,
		.w = 1
	},
	.parE = (ExeParams_t){
		.Tn = 96,
		.Tm = 1,
		.Tr = 1,
		.Tc = 1,
		.str = 1,
		.pad = 0,
		.lpOdr = IFM_ORIENTED
	},
	.parP = (PreParams_t){
		.preSz = 128,
	},
	.idxBuf = 0
},
{
	.lix = 2,
	.fun = CNN_Intermittent_LayerConv_Tiled_Std,
	.weights = (Mat_t){
		.data = 73676,
		.n = 48,
		.ch = 128,
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
		.ch = 128,
		.h = 1,
		.w = 1
	},
	.ofm = (Mat_t){
		.data = 600,
		.n = 1,
		.ch = 48,
		.h = 1,
		.w = 1
	},
	.parE = (ExeParams_t){
		.Tn = 128,
		.Tm = 1,
		.Tr = 1,
		.Tc = 1,
		.str = 1,
		.pad = 0,
		.lpOdr = IFM_ORIENTED
	},
	.parP = (PreParams_t){
		.preSz = 48,
	},
	.idxBuf = 0
},
{
	.lix = 3,
	.fun = CNN_Intermittent_LayerConv_Tiled_Std,
	.weights = (Mat_t){
		.data = 85964,
		.n = 48,
		.ch = 48,
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
		.data = 600,
		.n = 1,
		.ch = 48,
		.h = 1,
		.w = 1
	},
	.ofm = (Mat_t){
		.data = 100,
		.n = 1,
		.ch = 48,
		.h = 1,
		.w = 1
	},
	.parE = (ExeParams_t){
		.Tn = 48,
		.Tm = 1,
		.Tr = 1,
		.Tc = 1,
		.str = 1,
		.pad = 0,
		.lpOdr = IFM_ORIENTED
	},
	.parP = (PreParams_t){
		.preSz = 48,
	},
	.idxBuf = 0
},
{
	.lix = 4,
	.fun = CNN_Intermittent_LayerConv_Tiled_Std,
	.weights = (Mat_t){
		.data = 90572,
		.n = 12,
		.ch = 48,
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
		.ch = 48,
		.h = 1,
		.w = 1
	},
	.ofm = (Mat_t){
		.data = 600,
		.n = 1,
		.ch = 12,
		.h = 1,
		.w = 1
	},
	.parE = (ExeParams_t){
		.Tn = 48,
		.Tm = 12,
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
	.Layers       = TestModel_INTPOW_kws_cap01_ts3,
	.numLayers = 5,
	.name = "TestModel_INTPOW_kws_cap01_ts3"
};

#endif /* TESTMODEL_INTPOW_KWS_CAP01_TS3_H_ */
