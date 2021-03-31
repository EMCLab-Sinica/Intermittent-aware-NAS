/*
 * cnn_common.h
 * Common defines, constants and header includes related to the CNN module
 */

#ifndef CNN_COMMON_H_
#define CNN_COMMON_H_

#define EXTFRAM
#define FRAM_8Mb

#ifdef FRAM_8Mb
	#define EXTFRAM_SIZE  0x100000;
#else
	#define EXTFRAM_SIZE  0x80000;
#endif


#define Q15_SIZE    2           // how many bytes is a q15 ?

#define LEA_STACK       200
#define LEA_MEM_SIZE    (2048-LEA_STACK)


/* Benchmarking related */

// enable/disable benchmarking
#define CNN_BENCHMARKING_LEA_CONV1D    0
#define CNN_BENCHMARKING_LEA_MATADD    0
#define CNN_BENCHMARKING_DMA           0

#define CNN_BENCHMARKING_IM_LAY_CONV_TASKS      0
#define CNN_BENCHMARKING_IM_LAY_FC_TASKS        0
#define CNN_BENCHMARKING_IM_LAY_MAXPOOL_TASKS   0



#define CNN_TASKCOMPLETE_SYSSHUTDOWN        1


#define CNN_CONVTYPE_VIA1D          0
#define CNN_CONVTYPE_MATMUL         1
#define CNN_CONVTYPE_TILED_STD      2

#define CNN_CONVTYPE_SELECT     CNN_CONVTYPE_TILED_STD



/* testbench selection */
#define TB_CNN                  0
#define TB_SINGLELAYER_CONV     1
#define TB_SINGLELAYER_FC       2
#define TB_SINGLELAYER_POOL     3

#define TB_COMBOLAYER_CONV                 100


#define TB_CNN_MICROBENCH                  150

#define CNN_TB_TYPE   TB_CNN







//#pragma PERSISTENT(DummyOFMBuff)
//_q15 DummyOFMBuff[1][1][1] = {{{0}}};

// C standard headers
#include <math.h>
#include <stdint.h>
#include <string.h>
#include <stdbool.h>

// TI specific headers
#include "msp430.h"
#include "driverlib.h"
#include "DSPLib.h"

// local CNN lib headers
#include "cnn_types.h"
#include "cnn.h"
#include "cnn_utils.h"

// general app headers
#include "../utils/myuart.h"
#include "../utils/util_macros.h"
#include "../utils/sleep_timer.h"
#include "../utils/extfram.h"

#endif /* CNN_COMMON_H_ */
