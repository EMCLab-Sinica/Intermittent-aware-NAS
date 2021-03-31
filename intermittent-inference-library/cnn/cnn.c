/*
 * cnn.c
 * Main CNN handler (entry)
 */

#include "../utils/util_macros.h"

#include "cnn_common.h"


#include "tests/cnn_testbench_conv.h"
//#include "tests/cnn_testbench_fc.h"
//#include "tests/cnn_testbench_pool.h"
#include "tests/cnn_testbench_microbench.h"

#include "cnn_buffers.h"

#include "../data/test_model.h"



/* for conv combo testing */






#define NUM_RUNS        65535


#pragma PERSISTENT(NVM_init)
uint8_t NVM_init=0;

// current iteration of CNN execution
#pragma PERSISTENT(fpCount)
uint16_t fpCount = 0;

// current execution CNN layer
#pragma PERSISTENT(fpLayer)
uint8_t fpLayer = 0;

#pragma PERSISTENT(pulseCount)
uint16_t pulseCount = 0;

#pragma PERSISTENT(printFlag)
uint8_t printFlag = 0;
// globals
#pragma PERSISTENT(CurrLayerBench)
CNNLayerBenchmark_t CurrLayerBench = {false, 0, 0, 0};















/*******************************************************************
 * CNN runner
 *******************************************************************/



void CNN_run(){

    if(!NVM_init){
        eraseFRAM();
        NVM_init=1;
        while(1);
     }


#if     CNN_TB_TYPE == TB_CNN

    uint16_t lix=0;
    uint16_t cnt=0;
    uint8_t  fpL=0;
    CNNLayer_t *layer;
    SPI_ADDR A;
    A.L = LOC_LAYER_ID;
    SPI_READ(&A,(uint8_t*)&fpL,sizeof(uint8_t));

    pulseCount++;
    // test CNN - run iteratively
    for(cnt=fpCount; cnt < NUM_RUNS; cnt++){ // each channel in ifm
    	if( (lix==0)  && (printFlag==0)){_DBGUART("\r\nL-ST\r\n");printFlag=1;_SHUTDOWN();_STOP();}

        for(lix=fpL; lix < network.numLayers; lix++){ // each channel in ifm
            CNN_Benchmark_Set_LID(lix);

            layer = &network.Layers[lix];
            layer->fun(layer->lix, &layer->weights, &layer->bias, &layer->ifm, &layer->ofm,&layer->parE,&layer->parP,layer->idxBuf);

            fpL++;
            A.L = LOC_LAYER_ID;
            SPI_WRITE(&A,(uint8_t*)&fpL,sizeof(uint8_t));
            _DBGUART("L : %d, P: %d\r\n",fpCount,pulseCount);
        }

        fpCount++;
        _DBGUART("L-DN Cnt: %d, P: %d\r\n",fpCount,pulseCount);
        pulseCount=0;fpL=0;printFlag=0;
        A.L = LOC_LAYER_ID;
        SPI_WRITE(&A,(uint8_t*)&fpL,sizeof(uint8_t));
        _SHUTDOWN();_STOP();

    }




#elif (CNN_TB_TYPE == TB_COMBOLAYER_CONV)


    //test_LayerConv_Combo();


#elif (CNN_TB_TYPE == TB_CNN_MICROBENCH)

    /* LEA */
    

    /* DMA */
    //test_iterative_dma_fram_to_sram();
    //test_iterative_dma_sram_to_fram();
    //test_iterative_dma_fram_to_fram();
    //test_iterative_dma_sram_to_sram();

    /* MATH */
    //test_iterative_add();
    //test_iterative_multiply();
    //test_iterative_division();
    //test_iterative_modulo();

    /* CPU DATA MOVE */
    //test_iterative_cpu_fram_to_sram();
    //test_iterative_cpu_sram_to_fram();
    //test_iterative_cpu_fram_to_fram();
    //test_iterative_cpu_sram_to_sram();
    //test_iterative_cpu_fram_to_reg();

#else


    // test layer - run iteratively
    CNNLayer_t *layer = &network.Layers[0];

    uint16_t cnt;
    for (cnt = fpCount; cnt < NUM_RUNS; cnt++){
        CNN_Benchmark_Set_LID(0);
    #if   (CNN_TB_TYPE == TB_SINGLELAYER_CONV)
        test_LayerConv(layer);
    #elif (CNN_TB_TYPE == TB_SINGLELAYER_FC)
        test_LayerFC(layer);
    #elif (CNN_TB_TYPE == TB_SINGLELAYER_POOL)
        test_LayerPool(layer);
    #else
        _DBGUART("Error - no valid TB type specified \r\n");
    #endif

        fpCount++;

        // manually trigger EHM power switch close (try to start the new layer with a fresh power pulse)
        __delay_cycles(100);
        P1OUT = 0x1;
    }

    CNN_ClearFootprints_LayerConv_Tiled_Std(0);
	fpCount = 0;
    _STOP();

#endif


}


/*******************************************************************
 * Print Info
 *******************************************************************/
void CNN_printInput(Mat_t *ifm){
    uint16_t c;
    for(c=0; c<ifm->ch; c++){
        printQ15Matrix( (_q15*)(ifm->data + c),ifm->h, ifm->w);
    }
}

void CNN_printResult(Mat_t *ofm){
    uint16_t c;
    for(c=0; c<ofm->ch; c++){
        _DBGUART("[%d]: %d\r\n", c, *(ofm->data + c));
    }
}

void CNN_printLayerInfo(uint16_t lid, uint16_t ifm_t, uint16_t k_t, Mat_t* weights, Mat_t* bias, Mat_t* ifm, Mat_t* ofm){
    _DBGUART("L[%d] - IFM:[%d, %d, %d, %d], WEIGHTS:[%d, %d, %d, %d], OFM:[%d, %d, %d] \r\n",
             lid,
             ifm_t, ifm->ch, ifm->h, ifm->w,
             k_t, weights->n, weights->h, weights->w,
             ofm->ch, ofm->h, ofm->w
    );
}


/*******************************************************************
 * Getters/Setters
 *******************************************************************/

/* related to the model */
uint16_t CNN_GetModel_numLayers(){
    return network.numLayers;
}
/* related to buffers */
_q15* CNN_GetLEAMemoryLocation(){
    return pLEAMemory;
}
_q15* CNN_GetLayerTempBuff1Location(){
    return pLayerTempBuff1;
}
_q15* CNN_GetLayerTempBuff2Location(){
    return pLayerTempBuff2;
}
_q15* CNN_GetSRAMBuffLocation(){
    return pSRAMBuff;
}
_q15* CNN_GetOFMBuff1Location(){
    return pOFMBuff1;
}
_q15* CNN_GetOFMBuff2Location(){
    return pOFMBuff2;
}




/*******************************************************************
 * EHM related
 *******************************************************************/
void CNN_SystemShutdown(){    
    //__delay_cycles(10000);
    GPIO_setOutputHighOnPin( GPIO_PORT_P5, GPIO_PIN0 );
    //__disable_interrupt();
    _STOP();
}



/*******************************************************************
 * Benchmark related
 *******************************************************************/
void CNN_Benchmark_Set_TID(uint32_t tid){
    CurrLayerBench.tid = tid;
}
void CNN_Benchmark_Set_LID(uint16_t lid){
    CurrLayerBench.lid = lid;
}
void CNN_Benchmark_Set_CycleCount(uint32_t cc){
    CurrLayerBench.cycleCount = cc;
}
void CNN_Benchmark_Set_Active(bool a){
    CurrLayerBench.active = a;
}
void CNN_Benchmark_ClearData(){
    CurrLayerBench.active = false;
    CurrLayerBench.tid = 0;
    CurrLayerBench.cycleCount = 0;
}
CNNLayerBenchmark_t CNN_Benchmark_GetData(){
    return CurrLayerBench;
}
uint32_t CNN_Benchmark_Get_TID(){
    return CurrLayerBench.tid;
}
uint16_t CNN_Benchmark_Get_LID(){
    return CurrLayerBench.lid;
}








