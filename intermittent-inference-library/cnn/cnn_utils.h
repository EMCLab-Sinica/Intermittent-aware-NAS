/*
 * cnn_utils.h 
 */

#ifndef CNN_UTILS_H_
#define CNN_UTILS_H_


#include <stdint.h>
#include <string.h>


#include "DSPLib.h"

#include "cnn_types.h"

#define DMA_CH DMA_CHANNEL_0
#define DMA_DIR_INC     DMA_DIRECTION_INCREMENT
#define DMA_DIR_DEC     DMA_DIRECTION_DECREMENT
#define DMA_DIR_NC


#define Q15_8888    _Q15(+0.27124)
#define Q15_CLEAR   _Q15(+0.0)

#define HighB(x) (*((_q15 *) &(##x)+1))
_q15 iq31_to_q15(_iq31 *iq31_val_ptr);

void dumpMatrix(Mat_t *mat);
void printQ15Vector(_q15 *buff, uint16_t n);
void printQ15Matrix(_q15 *buff, uint16_t h, uint16_t w);
void setQ15VectorBuff(_q15 *buff, uint16_t n, _q15 val);
void printSumOfVector(_q15 *buff, uint16_t size);
uint32_t offset2D(uint16_t V2,uint16_t V1,uint16_t D1);
uint32_t offset3D(uint16_t V3,uint16_t V2,uint16_t V1,uint16_t D2,uint16_t D1);
uint32_t offset4D(uint16_t V4,uint16_t V3,uint16_t V2,uint16_t V1,uint16_t D3,uint16_t D2,uint16_t D1);

_q15 getIFMElement(Mat_t* m, uint16_t c, uint16_t h, uint16_t w);
_q15 getWeightElement(Mat_t* m, uint16_t n, uint16_t c, uint16_t h, uint16_t w);
_q15 getMatrixElement(Mat_t* m, uint16_t n, uint16_t c, uint16_t h, uint16_t w);

_q15 getMatrixElement_ext(Mat_t* m, uint16_t h, uint16_t w, uint16_t n, uint16_t c);
_q15 getWeightElement_ext(Mat_t* m, uint16_t h, uint16_t w, uint16_t n, uint16_t c);
_q15 getIFMElement_ext(Mat_t* m, uint16_t h, uint16_t w, uint16_t c);

void memcpy_dma_ext(uint32_t nvm_addr, const void* vm_addr, size_t n, size_t dstSize, uint16_t RW);
void memcpy_dma(void* dest, const void* src, size_t n, size_t dstSize, uint16_t srcDir, uint16_t dstDir);
uint16_t addr_loc_type(uint32_t addr);

void _fetch_ifm_tile_RCN_ext(Mat_t* ifm, _q15 *pBuffLoc, uint16_t ifm_t_h, uint16_t ifm_t_w, uint16_t row, uint16_t col, uint16_t ti, uint16_t t_n);
void _fetch_weights_tile_RCMN_ext(Mat_t* weights, _q15 *pBuffLoc, uint16_t to, uint16_t ti, uint16_t t_m, uint16_t t_n);
void _fetch_ofm_tile_RCN_ext(Mat_t* ofm, _q15 *pBuffLoc, uint16_t row, uint16_t col, uint16_t to, uint16_t t_m, uint16_t t_r, uint16_t t_c, uint16_t preSz, LOOPORDER_t lpOdr);
//void _save_ofm_tile_RCN_ext(Mat_t* ofm, _q15 *pBuffLoc, uint16_t row, uint16_t col, uint16_t to, uint16_t t_m, uint16_t t_r, uint16_t t_c);
void _save_ofm_tile_RCN_ext(Mat_t* ofm, uint16_t buffer_idx, _q15 *pBuffLoc, uint16_t row, uint16_t col, uint16_t to, uint16_t t_m, uint16_t t_r, uint16_t t_c, uint16_t preSz, LOOPORDER_t lpOdr);



#endif /* CNN_UTILS_H_ */
