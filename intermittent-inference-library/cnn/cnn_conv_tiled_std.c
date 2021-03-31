/*
 * cnn_conv_tiled_std.c
 * Standard Tiled Convolution as per FPGA 2015/CODES 2019 
 */

#include "../utils/util_macros.h"

#include "cnn_matops.h"

#include "cnn_conv_tiled_std.h"

#include "cnn_buffer_sizes.h"


#if CNN_CONVTYPE_SELECT == CNN_CONVTYPE_TILED_STD




void _clear_tile_buff(_q15 *pBuffLoc, uint16_t sz){
    uint16_t i;
    for(i=0; i<sz; i++){
        *(pBuffLoc + i) = 0;
    }
}

// Intra tile convolution loops
void _intra_tile_conv(ExeParams_t *parE, Mat_t* weights, uint16_t ifm_t_w, uint16_t ti, _q15 * pIFM_t_buff,_q15 * pWeight_t_buff,_q15* pOFM_t_buff,_iq31* pVMAC_result, uint16_t preSz, LOOPORDER_t lpOdr){
	_q15* pVec1;
	_q15* pVec2;
	for (uint16_t trr=0; trr<parE->Tr; trr++){
		for (uint16_t tcc=0; tcc<parE->Tc; tcc++){
			for (uint16_t i=0; i<weights->h; i++){
				for (uint16_t j=0; j<weights->w; j++){
					for (uint16_t too=0; too<parE->Tm; too++){
						// calculate input locations
						uint16_t v1_offset = ((((((parE->str*trr)+i)) * ifm_t_w) + ((parE->str*tcc)+j))*parE->Tn);
						uint16_t v2_offset =  ( (parE->Tn * parE->Tm * weights->h * i) + (parE->Tn * parE->Tm * j) + (parE->Tn * too) );
						pVec1 = pIFM_t_buff + v1_offset+ (v1_offset&0x1) ;
						pVec2 = pWeight_t_buff + v2_offset+ (v2_offset&0x1) ;
						_q15 *tmp2 = (_q15*)pVMAC_result;
						_q15 *tmp = 0;
						if(lpOdr == IFM_ORIENTED){
							tmp = (pOFM_t_buff + (trr * parE->Tc * parE->Tm * preSz) + (tcc * parE->Tm * preSz) + too);
						}else{
							tmp = (pOFM_t_buff + (trr * parE->Tc * parE->Tm) + (tcc * parE->Tm) + too);
						}

						if( (ti == 0))*tmp =0;
						CNN_VectorMAC(pVec1, pVec2, parE->Tn, pVMAC_result);
						*tmp =  __saturated_add_q15( tmp2[1]  , *tmp );
						if( (ti == (weights->n-1)))*tmp = *tmp > 0 ? *tmp : 0 ; //ReLU
					}

				}
			}
		}
	}
}

/*******************************************************************************************************************
 Tiled Convolution using LEA vector MAC command
 exec design params : Tr, Tc, Tm, Tn, loop order, preservation batch size
 Tn MACs performed in one command
 [UNDER CONTINUOUS POWER]
*******************************************************************************************************************/
void CNN_LayerConv_Tiled_Std(uint16_t lid, Mat_t* weights, Mat_t* bias, Mat_t* ifm, Mat_t* ofm, ExeParams_t *parE, PreParams_t *parP, uint8_t idxBuf){
    uint16_t ifm_t_h = (weights->h + (parE->str * parE->Tr) - parE->str);
    uint16_t ifm_t_w = (weights->w + (parE->str * parE->Tc) - parE->str);

    // 1D local buffer sizes and locations (directly inside LEA memory)
    uint16_t ifm_t_sz = (parE->Tn * ifm_t_h * ifm_t_w);
    uint16_t weight_t_sz = (parE->Tm * parE->Tn * weights->h * weights->w);
    uint16_t ofm_t_sz = (parE->Tm * parE->Tr * parE->Tc);
    if(OFM_ORIENTED == parE->lpOdr){
		if ((ifm_t_sz + weight_t_sz + ofm_t_sz) > LEA_MEM_SIZE){
			_DBGUART("CNN_LayerConv_Tiled_Std:: Error - tile sizes too large %d, %d, %d\r\n", ifm_t_sz, weight_t_sz, ofm_t_sz); _STOP();
		}
    }else{
		if ((ifm_t_sz + weight_t_sz + ofm_t_sz*parP->preSz) > LEA_MEM_SIZE){
			_DBGUART("CNN_LayerConv_Tiled_Std:: Error - tile sizes too large %d, %d, %d\r\n", ifm_t_sz, weight_t_sz, ofm_t_sz); _STOP();
		}
    }

    if (
         ((ofm->h     % parE->Tr) !=0) ||
         ((ofm->w     % parE->Tc) !=0) ||
         ((weights->n % parE->Tm) !=0) ||
         ((ifm->ch    % parE->Tn) !=0) ){
        _DBGUART("CNN_LayerConv_Tiled_Std:: Error - wrong tile sizes %d|%d, %d|%d, %d|%d, %d|%d\r\n",
            ofm->h,     parE->Tr,
            ofm->w,     parE->Tc,
            weights->n, parE->Tm,
            ifm->ch,    parE->Tn);
        _STOP();
    }
    // main handler
	switch(parE->lpOdr){
		case OFM_ORIENTED:
			if( ((ifm->ch / parE->Tn) % parP->preSz) !=0 ){_DBGUART("CNN_LayerConv_Tiled_OFM:: Error - wrong preSz sizes %d\r\n",parP->preSz);_STOP();}
			_CNN_LayerConv_Tiled_OFM( lid, weights, bias, ifm, ofm, parE, parP,idxBuf);break;
		case IFM_ORIENTED:
			if( ((ofm->ch / parE->Tm) % parP->preSz) !=0 ){_DBGUART("CNN_LayerConv_Tiled_IFM:: Error - wrong preSz sizes %d\r\n",parP->preSz);_STOP();}
			_CNN_LayerConv_Tiled_IFM( lid, weights, bias, ifm, ofm, parE, parP,idxBuf);break;
		case WEIGHT_ORIENTED:
			if( ( ((ofm->w / parE->Tc)*(ofm->h / parE->Tr)) % parP->preSz) !=0 ){_DBGUART("CNN_LayerConv_Tiled_WEI:: Error - wrong preSz sizes %d\r\n",parP->preSz);_STOP();}
			_CNN_LayerConv_Tiled_WEI( lid, weights, bias, ifm, ofm, parE, parP,idxBuf);break;
	}
}

void _CNN_LayerConv_Tiled_OFM(uint16_t lid, Mat_t* weights, Mat_t* bias, Mat_t* ifm, Mat_t* ofm, ExeParams_t *parE, PreParams_t *parP, uint8_t idxBuf){

	ConvTileIndices idx;
    uint16_t row=0, col=0, to=0, ti=0,buffer_idx=0;
    uint16_t iteration = 0;  // number of completed tiles

    _q15 *pLEAMEM = CNN_GetLEAMemoryLocation();
    _q15 *pIFM_t_buff, *pWeight_t_buff, *pOFM_t_buff;
    _iq31 *pVMAC_result;

    volatile _iq31 resiq31 = 0;
    volatile _q15 resq15 = 0;
    uint16_t ifm_t_h = (weights->h + (parE->str * parE->Tr) - parE->str);
    uint16_t ifm_t_w = (weights->w + (parE->str * parE->Tc) - parE->str);
    // 1D local buffer sizes and locations (directly inside LEA memory)
    uint16_t ifm_t_sz = (parE->Tn * ifm_t_h * ifm_t_w);
    uint16_t weight_t_sz = (parE->Tm * parE->Tn * weights->h * weights->w);
    uint16_t ofm_t_sz = (parE->Tm * parE->Tr * parE->Tc);

    pIFM_t_buff = pLEAMEM;
    pWeight_t_buff = pIFM_t_buff + ifm_t_sz + (ifm_t_sz & 0x1) ;
    pOFM_t_buff = pWeight_t_buff + weight_t_sz + (weight_t_sz & 0x1);
    pVMAC_result = (_iq31*)( (pOFM_t_buff + ofm_t_sz + (ofm_t_sz & 0x1))  ); // scalar vec mac result

    // =============== Inter-Tile =========================
    for (; row<ofm->h; row+=parE->Tr){
        for (; col<ofm->w; col+=parE->Tc){
            for (; to<ofm->ch; to+=parE->Tm){
                if( (ti !=0) ){
                	_fetch_ofm_tile_RCN_ext( ofm , pOFM_t_buff, row, col, to, parE->Tm, parE->Tr, parE->Tc, parP->preSz, parE->lpOdr);
                }
                for (; ti<ifm->ch; ti+=parE->Tn){
                    if(iteration==parP->preSz ){
                    	_save_ofm_tile_RCN_ext(ofm, buffer_idx , pOFM_t_buff, idx.r, idx.c, idx.m, parE->Tm, parE->Tr, parE->Tc, parP->preSz, parE->lpOdr);
                        iteration=0;  //reset the
                    }
                    // load ifm tile *
                    _fetch_ifm_tile_RCN_ext(ifm, pIFM_t_buff, ifm_t_h, ifm_t_w, row, col, ti, parE->Tn);
                    // load weight tile
                    _fetch_weights_tile_RCMN_ext(weights, pWeight_t_buff, to, ti, parE->Tm, parE->Tn);

                   // =============== Intra-Tile =========================
                    _intra_tile_conv(parE,weights,ifm_t_w,ti,pIFM_t_buff,pWeight_t_buff,pOFM_t_buff,pVMAC_result, parP->preSz, parE->lpOdr);
                    iteration++;
                   	idx.r = row;
                    idx.c = col;
                    idx.m = to;
                    idx.n = ti;
                }ti=0;
            }to=0;
        }col=0;
    }row=0;
    if(iteration==parP->preSz ){
    	_save_ofm_tile_RCN_ext(ofm, buffer_idx , pOFM_t_buff, idx.r, idx.c, idx.m, parE->Tm, parE->Tr, parE->Tc, parP->preSz, parE->lpOdr);
        iteration=0;  //reset the
    }
}

void _CNN_LayerConv_Tiled_IFM(uint16_t lid, Mat_t* weights, Mat_t* bias, Mat_t* ifm, Mat_t* ofm, ExeParams_t *parE, PreParams_t *parP, uint8_t idxBuf){
	ConvTileIndices idx;
    uint16_t row=0, col=0, to=0, ti=0,buffer_idx=0;
    uint16_t iteration = 0;  // number of completed tiles

    _q15 *pLEAMEM = CNN_GetLEAMemoryLocation();
    _q15 *pIFM_t_buff, *pWeight_t_buff, *pOFM_t_buff;
    _iq31 *pVMAC_result;

    volatile _iq31 resiq31 = 0;
    volatile _q15 resq15 = 0;
    uint16_t ifm_t_h = (weights->h + (parE->str * parE->Tr) - parE->str);
    uint16_t ifm_t_w = (weights->w + (parE->str * parE->Tc) - parE->str);

    // 1D local buffer sizes and locations (directly inside LEA memory)
    uint16_t ifm_t_sz = (parE->Tn * ifm_t_h * ifm_t_w);
    uint16_t weight_t_sz = (parE->Tm * parE->Tn * weights->h * weights->w);
    uint16_t ofm_t_sz = (parE->Tm * parE->Tr * parE->Tc);
    
    pIFM_t_buff = pLEAMEM;
    pWeight_t_buff = pIFM_t_buff + ifm_t_sz + (ifm_t_sz & 0x1) ;
    pOFM_t_buff = pWeight_t_buff + weight_t_sz + (weight_t_sz & 0x1);
    pVMAC_result = (_iq31*)( (pOFM_t_buff + ofm_t_sz)  ); // scalar vec mac result

    // =============== Inter-Tile =========================    
    for (; row<ofm->h; row+=parE->Tr){
        for (; col<ofm->w; col+=parE->Tc){
            for (; ti<ifm->ch; ti+=parE->Tn){
            	// load ifm tile *
            	_fetch_ifm_tile_RCN_ext(ifm, pIFM_t_buff, ifm_t_h, ifm_t_w, row, col, ti, parE->Tn);
            	for (; to<ofm->ch; to+=parE->Tm){
                    if(iteration==parP->preSz ){
                    	_save_ofm_tile_RCN_ext(ofm, buffer_idx , pOFM_t_buff- ofm_t_sz, idx.r, idx.c, idx.m, parE->Tm, parE->Tr, parE->Tc, parP->preSz, parE->lpOdr);
                        iteration=0;  //reset the
                        pOFM_t_buff = pWeight_t_buff + weight_t_sz + (weight_t_sz & 0x1);
                    }
                    //
                    if( (ti !=0) ){
                    	_fetch_ofm_tile_RCN_ext( ofm , pOFM_t_buff, row, col, to, parE->Tm, parE->Tr, parE->Tc, parP->preSz, parE->lpOdr);
                    }
                    // load weight tile
                    _fetch_weights_tile_RCMN_ext(weights, pWeight_t_buff, to, ti, parE->Tm, parE->Tn);
                    //
                   // =============== Intra-Tile =========================
                    _intra_tile_conv(parE,weights,ifm_t_w,ti,pIFM_t_buff,pWeight_t_buff,pOFM_t_buff,pVMAC_result, parP->preSz, parE->lpOdr);
                    pOFM_t_buff +=ofm_t_sz;
                    iteration++;
                   	idx.r = row;
                    idx.c = col;
                    idx.m = to;
                    idx.n = ti;
                }to=0;
            }ti=0;
        }col=0;
    }row=0;
    if(iteration==parP->preSz ){
    	_save_ofm_tile_RCN_ext(ofm, buffer_idx , pOFM_t_buff -ofm_t_sz, idx.r, idx.c, idx.m, parE->Tm, parE->Tr, parE->Tc, parP->preSz, parE->lpOdr);
        iteration=0;  //reset the
    }
}

void _CNN_LayerConv_Tiled_WEI(uint16_t lid, Mat_t* weights, Mat_t* bias, Mat_t* ifm, Mat_t* ofm, ExeParams_t *parE, PreParams_t *parP, uint8_t idxBuf){
	ConvTileIndices idx;
    uint16_t row=0, col=0, to=0, ti=0,buffer_idx=0;
    uint16_t iteration = 0;  // number of completed tiles

    _q15 *pLEAMEM = CNN_GetLEAMemoryLocation();
    _q15 *pIFM_t_buff, *pWeight_t_buff, *pOFM_t_buff;
    _iq31 *pVMAC_result;
    //_q15 *pVMAC_result;
    volatile _iq31 resiq31 = 0;
    volatile _q15 resq15 = 0;
    uint16_t ifm_t_h = (weights->h + (parE->str * parE->Tr) - parE->str);
    uint16_t ifm_t_w = (weights->w + (parE->str * parE->Tc) - parE->str);

    // 1D local buffer sizes and locations (directly inside LEA memory)
    uint16_t ifm_t_sz = (parE->Tn * ifm_t_h * ifm_t_w);
    uint16_t weight_t_sz = (parE->Tm * parE->Tn * weights->h * weights->w);
    uint16_t ofm_t_sz = (parE->Tm * parE->Tr * parE->Tc);
    
    pIFM_t_buff = pLEAMEM;
    pWeight_t_buff = pIFM_t_buff + ifm_t_sz + (ifm_t_sz & 0x1) ;
    pOFM_t_buff = pWeight_t_buff + weight_t_sz + (weight_t_sz & 0x1);
    pVMAC_result = (_iq31*)( (pOFM_t_buff + ofm_t_sz)  ); // scalar vec mac result

    // =============== Inter-Tile =========================    
    for (; to<ofm->ch; to+=parE->Tm){
    	for (; ti<ifm->ch; ti+=parE->Tn){
    		 // load weight tile
    		_fetch_weights_tile_RCMN_ext(weights, pWeight_t_buff, to, ti, parE->Tm, parE->Tn);
    		for (; row<ofm->h; row+=parE->Tr){
    			for (; col<ofm->w; col+=parE->Tc){
                    if(iteration==parP->preSz ){
                    	_save_ofm_tile_RCN_ext(ofm, buffer_idx , pOFM_t_buff- ofm_t_sz, idx.r, idx.c, idx.m, parE->Tm, parE->Tr, parE->Tc, parP->preSz, parE->lpOdr);
                    	iteration=0;  //reset the
                    	pOFM_t_buff = pWeight_t_buff + weight_t_sz + (weight_t_sz & 0x1);
                    }
                	// load ifm tile *
                	_fetch_ifm_tile_RCN_ext(ifm, pIFM_t_buff, ifm_t_h, ifm_t_w, row, col, ti, parE->Tn);
                    if( (ti !=0) ){
                    	_fetch_ofm_tile_RCN_ext( ofm , pOFM_t_buff, row, col, to, parE->Tm, parE->Tr, parE->Tc, parP->preSz, parE->lpOdr);
                    }
                   // =============== Intra-Tile =========================
                    _intra_tile_conv(parE,weights,ifm_t_w,ti,pIFM_t_buff,pWeight_t_buff,pOFM_t_buff,pVMAC_result, parP->preSz, parE->lpOdr);
                    iteration++;
                    pOFM_t_buff +=ofm_t_sz;
                   	idx.r = row;
                    idx.c = col;
                    idx.m = to;
                    idx.n = ti;
                }col=0;
            }row=0;
        }ti=0;
    }to=0;
    if(iteration==parP->preSz ){
    	_save_ofm_tile_RCN_ext(ofm, buffer_idx , pOFM_t_buff -ofm_t_sz , idx.r, idx.c, idx.m, parE->Tm, parE->Tr, parE->Tc, parP->preSz, parE->lpOdr);
        iteration=0;  //reset the
    }
}



/*******************************************************************************************************************
 Tiled Convolution using LEA vector MAC command
 exec design params : Tr, Tc, Tm, Tn, loop order, preservation batch size
 Tn MACs performed in one command
 [UNDER INTERMITTENT POWER]
*******************************************************************************************************************/
void CNN_Intermittent_LayerConv_Tiled_Std(uint16_t lid, Mat_t* weights, Mat_t* bias, Mat_t* ifm, Mat_t* ofm, ExeParams_t *parE,PreParams_t *parP, uint8_t idxBuf){
    uint16_t ifm_t_h = (weights->h + (parE->str * parE->Tr) - parE->str);
    uint16_t ifm_t_w = (weights->w + (parE->str * parE->Tc) - parE->str);
    // 1D local buffer sizes and locations (directly inside LEA memory)
    uint16_t ifm_t_sz = (parE->Tn * ifm_t_h * ifm_t_w);
    uint16_t weight_t_sz = (parE->Tm * parE->Tn * weights->h * weights->w);
    uint16_t ofm_t_sz = (parE->Tm * parE->Tr * parE->Tc); // TODO: fix for presSz !

    if(OFM_ORIENTED == parE->lpOdr){
  		if ((ifm_t_sz + weight_t_sz + ofm_t_sz) > LEA_MEM_SIZE){
  			_DBGUART("CNN_LayerConv_Tiled_Std:: Error - tile sizes too large %d, %d, %d\r\n", ifm_t_sz, weight_t_sz, ofm_t_sz); _STOP();
  		}
      }else{
  		if ((ifm_t_sz + weight_t_sz + ofm_t_sz*parP->preSz) > LEA_MEM_SIZE){
  			_DBGUART("CNN_LayerConv_Tiled_Std:: Error - tile sizes too large %d, %d, %d\r\n", ifm_t_sz, weight_t_sz, ofm_t_sz); _STOP();
  		}
      }

    if (
         ((ofm->h     % parE->Tr) !=0) ||
         ((ofm->w     % parE->Tc) !=0) ||
         ((weights->n % parE->Tm) !=0) ||
         ((ifm->ch    % parE->Tn) !=0) ){
        _DBGUART("CNN_LayerConv_Tiled_Std:: Error - wrong tile sizes %d|%d, %d|%d, %d|%d, %d|%d\r\n",
            ofm->h,     parE->Tr,
            ofm->w,     parE->Tc,
            weights->n, parE->Tm,
            ifm->ch,    parE->Tn);
        _STOP();
    }
    
    // main handler
	switch(parE->lpOdr){
		case OFM_ORIENTED:
			if( ((ifm->ch / parE->Tn) % parP->preSz) !=0 ){_DBGUART("CNN_LayerConv_Tiled_OFM:: Error - wrong preSz sizes %d\r\n",parP->preSz);_STOP();}
			_CNN_Intermittent_LayerConv_Tiled_OFM( lid, weights, bias, ifm, ofm, parE, parP,idxBuf);break;
		case IFM_ORIENTED:
			if( ((ofm->ch / parE->Tm) % parP->preSz) !=0 ){_DBGUART("CNN_LayerConv_Tiled_IFM:: Error - wrong preSz sizes %d\r\n",parP->preSz);_STOP();}
			_CNN_Intermittent_LayerConv_Tiled_IFM( lid, weights, bias, ifm, ofm, parE, parP,idxBuf);break;
		case WEIGHT_ORIENTED:
			if( ( ((ofm->w / parE->Tc)*(ofm->h / parE->Tr)) % parP->preSz) !=0 ){_DBGUART("CNN_LayerConv_Tiled_WEI:: Error - wrong preSz sizes %d\r\n",parP->preSz);_STOP();}
			_CNN_Intermittent_LayerConv_Tiled_WEI( lid, weights, bias, ifm, ofm, parE, parP,idxBuf);break;
	}
}

void _CNN_Intermittent_LayerConv_Tiled_OFM(uint16_t lid, Mat_t* weights, Mat_t* bias, Mat_t* ifm, Mat_t* ofm, ExeParams_t *parE, PreParams_t *parP, uint8_t idxBuf){
    SPI_ADDR A;
    ConvTileIndices idx;
    A.L = LOC_LOOP_INDICES;
    SPI_READ(&A,(uint8_t*)&idx,sizeof(ConvTileIndices)); //fetch loop indices
    //uint16_t buffer_idx = 0; // double buffering
    uint16_t row=idx.r, col=idx.c, to=idx.m, ti=idx.n,buffer_idx=idx.buf;
    uint16_t iteration = 0;  // number of completed tiles

    _q15 *pLEAMEM = CNN_GetLEAMemoryLocation();
    _q15 *pIFM_t_buff, *pWeight_t_buff, *pOFM_t_buff;
    _iq31 *pVMAC_result;

    volatile _iq31 resiq31 = 0;
    volatile _q15 resq15 = 0;
    uint16_t ifm_t_h = (weights->h + (parE->str * parE->Tr) - parE->str);
    uint16_t ifm_t_w = (weights->w + (parE->str * parE->Tc) - parE->str);

    // 1D local buffer sizes and locations (directly inside LEA memory)
    uint16_t ifm_t_sz = (parE->Tn * ifm_t_h * ifm_t_w);
    uint16_t weight_t_sz = (parE->Tm * parE->Tn * weights->h * weights->w);
    uint16_t ofm_t_sz = (parE->Tm * parE->Tr * parE->Tc);

    pIFM_t_buff = pLEAMEM;
    pWeight_t_buff = pIFM_t_buff + ifm_t_sz + (ifm_t_sz & 0x1) ;
    pOFM_t_buff = pWeight_t_buff + weight_t_sz + (weight_t_sz & 0x1);
    pVMAC_result = (_iq31*)( (pOFM_t_buff + ofm_t_sz)  ); // scalar vec mac result

    // =============== Inter-Tile =========================    
    for (; row<ofm->h; row+=parE->Tr){
        for (; col<ofm->w; col+=parE->Tc){
            for (; to<ofm->ch; to+=parE->Tm){
                if( (ti !=0) ){
                	_fetch_ofm_tile_RCN_ext( ofm , pOFM_t_buff, row, col, to, parE->Tm, parE->Tr, parE->Tc, parP->preSz, parE->lpOdr);
                }
                for (; ti<ifm->ch; ti+=parE->Tn){
                    if(iteration==parP->preSz ){
                    	_save_ofm_tile_RCN_ext(ofm, buffer_idx , pOFM_t_buff, idx.r, idx.c, idx.m, parE->Tm, parE->Tr, parE->Tc, parP->preSz, parE->lpOdr);
                    	idx.r = row;
                    	idx.c = col;
                    	idx.m = to;
                    	idx.n = ti;
                    	A.L = LOC_LOOP_INDICES;
                    	SPI_WRITE(&A,(uint8_t*)&idx, sizeof(ConvTileIndices));
                        iteration=0;  //reset the
                        _SHUTDOWN(); _STOP();
                    }
                    // load ifm tile *
                    _fetch_ifm_tile_RCN_ext(ifm, pIFM_t_buff, ifm_t_h, ifm_t_w, row, col, ti, parE->Tn);
                    // load weight tile
                    _fetch_weights_tile_RCMN_ext(weights, pWeight_t_buff, to, ti, parE->Tm, parE->Tn);

                   // =============== Intra-Tile =========================
                    _intra_tile_conv(parE,weights,ifm_t_w,ti,pIFM_t_buff,pWeight_t_buff,pOFM_t_buff,pVMAC_result, parP->preSz, parE->lpOdr);
                    iteration++;
                   	idx.r = row;
                    idx.c = col;
                    idx.m = to;
                    idx.n = ti;
                }ti=0;
            }to=0;
        }col=0;
    }
    if(iteration==parP->preSz ){
    	_save_ofm_tile_RCN_ext(ofm, buffer_idx , pOFM_t_buff, idx.r, idx.c, idx.m, parE->Tm, parE->Tr, parE->Tc, parP->preSz, parE->lpOdr);
    	idx.r = ofm->h;
    	idx.c = ofm->w;
    	idx.m = ofm->ch;
    	idx.n = ifm->ch;
    	A.L = LOC_LOOP_INDICES;
    	SPI_WRITE(&A,(uint8_t*)&idx, sizeof(ConvTileIndices));
        iteration=0;  //reset the
        _SHUTDOWN(); _STOP();
    }
    CNN_ClearFootprints_LayerConv_Tiled_Std(0);
}

void _CNN_Intermittent_LayerConv_Tiled_IFM(uint16_t lid, Mat_t* weights, Mat_t* bias, Mat_t* ifm, Mat_t* ofm, ExeParams_t *parE, PreParams_t *parP, uint8_t idxBuf){
    SPI_ADDR A;
    ConvTileIndices idx;
    A.L = LOC_LOOP_INDICES;
    SPI_READ(&A,(uint8_t*)&idx,sizeof(ConvTileIndices)); //fetch loop indices
    uint16_t row=idx.r, col=idx.c, to=idx.m, ti=idx.n,buffer_idx=idx.buf;

    uint16_t iteration = 0;  // number of completed tiles

    _q15 *pLEAMEM = CNN_GetLEAMemoryLocation();
    _q15 *pIFM_t_buff, *pWeight_t_buff, *pOFM_t_buff;
    _iq31 *pVMAC_result;

    volatile _iq31 resiq31 = 0;
    volatile _q15 resq15 = 0;

    uint16_t ifm_t_h = (weights->h + (parE->str * parE->Tr) - parE->str);
    uint16_t ifm_t_w = (weights->w + (parE->str * parE->Tc) - parE->str);

    // 1D local buffer sizes and locations (directly inside LEA memory)
    uint16_t ifm_t_sz = (parE->Tn * ifm_t_h * ifm_t_w);
    uint16_t weight_t_sz = (parE->Tm * parE->Tn * weights->h * weights->w);
    uint16_t ofm_t_sz = (parE->Tm * parE->Tr * parE->Tc)* parP->preSz;

    pIFM_t_buff = pLEAMEM;
    pWeight_t_buff = pIFM_t_buff + ifm_t_sz + (ifm_t_sz & 0x1);
    pOFM_t_buff = pWeight_t_buff + weight_t_sz + (weight_t_sz & 0x1);
    pVMAC_result = (_iq31*)( (pOFM_t_buff + ofm_t_sz)  ); // scalar vec mac result

    // =============== Inter-Tile =========================    
    for (; row<ofm->h; row+=parE->Tr){
        for (; col<ofm->w; col+=parE->Tc){
            for (; ti<ifm->ch; ti+=parE->Tn){            	
            	_fetch_ifm_tile_RCN_ext(ifm, pIFM_t_buff, ifm_t_h, ifm_t_w, row, col, ti, parE->Tn); // load ifm tile
            	for (; to<ofm->ch; to+=parE->Tm){
                    if(iteration==parP->preSz ){
                    	_save_ofm_tile_RCN_ext(ofm, buffer_idx , pOFM_t_buff- ofm_t_sz, idx.r, idx.c, idx.m, parE->Tm, parE->Tr, parE->Tc, parP->preSz, parE->lpOdr);
                       	idx.r = row;
                        idx.c = col;
                        idx.m = to;
                        idx.n = ti;
                    	A.L = LOC_LOOP_INDICES;
                    	SPI_WRITE(&A,(uint8_t*)&idx, sizeof(ConvTileIndices));//
                        iteration=0;  
                        _SHUTDOWN(); _STOP();
                    }
                    //
                    if( (ti !=0) ){
                    	_fetch_ofm_tile_RCN_ext( ofm , pOFM_t_buff, row, col, to, parE->Tm, parE->Tr, parE->Tc, parP->preSz, parE->lpOdr);
                    }
                    // load weight tile
                    _fetch_weights_tile_RCMN_ext(weights, pWeight_t_buff, to, ti, parE->Tm, parE->Tn);
                    //
                   // =============== Intra-Tile =========================
                    _intra_tile_conv(parE,weights,ifm_t_w,ti,pIFM_t_buff,pWeight_t_buff,pOFM_t_buff,pVMAC_result, parP->preSz, parE->lpOdr);
                   	idx.r = row;
                    idx.c = col;
                    idx.m = to;
                    idx.n = ti;
                    iteration++;
                    pOFM_t_buff +=parE->Tm;
                }to=0;
            }ti=0;
        }col=0;
    }
    if(iteration==parP->preSz ){
    	_save_ofm_tile_RCN_ext(ofm, buffer_idx , pOFM_t_buff - ofm_t_sz, idx.r, idx.c, idx.m, parE->Tm, parE->Tr, parE->Tc, parP->preSz, parE->lpOdr);
    	idx.r = ofm->h;
    	idx.c = ofm->w;
    	idx.m = ofm->ch;
    	idx.n = ifm->ch;

    	A.L = LOC_LOOP_INDICES;
    	SPI_WRITE(&A,(uint8_t*)&idx, sizeof(ConvTileIndices));
        iteration=0;  //reset the
        _SHUTDOWN(); _STOP();
    }
    CNN_ClearFootprints_LayerConv_Tiled_Std(idxBuf);
}

void _CNN_Intermittent_LayerConv_Tiled_WEI(uint16_t lid, Mat_t* weights, Mat_t* bias, Mat_t* ifm, Mat_t* ofm, ExeParams_t *parE, PreParams_t *parP, uint8_t idxBuf){
    SPI_ADDR A;
    ConvTileIndices idx;
    A.L = LOC_LOOP_INDICES;
    SPI_READ(&A,(uint8_t*)&idx,sizeof(ConvTileIndices)); //fetch loop indices
    //uint16_t buffer_idx = 0; // double buffering
    uint16_t row=idx.r, col=idx.c, to=idx.m, ti=idx.n,buffer_idx=idx.buf;
    uint16_t iteration = 0;  // number of completed tiles

    _q15 *pLEAMEM = CNN_GetLEAMemoryLocation();
    _q15 *pIFM_t_buff, *pWeight_t_buff, *pOFM_t_buff;
    _iq31 *pVMAC_result;
    
    volatile _iq31 resiq31 = 0;
    volatile _q15 resq15 = 0;
    uint16_t ifm_t_h = (weights->h + (parE->str * parE->Tr) - parE->str);
    uint16_t ifm_t_w = (weights->w + (parE->str * parE->Tc) - parE->str);

    // 1D local buffer sizes and locations (directly inside LEA memory)
    uint16_t ifm_t_sz = (parE->Tn * ifm_t_h * ifm_t_w);
    uint16_t weight_t_sz = (parE->Tm * parE->Tn * weights->h * weights->w);
    uint16_t ofm_t_sz = (parE->Tm * parE->Tr * parE->Tc)* parP->preSz;

    pIFM_t_buff = pLEAMEM;
    pWeight_t_buff = pIFM_t_buff + ifm_t_sz + (ifm_t_sz & 0x1) ;
    pOFM_t_buff = pWeight_t_buff + weight_t_sz * parP->preSz + (weight_t_sz & 0x1);
    pVMAC_result = (_iq31*)( (pOFM_t_buff + ofm_t_sz)  ); // scalar vec mac result

    // =============== Inter-Tile =========================    
    for (; to<ofm->ch; to+=parE->Tm){
    	for (; ti<ifm->ch; ti+=parE->Tn){
    		 // load weight tile
    		_fetch_weights_tile_RCMN_ext(weights, pWeight_t_buff, to, ti, parE->Tm, parE->Tn);
    		for (; row<ofm->h; row+=parE->Tr){
    			for (; col<ofm->w; col+=parE->Tc){
                    if(iteration==parP->preSz ){
                    	_save_ofm_tile_RCN_ext(ofm, buffer_idx , pOFM_t_buff - ofm_t_sz, idx.r, idx.c, idx.m, parE->Tm, parE->Tr, parE->Tc, parP->preSz, parE->lpOdr);
                    	buffer_idx^=0x1; //buffer swapping
                       	idx.r = row;
                        idx.c = col;
                        idx.m = to;
                        idx.n = ti;
                    	A.L =  LOC_LOOP_INDICES;
                    	SPI_WRITE(&A,(uint8_t*)&idx, sizeof(ConvTileIndices));
                        iteration=0;  //reset the
                        _SHUTDOWN(); _STOP();
                    }
                	// load ifm tile *
                	_fetch_ifm_tile_RCN_ext(ifm, pIFM_t_buff, ifm_t_h, ifm_t_w, row, col, ti, parE->Tn);
                    if( (ti !=0) ){
                    	_fetch_ofm_tile_RCN_ext( ofm , pOFM_t_buff, row, col, to, parE->Tm, parE->Tr, parE->Tc, parP->preSz, parE->lpOdr);
                    }

                   // =============== Intra-Tile =========================
                    _intra_tile_conv(parE,weights,ifm_t_w,ti,pIFM_t_buff,pWeight_t_buff,pOFM_t_buff,pVMAC_result, parP->preSz, parE->lpOdr);
                    iteration++;
                    pOFM_t_buff +=ofm_t_sz;
                   	idx.r = row;
                    idx.c = col;
                    idx.m = to;
                    idx.n = ti;

                }col=0;
            }row=0;
        }ti=0;
    }
    if(iteration==parP->preSz ){
    	_save_ofm_tile_RCN_ext(ofm, buffer_idx , pOFM_t_buff - ofm_t_sz, idx.r, idx.c, idx.m, parE->Tm, parE->Tr, parE->Tc, parP->preSz, parE->lpOdr);
    	idx.r = ofm->h;
    	idx.c = ofm->w;
    	idx.m = ofm->ch;
    	idx.n = ifm->ch;
    	A.L = LOC_LOOP_INDICES;
    	SPI_WRITE(&A,(uint8_t*)&idx, sizeof(ConvTileIndices));
        iteration=0;  //reset the
        _SHUTDOWN(); _STOP();
    }
    CNN_ClearFootprints_LayerConv_Tiled_Std(idxBuf);
}






/*************************************************************************
 * GET/SET global vars
 *************************************************************************/



/*************************************************************************
 * FOOTPRINTING
 *************************************************************************/
void CNN_ClearFootprints_LayerConv_Tiled_Std(uint8_t idxBuf){
    SPI_ADDR A;
    A.L = LOC_LOOP_INDICES;
    ConvTileIndices idx={0,0,0,0, 0 };
    SPI_WRITE(&A,(uint8_t*)&idx,sizeof(ConvTileIndices));

}

void CNN_PrintFootprints_LayerConv_Tiled_Std(){
    //_DBGUART("FP(conv-matmul):: %d, %d, %d, %d \r\n", FP_LayerConv.n, FP_LayerConv.ch, FP_LayerConv.chloop_task, FP_LayerConv.nloop_task);
}

#endif
