import sys, os
from pprint import pprint
import numpy as np
from time import perf_counter 
import inspect


# local imports
from CostModel import common
from CostModel.conv_tiled import est_cost_CONV_powcycle_intpow, est_cost_CONV_contpow, est_cost_CONV_reboot_contpow
from CostModel.pool_tiled import est_cost_POOL_powcycle_intpow, est_cost_POOL_contpow
from CostModel.capacitor import cal_cap_recharge_time_custom, cap_energy




############################################################################
# CONSTRAINT CHECKING
############################################################################
# will the min exec and pres params make forward progress under given energy budget ?
def pass_constraint_atomicity(Epc, plat_settings):
    Eav = cap_energy(plat_settings['CCAP'], plat_settings['VON'], plat_settings['VOFF']) * plat_settings['EAV_SAFE_MARGIN']

    if Epc > Eav:
        return [False, Eav, Epc]
    else:
        return [True, Eav, Epc]

# will the min tile size fit into the available volatile memory of the system ?
def pass_constraint_spatial(layer, plat_settings, params_exec, params_pres):
    vm_capacity = plat_settings['VM_CAPACITY']
    Kh, Kw, Tri, Tci, Tr, Tc, Tm, Tn = params_exec['tile_size']
    inter_lo = params_exec['inter_lo']
    S = params_pres['backup_batch_size']

    B_in, B_w, B_out = common._vm_buff_size(Kh, Kw, Tri, Tci, Tr, Tc, Tm, Tn, inter_lo, S, layer_type = layer['type'])
    total_vm_req = (B_in + B_w + B_out) * plat_settings['DATA_SZ']

    if total_vm_req > vm_capacity:
        return [False, vm_capacity, total_vm_req]
    else:
        return [True, vm_capacity, total_vm_req]
        
# is the min achievable E2E latency lower than the latency constraint ?
def pass_constraint_responsiveness(L_e2e, plat_settings):
    lat_e2e_req = plat_settings['LAT_E2E_REQ']
    if L_e2e > lat_e2e_req:
        return [False, lat_e2e_req, L_e2e]
    else:
        return [True, lat_e2e_req, L_e2e]

############################################################################
# COST ANALYSIS (continuous power)
############################################################################
# --- SINGLE LAYER ----
def est_cost_layer_contpow(layer, params_exec, plat_settings, plat_cost_profile):    
    layer_type = layer['type']        
    R = layer['OFM'].h; C = layer['OFM'].h; M = layer['OFM'].ch; N = layer['IFM'].ch    
    inter_lo = params_exec['inter_lo']    
    Kh, Kw, Tri, Tci, Tr, Tc, Tm, Tn = params_exec['tile_size']
    
    # get per layer energy and latency
    if layer_type == "CONV":        
        if (common.check_conv(layer)):
            lay_E, lay_L = est_cost_CONV_contpow(layer, params_exec, plat_settings, plat_cost_profile)                
        else:
            sys.exit(inspect.currentframe().f_code.co_name+"::Error - CONV dimensions incorrect") 

    elif (layer_type == "POOL") or (layer_type == "GAVGPOOL"):
        if (common.check_pool(layer)):
            lay_E, lay_L = est_cost_POOL_contpow(layer, params_exec, plat_settings, plat_cost_profile)              
        else:
            sys.exit(inspect.currentframe().f_code.co_name+"::Error - POOL dimensions incorrect") 

    elif layer_type == "FC":
        if (common.check_fc(layer)):
            lay_E, lay_L = est_cost_CONV_contpow(layer, params_exec, plat_settings, plat_cost_profile)  
        else:
            sys.exit(inspect.currentframe().f_code.co_name+"::Error - FC dimensions incorrect") 

    else:
        sys.exit(inspect.currentframe().f_code.co_name+"::Error - unknown layer type")
        
    return lay_E, lay_L

def est_cost_onetime_reboot(plat_cost_profile):
    en_cost, lat_cost = est_cost_CONV_reboot_contpow(plat_cost_profile)
    return en_cost, lat_cost

############################################################################
# COST ANALYSIS (intermittent power)
############################################################################
# --- SINGLE LAYER ----
def est_cost_layer_intpow(layer, params_exec, params_pres, plat_settings, plat_cost_profile):     
    layer_type = layer['type']            
    R = layer['OFM'].h; C = layer['OFM'].w; M = layer['OFM'].ch; N = layer['IFM'].ch    
    H = layer['IFM'].h; W = layer['IFM'].w
    inter_lo = params_exec['inter_lo']
    S = params_pres['backup_batch_size']
    Kh, Kw, Tri, Tci, Tr, Tc, Tm, Tn = params_exec['tile_size']
    npc, npc_n0, npc_ngt0 = common._num_pow_cycles(H, W, R, C, M, N, Tr, Tc, Tm, Tn, S, inter_lo, layer_type = layer['type'])

    # get per power cycle energy and latency        
    if layer_type == "CONV":        
        if (common.check_conv(layer)):
            Epc_max, Lpc_max, Epc_min, Lpc_min = est_cost_CONV_powcycle_intpow(params_exec, params_pres, plat_settings, plat_cost_profile)                
        else:
            sys.exit(inspect.currentframe().f_code.co_name+"::Error - CONV dimensions incorrect") 

    elif (layer_type == "POOL") or (layer_type == "GAVGPOOL"):
        if (common.check_pool(layer)):
            Epc_min, Lpc_min = est_cost_POOL_powcycle_intpow(params_exec, params_pres, plat_settings, plat_cost_profile)  
            Epc_max=Epc_min; Lpc_max=Lpc_min
        else:
            sys.exit(inspect.currentframe().f_code.co_name+"::Error - POOL dimensions incorrect") 

    elif layer_type == "FC":
        if (common.check_fc(layer)):
            Epc_max, Lpc_max, Epc_min, Lpc_min = est_cost_CONV_powcycle_intpow(params_exec, params_pres, plat_settings, plat_cost_profile)  
        else:
            sys.exit(inspect.currentframe().f_code.co_name+"::Error - FC dimensions incorrect") 

    else:
        sys.exit(inspect.currentframe().f_code.co_name+"::Error - unknown layer type")

    # if no power cycle contains n>0 iterations, then Epc is same in every power cycle
    if npc_ngt0 == 0:
        Epc_max = Epc_min
        Lpc_max = Lpc_min
        
    return Epc_max, Lpc_max, Epc_min, Lpc_min


# estimate single layer E2E latency
def est_latency_e2e_layer_intpow(layer, Epc_max, Lpc_max, Epc_min, Lpc_min, plat_settings, params_exec, params_pres):
    H, W, R, C, M, N, Kh, Kw, stride, Ri, Ci =  common._get_layer_props(layer)
    Kh, Kw, Tri, Tci, Tr, Tc, Tm, Tn = params_exec['tile_size']
    inter_lo = params_exec['inter_lo']
    S = params_pres['backup_batch_size']
    Ccap=plat_settings['CCAP']; Rehm=plat_settings['REHM']; Vsup=plat_settings['VSUP']; Von=plat_settings['VON']; Voff=plat_settings['VOFF']
    safe_margin=plat_settings['EAV_SAFE_MARGIN']
    
    recharge_time_min = cal_cap_recharge_time_custom(Epc_min, Ccap, Rehm, Vsup, Von, Voff, safe_margin)
    recharge_time_max = cal_cap_recharge_time_custom(Epc_max, Ccap, Rehm, Vsup, Von, Voff, safe_margin)

    # num power cycles where loop iteration n=0 and n>0
    npc, npc_n0, npc_ngt0 = common._num_pow_cycles(H, W, R, C, M, N, Tr, Tc, Tm, Tn, S, inter_lo, layer_type = layer['type'])

    # all power on (system active) + power off (recharge durations)
    # considering that some power cycles the energy consumption and recharge duration will be lower    
    tot_latency = (npc_n0 * (Lpc_min + recharge_time_min)) + (npc_ngt0 * (Lpc_max + recharge_time_max))

    return tot_latency, npc, npc_n0, npc_ngt0, recharge_time_min, recharge_time_max



def est_npc_layer_intpow(layer, params_exec, params_pres):
    H, W, R, C, M, N, Kh, Kw, stride, Ri, Ci =  common._get_layer_props(layer)
    Kh, Kw, Tri, Tci, Tr, Tc, Tm, Tn = params_exec['tile_size']
    inter_lo = params_exec['inter_lo']
    S = params_pres['backup_batch_size']
    npc, npc_n0, npc_ngt0 = common._num_pow_cycles(H, W, R, C, M, N, Tr, Tc, Tm, Tn, S, inter_lo, layer_type = layer['type'])
    return npc, npc_n0, npc_ngt0



 # ---- NETWORK COST ----
def est_cost_alllayers_intpow(network, params_exec, params_pres, plat_settings, plat_cost_profile):
    alllayer_costs = []
    for each_layer in network:
        layer_type = each_layer['type']
        layer_name = each_layer['name']

        Epc_max, Lpc_max, Epc_min, Lpc_min = est_cost_layer_intpow(each_layer, params_exec, params_pres, plat_settings, plat_cost_profile)
        alllayer_costs.append([layer_name, layer_type, Epc_max, Lpc_max, Epc_min, Lpc_min])

    return alllayer_costs

# VM <-> NVM access cost for the layer        
def est_data_access_layer_intpow(layer, params_exec, params_pres, plat_settings, plat_cost_profile, all_pc=True):
    layer_type = layer['type']            
    R = layer['OFM'].h; C = layer['OFM'].w; M = layer['OFM'].ch; N = layer['IFM'].ch    
    H = layer['IFM'].h; W = layer['IFM'].w
    inter_lo = params_exec['inter_lo']
    S = params_pres['backup_batch_size']
    Kh, Kw, Tri, Tci, Tr, Tc, Tm, Tn = params_exec['tile_size']

    npc, npc_n0, npc_ngt0 = common._num_pow_cycles(H, W, R, C, M, N, Tr, Tc, Tm, Tn, S, inter_lo, layer_type = layer['type'])

    # get per power cycle energy and latency        
    if layer_type == "CONV":        
        if (common.check_conv(layer)):
            E_rb, L_rb, E_fd_ngt0, L_fd_ngt0, E_fd_n0, L_fd_n0, E_fl, L_fl, E_cp, L_cp, E_bd, L_bd, E_bl, L_bl = est_cost_CONV_powcycle_intpow(params_exec, params_pres, plat_settings, plat_cost_profile, return_breakdown=True)                

            if (all_pc): # all power cycles
                total_nvm_read_cost_L = (L_fd_ngt0*npc_ngt0) + (L_fd_n0*npc_n0) + (L_fl*npc)
                total_nvm_write_cost_L = (L_bd + L_bl)*npc
                total_nvm_read_cost_E = (E_fd_ngt0*npc_ngt0) + (E_fd_n0*npc_n0) + (E_fl*npc)
                total_nvm_write_cost_E = (E_bd + E_bl)*npc          
            else:   # single power cycle
                total_nvm_read_cost_L = L_fd_ngt0 + L_fd_n0 + L_fl
                total_nvm_write_cost_L = L_bd + L_bl            
                total_nvm_read_cost_E = E_fd_ngt0 + E_fd_n0 + E_fl
                total_nvm_write_cost_E = E_bd + E_bl

        else:
            sys.exit(inspect.currentframe().f_code.co_name+"::Error - CONV dimensions incorrect") 

    elif (layer_type == "POOL") or (layer_type == "GAVGPOOL"):
        if (common.check_pool(layer)):
            E_rb, L_rb, E_fd, L_fd, E_fl, L_fl, E_cp, L_cp, E_bd, L_bd, E_bl, L_bl = est_cost_POOL_powcycle_intpow(params_exec, params_pres, plat_settings, plat_cost_profile, return_breakdown=True)              
            
            if (all_pc): # all power cycles
                total_nvm_read_cost_L = (L_fd + L_fl)*npc
                total_nvm_write_cost_L = (L_bd + L_bl)*npc
                total_nvm_read_cost_E = (E_fd + E_fl)*npc
                total_nvm_write_cost_E = (E_bd + E_bl)*npc
            else:   # single power cycle
                total_nvm_read_cost_L = L_fd + L_fl
                total_nvm_write_cost_L = L_bd + L_bl            
                total_nvm_read_cost_E = E_fd + E_fl
                total_nvm_write_cost_E = E_bd + E_bl

        else:
            sys.exit(inspect.currentframe().f_code.co_name+"::Error - POOL dimensions incorrect") 

    elif layer_type == "FC":
        if (common.check_fc(layer)):
            E_rb, L_rb, E_fd_ngt0, L_fd_ngt0, E_fd_n0, L_fd_n0, E_fl, L_fl, E_cp, L_cp, E_bd, L_bd, E_bl, L_bl = est_cost_CONV_powcycle_intpow(params_exec, params_pres, plat_settings, plat_cost_profile, return_breakdown=True)                
            
            if (all_pc): # all power cycles
                total_nvm_read_cost_L = (L_fd_ngt0*npc_ngt0) + (L_fd_n0*npc_n0) + (L_fl*npc)
                total_nvm_write_cost_L = (L_bd + L_bl)*npc
                total_nvm_read_cost_E = (E_fd_ngt0*npc_ngt0) + (E_fd_n0*npc_n0) + (E_fl*npc)
                total_nvm_write_cost_E = (E_bd + E_bl)*npc
            else:   # single power cycle
                total_nvm_read_cost_L = L_fd_ngt0 + L_fd_n0 + L_fl
                total_nvm_write_cost_L = L_bd + L_bl            
                total_nvm_read_cost_E = E_fd_ngt0 + E_fd_n0 + E_fl
                total_nvm_write_cost_E = E_bd + E_bl        


        else:
            sys.exit(inspect.currentframe().f_code.co_name+"::Error - FC dimensions incorrect") 

    else:
        sys.exit(inspect.currentframe().f_code.co_name+"::Error - unknown layer type")


    return total_nvm_read_cost_L, total_nvm_write_cost_L, total_nvm_read_cost_E, total_nvm_write_cost_E










