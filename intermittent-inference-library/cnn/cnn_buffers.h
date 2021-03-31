/*
 * cnn_buffers.h
 *
 * Only used for internal FRAM buffers
 */

#ifndef CNN_BUFFERS_H_
#define CNN_BUFFERS_H_





DSPLIB_DATA(LEA_MEMORY,4)
_q15 LEA_MEMORY[LEA_MEM_SIZE];
_q15 *pLEAMemory = LEA_MEMORY;



#endif /* CNN_BUFFERS_H_ */
