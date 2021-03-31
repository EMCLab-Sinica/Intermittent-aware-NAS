/*
 * cnn_testbench_microbench.c
 * benchmarking small operations (LEA/DMA)
 */



#include "../cnn_common.h"

#include "cnn_testbench_microbench.h"
#include "../cnn_matops.h"


#define NUM_POWER_PULSES 50


#if (CNN_TB_MICRO_TYPE == CNN_TB_MICRO_DMA) || (CNN_TB_MICRO_TYPE == CNN_TB_MICRO_CPU_DATA)

#pragma PERSISTENT(TMP_TB_BUFF1)
_q15 TMP_TB_BUFF1[2000] = {[0 ... 1999] = 0x00AE};

#pragma PERSISTENT(TMP_TB_BUFF2)
_q15 TMP_TB_BUFF2[2000] = {[0 ... 1999] = 0x00AB};

_q15 *pTmpTbBuff1 = TMP_TB_BUFF1;
_q15 *pTmpTbBuff2 = TMP_TB_BUFF2;


#elif CNN_TB_MICRO_TYPE == CNN_TB_MICRO_LEACONV1D


#elif CNN_TB_MICRO_TYPE == CNN_TB_MICRO_LEAMADD



#elif CNN_TB_MICRO_TYPE == CNN_TB_MICRO_LEAMMULT

#pragma PERSISTENT(TMP_TB_VEC_A)
_q15 TMP_TB_VEC_A[2048] = {[0 ... 2047] = 0x00FF};

#pragma PERSISTENT(TMP_TB_VEC_B)
_q15 TMP_TB_VEC_B[2048] = {[0 ... 2047] = 0x00AB};

_q15 *pTmpTbVecA = TMP_TB_VEC_A;
_q15 *pTmpTbVecB = TMP_TB_VEC_B;


#elif CNN_TB_MICRO_TYPE == CNN_TB_MICRO_LEAVECMAC

#pragma PERSISTENT(TMP_TB_VEC_A)
_q15 TMP_TB_VEC_A[256] = {[0 ... 255] = 0x00FF};

#pragma PERSISTENT(TMP_TB_VEC_B)
_q15 TMP_TB_VEC_B[256] = {[0 ... 255] = 0x00AB};

_q15 *pTmpTbVecA = TMP_TB_VEC_A;
_q15 *pTmpTbVecB = TMP_TB_VEC_B;


#elif CNN_TB_MICRO_TYPE == CNN_TB_MICRO_MATHOPS
#pragma PERSISTENT(TMP_TB_BUFF1)
uint16_t TMP_TB_BUFF1[10] = {0x0A01, 0x0A02, 0x0A03, 0x0A04, 0x0A05, 0x0A06, 0x0A07, 0x0A08, 0x0A09, 0x0A0A};


#elif CNN_TB_MICRO_TYPE == CNN_TB_MICRO_LAT_MULTIPLE

#pragma PERSISTENT(TMP_TB_VEC_A)
_q15 TMP_TB_VEC_A[256] = {[0 ... 255] = 0x00FF};
_q15 *pTmpTbVecA = TMP_TB_VEC_A;



#endif













/*
void _lpm_sleep(uint16_t delayCycles);
void _config_sleep_timer(uint16_t delayCycles);
*/

/********************************************************************
 * Energy Cost of LEA Operations
 ********************************************************************/
void test_iterative_lea_conv1d(){
#if CNN_TB_MICRO_TYPE == CNN_TB_MICRO_LEACONV1D
    
#endif
}

void test_iterative_lea_matadd(){
#if CNN_TB_MICRO_TYPE == CNN_TB_MICRO_LEAMADD
    
#endif
}





void test_iterative_lea_vecmac(){
#if CNN_TB_MICRO_TYPE == CNN_TB_MICRO_LEAVECMAC
    uint16_t i;
    uint16_t sz_range=64;
    uint16_t A_vec=0,B_vec=0;
    uint16_t A_sz=0, B_sz=0;
    _q15 *pLEAMEM;

    pLEAMEM = CNN_GetLEAMemoryLocation();
    _q15 *pA = pLEAMEM;
    _q15 *pB = pLEAMEM + sz_range;
    _q15 *pO = pLEAMEM + 2*sz_range;

    // initialise LEA SRAM
    memcpy_dma(pLEAMEM, pTmpTbVecA, 256*Q15_SIZE, LEA_MEM_SIZE*Q15_SIZE, DMA_DIR_INC, DMA_DIR_INC); // copying the fram data to LEA memory

    _lpm_sleep(50);
    for (A_sz=1; A_sz<=sz_range; A_sz+=1){

                if ((A_sz == 1) || ((A_sz % 2) == 0)){

                    // run multiple times, divide by count to get mean energy consumption
                      _lpm_sleep(10);
                      //_DBGUART("-starting - [%d,%d,%d]\r\n", A_Cols, A_Rows, B_Cols);
                      for (i=0; i < 5000; i++){
                    	  CNN_VectorMAC(pA,pB,A_sz,(_iq31*)pO);

                      }
                      //_DBGUART("-done\r\n");
                      _lpm_sleep(10);
                }
              }


    _lpm_sleep(50);
    //_DBGUART("-finished\r\n");
#endif
}







/********************************************************************
 * Energy Cost of DMA operations
 ********************************************************************/

// DMA read from NVM
void test_iterative_dma_fram_to_sram(){
#if CNN_TB_MICRO_TYPE == CNN_TB_MICRO_DMA
    uint16_t i, sz;
    _q15 *pLEAMEM;
    pLEAMEM = CNN_GetLEAMemoryLocation(); // sram

    _lpm_sleep(50);

    /* small steps , short run */
    for (sz=1; sz <= 128  ; sz+=1){
        // run multiple times, divide by count to get mean energy consumption
        for (i=0; i < 3000; i++){
            //memcpy_dma_ext(uint32_t nvm_addr, const void* vm_addr, size_t n, size_t dstSize, uint16_t RW) {
            memcpy_dma_ext( 0x00AB , pLEAMEM, sz*Q15_SIZE, LEA_MEM_SIZE*Q15_SIZE, 0);
        }
        _lpm_sleep(5);
    }
    _lpm_sleep(5);
    _STOP();

#endif
}


// DMA write to NVM
void test_iterative_dma_sram_to_fram(){
#if CNN_TB_MICRO_TYPE == CNN_TB_MICRO_DMA
    uint16_t i, sz;
    _q15 *pLEAMEM;
    pLEAMEM = CNN_GetLEAMemoryLocation(); // sram

    _lpm_sleep(50);

    /* small steps , short run */
    for (sz=1; sz <= 128 ; sz+=1){
        // run multiple times, divide by count to get mean energy consumption
        for (i=0; i < 3000; i++){
            memcpy_dma_ext(0x00AB, pLEAMEM, sz*Q15_SIZE, 2000*Q15_SIZE, 1);
        }
        _lpm_sleep(5);
    }
    _lpm_sleep(5);
    _STOP();

#endif
}


// DMA transfer : FRAM to FRAM
void test_iterative_dma_fram_to_fram(){
#if CNN_TB_MICRO_TYPE == CNN_TB_MICRO_DMA
    uint16_t i, sz;

    _lpm_sleep(50);

    /* small steps , short run */
    for (sz=1; sz < 256 ; sz+=1){
        // run multiple times, divide by count to get mean energy consumption
        for (i=0; i < 5000; i++){
            memcpy_dma(pTmpTbBuff2, pTmpTbBuff1, sz*Q15_SIZE, 2000*Q15_SIZE, DMA_DIR_INC, DMA_DIR_INC);
        }
        _lpm_sleep(5);
    }
    _lpm_sleep(5);
    _STOP();

#endif
}


// DMA transfer : SRAM to SRAM
void test_iterative_dma_sram_to_sram(){
#if CNN_TB_MICRO_TYPE == CNN_TB_MICRO_DMA
    uint16_t i, sz;
    _q15 *pLEAMEM, *pSRAMBUFF;
    pLEAMEM = CNN_GetLEAMemoryLocation(); // sram
    pSRAMBUFF = CNN_GetSRAMBuffLocation(); // sram

    _lpm_sleep(50);

    /* small steps , short run */
    for (sz=1; sz < 256 ; sz+=1){
        // run multiple times, divide by count to get mean energy consumption
        for (i=0; i < 5000; i++){
            memcpy_dma(pSRAMBUFF, pLEAMEM, sz*Q15_SIZE, 900*Q15_SIZE, DMA_DIR_INC, DMA_DIR_INC);
        }
        _lpm_sleep(5);
    }
    _lpm_sleep(5);
    _STOP();

#endif
}



/********************************************************************
 * Energy Cost of CPU based data operations
 ********************************************************************/
void test_iterative_cpu_fram_to_sram(){
#if (CNN_TB_MICRO_TYPE == CNN_TB_MICRO_CPU_DATA)
    uint16_t i, j;
    _q15 *pLEAMEM;
    pLEAMEM = CNN_GetLEAMemoryLocation(); // sram

    // cpu transfers 1 data item at a time
    _lpm_sleep(100);
    for (i=0; i < 200; i++){
        for (j=0; j < 1800; j++){
            *(pLEAMEM + j) = *(pTmpTbBuff1 + j);
        }
    }
    _lpm_sleep(100);

    _STOP();
#endif
}

void test_iterative_cpu_sram_to_fram(){
#if (CNN_TB_MICRO_TYPE == CNN_TB_MICRO_CPU_DATA)
    uint16_t i, j;
    _q15 *pLEAMEM;
    pLEAMEM = CNN_GetLEAMemoryLocation(); // sram

    // cpu transfers 1 data item at a time
    _lpm_sleep(100);
    for (i=0; i < 200; i++){
        for (j=0; j < 1800; j++){
            *(pTmpTbBuff1 + j) = *(pLEAMEM + j);
        }
    }
    _lpm_sleep(100);

    _STOP();
#endif
}

void test_iterative_cpu_fram_to_fram(){
#if (CNN_TB_MICRO_TYPE == CNN_TB_MICRO_CPU_DATA)
    uint16_t i, j;

    // cpu transfers 1 data item at a time
    _lpm_sleep(100);
    for (i=0; i < 200; i++){
        for (j=0; j < 1800; j++){
            *(pTmpTbBuff2 + j) = *(pTmpTbBuff1 + j);
        }
    }
    _lpm_sleep(100);

    _STOP();
#endif
}

void test_iterative_cpu_sram_to_sram(){
#if (CNN_TB_MICRO_TYPE == CNN_TB_MICRO_CPU_DATA)
    uint16_t i, j;
    _q15 *pLEAMEM, *pSRAMBUFF;
    pLEAMEM = CNN_GetLEAMemoryLocation(); // sram
    pSRAMBUFF = CNN_GetSRAMBuffLocation(); // sram

    // cpu transfers 1 data item at a time
    _lpm_sleep(100);
    for (i=0; i < 400; i++){
        for (j=0; j < 900; j++){
            *(pSRAMBUFF + j) = *(pLEAMEM + j);
        }
    }
    _lpm_sleep(100);

    _STOP();
#endif
}


void test_iterative_cpu_fram_to_reg(){
#if (CNN_TB_MICRO_TYPE == CNN_TB_MICRO_CPU_DATA)
    uint16_t i, j;
    volatile _q15 val=0;

    // cpu transfers 1 data item at a time
    _lpm_sleep(100);
    for (i=0; i < 200; i++){
        for (j=0; j < 1800; j++){
            val = *(pTmpTbBuff1 + j);
        }
    }
    _lpm_sleep(100);

    _STOP();
#endif
}


/********************************************************************
 * Energy Cost of Basic Math Operations
 ********************************************************************/
void test_iterative_add(){
    volatile uint16_t result=0;
    volatile uint16_t a=0;
    volatile uint16_t b=0;
    uint16_t i;
    uint16_t j;


    a=123;
    b=1234;

    _lpm_sleep(100);
    for(j=0;j<10;j++){
		for (i=0; i < 65000; i++){
			result = a + b;
		}
		_lpm_sleep(100);
    }

    _STOP();

}

void test_iterative_multiply(){
    volatile uint16_t result=0;
    volatile uint16_t a=0;
    volatile uint16_t b=0;
    uint16_t i;

    a=123;
    b=1234;

    _lpm_sleep(100);
    for(uint16_t j=0;j<10;j++){
		for (i=0; i < 65000; i++){
			result = a * b;
		}
		_lpm_sleep(50);
    }

    _STOP();

}

void test_iterative_division(){
    volatile uint16_t result=0;
    volatile uint16_t a=0;
    volatile uint16_t b=0;
    uint16_t i;

    a=123;
    b=1234;
    _lpm_sleep(100);
    for(uint16_t j=0;j<10;j++){

		for (i=0; i < 65000; i++){
			result = b / a;
		}
		_lpm_sleep(50);
    }

    _STOP();
}

void test_iterative_modulo(){
    volatile uint16_t result=0;
    volatile uint16_t a=0;
    volatile uint16_t b=0;
    uint16_t i;

    a=123;
    b=1234;

    _lpm_sleep(100);
    for(uint16_t j=0;j<10;j++){
		for (i=0; i < 65000; i++){
			result = b % a;
		}
		_lpm_sleep(50);
    }

    _STOP();
}

void test_iterative_max(){
    volatile uint16_t result=0;
    volatile uint16_t a=0;    
    uint16_t i;

    a=123;
    
    _lpm_sleep(100);
    for(uint16_t j=0;j<10;j++){
		for (i=0; i < 65000; i++){
			result = a > i ? a : i;
		}
		_lpm_sleep(50);
    }
    //if(result){}    

    _STOP();
}



/********************************************************************
 * Get Latency Cost - all micro benchmarks
 ********************************************************************/
void test_microbench_multiple_latency(){
#if CNN_TB_MICRO_TYPE == CNN_TB_MICRO_LAT_MULTIPLE

    volatile uint16_t result=0;
    volatile uint16_t a=0;
    volatile uint16_t b=0;
    volatile uint32_t cycleCount = 0; //Benchmark cycle counts
    uint16_t sz=0;
    uint16_t i=0;
    uint16_t sz_range=0;
    _q15 *pLEAMEM;
    pLEAMEM = CNN_GetLEAMemoryLocation(); // sram


    _DBGUART("-------- test_microbench_multiple_latency:: START --------\r\n");

    /****** DMA - read ******/
   _DBGUART("-------- DMA_READ \r\n");
   for (sz=1; sz <= 128  ; sz+=1){
       msp_benchmarkStart(TIMER_A1_BASE, 1);

       memcpy_dma_ext( 0x00AB , pLEAMEM, sz*Q15_SIZE, LEA_MEM_SIZE*Q15_SIZE, 0);

       cycleCount += msp_benchmarkStop(TIMER_A1_BASE); _DBGUART("dma_read::,sz=%d,cc=%l\r\n", sz, (uint32_t)cycleCount); cycleCount = 0;
       _lpm_sleep(5); // this gives some time for the previous dma/SPI operation to settle down
   }
   _lpm_sleep(10);


    /****** DMA - write ******/
    _DBGUART("-------- DMA_WRITE \r\n");
    for (sz=1; sz <= 128 ; sz+=1){
    	uint16_t sz2 = sz*2;
        msp_benchmarkStart(TIMER_A1_BASE, 1);

        memcpy_dma_ext(0x00AB, pLEAMEM, sz2, 4000, 1);

        cycleCount += msp_benchmarkStop(TIMER_A1_BASE); _DBGUART("dma_write::,sz=%d,cc=%l\r\n", sz, (uint32_t)cycleCount); cycleCount = 0;
        _lpm_sleep(5); // this gives some time for the previous dma/SPI operation to settle down
    }
    _lpm_sleep(5);


   /****** LEA vecmac ******/
   _DBGUART("-------- LEA_VECMAC \r\n");
   sz_range=64;
   _q15 *pA = pLEAMEM;
   _q15 *pB = pLEAMEM + sz_range;
   _q15 *pO = pLEAMEM + 2*sz_range;

   // initialise LEA SRAM
   memcpy_dma(pLEAMEM, pTmpTbVecA, 256*Q15_SIZE, LEA_MEM_SIZE*Q15_SIZE, DMA_DIR_INC, DMA_DIR_INC); // copying the fram data to LEA memory

   for (sz=1; sz<=sz_range; sz+=1){
       if ((sz == 1) || ((sz % 2) == 0)){
           msp_benchmarkStart(TIMER_A1_BASE, 1);

           CNN_VectorMAC(pA,pB,sz,(_iq31*)pO);

           cycleCount += msp_benchmarkStop(TIMER_A1_BASE); _DBGUART("lea_vecmac::,sz=%d,cc=%l\r\n", sz, (uint32_t)cycleCount); cycleCount = 0;
       }
   }
   _lpm_sleep(5);

   /****** MathOps - ADD ******/
   _DBGUART("-------- MATHOPS_ADD \r\n");
   a=123;
   b=1234;
   for(i=0;i<10;i++){
       msp_benchmarkStart(TIMER_A1_BASE, 1);
       result = a + b;
       cycleCount += msp_benchmarkStop(TIMER_A1_BASE); _DBGUART("math_add::,i=%d,cc=%l\r\n", i, (uint32_t)cycleCount); cycleCount = 0;
   }
   _lpm_sleep(5);

   /****** MathOps - MUL ******/
   _DBGUART("-------- MATHOPS_MUL \r\n");
   a=123;
   b=1234;
   for(i=0;i<10;i++){
       msp_benchmarkStart(TIMER_A1_BASE, 1);
       result = a * b;
       cycleCount += msp_benchmarkStop(TIMER_A1_BASE); _DBGUART("math_mul::,i=%d,cc=%l\r\n", i, (uint32_t)cycleCount); cycleCount = 0;
   }
   _lpm_sleep(5);

   /****** MathOps - DIV ******/
   _DBGUART("-------- MATHOPS_DIV \r\n");
   a=123;
   b=1234;
   for(i=0;i<10;i++){
       msp_benchmarkStart(TIMER_A1_BASE, 1);
       result = b / a;
       cycleCount += msp_benchmarkStop(TIMER_A1_BASE); _DBGUART("math_div::,i=%d,cc=%l\r\n", i, (uint32_t)cycleCount); cycleCount = 0;
   }
   _lpm_sleep(5);

   /****** MathOps - MOD ******/
   _DBGUART("-------- MATHOPS_MOD \r\n");
   a=123;
   b=1234;
   for(i=0;i<10;i++){
       msp_benchmarkStart(TIMER_A1_BASE, 1);
       result = b % a;
       cycleCount += msp_benchmarkStop(TIMER_A1_BASE); _DBGUART("math_mod::,i=%d,cc=%l\r\n", i, (uint32_t)cycleCount); cycleCount = 0;
   }
   _lpm_sleep(5);

   /****** MathOps - MAX ******/
   _DBGUART("-------- MATHOPS_MAX \r\n");
   a=123;
   b=1234;
   for(i=0;i<10;i++){
       msp_benchmarkStart(TIMER_A1_BASE, 1);
       result = a > i ? a : i;
       cycleCount += msp_benchmarkStop(TIMER_A1_BASE); _DBGUART("math_max::,i=%d,cc=%l\r\n", i, (uint32_t)cycleCount); cycleCount = 0;
   }
   _lpm_sleep(5);


    _DBGUART("-------- test_microbench_multiple_latency:: END --------\r\n");
#endif
}



/********************************************************************
 * Helpers
 ********************************************************************/
