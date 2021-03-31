/*
 * VoltageMonitor.h
 *
 */

#ifndef VOLTAGEMONITOR_H_
#define VOLTAGEMONITOR_H_

#define ENABLE_VMON 0


#define VMON_ISR_TYPE   1   // 0 - default , 1 - quick hand-over to callback


typedef enum  {

    VMON_ABOVE_THRESHOLD=0,
    VMON_BELOW_THRESHOLD

}VMonState_Type_t;

typedef enum  {
    VMON_INT_EDGE_FALLING=0,
    VMON_INT_EDGE_RISING

}VMonIntEdgeDir_Type_t;


// public
void VMon_enable(void);
void VMon_init(void (*CallBackArg)(void));
void VMon_disable(void);
VMonState_Type_t VMon_Get_State(void);






#endif /* VOLTAGEMONITOR_H_ */
