/*
 * sleep_timer.h
 */

#ifndef UTILS_SLEEP_TIMER_H_
#define UTILS_SLEEP_TIMER_H_

#include <math.h>
#include <stdint.h>
#include <string.h>

// TI specific headers
#include "msp430.h"
#include "driverlib.h"


void _lpm_sleep(uint16_t delayCycles);
void _config_sleep_timer(uint16_t delayCycles);



#endif /* UTILS_SLEEP_TIMER_H_ */
