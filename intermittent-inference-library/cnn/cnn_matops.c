/*
 * cnn_matops.c
 * Common vector math operations (add/multiply/MAC etc.) using LEA
 */


#include "cnn_matops.h"



// add 2 matrices
void CNN_MatrixAdd(_q15 *matA, _q15 *matB, _q15 *result, uint16_t h, uint16_t w){
#ifdef __MSP430__

#if CNN_BENCHMARKING_LEA_MATADD
    volatile uint32_t cycleCount = 0; //Benchmark cycle counts
#endif
#ifdef CNN_BENCHMARKING_LEA_MATADD
    msp_benchmarkStart(TIMER_A1_BASE, 1);
#endif

    msp_status status;
    msp_matrix_add_q15_params addParams;

    /* Initialize the parameter structure. */
    addParams.rows = h;
    addParams.cols = w;

    status = msp_matrix_add_q15(&addParams, matA, matB, result);
    if (status != 0){_DBGUART("ERROR: msp_matrix_add_q15 - status = %d\r\n", status);}
    msp_checkStatus(status);

#if CNN_BENCHMARKING_LEA_MATADD
    cycleCount += msp_benchmarkStop(TIMER_A1_BASE);
    _DBGUART("CNN_MatrixAdd (bench):: [lid=%d] [tid=%l] [sz=%d] [cc=%l]\r\n",
             CNN_Benchmark_Get_LID(), CNN_Benchmark_Get_TID(),
             (uint16_t)(h*w*2), (uint32_t)cycleCount);
    cycleCount = 0;
#endif

#else // MSP432
    arm_add_q15 (matA, matB, result, h*w);
#endif

}


// multiply 2 matrices
void CNN_MatrixMultiply(_q15 *matA, _q15 *matB, _q15 *result,
                        uint16_t matA_h, uint16_t matA_w, uint16_t matB_h, uint16_t matB_w){

    msp_status status;
    msp_matrix_mpy_q15_params mpyParams;

    /* Initialize the parameter structure. */
    mpyParams.srcARows = matA_h;
    mpyParams.srcACols = matA_w;
    mpyParams.srcBRows = matB_h;
    mpyParams.srcBCols = matB_w;

    status = msp_matrix_mpy_q15(&mpyParams, matA, matB, result);

    if (status != 0 ){_DBGUART("ERROR: msp_matrix_mpy_q15 - status = %d\r\n", status);}
    msp_checkStatus(status);
}


// MAC between two vectors of length vecLen
void CNN_VectorMAC(_q15 *vecA, _q15 *vecB, uint16_t vecLen, _iq31 *result){
   //_iq31 tmpResult;
#ifdef __MSP430__
    msp_status status;
    msp_mac_q15_params mac_params;
    mac_params.length = vecLen + (vecLen&0x1);
//    if( !(MSP_LEA_VALID_ADDRESS(vecA, 4)) ){
//    	vecA+=1
//    }
//    	if( !(MSP_LEA_VALID_ADDRESS(result, 4)) ){
//    		result = (uint32_t)result&0xfffffffc;
//    	}
//    if (!(MSP_LEA_VALID_ADDRESS(vecA, 4) &
//          MSP_LEA_VALID_ADDRESS(vecB, 4) &
//          MSP_LEA_VALID_ADDRESS(result, 4))) {
//        return MSP_LEA_INVALID_ADDRESS;
//    }
    status = msp_mac_q15(&mac_params, vecA, vecB, result);
//    if (status != 0){_DBGUART("%l %l %l\r\n", vecA, vecB, result);}
//    if(status == 6)status=0;
    if (status != 0){_DBGUART("ERROR: msp_mac_q15 - status = %d %l %l %l\r\n", status,vecA, vecB, result);}
    msp_checkStatus(status);
#else
    q63_t *result_t;
    arm_dot_prod_q15(vecA,vecB,vecLen,result_t);   
    *result = clip_q63_to_q31(*result_t); 
#endif

}


