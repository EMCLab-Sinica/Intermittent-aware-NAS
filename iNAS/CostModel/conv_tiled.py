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
    blkI = Tn
    blkW = Tn
    blkO = Tm

    # num of transfers per buffer type
    nI = Tri * Tci
    nW = Kh * Kw * Tm
    nO = Tr * Tc

    return nI, nW, nO, blkI, blkW, blkO

def _num_datatrcmds_backup_tile_data(params_exec, dma_type='1D'):
    Kh, Kw, Tri, Tci, Tr, Tc, Tm, Tn = params_exec['tile_size']    
    # block size for each DMA transfer per buffer type    
    blkO = Tm

    # num of transfers per buffer type    
    nO = Tr * Tc

    return nO, blkO



############################################################################
# MAIN COST MODEL - CONTINUOUS POWER
############################################################################

def est_cost_CONV_contpow(layer, params_exec, plat_settings, plat_cost_profile):      
    E_fd, L_fd = est_cost_CONV_layerinputfetch_contpow(layer, params_exec, plat_cost_profile)    
    E_cp, L_cp = est_cost_CONV_layercomp_contpow(layer, params_exec, plat_cost_profile)
    E_bd, L_bd = est_cost_CONV_layeroutputbackup_contpow(layer, params_exec, plat_cost_profile) 
    
    # only considering, [fetch -> compute -> save result] per layer
    total_energy = E_fd + E_cp + E_bd
    total_latency = L_fd + L_cp + L_bd

    return total_energy, total_latency

def est_cost_CONV_reboot_contpow(plat_cost_profile):    
    total_en_cost, total_lat_cost = est_cost_CONV_reboot_intpow(plat_cost_profile) # same as intermittent power
    return total_en_cost, total_lat_cost

# get layer data input fetch energy cost (overall layer)
def est_cost_CONV_layerinputfetch_contpow(layer, params_exec, plat_cost_profile):
    total_en_cost = 0    
    total_lat_cost = 0  
       
    # execution space
    inter_lo = params_exec['inter_lo']    
    Kh, Kw, Tri, Tci, Tr, Tc, Tm, Tn = params_exec['tile_size']    
       
    # num of data transfer command invocations
    nI, nW, nO, blkI, blkW, blkO = _num_datatrcmds_fetch_tile_data(params_exec)

    H, W, R, C, M, N, Kh, Kw, stride, Ri, Ci = common._get_layer_props(layer)
    num_tiles = common._num_tiles(H, W, R, C, M, N, Tr, Tc, Tm, Tn)
    Rtr = np.ceil(R/Tr); Ctc = np.ceil(C/Tc); Mtm = np.ceil(M/Tm); Ntn = np.ceil(N/Tn)

    ngt0 = (num_tiles-(Rtr*Ctc*Mtm)) # num iterations where n>0
        
    # energy/latency cost of the transfer (for a given block size)
    er_Tn = plat_cost_profile['E_DMA_NVM_TO_VM'](Tn); lr_Tn = plat_cost_profile['L_DMA_NVM_TO_VM'](Tn)
    er_Tm = plat_cost_profile['E_DMA_NVM_TO_VM'](Tm); lr_Tm = plat_cost_profile['L_DMA_NVM_TO_VM'](Tm)
    # energy/latency overhead of each transfer
    eofI = plat_cost_profile['E_FD_I_OVHD']; lofI = plat_cost_profile['L_FD_I_OVHD']
    eofW = plat_cost_profile['E_FD_W_OVHD']; lofW = plat_cost_profile['L_FD_W_OVHD']
    
    eofO_ruI = plat_cost_profile['E_FD_O_RUI_OVHD']; lofO_ruI = plat_cost_profile['L_FD_O_RUI_OVHD']
    eofO_ruW = plat_cost_profile['E_FD_O_RUW_OVHD']; lofO_ruW = plat_cost_profile['L_FD_O_RUW_OVHD']
    eofO_ruO = plat_cost_profile['E_FD_O_RUO_OVHD']; lofO_ruO = plat_cost_profile['L_FD_O_RUO_OVHD']
    
    # -- calc energy cost depending on reuse scheme        
    if inter_lo == "reuse_I":
        total_en_cost = ((Rtr*Ctc*Ntn)*(nI*(er_Tn + eofI))) + ((num_tiles)*(nW * (er_Tn + eofW))) + (ngt0*(nO * (er_Tm + eofO_ruI)))
        total_lat_cost = ((Rtr*Ctc*Ntn)*(nI*(lr_Tn + lofI))) + ((num_tiles)*(nW * (lr_Tn + lofW))) + (ngt0*(nO * (lr_Tm + lofO_ruI)))

    elif inter_lo == "reuse_W":
        total_en_cost = ((num_tiles)*(nI*(er_Tn + eofI))) + ((Mtm*Ntn)*(nW * (er_Tn + eofW))) + (ngt0*(nO * (er_Tm + eofO_ruW)))
        total_lat_cost = ((num_tiles)*(nI*(lr_Tn + lofI))) + ((Mtm*Ntn)*(nW * (lr_Tn + lofW))) + (ngt0*(nO * (lr_Tm + lofO_ruW)))
                        
    elif inter_lo == "reuse_O":
        total_en_cost = ((num_tiles)*(nI*(er_Tn + eofI))) + ((num_tiles)*(nW * (er_Tn + eofW)))
        total_lat_cost = ((num_tiles)*(nI*(lr_Tn + lofI))) + ((num_tiles)*(nW * (lr_Tn + lofW)))
                
    else:
        sys.exit(inspect.currentframe().f_code.co_name+"::Error - unknown inter-tile order")

    return total_en_cost, total_lat_cost

# backup layer output energy cost (overall layer)
def est_cost_CONV_layeroutputbackup_contpow(layer, params_exec, plat_cost_profile):
    total_en_cost = 0    
    total_lat_cost = 0  
       
    # execution space
    inter_lo = params_exec['inter_lo']    
    Kh, Kw, Tri, Tci, Tr, Tc, Tm, Tn = params_exec['tile_size']    
       
    # num of data transfer command invocations
    nO, blkO = _num_datatrcmds_backup_tile_data(params_exec)

    H, W, R, C, M, N, Kh, Kw, stride, Ri, Ci = common._get_layer_props(layer)
    num_tiles = common._num_tiles(H, W, R, C, M, N, Tr, Tc, Tm, Tn)
    Rtr = np.ceil(R/Tr); Ctc = np.ceil(C/Tc); Mtm = np.ceil(M/Tm); Ntn = np.ceil(N/Tn)

    params_pres = {'backup_batch_size': 1} # S=1
    tile_en_cost, tile_lat_cost = est_cost_CONV_tileoutputbackup_intpow(params_exec, params_pres, plat_cost_profile) # cost for one tile # same as intermittent power, but S=1

    total_en_cost = tile_en_cost * num_tiles
    total_lat_cost = tile_lat_cost * num_tiles

    # # energy/latency cost of the transfer (for a given block size)    
    # ew_Tm = plat_cost_profile['E_DMA_VM_TO_NVM'](Tm); lw_Tm = plat_cost_profile['L_DMA_VM_TO_NVM'](Tm)
    # ew_STm = plat_cost_profile['E_DMA_VM_TO_NVM'](Tm); lw_STm = plat_cost_profile['L_DMA_VM_TO_NVM'](Tm)
    # # energy/latency overhead of each transfer    
    # eobO = plat_cost_profile['E_BD_O_OVHD']; lobO = plat_cost_profile['L_BD_O_OVHD']
        
    # # -- calc energy cost depending on reuse scheme        
    # if inter_lo == "reuse_I":
    #     total_en_cost = ((num_tiles)*(nO * (ew_Tm + eobO)))
    #     total_lat_cost = ((num_tiles)*(nO * (lw_Tm + lobO)))

    # elif inter_lo == "reuse_W":
    #     total_en_cost = ((num_tiles)*(nO * (ew_Tm + eobO)))
    #     total_lat_cost = ((num_tiles)*(nO * (lw_Tm + lobO)))
                        
    # elif inter_lo == "reuse_O":
    #     #total_en_cost = ((Rtr*Ctc*Mtm)*(nO * (ew_Tm + eobO)))   # Bout is backed up at end of n loop
    #     #total_lat_cost = ((Rtr*Ctc*Mtm)*(nO * (lw_Tm + lobO)))

    #     total_en_cost = ((num_tiles)*(nO * (ew_Tm + eobO)))   # Bout is backed up at end of n loop
    #     total_lat_cost = ((num_tiles)*(nO * (lw_Tm + lobO)))          
    # else:
    #     sys.exit(inspect.currentframe().f_code.co_name+"::Error - unknown inter-tile order")

    return total_en_cost, total_lat_cost


def est_cost_CONV_layercomp_contpow(layer, params_exec, plat_cost_profile):    
    Kh, Kw, Tri, Tci, Tr, Tc, Tm, Tn = params_exec['tile_size']    
    H, W, R, C, M, N, Kh, Kw, stride, Ri, Ci = common._get_layer_props(layer)
    num_tiles = common._num_tiles(H, W, R, C, M, N, Tr, Tc, Tm, Tn)
    
    params_pres = {'backup_batch_size': 1} # S=1
    tile_en_cost, tile_lat_cost = est_cost_CONV_tilecomp_intpow(params_exec, params_pres, plat_cost_profile) # cost for one tile # same as intermittent power, but S=1
    
    total_en_cost = tile_en_cost * num_tiles
    total_lat_cost = tile_lat_cost * num_tiles

    return total_en_cost, total_lat_cost




############################################################################
# MAIN COST MODEL - INTERMITTENT POWER (per power cycle)
############################################################################
# get estimated total energy consumption in a power cycle
def est_cost_CONV_powcycle_intpow(params_exec, params_pres, plat_settings, plat_cost_profile, exclude_rb_cost=False, return_breakdown=False):        
    E_rb, L_rb = est_cost_CONV_reboot_intpow(plat_cost_profile)
    E_fd_ngt0, L_fd_ngt0, E_fd_n0, L_fd_n0 = est_cost_CONV_tileinputfetch_intpow(params_exec, params_pres, plat_cost_profile)
    E_fl, L_fl = est_cost_CONV_tileidxfetch_intpow(plat_cost_profile)
    E_cp, L_cp = est_cost_CONV_tilecomp_intpow(params_exec, params_pres, plat_cost_profile)
    E_bd, L_bd = est_cost_CONV_tileoutputbackup_intpow(params_exec, params_pres, plat_cost_profile)
    E_bl, L_bl = est_cost_CONV_tileidxbackup_intpow(plat_cost_profile)

    total_energy_powcycle_ngt0 = E_rb + E_fd_ngt0 + E_fl + E_cp + E_bd + E_bl
    total_latency_powcycle_ngt0 = L_rb + L_fd_ngt0 + L_fl + L_cp + L_bd + L_bl

    total_energy_powcycle_n0 = E_rb + E_fd_n0 + E_fl + E_cp + E_bd + E_bl
    total_latency_powcycle_n0 = L_rb + L_fd_n0 + L_fl + L_cp + L_bd + L_bl

    if (return_breakdown == False):
        return total_energy_powcycle_ngt0, total_latency_powcycle_ngt0, total_energy_powcycle_n0, total_latency_powcycle_n0
    else:
        return E_rb, L_rb, E_fd_ngt0, L_fd_ngt0, E_fd_n0, L_fd_n0, E_fl, L_fl, E_cp, L_cp, E_bd, L_bd, E_bl, L_bl
    

# get reboot energy cost
def est_cost_CONV_reboot_intpow(plat_cost_profile):
    total_en_cost = plat_cost_profile['E_RB']
    total_lat_cost = plat_cost_profile['L_RB']
    return total_en_cost, total_lat_cost


# get tile data input fetch energy cost per power cycle
def est_cost_CONV_tileinputfetch_intpow(params_exec, params_pres, plat_cost_profile):
    total_en_cost_ngt0 = 0    
    total_lat_cost_ngt0 = 0  
    total_en_cost_n0 = 0    
    total_lat_cost_n0 = 0    

    # execution space
    inter_lo = params_exec['inter_lo']    
    Kh, Kw, Tri, Tci, Tr, Tc, Tm, Tn = params_exec['tile_size']    
    # preservation space   
    S = params_pres['backup_batch_size']
   
    # num of data transfer command invocations
    nI, nW, nO, blkI, blkW, blkO = _num_datatrcmds_fetch_tile_data(params_exec)
    #print(nI, nW, nO, blkI, blkW, blkO)
    
    # energy/latency cost of the transfer (for a given block size)
    er_Tn = plat_cost_profile['E_DMA_NVM_TO_VM'](Tn); lr_Tn = plat_cost_profile['L_DMA_NVM_TO_VM'](Tn)
    er_Tm = plat_cost_profile['E_DMA_NVM_TO_VM'](Tm); lr_Tm = plat_cost_profile['L_DMA_NVM_TO_VM'](Tm)
    # energy/latency overhead of each transfer
    eofI = plat_cost_profile['E_FD_I_OVHD']; lofI = plat_cost_profile['L_FD_I_OVHD']
    eofW = plat_cost_profile['E_FD_W_OVHD']; lofW = plat_cost_profile['L_FD_W_OVHD']    
    eofO_ruI = plat_cost_profile['E_FD_O_RUI_OVHD']; lofO_ruI = plat_cost_profile['L_FD_O_RUI_OVHD']
    eofO_ruW = plat_cost_profile['E_FD_O_RUW_OVHD']; lofO_ruW = plat_cost_profile['L_FD_O_RUW_OVHD']
    eofO_ruO = plat_cost_profile['E_FD_O_RUO_OVHD']; lofO_ruO = plat_cost_profile['L_FD_O_RUO_OVHD']    

    # -- calc energy cost depending on reuse scheme        
    if inter_lo == "reuse_I":
        total_en_cost_ngt0 = (S * ((nW * (er_Tn + eofW)) + (nO * (er_Tm + eofO_ruI)))) + (nI*(er_Tn + eofI))
        total_lat_cost_ngt0 = (S * ((nW * (lr_Tn + lofW)) + (nO * (lr_Tm + lofO_ruI)))) + (nI*(lr_Tn + lofI))
        total_en_cost_n0 = (S * ((nW * (er_Tn + eofW)))) + (nI*(er_Tn + eofI))
        total_lat_cost_n0 = (S * ((nW * (lr_Tn + lofW)))) + (nI*(lr_Tn + lofI))

    elif inter_lo == "reuse_W":
        total_en_cost_ngt0 = (S * ((nI * (er_Tn + eofI)) + (nO * (er_Tm + eofO_ruW)))) + (nW*(er_Tn + eofW))
        total_lat_cost_ngt0 = (S * ((nI * (lr_Tn + lofI)) + (nO * (lr_Tm + lofO_ruW)))) + (nW*(lr_Tn + lofW))
        total_en_cost_n0 = (S * (nI * (er_Tn + eofI)) ) + (nW*(er_Tn + eofW))
        total_lat_cost_n0 = (S * (nI * (lr_Tn + lofI)) ) + (nW*(lr_Tn + lofW))
        
    elif inter_lo == "reuse_O":
        total_en_cost_ngt0 = (S * ((nI * (er_Tn + eofI)) + (nW * (er_Tn + eofW)))) + (nO*(er_Tm + eofO_ruO))
        total_lat_cost_ngt0 = (S * ((nI * (lr_Tn + lofI)) + (nW * (lr_Tn + lofW)))) + (nO*(lr_Tm + lofO_ruO))
        total_en_cost_n0 = (S * ((nI * (er_Tn + eofI)) + (nW * (er_Tn + eofW))))
        total_lat_cost_n0 = (S * ((nI * (lr_Tn + lofI)) + (nW * (lr_Tn + lofW))))
        
    else:
        sys.exit(inspect.currentframe().f_code.co_name+"::Error - unknown inter-tile order")

    #print(inter_lo, total_en_cost_ngt0)
    #input()
    
    return total_en_cost_ngt0, total_lat_cost_ngt0, total_en_cost_n0, total_lat_cost_n0


# get tile data output backup energy cost per power cycle
def est_cost_CONV_tileoutputbackup_intpow(params_exec, params_pres, plat_cost_profile):
    total_en_cost = 0    
    total_lat_cost = 0    

    # execution space
    inter_lo = params_exec['inter_lo']    
    Kh, Kw, Tri, Tci, Tr, Tc, Tm, Tn = params_exec['tile_size']    
    # preservation space   
    S = params_pres['backup_batch_size']
   
    # num of data transfer command invocations
    #nO, blkO = _num_datatrcmds_backup_tile_data(params_exec)
    # energy/latency cost of the transfer (for a given block size)    
    ew_Tm = plat_cost_profile['E_DMA_VM_TO_NVM'](Tm); lw_Tm = plat_cost_profile['L_DMA_VM_TO_NVM'](Tm)
    ew_STm = plat_cost_profile['E_DMA_VM_TO_NVM'](S*Tm); lw_STm = plat_cost_profile['L_DMA_VM_TO_NVM'](S*Tm)
    # energy/latency overhead of each transfer    
    eobO_ruI = plat_cost_profile['E_BD_O_RUI_OVHD']; lobO_ruI = plat_cost_profile['L_BD_O_RUI_OVHD']
    eobO_ruW = plat_cost_profile['E_BD_O_RUW_OVHD']; lobO_ruW = plat_cost_profile['L_BD_O_RUW_OVHD']
    eobO_ruO = plat_cost_profile['E_BD_O_RUO_OVHD']; lobO_ruO = plat_cost_profile['L_BD_O_RUO_OVHD']

    # -- calc energy cost depending on reuse scheme        
    if (inter_lo == "reuse_I"):
        total_en_cost = Tr * Tc * (ew_STm + eobO_ruI) 
        total_lat_cost = Tr * Tc * (lw_STm + lobO_ruI)
    elif (inter_lo == "reuse_W"):
        total_en_cost = S * Tr * Tc * (ew_Tm + eobO_ruW) 
        total_lat_cost = S * Tr * Tc * (lw_Tm + lobO_ruW) 
    elif inter_lo == "reuse_O":
        total_en_cost = Tr * Tc * (ew_Tm + eobO_ruO) 
        total_lat_cost = Tr * Tc * (lw_Tm + lobO_ruO) 
    else:
        sys.exit(inspect.currentframe().f_code.co_name+"::Error - unknown inter-tile order")
    
    return total_en_cost, total_lat_cost


def est_cost_CONV_tilecomp_intpow(params_exec, params_pres, plat_cost_profile):
    total_en_cost = 0    
    total_lat_cost = 0

    # execution space
    inter_lo = params_exec['inter_lo']    
    Kh, Kw, Tri, Tci, Tr, Tc, Tm, Tn = params_exec['tile_size']    
    # preservation space   
    S = params_pres['backup_batch_size']
   
    evmac = plat_cost_profile['E_OP_VECMAC'](Tn)
    eadd = plat_cost_profile['E_ADD']
    ecomp_ovh = plat_cost_profile['E_OP_PSUM_OVHD'] + plat_cost_profile['E_OP_ACUM_OVHD'] # addressing overhead

    lvmac = plat_cost_profile['L_OP_VECMAC'](Tn)
    ladd = plat_cost_profile['L_ADD']
    lcomp_ovh = plat_cost_profile['L_OP_PSUM_OVHD'] + plat_cost_profile['L_OP_ACUM_OVHD'] # addressing overhead

    total_en_cost = S * Kh * Kw * Tr * Tc * Tm * (evmac + eadd + ecomp_ovh)
    total_lat_cost = S * Kh * Kw * Tr * Tc * Tm * (lvmac + ladd + lcomp_ovh)

    return total_en_cost, total_lat_cost

# cost of fetch inter tile indices
def est_cost_CONV_tileidxfetch_intpow(plat_cost_profile):
    total_en_cost = plat_cost_profile['E_DMA_NVM_TO_VM'](4)
    total_lat_cost = plat_cost_profile['L_DMA_NVM_TO_VM'](4)
    return total_en_cost, total_lat_cost


# cost of backup inter tile indices
def est_cost_CONV_tileidxbackup_intpow(plat_cost_profile):
    total_en_cost = plat_cost_profile['E_DMA_VM_TO_NVM'](4)
    total_lat_cost = plat_cost_profile['L_DMA_VM_TO_NVM'](4)
    return total_en_cost, total_lat_cost












    

















