/*
 * helper_functions.h
 *
 */

#ifndef UTILS_HELPER_FUNCTIONS_H_
#define UTILS_HELPER_FUNCTIONS_H_

#include <stdint.h>


#define BASE_DECIMAL     10


void wait_forever(void);
void swap(uint8_t **buff1_ptr, uint8_t **buff2_ptr);
void itoa(long unsigned int value, char* result, int base);


#endif /* UTILS_HELPER_FUNCTIONS_H_ */
