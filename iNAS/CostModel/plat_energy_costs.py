import sys


from CostModel.microbench_measurements import predict_dma_energy, predict_leavecmac_energy, predict_mathop_energy, predict_latency


CPU_CLOCK_MSP430 = 16000000


TMP_MIN_E = 0.000001
TMP_MIN_L = 0.001


# proxy functions - pointing to real platform measurements ---

def _proxy_datatr_rd_energy(v):
    return predict_dma_energy("FRAM_TO_SRAM", v)
def _proxy_datatr_wr_energy(v):
    return predict_dma_energy("SRAM_TO_FRAM", v)
def _proxy_leavecmac_energy(v):
    return predict_leavecmac_energy("LEAVECMAC", v)

E_ADD = predict_mathop_energy("ADD") * 1.0
E_MUL = predict_mathop_energy("MULTIPLY") * 1.0
E_DIV = predict_mathop_energy("DIVIDE") * 1.0
E_MOD = predict_mathop_energy("MODULO") * 1.0
E_MAX = predict_mathop_energy("MAX") * 1.0


# latency is in clock cycles, need to convert to seconds

L_ADD = predict_latency("MATHOPS_ADD", None) / CPU_CLOCK_MSP430
L_MUL = predict_latency("MATHOPS_MUL", None) / CPU_CLOCK_MSP430
L_DIV = predict_latency("MATHOPS_DIV", None) / CPU_CLOCK_MSP430
L_MOD = predict_latency("MATHOPS_MOD", None) / CPU_CLOCK_MSP430
L_MAX = predict_latency("MATHOPS_MAX", None) / CPU_CLOCK_MSP430

def _proxy_datatr_rd_latency(v):
    return (predict_latency("FRAM_TO_SRAM", v) / CPU_CLOCK_MSP430)
def _proxy_datatr_wr_latency(v):
    return (predict_latency("SRAM_TO_FRAM", v) / CPU_CLOCK_MSP430)
def _proxy_leavecmac_latency(v):
    return (predict_latency("LEAVECMAC", v) / CPU_CLOCK_MSP430)



# -- temp functions used for testing --
def _temp_datatr_rd_energy(v):
    return v*TMP_MIN_E*8
def _temp_datatr_wr_energy(v):
    return v*TMP_MIN_E*10

def _temp_datatr_latency(v):
    return v*TMP_MIN_L*5
def _temp_comp_energy(v):
    return v*TMP_MIN_E
def _temp_comp_latency(v):
    return v*TMP_MIN_L



class PlatformCostModel:
    
    # micro cost measurements for the MSP430 platform
    PLAT_MSP430_EXTNVM = {
        
        # =========== Energy ===========        
        # reboot cost (obtained via oscilloscope)
        "E_RB" : 0.00007788,  # E=0.5 * C * (V1^2 - V2^2) = 0.5 * 0.00033 * (2.99^2 - 2.91^2)
                 
        # CPU ops cost
        "E_ADD" : E_ADD,
        "E_SUB" : E_ADD, # assume same cost as add
        "E_MUL" : E_MUL,
        "E_DIV" : E_DIV,
        "E_MOD" : E_MOD,

        # data move cost
        "E_DMA_NVM_TO_VM" : _proxy_datatr_rd_energy,
        "E_DMA_VM_TO_NVM" : _proxy_datatr_wr_energy,        

        # data fetch overhead (addressing) - num of addressing operations found by inspecting the compiled asm        
        "E_FD_I_OVHD" : (E_ADD * (5+2)) + (E_MUL * (3+2)),            # according to asm: (E_ADD * (8+2)) + (E_MUL * (3+2)),
        "E_FD_W_OVHD" : (E_ADD * (5+3)) + (E_MUL * (6+3)),            # according to asm: (E_ADD * (7+3)) + (E_MUL * (6+3)),        
        "E_FD_O_RUI_OVHD" : (E_ADD * (5+2)) + (E_MUL * (2+3)),            # according to asm: (E_ADD * (5+2)) + (E_MUL * (2+3)),
        "E_FD_O_RUW_OVHD" : (E_ADD * (5+2)) + (E_MUL * (2+2)),            # according to asm: (E_ADD * (5+2)) + (E_MUL * (2+2)),
        "E_FD_O_RUO_OVHD" : (E_ADD * (5+2)) + (E_MUL * (2+2)),            # according to asm: (E_ADD * (5+2)) + (E_MUL * (2+2)),        
        "E_BD_O_RUI_OVHD" : (E_ADD * (4+5)) + (E_MUL * (6+2)),            # according to asm: (E_ADD * (4+5)) + (E_MUL * (6+2)),    
        "E_BD_O_RUW_OVHD" : (E_ADD * (4+7)) + (E_MUL * (4+5)),            # according to asm: (E_ADD * (4+7)) + (E_MUL * (4+5)),    
        "E_BD_O_RUO_OVHD" : (E_ADD * (2+5)) + (E_MUL * (3+2)),            # according to asm: (E_ADD * (2+5)) + (E_MUL * (3+2)),    

        # vector MAC compute cost
        "E_OP_VECMAC" : _proxy_leavecmac_energy,
        # computation invocation overhead (addressing)
        "E_OP_PSUM_OVHD" : (E_ADD * (4+3)) + (E_MUL * (2+3)),               # according to asm: (E_ADD * (4+3)) + (E_MUL * (2+3)),  
        "E_OP_ACUM_OVHD" : (E_ADD * (3)) + (E_MUL * (3)),                   # according to asm: (E_ADD * (3)) + (E_MUL * (3)),  

        # q15 compare operation
        "E_OP_MAXCOMPARE" : E_MAX,
        "E_OP_MAX_OVHD"   : (E_ADD * (2)) + (E_MUL * (1)),                  # according to asm: (E_ADD * (2)) + (E_MUL * (1)),  


        # =========== Latency (in seconds) ===========
        # reboot cost (obtained via oscilloscope)
        "L_RB" : 0.07, # 70 ms

        # CPU ops cost
        "L_ADD" : L_ADD,
        "L_SUB" : L_ADD, # assume same cost as add
        "L_MUL" : L_MUL,
        "L_DIV" : L_DIV,
        "L_MOD" : L_MOD,

        # data move cost
        "L_DMA_NVM_TO_VM" : _proxy_datatr_rd_latency,
        "L_DMA_VM_TO_NVM" : _proxy_datatr_wr_latency,
        
        # data fetch overhead (addressing) - num of addressing operations found by inspecting the compiled asm        
        "L_FD_I_OVHD" : (L_ADD * (5+2)) + (L_MUL * (3+2)),
        "L_FD_W_OVHD" : (L_ADD * (5+3)) + (L_MUL * (6+4)),        
        "L_FD_O_RUI_OVHD" : (E_ADD * (5+2)) + (E_MUL * (2+3)),            # according to asm: (L_ADD * (5+2)) + (L_MUL * (2+3)),
        "L_FD_O_RUW_OVHD" : (E_ADD * (5+2)) + (E_MUL * (2+2)),            # according to asm: (L_ADD * (5+2)) + (L_MUL * (2+2)),
        "L_FD_O_RUO_OVHD" : (E_ADD * (5+2)) + (E_MUL * (2+2)),            # according to asm: (L_ADD * (5+2)) + (L_MUL * (2+2)),        
        "L_BD_O_RUI_OVHD" : (E_ADD * (4+5)) + (E_MUL * (6+2)),            # according to asm: (L_ADD * (4+5)) + (L_MUL * (6+2)),    
        "L_BD_O_RUW_OVHD" : (E_ADD * (4+7)) + (E_MUL * (4+5)),            # according to asm: (L_ADD * (4+7)) + (L_MUL * (4+5)),    
        "L_BD_O_RUO_OVHD" : (E_ADD * (2+5)) + (E_MUL * (3+2)),            # according to asm: (L_ADD * (2+5)) + (L_MUL * (3+2)),

        # vector MAC compute cost
        "L_OP_VECMAC" : _proxy_leavecmac_latency,
        # computation invocation overhead (addressing)
        "L_OP_PSUM_OVHD" : (L_ADD * (4+3)) + (L_MUL * (4+6)),
        "L_OP_ACUM_OVHD" : (L_ADD * (3)) + (L_MUL * (3)),

        # q15 compare operation
        "L_OP_MAXCOMPARE" : L_MAX,
        "L_OP_MAX_OVHD"   : (L_ADD * (2)) + (L_MUL * (1)),
    }

    PLAT_MSP432_EXTNVM = {        
        # unsupported       
    }



