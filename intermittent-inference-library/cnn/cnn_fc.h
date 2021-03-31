/*
 * cnn_fc.h
 */

#ifndef CNN_FC_H_
#define CNN_FC_H_

#include <stdint.h>

#include "DSPLib.h"

#include "cnn_types.h"

void CNN_LayerFC(uint16_t lid, Mat_t* weights, Mat_t* bias, Mat_t* ifm, Mat_t* ofm);
void CNN_Intermittent_LayerFC(uint16_t lid, Mat_t* weights, Mat_t* bias, Mat_t* ifm, Mat_t* ofm);


// helpers
void CNN_ClearFootprints_LayerFC(void);
void CNN_PrintFootprints_LayerFC(void);

#endif /* CNN_FC_H_ */
