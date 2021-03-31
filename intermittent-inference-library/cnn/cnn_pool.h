/*
 * cnn_pool.h
 */

#ifndef CNN_POOL_H_
#define CNN_POOL_H_

#include <stdint.h>

#include "DSPLib.h"

#include "cnn_types.h"


void CNN_GlobalAveragePool(uint16_t lid, Mat_t* weights, Mat_t* bias, Mat_t* ifm, Mat_t* ofm, ExeParams_t *parE, PreParams_t *parP, uint8_t idxBuf);
void CNN_Intermittent_GlobalAveragePool(uint16_t lid, Mat_t* weights, Mat_t* bias, Mat_t* ifm, Mat_t* ofm, ExeParams_t *parE, PreParams_t *parP, uint8_t idxBuf);


#endif /* CNN_POOL_H_ */
