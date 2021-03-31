import sys, os
from pprint import pprint
import numpy as np
from time import perf_counter 
import inspect


# local imports
from CostModel import common



############################################################################
# HELPERS
############################################################################

# assuming a 1D DMA transfer (non-strided)
def _num_datatrcmds_fetch_tile_data(params_exec, dma_type='1D'):
    Kh, Kw, Tri, Tci, Tr, Tc, Tm, Tn = params_exec['tile_size']    
    # block size for each DMA transfer per buffer type
    blkI = Tm    
    blkO = Tm
    # num of transfers per buffer type
    nI = Tri * Tci    
    nO = 1 * 1    
    return nI, nO, blkI, blkO

def _num_datatrcmds_backup_tile_data(params_exec, dma_type='1D'):
    Kh, Kw, Tri, Tci, Tr, Tc, Tm, Tn = params_exec['tile_size']    
    # block size for each DMA transfer per buffer type    
    blkO = Tm
    # num of transfers per buffer type    
    nO = 1 * 1
    return nO, blkO




############################################################################
# MAIN COST MODEL - CONTINUOUS POWER
############################################################################
# get estimated total energy consumption in a power cycle
def est_cost_POOL_contpow(layer, params_exec, plat_settings, plat_cost_profile):        
    E_fd, L_fd = est_cost_POOL_layerinputfetch_contpow(layer, params_exec, plat_cost_profile)    
    E_cp, L_cp = est_cost_POOL_layercomp_contpow(layer, params_exec, plat_cost_profile)
    E_bd, L_bd = est_cost_POOL_layeroutputbackup_contpow(layer, params_exec, plat_cost_profile)
        
    total_energy = E_fd + E_cp + E_bd
    total_latency = L_fd + L_cp + L_bd

    return total_energy, total_latency

# get reboot energy cost
def est_cost_POOL_reboot_contpow(plat_cost_profile):
    total_en_cost, total_lat_cost = est_cost_POOL_reboot_intpow(plat_cost_profile)    
    return total_en_cost, total_lat_cost


# get layer data input fetch energy cost (overall layer)
def est_cost_POOL_layerinputfetch_contpow(layer, params_exec, plat_cost_profile):
    total_en_cost = 0    
    total_lat_cost = 0  
    
    # execution space    
    Kh, Kw, Tri, Tci, Tr, Tc, Tm, Tn = params_exec['tile_size']        
   
    # num of data transfer command invocations
    nI, nO, blkI, blkO = _num_datatrcmds_fetch_tile_data(params_exec)
        
    # energy/latency cost of the transfer (for a given block size)
    er_Tm = plat_cost_profile['E_DMA_NVM_TO_VM'](Tm); lr_Tm = plat_cost_profile['L_DMA_NVM_TO_VM'](Tm)    
    # energy/latency overhead of each transfer
    eofI = plat_cost_profile['E_FD_I_OVHD']; lofI = plat_cost_profile['L_FD_I_OVHD']    
    eofO = plat_cost_profile['E_FD_O_RUO_OVHD']; lofO = plat_cost_profile['L_FD_O_RUO_OVHD']    

    # -- calc energy cost (no reuse schemes)
    tile_en_cost = (nI*(er_Tm + eofI)) + (nO*(er_Tm + eofO))
    tile_lat_cost = (nI*(lr_Tm + lofI)) + (nO*(lr_Tm + lofO))
    
    H, W, R, C, M, N, Kh, Kw, stride, Ri, Ci = common._get_layer_props(layer)
    num_tiles = common._num_tiles(H, W, R, C, M, N, Tr, Tc, Tm, Tn, layer_type=layer['type'])

    total_en_cost = num_tiles * tile_en_cost
    total_lat_cost = num_tiles * tile_lat_cost
    
    return total_en_cost, total_lat_cost



# backup layer output energy cost (overall layer)
def est_cost_POOL_layeroutputbackup_contpow(layer, params_exec, plat_cost_profile):
    total_en_cost = 0    
    total_lat_cost = 0    

    # execution space
    inter_lo = params_exec['inter_lo']    
    Kh, Kw, Tri, Tci, Tr, Tc, Tm, Tn = params_exec['tile_size']    
          
    # num of data transfer command invocations
    nO, blkO = _num_datatrcmds_backup_tile_data(params_exec)
    # energy/latency cost of the transfer (for a given block size)        
    ew_Tm = plat_cost_profile['E_DMA_VM_TO_NVM'](Tm); lw_Tm = plat_cost_profile['L_DMA_VM_TO_NVM'](Tm)
    # energy/latency overhead of each transfer    
    eobO = plat_cost_profile['E_BD_O_RUO_OVHD']; lobO = plat_cost_profile['L_BD_O_RUO_OVHD']
    
    # -- calc energy cost depending on reuse scheme            
    tile_en_cost = nO * (ew_Tm + eobO) 
    tile_lat_cost = nO * (lw_Tm + lobO) 

    H, W, R, C, M, N, Kh, Kw, stride, Ri, Ci = common._get_layer_props(layer)
    num_tiles = common._num_tiles(H, W, R, C, M, N, Tr, Tc, Tm, Tn, layer_type=layer['type'])

    total_en_cost = num_tiles * tile_en_cost
    total_lat_cost = num_tiles * tile_lat_cost    
        
    return total_en_cost, total_lat_cost


def est_cost_POOL_layercomp_contpow(layer, params_exec, plat_cost_profile):
    total_en_cost = 0    
    total_lat_cost = 0

    # execution space
    inter_lo = params_exec['inter_lo']    
    Kh, Kw, Tri, Tci, Tr, Tc, Tm, Tn = params_exec['tile_size']        
   
    emaxcomp = plat_cost_profile['E_OP_MAXCOMPARE']    
    emaxcomp_ovh = plat_cost_profile['E_OP_MAX_OVHD'] # addressing overhead
    lmaxcomp = plat_cost_profile['L_OP_MAXCOMPARE']    
    lmaxcomp_ovh = plat_cost_profile['L_OP_MAX_OVHD'] # addressing overhead

    # tile_en_cost = Kh * Kw * Tr * Tc * Tm * (emaxcomp + emaxcomp_ovh)
    # tile_lat_cost = Kh * Kw * Tr * Tc * Tm * (lmaxcomp + lmaxcomp_ovh)
    tile_en_cost = Tr * Tc * Tm * (emaxcomp + emaxcomp_ovh)
    tile_lat_cost = Tr * Tc * Tm * (lmaxcomp + lmaxcomp_ovh)    

    H, W, R, C, M, N, Kh, Kw, stride, Ri, Ci = common._get_layer_props(layer)
    num_tiles = common._num_tiles(H, W, R, C, M, N, Tr, Tc, Tm, Tn, layer_type=layer['type'])

    total_en_cost = num_tiles * tile_en_cost
    total_lat_cost = num_tiles * tile_lat_cost

    return total_en_cost, total_lat_cost




############################################################################
# MAIN COST MODEL - INTERMITTENT POWER (per power cycle)
############################################################################
# get estimated total energy consumption in a power cycle
def est_cost_POOL_powcycle_intpow(params_exec, params_pres, plat_settings, plat_cost_profile, return_breakdown=False):    
    E_rb, L_rb = est_cost_POOL_reboot_intpow(plat_cost_profile)
    E_fd, L_fd = est_cost_POOL_tileinputfetch_intpow(params_exec, params_pres, plat_cost_profile)
    E_fl, L_fl = est_cost_POOL_tileidxfetch_intpow(plat_cost_profile)
    E_cp, L_cp = est_cost_POOL_tilecomp_intpow(params_exec, params_pres, plat_cost_profile)
    E_bd, L_bd = est_cost_POOL_tileoutputbackup_intpow(params_exec, params_pres, plat_cost_profile)
    E_bl, L_bl = est_cost_POOL_tileidxbackup_intpow(plat_cost_profile)

    total_energy_powcycle = E_rb + E_fd + E_fl + E_cp + E_bd + E_bl
    total_latency_powcycle = L_rb + L_fd + L_fl + L_cp + L_bd + L_bl
    
    if (return_breakdown==False):
        return total_energy_powcycle, total_latency_powcycle
    else:
        return E_rb, L_rb, E_fd, L_fd, E_fl, L_fl, E_cp, L_cp, E_bd, L_bd, E_bl, L_bl


# get reboot energy cost
def est_cost_POOL_reboot_intpow(plat_cost_profile):
    total_en_cost = plat_cost_profile['E_RB']
    total_lat_cost = plat_cost_profile['L_RB']
    return total_en_cost, total_lat_cost


# get tile data input fetch energy cost per power cycle
def est_cost_POOL_tileinputfetch_intpow(params_exec, params_pres, plat_cost_profile):
    total_en_cost = 0    
    total_lat_cost = 0  
    
    # execution space    
    Kh, Kw, Tri, Tci, Tr, Tc, Tm, Tn = params_exec['tile_size']    
    # preservation space   
    S = params_pres['backup_batch_size']
   
    # num of data transfer command invocations
    nI, nO, blkI, blkO = _num_datatrcmds_fetch_tile_data(params_exec)
        
    # energy/latency cost of the transfer (for a given block size)
    er_Tm = plat_cost_profile['E_DMA_NVM_TO_VM'](Tm); lr_Tm = plat_cost_profile['L_DMA_NVM_TO_VM'](Tm)    
    # energy/latency overhead of each transfer
    eofI = plat_cost_profile['E_FD_I_OVHD']; lofI = plat_cost_profile['L_FD_I_OVHD']    
    eofO = plat_cost_profile['E_FD_O_RUO_OVHD']; lofO = plat_cost_profile['L_FD_O_RUO_OVHD']    

    # -- calc energy cost (no reuse schemes)
    total_en_cost = (S * (nI*(er_Tm + eofI))) + (nO*(er_Tm + eofO))
    total_lat_cost = (S * (nI*(lr_Tm + lofI))) + (nO*(lr_Tm + lofO))
    
    return total_en_cost, total_lat_cost

# get tile data output backup energy cost per power cycle
def est_cost_POOL_tileoutputbackup_intpow(params_exec, params_pres, plat_cost_profile):
    total_en_cost = 0    
    total_lat_cost = 0    

    # execution space
    inter_lo = params_exec['inter_lo']    
    Kh, Kw, Tri, Tci, Tr, Tc, Tm, Tn = params_exec['tile_size']    
    # preservation space   
    S = params_pres['backup_batch_size']
   
    # num of data transfer command invocations
    nO, blkO = _num_datatrcmds_backup_tile_data(params_exec)
    # energy/latency cost of the transfer (for a given block size)        
    ew_Tm = plat_cost_profile['E_DMA_VM_TO_NVM'](Tm); lw_Tm = plat_cost_profile['L_DMA_VM_TO_NVM'](Tm)  # preservation batch size in the Tr, Tc direction, so output buffer is overwritten
    # energy/latency overhead of each transfer    
    eobO = plat_cost_profile['E_BD_O_RUO_OVHD']; lobO = plat_cost_profile['L_BD_O_RUO_OVHD']
    
    # -- calc energy cost depending on reuse scheme            
    total_en_cost = nO * (ew_Tm + eobO) 
    total_lat_cost = nO * (lw_Tm + lobO) 
        
    return total_en_cost, total_lat_cost


def est_cost_POOL_tilecomp_intpow(params_exec, params_pres, plat_cost_profile):
    total_en_cost = 0    
    total_lat_cost = 0

    # execution space
    inter_lo = params_exec['inter_lo']    
    Kh, Kw, Tri, Tci, Tr, Tc, Tm, Tn = params_exec['tile_size']    
    # preservation space   
    S = params_pres['backup_batch_size']
   
    emaxcomp = plat_cost_profile['E_OP_MAXCOMPARE']    
    emaxcomp_ovh = plat_cost_profile['E_OP_MAX_OVHD'] # addressing overhead
    lmaxcomp = plat_cost_profile['L_OP_MAXCOMPARE']    
    lmaxcomp_ovh = plat_cost_profile['L_OP_MAX_OVHD'] # addressing overhead

    #total_en_cost = S * Kh * Kw * Tr * Tc * Tm * (emaxcomp + emaxcomp_ovh)
    #total_lat_cost = S * Kh * Kw * Tr * Tc * Tm * (lmaxcomp + lmaxcomp_ovh)

    total_en_cost = S * Tr * Tc * Tm * (emaxcomp + emaxcomp_ovh)
    total_lat_cost = S * Tr * Tc * Tm * (lmaxcomp + lmaxcomp_ovh)    

    return total_en_cost, total_lat_cost

# cost of fetch inter tile indices
def est_cost_POOL_tileidxfetch_intpow(plat_cost_profile):
    total_en_cost = plat_cost_profile['E_DMA_NVM_TO_VM'](4) # fetch 4 but use only 3?
    total_lat_cost = plat_cost_profile['L_DMA_NVM_TO_VM'](4)
    return total_en_cost, total_lat_cost

# cost of backup inter tile indices
def est_cost_POOL_tileidxbackup_intpow(plat_cost_profile):
    total_en_cost = plat_cost_profile['E_DMA_VM_TO_NVM'](4) # backup 4 but use only 3?
    total_lat_cost = plat_cost_profile['L_DMA_VM_TO_NVM'](4)
    return total_en_cost, total_lat_cost












    

















