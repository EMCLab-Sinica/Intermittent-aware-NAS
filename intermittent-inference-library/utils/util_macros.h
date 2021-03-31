/*
 * util_macros.h
 */

#ifndef UTILS_UTIL_MACROS_H_
#define UTILS_UTIL_MACROS_H_


// bit manipulation
#define BSET(num,pos) num |= (1 << pos) // set bit
#define BCLR(num,pos) num &= ~(1<< pos) // clear bit
#define BCHK(num,pos) num & (1<<pos)    // check bit


#define _STOP() \
while(true) __no_operation();

#define _SHUTDOWN() \
P3OUT |= GPIO_PIN7;
//GPIO_setOutputHighOnPin( GPIO_PORT_P5, GPIO_PIN0 );


#define CPU_F                                   ((double)16000000)

#define _delay_us(A)\
  __delay_cycles( (uint32_t) ( (double)(CPU_F) *((A)/1000000.0) + 0.5))

#define _delay_ms(A)\
  __delay_cycles( (uint32_t) ( (double)(CPU_F)*((A)/1000.0) + 0.5))

#define _delay_s(A)\
  __delay_cycles( (uint32_t) ( (double)(CPU_F)*((A)/1.0) + 0.5))




#endif /* UTILS_UTIL_MACROS_H_ */
