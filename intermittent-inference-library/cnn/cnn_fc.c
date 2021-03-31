/*
 * cnn_fc.c
 * FC Layer is essentially a CONV layer, so we can use the CONV implementation
 * Only dummy functions (for future extensions, if any)
 */

#include "../utils/util_macros.h"

#include "cnn_common.h"
#include "cnn_matops.h"

#include "cnn_fc.h"

#include "cnn_buffer_sizes.h"


#pragma PERSISTENT(FP_LayerFC)
FootprintsLayerFC_t FP_LayerFC= {0};

// continuous power
void CNN_LayerFC(uint16_t lid, Mat_t* weights, Mat_t* bias, Mat_t* ifm, Mat_t* ofm){
    //_DBGUART("CNN_LayerFC::Enter\r\n");
}
// intermittent power
void CNN_Intermittent_LayerFC(uint16_t lid, Mat_t* weights, Mat_t* bias, Mat_t* ifm, Mat_t* ofm){
    //_DBGUART("CNN_Intermittent_LayerFC::Enter\r\n");    
}


/*************************************************************************
 * FOOTPRINTING
 *************************************************************************/
void CNN_ClearFootprints_LayerFC(){
    FP_LayerFC.ch = 0;
}
void CNN_PrintFootprints_LayerFC(){
    _DBGUART("FP(fc):: %d \r\n", FP_LayerFC.ch);
}
