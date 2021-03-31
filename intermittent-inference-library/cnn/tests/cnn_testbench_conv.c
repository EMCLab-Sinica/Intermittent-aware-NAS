/*
 * cnn_testbench_conv.c
 *
 */


#include "../cnn_common.h"

#include "cnn_testbench_conv.h"
#include "../cnn_conv_tiled_std.h"
#include "../cnn_matops.h"






#if (CNN_TB_TYPE == TB_COMBOLAYER_CONV)


#pragma PERSISTENT(TBlayer)
CNNLayer_t TBlayer = (CNNLayer_t){
    .lix = 0,
    .fun = CNN_LayerConv_Tiled_Std,
    .weights = (Mat_t){
        .data = 100,    .n = 0, .ch = 0, .h = 0, .w = 0
    },
    .bias = (Mat_t){
        .data = 316,    .n = 0, .ch = 0, .h = 0, .w = 0
    },
    .ifm = (Mat_t){
        .data = 324,    .n = 0, .ch = 0, .h = 0, .w = 0
    },
    .ofm = (Mat_t){
        .data = 400,    .n = 0, .ch = 0, .h = 0, .w = 0
    },
    .parE = (ExeParams_t){
        .Tn = 0, .Tm = 0, .Tr = 0, .Tc = 0, .str=1, .pad=0, .lpOdr = WEIGHT_ORIENTED,
    },
    .parP = (PreParams_t) {
        .preSz = 1
    },
    .idxBuf = 0
};


#endif




void test_LayerConv_Combo(){
#if (CNN_TB_TYPE == TB_COMBOLAYER_CONV)
    uint16_t i;
    uint16_t itr, itc, itm, itn, iH, iK, iM, iN;
    uint16_t combo_count = 0;
    uint16_t Bin, Bw, Bout;

    // combos
    uint16_t arr_tr[1]          = {2};
    uint16_t arr_tc[1]          = {2};
    uint16_t arr_tm[4]          = {2, 8 , 16 , 32};
    uint16_t arr_tn[4]          = {2, 8 , 16 , 32};
    uint16_t arr_ifm_size[1]    = {8};
    uint16_t arr_N[1]           = {32};
    uint16_t arr_k_size[1]      = {5};
    uint16_t arr_M[1]           = {32};


    // loop through all combos
    for (itr=0; itr<1; itr++){
      for (itc=0; itc<1; itc++){
        for (itm=0; itm<4; itm++){
          for (itn=0; itn<4; itn++){

            // layer dims
            for (iH=0; iH<1; iH++){
              for (iK=0; iK<1; iK++){
                for (iM=0; iM<1; iM++){
                  for (iN=0; iN<1; iN++){

                      // set the layer properties
                      TBlayer.weights.n     = arr_M[iM];
                      TBlayer.weights.ch    = arr_N[iN];
                      TBlayer.weights.h     = arr_k_size[iK];
                      TBlayer.weights.w     = arr_k_size[iK];

                      TBlayer.ifm.ch        = arr_N[iN];
                      TBlayer.ifm.h         = arr_ifm_size[iH];
                      TBlayer.ifm.w         = arr_ifm_size[iH];

                      TBlayer.ofm.ch = arr_M[iM];
                      TBlayer.ofm.h = ((( (arr_ifm_size[iH] - arr_k_size[iK]) + (2*0))/1) + 1); // stride = 1, padding 0
                      TBlayer.ofm.w = ((( (arr_ifm_size[iH] - arr_k_size[iK]) + (2*0))/1) + 1); // stride = 1, padding 0

                      TBlayer.parE.Tr = arr_tr[itr];
                      TBlayer.parE.Tc = arr_tc[itc];
                      TBlayer.parE.Tm = arr_tm[itm];
                      TBlayer.parE.Tn = arr_tn[itn];


                      Bin = ( (1*TBlayer.parE.Tr + TBlayer.weights.h) - 1) * ( (1*TBlayer.parE.Tc + TBlayer.weights.w) - 1) * TBlayer.parE.Tn;
                      Bw = TBlayer.weights.h * TBlayer.weights.w * TBlayer.parE.Tn * TBlayer.parE.Tm;
                      Bout = TBlayer.parE.Tr * TBlayer.parE.Tc * TBlayer.parE.Tm;

                      if ((Bin+Bw+Bout) < LEA_MEM_SIZE){ // fits in LEAMEM ?

                          if ( (  (TBlayer.ofm.h % TBlayer.parE.Tr)==0) && ((TBlayer.ofm.w % TBlayer.parE.Tc)==0) && \
                             ((TBlayer.ofm.ch % TBlayer.parE.Tm)==0) && ((TBlayer.ifm.ch % TBlayer.parE.Tn)==0) && \
                             (TBlayer.weights.h < TBlayer.ifm.h) && (TBlayer.ofm.ch >= TBlayer.ifm.ch)){

                              TBlayer.lix=combo_count; // temp counter (for display)


//                              _DBGUART("running - %d, %d, %d, %d, %d, %d, %d, %d\r\n",TBlayer.parE.Tr, TBlayer.parE.Tc, TBlayer.parE.Tm, TBlayer.parE.Tn,
//                                                                                       TBlayer.ifm.h, TBlayer.ifm.ch, TBlayer.weights.h, TBlayer.weights.n);

                              // ==============================================
                              _lpm_sleep(10);
                              for (i=0;i<1;i++){
//                            	  if(combo_count < 38)break;
                                  test_LayerConv(&TBlayer);
//                                  _DBGUART("-- Done %d %d %d %d\r\n",Bin,Bw,Bout,combo_count);
                              }
                              _lpm_sleep(10);
                              // ==============================================

//                              _DBGUART("finished combo_count = %d\r\n",combo_count);

                              combo_count++;


                          }
                      }
                  }
                }
              }
            }
          }
        }
      }
    }

//    _DBGUART("-- Done CNT : %d\r\n",combo_count);


    _STOP();
#endif
}



// test a full layer
void test_LayerConv(CNNLayer_t *layer){

    Mat_t* pWeights = &layer->weights;
    Mat_t* pBias = &layer->bias;
    Mat_t* pIFM = &layer->ifm;
    Mat_t* pOFM = &layer->ofm;
    ExeParams_t *parE = &layer->parE;
	PreParams_t *parP = &layer->parP;

    layer->fun(layer->lix, pWeights, pBias, pIFM, pOFM,parE,parP,layer->idxBuf);
//    layer->idxBuf^=0x1;
//    CNN_ClearFootprints_LayerConv();
}


