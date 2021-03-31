/*
 * cnn_testbench_fc.c
 */



#include "cnn_testbench_fc.h"

#include "../cnn_fc.h"


void test_LayerFC(CNNLayer_t *layer){

//    Mat_t* pWeights = &layer->weights;
//    Mat_t* pBias = &layer->bias;
//    Mat_t* pIFM = &layer->ifm;
//    Mat_t* pOFM = &layer->ofm;
    //uint16_t tmp_obuff_size = layer->ofm.ch * layer->ofm.h * layer->ofm.w;

    //CNN_LayerFC(0, pWeights, pBias, pIFM, pOFM);
//    layer->fun(0, pWeights, pBias, pIFM, pOFM);

    // clear footprints
    CNN_ClearFootprints_LayerFC();
}

