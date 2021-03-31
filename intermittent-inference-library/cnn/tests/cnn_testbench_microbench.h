/*
 * cnn_testbench_microbench.h
 */

#ifndef CNN_TESTBENCH_MICROBENCH_H_
#define CNN_TESTBENCH_MICROBENCH_H_




#define CNN_TB_MICRO_NONE           0
#define CNN_TB_MICRO_DMA            1
#define CNN_TB_MICRO_LEACONV1D      2
#define CNN_TB_MICRO_LEAMADD        3
#define CNN_TB_MICRO_LEAMMULT       4
#define CNN_TB_MICRO_LEAVECMAC      5
#define CNN_TB_MICRO_MATHOPS        6
#define CNN_TB_MICRO_CPU_DATA       7

#define CNN_TB_MICRO_LAT_MULTIPLE   20



#define CNN_TB_MICRO_TYPE   CNN_TB_MICRO_LAT_MULTIPLE








// lea
void test_iterative_lea_vecmac(void);

// dma
void test_iterative_dma_fram_to_sram(void);
void test_iterative_dma_sram_to_fram(void);
void test_iterative_dma_fram_to_fram(void);
void test_iterative_dma_sram_to_sram(void);

// math ops
void test_iterative_add(void);
void test_iterative_multiply(void);
void test_iterative_division(void);
void test_iterative_modulo(void);
void test_iterative_max(void);

// cpu based data transfer
void test_iterative_cpu_fram_to_sram(void);
void test_iterative_cpu_sram_to_fram(void);
void test_iterative_cpu_fram_to_fram(void);
void test_iterative_cpu_sram_to_sram(void);
void test_iterative_cpu_fram_to_reg(void);

// latency benchmarks (multiple)
void test_microbench_multiple_latency(void);



#endif /* CNN_TESTBENCH_MICROBENCH_H_ */
