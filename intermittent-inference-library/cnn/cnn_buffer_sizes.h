/* 
* cnn_buffer_sizes.h 
*/

#ifndef CNN_BUFFER_SIZES_H_
#define CNN_BUFFER_SIZES_H_

// computation buffer sizes
#define LAY_TMPBUFF1_SIZE    (1*1*1)
#define LAY_TMPBUFF2_SIZE    (1*1*1)
#define LAY_OFMBUFF1_SIZE    (4*4*4)
#define LAY_OFMBUFF2_SIZE    (4*4*4)

#define SRAM_BUFF_SIZE       (1)

// locations of computation buffers
#define LOC_TEMPBUFF1      0x1A5CC
#define LOC_TEMPBUFF2      LOC_TEMPBUFF1 + (LAY_TMPBUFF1_SIZE*Q15_SIZE) + 4
#define LOC_OFMBUFF1       LOC_TEMPBUFF2 + (LAY_TMPBUFF2_SIZE*Q15_SIZE) + 4
#define LOC_OFMBUFF2       LOC_OFMBUFF1  + (LAY_OFMBUFF1_SIZE*Q15_SIZE) + 4

// locations of weights
#define LOC_TESTCONV_WEIGHT      LOC_OFMBUFF2 + (LAY_OFMBUFF2_SIZE*Q15_SIZE) + 4

// locations of loop indices (ext)
#define LOC_LOOP_INDICES 0
#define LOC_LAYER_ID 40


#endif /* CNN_BUFFER_SIZES_H_ */
