/*
 * cnn_testbench_pool.c
 */


#include "../cnn_common.h"

#include "cnn_testbench_pool.h"
#include "../cnn_pool.h"

void test_LayerPool(CNNLayer_t *layer){

//    Mat_t* pWeights = &layer->weights;
//    Mat_t* pBias = &layer->bias;
//    Mat_t* pIFM = &layer->ifm;
//    Mat_t* pOFM = &layer->ofm;
    //uint16_t tmp_obuff_size = layer->ofm.ch * layer->ofm.h * layer->ofm.w;
    
//    layer->fun(0, pWeights, pBias, pIFM, pOFM);

    // clear footprints
    CNN_ClearFootprints_LayerMaxPool();
}

