/*
 * cnn_matops.h 
 */

#ifndef CNN_MATOPS_H_
#define CNN_MATOPS_H_

#include "../utils/util_macros.h"
#include "cnn_common.h"



void CNN_MatrixAdd(_q15 *matA, _q15 *matB, _q15 *result, uint16_t h, uint16_t w);
void CNN_MatrixMultiply(_q15 *matA, _q15 *matB, _q15 *result,
                        uint16_t matA_h, uint16_t matA_w, uint16_t matB_h, uint16_t matB_w);

void CNN_VectorMAC(_q15 *vecA, _q15 *vecB, uint16_t vecLen, _iq31 *result);

#endif /* CNN_MATOPS_H_ */
