import sys, os
from pprint import pprint
import numpy as np
from time import perf_counter 
import inspect


## -- modelling the capacitor based energy buffer


def cap_energy(C, Vtop, Vbot):    
    E = 0.5 * C * ((Vtop**2) - (Vbot**2))
    return E

def cap_v_after_use(C, Etop, Ebot, Vbot):
    V = np.sqrt((2 * (Etop - Ebot))/C)
    return V

def cap_recharge_time(R, C, Vinit, Vtop, Vsup):
    t = -1 * R * C * np.log((Vtop - Vsup) / (Vinit - Vsup))
    return t


# Epc : energy consumption per power cycle
# Von : system starts when cap voltage reaches this level
# Voff : system shutsdown when cap voltage reaches this level
# C : capacitance
# Vsup : supply voltage charging the capacitor
# R : EHM unit equivalent resistance
def cal_cap_recharge_time_custom(Epc, C=0.0001, R=1000, Vsup=3, Von=2.8, Voff=2.4, safe_margin=1.0):    
    Eavail = 0.5 * C * ((Von**2) - (Voff**2)) * safe_margin   # available capacitor energy
    
    # check first
    if (Epc <= 0) or (Eavail <= Epc) or (Eavail < 0) or (Vsup < Von) or (Voff > Von):
        sys.exit(inspect.currentframe().f_code.co_name+"::Error - calc invalid:En, %f, %f, %f, %f, %f, %f" % (C, Eavail, Epc, Vsup, Von, Voff) )
    
    Vpce = (np.sqrt( ((2 * (Eavail - Epc))/C) + Voff**2))

    if (Vpce > Vsup) or (Von > Vsup) or (Voff > Von):        
        sys.exit(inspect.currentframe().f_code.co_name+"::Error - calc invalid:V, %f, %f, %f, %f, %f, %f, %f" % (C, Eavail, Epc, Vsup, Von, Voff, Vpce))    

    Lrecharge = -1.0 * R * C * np.log((Von - Vsup) / (Vpce - Vsup))    

    return Lrecharge






