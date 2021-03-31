

#include <msp430.h>

#include "driverlib.h"
#include "DSPLib.h"

/*  local imports */

// general utilities
#include "utils/myuart.h"
#include "utils/voltage_monitor.h"
#include "utils/helper_functions.h"
#include "cnn/tests/cnn_testbench_microbench.h"
#include "cnn/tests/cnn_testbench_conv.h"

// cnn library
#include "cnn/cnn.h"


// globals
unsigned int FreqLevel = 8;
int uartsetup=0;
volatile uint32_t cycleCount;


#pragma PERSISTENT(_init)
uint8_t _init=0;

// func prototypes
void gpio_setup(void);
int boardSetup(void);
void VMon_ISR_Callback(void);






void VMon_ISR_Callback(void){
#ifdef ENABLE_VMON
    switch (__even_in_range(CEIV, CEIV_CERDYIFG)) {
        case CEIV_NONE:        break;
        case CEIV_CEIFG:

            break;
        case CEIV_CEIIFG:
            CEIV &= ~(CEIV_CEIIFG);

            VMon_disable();
            __disable_interrupt();
            _DBGUART("-- VM_I2 --\r\n");
            _SHUTDOWN(); _STOP();

            break;
        case CEIV_CERDYIFG:    break;
    }
#endif
}


void gpio_setup(void){

    /* set direction */
    GPIO_setAsOutputPin( GPIO_PORT_P1, GPIO_PIN0 ); // led
    GPIO_setAsOutputPin( GPIO_PORT_P1, GPIO_PIN1 ); // led
    GPIO_setAsOutputPin( GPIO_PORT_P4, GPIO_PIN1 ); // for debug
    GPIO_setAsOutputPin( GPIO_PORT_P5, GPIO_PIN0 ); // EHM shutdown
    GPIO_setAsOutputPin( GPIO_PORT_P5, GPIO_PIN1 ); // EXT_FLAG : to signal the FT232H to complete exp run

    /* set initial value */
    // leds
    GPIO_setOutputLowOnPin( GPIO_PORT_P1, GPIO_PIN0 );  // led
    GPIO_setOutputLowOnPin( GPIO_PORT_P1, GPIO_PIN1 ); // led
    GPIO_setOutputLowOnPin( GPIO_PORT_P4, GPIO_PIN1 );  // debug
    GPIO_setOutputLowOnPin( GPIO_PORT_P5, GPIO_PIN0 );  // EHM shutdown
    GPIO_setOutputLowOnPin( GPIO_PORT_P5, GPIO_PIN1 );  // EXT_FLAG : to signal the FT232H to complete exp run

    }


int boardSetup(){
    WDTCTL = WDTPW + WDTHOLD;    /* disable watchdog timer  */



    PM5CTL0 &= ~LOCKLPM5;       // Disable the GPIO power-on default high-impedance mode

    /* setup UART */
    uartsetup=0;
    setFrequency(8);
    CS_initClockSignal( CS_SMCLK, CS_DCOCLK_SELECT, CS_CLOCK_DIVIDER_1 );
    CS_initClockSignal( CS_ACLK,  CS_LFXTCLK_SELECT, CS_CLOCK_DIVIDER_1); //ACLK=32768 HZ,
    uartinit();

    /* clock setup */

    // Configure one FRAM waitstate as required by the device datasheet for MCLK
    // operation beyond 8MHz _before_ configuring the clock system.
    FRCTL0 = FRCTLPW | NWAITS_1;
    // Clock System Setup
    CSCTL0_H = CSKEY_H;                     // Unlock CS registers
    CSCTL1 = DCOFSEL_0;                     // Set DCO to 1MHz
    // Set SMCLK = MCLK = DCO, ACLK = VLOCLK
    CSCTL2 = SELA__VLOCLK | SELS__DCOCLK | SELM__DCOCLK;
    // Per Device Errata set divider to 4 before changing frequency to
    // prevent out of spec operation from overshoot transient
    CSCTL3 = DIVA__4 | DIVS__4 | DIVM__4;   // Set all corresponding clk sources to divide by 4 for errata
    CSCTL1 = DCOFSEL_4 | DCORSEL;           // Set DCO to 16MHz
    // Delay by ~10us to let DCO settle. 60 cycles = 20 cycles buffer + (10us / (1/4MHz))
    __delay_cycles(60);
    CSCTL3 = DIVA__1 | DIVS__1 | DIVM__1;   // Set all dividers to 1 for 16MHz operation
    CSCTL0_H = 0;

    PMM_unlockLPM5();
    _enable_interrupt();

    // setup gpio
    gpio_setup();


    //Verify if the Clock settings are as expected
    volatile uint32_t clockValue;
    clockValue = CS_getMCLK();  //24969216
    clockValue = CS_getACLK();  //32768
    clockValue = CS_getSMCLK(); //24969216
    if(clockValue);


    return 0;
};


int main() {


    boardSetup();
    __delay_cycles(100000);
    initSPI();

    if(!_init){
    	_init =1;
    	while(1);
    }


#ifdef ENABLE_VMON
   VMon_init(&VMon_ISR_Callback); // initiate Voltage Monitor (VMon)
   VMon_enable();  // start VMon
#endif

    msp_lea_init();
//    _SHUTDOWN();
    // run microbenchmark
    //GPIO_toggleOutputOnPin( GPIO_PORT_P4, GPIO_PIN1 );
    //GPIO_toggleOutputOnPin( GPIO_PORT_P4, GPIO_PIN1 );

//    test_iterative_dma_fram_to_sram();

//    test_iterative_dma_sram_to_fram();
//
//    test_iterative_add();
//    test_iterative_multiply();
//    test_iterative_division();
//    test_iterative_modulo();
//    test_iterative_max();
//    test_microbench_multiple_latency();
    _lpm_sleep(10);
    test_LayerConv_Combo();


	return 0;
}




