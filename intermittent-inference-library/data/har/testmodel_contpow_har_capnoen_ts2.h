/* 
* TestModel_CONTPOW_har_capNoEn_ts2.h 
* (Auto-generated)
* Created on: 02/27/21,17:01:13 
* Label : TestModel_CONTPOW_har_capNoEn_ts2 
*/

#ifndef TESTMODEL_CONTPOW_HAR_CAPNOEN_TS2_H_
#define TESTMODEL_CONTPOW_HAR_CAPNOEN_TS2_H_

#include "../cnn/cnn_types.h"
#include "../cnn/cnn_conv_tiled_std.h"
#include "../cnn/cnn_fc.h"
#include "../cnn/cnn_pool.h"



#pragma PERSISTENT(TestModel_CONTPOW_har_capNoEn_ts2)
CNNLayer_t TestModel_CONTPOW_har_capNoEn_ts2[5] = {
{
	.lix = 0,
	.fun = CNN_Intermittent_LayerConv_Tiled_Std,
	.weights = (Mat_t){
		.data = 129124,
		.n = 16,
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
		.data = 64612,
		.n = 1,
		.ch = 16,
		.h = 128,
		.w = 1
	},
	.parE = (ExeParams_t){
		.Tn = 1,
		.Tm = 16,
		.Tr = 32,
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
		.data = 129412,
		.n = 16,
		.ch = 16,
		.h = 3,
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
		.data = 64612,
		.n = 1,
		.ch = 16,
		.h = 128,
		.w = 1
	},
	.ofm = (Mat_t){
		.data = 100,
		.n = 1,
		.ch = 16,
		.h = 126,
		.w = 1
	},
	.parE = (ExeParams_t){
		.Tn = 16,
		.Tm = 16,
		.Tr = 7,
		.Tc = 1,
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
		.data = 130948,
		.n = 8,
		.ch = 16,
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
		.data = 100,
		.n = 1,
		.ch = 16,
		.h = 126,
		.w = 1
	},
	.ofm = (Mat_t){
		.data = 64612,
		.n = 1,
		.ch = 8,
		.h = 122,
		.w = 1
	},
	.parE = (ExeParams_t){
		.Tn = 16,
		.Tm = 8,
		.Tr = 2,
		.Tc = 1,
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
		.data = 64612,
		.n = 1,
		.ch = 8,
		.h = 122,
		.w = 1
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
		.Tr = 122,
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
	.lix = 4,
	.fun = CNN_Intermittent_LayerConv_Tiled_Std,
	.weights = (Mat_t){
		.data = 132228,
		.n = 6,
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
		.data = 64612,
		.n = 1,
		.ch = 6,
		.h = 1,
		.w = 1
	},
	.parE = (ExeParams_t){
		.Tn = 8,
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
	.Layers       = TestModel_CONTPOW_har_capNoEn_ts2,
	.numLayers = 5,
	.name = "TestModel_CONTPOW_har_capNoEn_ts2"
};

#endif /* TESTMODEL_CONTPOW_HAR_CAPNOEN_TS2_H_ */
