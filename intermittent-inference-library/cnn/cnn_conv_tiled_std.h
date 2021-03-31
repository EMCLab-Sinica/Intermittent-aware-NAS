/*
 * cnn_conv_matmul.h  
 */

#ifndef CNN_CONV_TILED_STD_H_
#define CNN_CONV_TILED_STD_H_


#include <stdint.h>

#include "DSPLib.h"

#include "cnn_types.h"

#include "cnn_common.h"


#if CNN_CONVTYPE_SELECT == CNN_CONVTYPE_TILED_STD



void _clear_tile_buff(_q15 *pBuffLoc, uint16_t sz);
void _intra_tile_conv(ExeParams_t *parE, Mat_t* weights, uint16_t ifm_t_w, uint16_t ti, _q15 * pIFM_t_buff,_q15 * pWeight_t_buff,_q15* pOFM_t_buff, _iq31* pVMAC_result, uint16_t preSz, LOOPORDER_t lpOdr);


void CNN_LayerConv_Tiled_Std(uint16_t lid, Mat_t* weights, Mat_t* bias, Mat_t* ifm, Mat_t* ofm, ExeParams_t *parE,PreParams_t *parP, uint8_t idxBuf);
void CNN_Intermittent_LayerConv_Tiled_Std(uint16_t lid, Mat_t* weights, Mat_t* bias, Mat_t* ifm, Mat_t* ofm, ExeParams_t *parE,PreParams_t *parP, uint8_t idxBuf);
void _CNN_LayerConv_Tiled_OFM(uint16_t lid, Mat_t* weights, Mat_t* bias, Mat_t* ifm, Mat_t* ofm, ExeParams_t *parE,PreParams_t *parP, uint8_t idxBuf);
void _CNN_LayerConv_Tiled_IFM(uint16_t lid, Mat_t* weights, Mat_t* bias, Mat_t* ifm, Mat_t* ofm, ExeParams_t *parE,PreParams_t *parP, uint8_t idxBuf);
void _CNN_LayerConv_Tiled_WEI(uint16_t lid, Mat_t* weights, Mat_t* bias, Mat_t* ifm, Mat_t* ofm, ExeParams_t *parE,PreParams_t *parP, uint8_t idxBuf);
void _CNN_Intermittent_LayerConv_Tiled_OFM(uint16_t lid, Mat_t* weights, Mat_t* bias, Mat_t* ifm, Mat_t* ofm, ExeParams_t *parE,PreParams_t *parP, uint8_t idxBuf);
void _CNN_Intermittent_LayerConv_Tiled_IFM(uint16_t lid, Mat_t* weights, Mat_t* bias, Mat_t* ifm, Mat_t* ofm, ExeParams_t *parE,PreParams_t *parP, uint8_t idxBuf);
void _CNN_Intermittent_LayerConv_Tiled_WEI(uint16_t lid, Mat_t* weights, Mat_t* bias, Mat_t* ifm, Mat_t* ofm, ExeParams_t *parE,PreParams_t *parP, uint8_t idxBuf);

// intermittence related
void CNN_ClearFootprints_LayerConv_Tiled_Std(uint8_t idxBuf);
void CNN_PrintFootprints_LayerConv_Tiled_Std(void);


#endif

#endif /* CNN_CONV_TILED_STD_H_ */
