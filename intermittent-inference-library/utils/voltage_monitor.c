/*
 * VoltageMonitor.c
 *
 *  Allows detection of voltage levels using COMP_E module
 */

#include <msp430.h>
#include "driverlib.h"

#include "voltage_monitor.h"

/*******************************************************************************
 * Global variables
 *******************************************************************************/

/* persistent variables */

#pragma PERSISTENT (VMonState)
VMonState_Type_t VMonState = VMON_BELOW_THRESHOLD;

#pragma PERSISTENT (VMonIntrEdgeDir)
VMonIntEdgeDir_Type_t VMonIntrEdgeDir = VMON_INT_EDGE_RISING;





/*******************************************************************************
 * Private Function Prototypes
 *******************************************************************************/
uint16_t _getInterruptEdgeDir(void);

void (*VMon_Callback)(void);




/*******************************************************************************
 * Public functions
 *******************************************************************************/

// Enable interrupts, VMon power on
void VMon_enable(void){
//    Comp_E_enableInterrupt(COMP_E_BASE, COMP_E_OUTPUT_INTERRUPT);

    Comp_E_enable(COMP_E_BASE); //Allow power to Comparator module

    //__delay_cycles(400);           // delay for the reference to settle
    //__enable_interrupt();
    //__delay_cycles(100);
}

// Disable interrupts, VMon power off
void VMon_disable(void){
    Comp_E_disableInterrupt(COMP_E_BASE, COMP_E_OUTPUT_INTERRUPT);
    Comp_E_disable(COMP_E_BASE);     // switch off power to Comparator module
}



void VMon_init(void (*CallBackArg)(void)){

    VMon_Callback = CallBackArg;

    /* Set P1.4 to Vcc and P4.7 to GND. */
    //P1OUT |= BIT4;
    //P4OUT &= ~BIT7;

    P1SEL0 |= BIT5;
    P1SEL1 |= BIT5;

    // Configure Comp_E COUT
    P1SEL1 |= BIT2;
    P1SEL0 &= ~(BIT2);
    P1DIR |= BIT2;

    CECTL0 = CEIPEN | CEIPSEL_5;           // Enable V+, input channel CE12
    CECTL1 = CEPWRMD_1 + CEF + CEFDLY_3;                     // normal power mode
    CECTL2 = CEREFL_2 | CERS_2 | CERSEL | 0x1600 | 0x16; //Ref : 2V ~/1.9
//    CECTL2 = CEREFL_1 | CERS_3 | CERSEL | 0x1600 | 0x16;
    // 0x16 = 22/32 * 1.2 Min
    // 0x17 = 23/32 * 1.2 may fail
                                            // R-ladder off; bandgap ref voltage
                                            // supplied to ref amplifier to get Vcref=2.0V
//    CECTL3 = BIT5;
    CEINT = CEIE | CEIIE;
//    CECTL1 |= CEON;
    //Initialize the Comparator E module
    /*
     * Pin CE5 (P1.5 @msp430fr5994LP) to Positive(+) Terminal
     * Reference Voltage to Negative(-) Terminal
     * Normal Power Mode
     * Output Filter On with minimal delay
     * Non-Inverted Output Polarity
     */
//    Comp_E_initParam param = {0};
//    param.posTerminalInput = COMP_E_INPUT5; // P1.5
//    param.negTerminalInput = COMP_E_VREF;
//    param.outputFilterEnableAndDelayLevel = COMP_E_FILTEROUTPUT_DLYLVL4;
//    param.invertedOutputPolarity = COMP_E_NORMALOUTPUTPOLARITY;
//    Comp_E_init(COMP_E_BASE, &param);
//
//    //Set the reference voltage that is being supplied to the (-) terminal
//    /*
//     * Reference Voltage of 2.0 V,
//     * Lower Limit of 2.0*(20/32) = 1.25V,
//     * Upper Limit of 2.0*(20/32) = 1.25V
//     *
//     * This triggers when Vcc is 2.7V (1.375+1.375), voltage divider is used to
//     * halve the input vol value.
//     * EPD min operational voltage is 2.3V, max 3.6V
//     */
//    Comp_E_setReferenceVoltage(COMP_E_BASE,
//        /*COMP_E_VREFBASE2_5V*/COMP_E_VREFBASE2_0V,
//        22/*22  22/32 * 2 = 1.375*/,
//        22/*22*/
//        );
//
//    //Enable COMP_E Interrupt on default rising edge for CEIFG
//    //Comp_E_setInterruptEdgeDirection(COMP_E_BASE, COMP_E_RISINGEDGE);
//    Comp_E_setInterruptEdgeDirection(COMP_E_BASE, COMP_E_FALLINGEDGE);
//
//    // Clear any erroneous interrupts
//    Comp_E_clearInterrupt(COMP_E_BASE, (COMP_E_OUTPUT_INTERRUPT_FLAG + COMP_E_INTERRUPT_FLAG_INVERTED_POLARITY));

    //Enable Interrupts
    /*
     * Base Address of Comparator E,
     * Enable COMPE Interrupt on default rising edge for CEIFG
     */
    //Comp_E_clearInterrupt(COMP_E_BASE, COMP_E_OUTPUT_INTERRUPT_FLAG);

}


VMonState_Type_t VMon_Get_State(void){
    return VMonState;
}



/*******************************************************************************
 * Private functions
 *******************************************************************************/
// get interrupt direction based on state
uint16_t _getInterruptEdgeDir(void){
    if (VMonIntrEdgeDir == VMON_INT_EDGE_RISING){
        return COMP_E_RISINGEDGE;
    }
    else{
        return COMP_E_FALLINGEDGE;
    }
}




//******************************************************************************
//
//This is the COMP_E_VECTOR interrupt vector service routine.
//
//******************************************************************************
#if defined(__TI_COMPILER_VERSION__) || defined(__IAR_SYSTEMS_ICC__)
#pragma vector=COMP_E_VECTOR
__interrupt
#elif defined(__GNUC__)
__attribute__((interrupt(COMP_E_VECTOR)))
#endif

#if (VMON_ISR_TYPE == 0)
void COMP_E_ISR(void){
        VMon_disable();
        __delay_cycles(25000); // 3ms @ 8MHz // to stop bouncy-ness when input is switching

        /*
        //Toggle the edge at which an interrupt is generated
        // also change the state of the VMon
        if (_getInterruptEdgeDir() == COMP_E_RISINGEDGE){
            //GPIO_setOutputHighOnPin( GPIO_PORT_P4, GPIO_PIN1 );
            Comp_E_setInterruptEdgeDirection(COMP_E_BASE, COMP_E_FALLINGEDGE);
            VMonIntrEdgeDir = VMON_INT_EDGE_FALLING;
            VMonState = VMON_ABOVE_THRESHOLD;
        }
        else if (_getInterruptEdgeDir() == COMP_E_FALLINGEDGE){
            //GPIO_setOutputLowOnPin( GPIO_PORT_P4, GPIO_PIN1 );
            Comp_E_setInterruptEdgeDirection(COMP_E_BASE, COMP_E_RISINGEDGE);
            VMonIntrEdgeDir = VMON_INT_EDGE_RISING;
            VMonState = VMON_BELOW_THRESHOLD;
        }
        */

        //Comp_E_toggleInterruptEdgeDirection(COMP_E_BASE);

        //Clear Interrupt flag
        Comp_E_clearInterrupt(COMP_E_BASE, COMP_E_OUTPUT_INTERRUPT_FLAG);


        //VMon_enable();
        VMon_Callback(); // execute the callback

}

#else
void COMP_E_ISR(void){

    VMon_Callback(); // execute the callback
}

#endif
