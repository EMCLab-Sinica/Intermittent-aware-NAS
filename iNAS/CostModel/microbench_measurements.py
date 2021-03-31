import sys
from pprint import pprint

####################################
#   ENERGY (J)
####################################

# FOR DMA
# --------
PARAM_EN_FRAM_TO_SRAM_LINREG_M = 2.7e-08
PARAM_EN_FRAM_TO_SRAM_LINREG_B = 2.0e-07

PARAM_EN_SRAM_TO_FRAM_LINREG_M = 2.6815e-08
PARAM_EN_SRAM_TO_FRAM_LINREG_B = 1.9336e-07

# linear prediction
def predict_dma_energy(tr_type, data_size):
    if (tr_type == "FRAM_TO_SRAM"):        
        y = (PARAM_EN_FRAM_TO_SRAM_LINREG_M * data_size) + PARAM_EN_FRAM_TO_SRAM_LINREG_B
    elif (tr_type == "SRAM_TO_FRAM"):
        y = (PARAM_EN_SRAM_TO_FRAM_LINREG_M * data_size) + PARAM_EN_SRAM_TO_FRAM_LINREG_B
    else:
        sys.exit("Error: predict_dma_energy: unknown")
    return y


# FOR LEA
# --------
PARAM_EN_LEAVECMAC_LINREG_M = 5.27308646249e-10
PARAM_EN_LEAVECMAC_LINREG_B = 2.04412689725e-07

def predict_leavecmac_energy(tr_type, vec_size):
    if (tr_type == "LEAVECMAC"):        
        y = (PARAM_EN_LEAVECMAC_LINREG_M * vec_size) + PARAM_EN_LEAVECMAC_LINREG_B    
    else:
        sys.exit("Error: predict_dma_energy: unknown")
    return y

# FOR CPU
# ----------
PARAM_EN_ADD_ENERGY = 3.935538461538471e-09
PARAM_EN_MULTIPLY_ENERGY = 1.9253346153846146e-08
PARAM_EN_DIVIDE_ENERGY = 4.373834615384616e-08
PARAM_EN_MODULO_ENERGY = 4.366230769230769e-08
PARAM_EN_MAX_ENERGY = 4.228153846153846e-09

def predict_mathop_energy(tr_type):
    if (tr_type == "ADD"):
        return PARAM_EN_ADD_ENERGY
    elif (tr_type == "MULTIPLY"):
        return PARAM_EN_MULTIPLY_ENERGY
    elif (tr_type == "DIVIDE"):
        return PARAM_EN_DIVIDE_ENERGY
    elif (tr_type == "MODULO"):
        return PARAM_EN_MODULO_ENERGY
    elif (tr_type == "MAX"):
        return PARAM_EN_MAX_ENERGY
    else:
        sys.exit("Error: predict_mathop_energy: unknown")



######################################################
#   LATENCY (clock cycles on the TI MSP430FR5994)
######################################################
PARAM_LAT_FRAM_TO_SRAM_LINREG_M = 64.00000000000001
PARAM_LAT_FRAM_TO_SRAM_LINREG_B = 423.99999999999994

PARAM_LAT_SRAM_TO_FRAM_LINREG_M = 64.00082974729904
PARAM_LAT_SRAM_TO_FRAM_LINREG_B = 422.22773129921234

PARAM_LAT_LEAVECMAC_LINREG_M = 1.4999999999999978
PARAM_LAT_LEAVECMAC_LINREG_B = 616.0000000000002

PARAM_LAT_ADD_LATENCY = 12
PARAM_LAT_MULTIPLY_LATENCY = 44
PARAM_LAT_DIVIDE_LATENCY = 160
PARAM_LAT_MODULO_LATENCY = 160
PARAM_LAT_MAX_LATENCY = 14

def predict_latency(tr_type, data_size):
    
    # ---- FOR DMA -----
    if tr_type == "FRAM_TO_SRAM":
        y = (PARAM_LAT_FRAM_TO_SRAM_LINREG_M * data_size) + PARAM_LAT_FRAM_TO_SRAM_LINREG_B
    elif tr_type == "SRAM_TO_FRAM":
        y = (PARAM_LAT_SRAM_TO_FRAM_LINREG_M * data_size) + PARAM_LAT_SRAM_TO_FRAM_LINREG_B
    
    # ---- FOR LEA -----
    elif tr_type == "LEAVECMAC":
        y = (PARAM_LAT_LEAVECMAC_LINREG_M * data_size) + PARAM_LAT_LEAVECMAC_LINREG_B
    
    # ---- FOR CPU -----
    elif tr_type == "MATHOPS_ADD":
        y = PARAM_LAT_ADD_LATENCY
    elif tr_type == "MATHOPS_DIV":
        y = PARAM_LAT_DIVIDE_LATENCY
    elif tr_type == "MATHOPS_MUL":
        y = PARAM_LAT_MULTIPLY_LATENCY
    elif tr_type == "MATHOPS_MOD":
        y = PARAM_LAT_MODULO_LATENCY
    elif tr_type == "MATHOPS_MAX":
        y = PARAM_LAT_MAX_LATENCY

    else:
        sys.exit("Error: predict_latency: unknown")

    return y