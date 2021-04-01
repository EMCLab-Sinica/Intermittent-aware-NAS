/* 
* test_model.h 
* (Auto-generated)
* Created on: 05/18/20 
* Label : test_model_i_5_4_c_4_2_1 
*/

#ifndef TEST_MODEL_H_
#define TEST_MODEL_H_

#include "../cnn/cnn_types.h"
#include "../cnn/cnn_conv_tiled_std.h"
#include "../cnn/cnn_fc.h"
#include "../cnn/cnn_pool.h"


// ---- testing for convolution layer -----
#pragma PERSISTENT(DBG_W)
_q15 DBG_W[7][7][2][4]={0};

#pragma PERSISTENT(DBG_I)
_q15 DBG_I[12][12][4]={0};

#pragma PERSISTENT(DBG_O)
_q15 DBG_O[2][2][2]={0};
#pragma PERSISTENT(TestConvLayers_ex1)
CNNLayer_t TestConvLayers_ex1[1]={{
		.lix = 0,
		.fun = CNN_Intermittent_LayerConv_Tiled_Std,
		.weights = (Mat_t){
			.data = 100,
			.n = 16,
			.ch = 32,
			.h = 5,
			.w = 5
		},
		.bias = (Mat_t){
			.data = 316,
			.n = 0,
			.ch = 32,
			.h = 1,
			.w = 1
		},
		.ifm = (Mat_t){
			.data = 324,
			.n = 0,
			.ch = 16,
			.h = 16,
			.w = 16
		},
		.ofm = (Mat_t){
			.data = 400,
			.n = 0,
			.ch = 32,
			.h = 12,
			.w = 12
		},
		.parE = (ExeParams_t){
			.Tn = 16,
			.Tm = 1,
			.Tr = 4,
			.Tc = 6,
			.str= 1,
			.pad= 0,
			.lpOdr = IFM_ORIENTED,
		},
		.parP = (PreParams_t) {
			.preSz = 1
		},
		.idxBuf = 0
}};
#pragma PERSISTENT(TestConvLayers_ex2)
CNNLayer_t TestConvLayers_ex2[1]={{
		.lix = 0,
		.fun = CNN_Intermittent_LayerConv_Tiled_Std,
		.weights = (Mat_t){
			.data = 100,
			.n = 16,
			.ch = 32,
			.h = 5,
			.w = 5
		},
		.bias = (Mat_t){
			.data = 316,
			.n = 0,
			.ch = 32,
			.h = 1,
			.w = 1
		},
		.ifm = (Mat_t){
			.data = 324,
			.n = 0,
			.ch = 16,
			.h = 16,
			.w = 16
		},
		.ofm = (Mat_t){
			.data = 400,
			.n = 0,
			.ch = 32,
			.h = 12,
			.w = 12
		},
		.parE = (ExeParams_t){
			.Tn = 16,
			.Tm = 2,
			.Tr = 4,
			.Tc = 4,
			.str= 1,
			.pad= 0,
			.lpOdr = OFM_ORIENTED,
		},
		.parP = (PreParams_t) {
			.preSz = 1
		},
		.idxBuf = 0
}};
#pragma PERSISTENT(TestConvLayers_ex3)
CNNLayer_t TestConvLayers_ex3[1]={{
		.lix = 0,
		.fun = CNN_Intermittent_LayerConv_Tiled_Std,
		.weights = (Mat_t){
			.data = 100,
			.n = 16,
			.ch = 32,
			.h = 5,
			.w = 5
		},
		.bias = (Mat_t){
			.data = 316,
			.n = 0,
			.ch = 32,
			.h = 1,
			.w = 1
		},
		.ifm = (Mat_t){
			.data = 324,
			.n = 0,
			.ch = 16,
			.h = 16,
			.w = 16
		},
		.ofm = (Mat_t){
			.data = 400,
			.n = 0,
			.ch = 32,
			.h = 12,
			.w = 12
		},
		.parE = (ExeParams_t){
			.Tn = 16,
			.Tm = 1,
			.Tr = 3,
			.Tc = 6,
			.str= 1,
			.pad= 0,
			.lpOdr = IFM_ORIENTED,
		},
		.parP = (PreParams_t) {
			.preSz = 16
		},
		.idxBuf = 0
}};
#pragma PERSISTENT(TestConvLayers_i_5_4_c_4_2_1)
CNNLayer_t TestConvLayers_i_5_4_c_4_2_1[2] = {
{
	.lix = 0,
	.fun = CNN_Intermittent_LayerConv_Tiled_Std,
	.weights = (Mat_t){
		.data = 100,
		.n = 4,
		.ch = 2,
		.h = 7,
		.w = 7
	},
	.bias = (Mat_t){
		.data = 316,
		.n = 0,
		.ch = 4,
		.h = 1,
		.w = 1
	},
	.ifm = (Mat_t){
		.data = 324,
		.n = 0,
		.ch = 4,
		.h = 12,
		.w = 12
	},
	.ofm = (Mat_t){
		.data = 400,
		.n = 0,
		.ch = 2,
		.h = 2,
		.w = 2
	},
	.parE = (ExeParams_t){
		.Tn = 2,
		.Tm = 2,
		.Tr = 1,
		.Tc = 1,
		.str= 1,
		.pad= 0,
		.lpOdr = OFM_ORIENTED,
	},
	.parP = (PreParams_t) {
		.preSz = 1
	},
	.idxBuf = 0
},
{
	.lix = 1,
	.fun = CNN_Intermittent_LayerConv_Tiled_Std,
	.weights = (Mat_t){
		.data = 1100,
		.n = 4,
		.ch = 2,
		.h = 7,
		.w = 7
	},
	.bias = (Mat_t){
		.data = 1316,
		.n = 0,
		.ch = 4,
		.h = 1,
		.w = 1
	},
	.ifm = (Mat_t){
		.data = 1324,
		.n = 0,
		.ch = 4,
		.h = 12,
		.w = 12
	},
	.ofm = (Mat_t){
		.data = 1400,
		.n = 0,
		.ch = 2,
		.h = 2,
		.w = 2
	},
	.parE = (ExeParams_t){
		.Tn = 2,
		.Tm = 2,
		.Tr = 1,
		.Tc = 1,
		.str= 1,
		.pad= 0,
		.lpOdr = OFM_ORIENTED,
	},
	.parP = (PreParams_t) {
		.preSz = 1
	},
	.idxBuf = 0
}
};
#pragma PERSISTENT(TEST_CNN_MODEL)
CNNLayer_t TEST_CNN_MODEL[6] = {
{
	.lix = 0,
	.fun = CNN_Intermittent_LayerConv_Tiled_Std,
	.weights = (Mat_t){
		.data = 23332,
		.n = 10,
		.ch = 1,
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
		.ch = 1,
		.h = 28,
		.w = 28
	},
	.ofm = (Mat_t){
		.data = 11716,
		.n = 1,
		.ch = 10,
		.h = 24,
		.w = 24
	},
	.parE = (ExeParams_t){
		.Tn = 2,
		.Tm = 2,
		.Tr = 2,
		.Tc = 2,
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
		.data = 23832,
		.n = 12,
		.ch = 10,
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
		.data = 11716,
		.n = 1,
		.ch = 10,
		.h = 24,
		.w = 24
	},
	.ofm = (Mat_t){
		.data = 100,
		.n = 1,
		.ch = 12,
		.h = 22,
		.w = 22
	},
	.parE = (ExeParams_t){
		.Tn = 2,
		.Tm = 2,
		.Tr = 2,
		.Tc = 2,
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
	.lix = 2,
	.fun = CNN_Intermittent_LayerConv_Tiled_Std,
	.weights = (Mat_t){
		.data = 25992,
		.n = 14,
		.ch = 12,
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
		.ch = 12,
		.h = 22,
		.w = 22
	},
	.ofm = (Mat_t){
		.data = 11716,
		.n = 1,
		.ch = 14,
		.h = 20,
		.w = 20
	},
	.parE = (ExeParams_t){
		.Tn = 2,
		.Tm = 2,
		.Tr = 2,
		.Tc = 2,
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
	.lix = 3,
	.fun = CNN_Intermittent_LayerConv_Tiled_Std,
	.weights = (Mat_t){
		.data = 29016,
		.n = 16,
		.ch = 14,
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
		.data = 11716,
		.n = 1,
		.ch = 14,
		.h = 20,
		.w = 20
	},
	.ofm = (Mat_t){
		.data = 100,
		.n = 1,
		.ch = 16,
		.h = 18,
		.w = 18
	},
	.parE = (ExeParams_t){
		.Tn = 2,
		.Tm = 2,
		.Tr = 2,
		.Tc = 2,
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
		.data = 100,
		.n = 1,
		.ch = 16,
		.h = 18,
		.w = 18
	},
	.ofm = (Mat_t){
		.data = 11716,
		.n = 1,
		.ch = 16,
		.h = 1,
		.w = 1
	},
	.parE = (ExeParams_t){
		.Tn = 2,
		.Tm = 2,
		.Tr = 2,
		.Tc = 2,
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
	.lix = 5,
	.fun = CNN_Intermittent_LayerConv_Tiled_Std,
	.weights = (Mat_t){
		.data = 33048,
		.n = 10,
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
		.data = 11716,
		.n = 1,
		.ch = 16,
		.h = 1,
		.w = 1
	},
	.ofm = (Mat_t){
		.data = 100,
		.n = 1,
		.ch = 10,
		.h = 1,
		.w = 1
	},
	.parE = (ExeParams_t){
		.Tn = 2,
		.Tm = 2,
		.Tr = 2,
		.Tc = 2,
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
	.Layers       = TestConvLayers_ex1,
	.numLayers = 1,
	.name = "TestConvLayers_ex3"
};

#endif /* TEST_MODEL_H_ */
