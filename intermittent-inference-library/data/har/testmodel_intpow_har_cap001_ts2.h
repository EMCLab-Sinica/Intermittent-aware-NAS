/* 
* TestModel_INTPOW_har_cap001_ts2.h 
* (Auto-generated)
* Created on: 02/27/21,17:01:13 
* Label : TestModel_INTPOW_har_cap001_ts2 
*/

#ifndef TESTMODEL_INTPOW_HAR_CAP001_TS2_H_
#define TESTMODEL_INTPOW_HAR_CAP001_TS2_H_

#include "../cnn/cnn_types.h"
#include "../cnn/cnn_conv_tiled_std.h"
#include "../cnn/cnn_fc.h"
#include "../cnn/cnn_pool.h"



#pragma PERSISTENT(TestModel_INTPOW_har_cap001_ts2)
CNNLayer_t TestModel_INTPOW_har_cap001_ts2[5] = {
{
	.lix = 0,
	.fun = CNN_Intermittent_LayerConv_Tiled_Std,
	.weights = (Mat_t){
		.data = 285796,
		.n = 24,
		.ch = 9,
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
		.ch = 9,
		.h = 128,
		.w = 1
	},
	.ofm = (Mat_t){
		.data = 142948,
		.n = 1,
		.ch = 24,
		.h = 128,
		.w = 1
	},
	.parE = (ExeParams_t){
		.Tn = 1,
		.Tm = 24,
		.Tr = 16,
		.Tc = 1,
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
		.data = 286228,
		.n = 24,
		.ch = 24,
		.h = 5,
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
		.data = 142948,
		.n = 1,
		.ch = 24,
		.h = 128,
		.w = 1
	},
	.ofm = (Mat_t){
		.data = 100,
		.n = 1,
		.ch = 24,
		.h = 124,
		.w = 1
	},
	.parE = (ExeParams_t){
		.Tn = 24,
		.Tm = 1,
		.Tr = 31,
		.Tc = 1,
		.str = 1,
		.pad = 0,
		.lpOdr = IFM_ORIENTED
	},
	.parP = (PreParams_t){
		.preSz = 2,
	},
	.idxBuf = 0
},
{
	.lix = 2,
	.fun = CNN_Intermittent_LayerConv_Tiled_Std,
	.weights = (Mat_t){
		.data = 291988,
		.n = 16,
		.ch = 24,
		.h = 7,
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
		.h = 124,
		.w = 1
	},
	.ofm = (Mat_t){
		.data = 142948,
		.n = 1,
		.ch = 16,
		.h = 118,
		.w = 1
	},
	.parE = (ExeParams_t){
		.Tn = 24,
		.Tm = 1,
		.Tr = 2,
		.Tc = 1,
		.str = 1,
		.pad = 0,
		.lpOdr = IFM_ORIENTED
	},
	.parP = (PreParams_t){
		.preSz = 16,
	},
	.idxBuf = 0
},
{
	.lix = 3,
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
		.data = 142948,
		.n = 1,
		.ch = 16,
		.h = 118,
		.w = 1
	},
	.ofm = (Mat_t){
		.data = 100,
		.n = 1,
		.ch = 16,
		.h = 1,
		.w = 1
	},
	.parE = (ExeParams_t){
		.Tn = 1,
		.Tm = 8,
		.Tr = 1,
		.Tc = 1,
		.str = 1,
		.pad = 0,
		.lpOdr = OFM_ORIENTED
	},
	.parP = (PreParams_t){
		.preSz = 118,
	},
	.idxBuf = 0
},
{
	.lix = 4,
	.fun = CNN_Intermittent_LayerConv_Tiled_Std,
	.weights = (Mat_t){
		.data = 297364,
		.n = 6,
		.ch = 16,
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
		.ch = 16,
		.h = 1,
		.w = 1
	},
	.ofm = (Mat_t){
		.data = 142948,
		.n = 1,
		.ch = 6,
		.h = 1,
		.w = 1
	},
	.parE = (ExeParams_t){
		.Tn = 16,
		.Tm = 6,
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
	.Layers       = TestModel_INTPOW_har_cap001_ts2,
	.numLayers = 5,
	.name = "TestModel_INTPOW_har_cap001_ts2"
};

#endif /* TESTMODEL_INTPOW_HAR_CAP001_TS2_H_ */
