/*
 * mat_types.h
 * Custom data types and structures used for CNN
 */

#ifndef MAT_TYPES_H_
#define MAT_TYPES_H_

#include <stdint.h>
#include "msp430.h"
#include "DSPLib.h"


/*************************************************************************
 * General CNN types
 *************************************************************************/
typedef enum{
    NONE_ORIENTED = -1,
    OFM_ORIENTED = 0,
	IFM_ORIENTED = 1,
	WEIGHT_ORIENTED = 2
}LOOPORDER_t; // corresponds to reuse scheme

typedef struct{
    #ifndef EXTFRAM
    _q15 *data;     //address
    #else
    uint32_t data;  //address
    #endif
    
    uint16_t n;     // e.g., num filters
    uint16_t ch;    // e.g., num channels
    uint16_t h;     // e.g., filter height
    uint16_t w;     // e.g., filter width
}Mat_t;

// standard tile params
typedef struct{
    uint16_t Tn;    // tile input channels
    uint16_t Tm;    // tile output channels
    uint16_t Tr;    // tile ofm rows
    uint16_t Tc;    // tile ofm cols

    uint16_t str;   //stride
    uint16_t pad;   //padding
    LOOPORDER_t lpOdr;//enum
}ExeParams_t;

typedef struct{
	uint8_t preSz;
}PreParams_t;


typedef struct{
	//inter
    uint16_t r;
    uint16_t c;
    uint16_t m;
    uint16_t n;

    uint16_t buf;
    

}ConvTileIndices;

typedef struct{
    uint16_t lix;
    void (*fun)(uint16_t lid, Mat_t* weights, Mat_t* bias, Mat_t* ifm, Mat_t* ofm, ExeParams_t *parE,PreParams_t *parP, uint8_t idxBuf);
    Mat_t weights;
    Mat_t bias;
    Mat_t ifm;
    Mat_t ofm;
    ExeParams_t parE;
    PreParams_t parP;
    uint8_t idxBuf;
}CNNLayer_t;

typedef struct{
    CNNLayer_t *Layers;
    uint16_t numLayers;
    char name[32];
}CNNModel_t;


typedef struct{
    uint16_t ch;    // e.g., num channels
    uint16_t h;     // e.g., filter height
    uint16_t w;     // e.g., filter width
}Tile_t;


/*************************************************************************
 * Intermittent CNN types
 *************************************************************************/
typedef enum{
    TASK_LAYERCONV_CONV1D = 0,
    TASK_LAYERCONV_MADD_SINGLE_CH,
    TASK_LAYERCONV_MADD_ALL_CH
    //TASK_LAYERCONV_BIASRELU
}TaskID_t;

// convolution (via 1D)
typedef struct{
    uint16_t n; // loop index - current filter
    uint16_t ch; // loop index - current channel
    TaskID_t chloop_task; // tasks completed inside the channel loop
    TaskID_t nloop_task;  // tasks completed inside the filter loop
}FootprintsLayerConv_t;

// fullyconnected (via vectorMAC)
typedef struct{
    uint16_t ch; // loop index - current channel
}FootprintsLayerFC_t;


// pooling (via vectorMAC)
typedef struct{
    uint16_t ch; // loop index - current channel
}FootprintsLayerPool_t;



/*************************************************************************
 * Benchmarking related types
 *************************************************************************/

typedef struct{
    bool active;                // is task active
    uint16_t lid;                // current layer id
    uint32_t tid;               // current task/tile that was executing
    uint32_t cycleCount;        // Benchmark cycle counts
}CNNLayerBenchmark_t;





#endif /* MAT_TYPES_H_ */
