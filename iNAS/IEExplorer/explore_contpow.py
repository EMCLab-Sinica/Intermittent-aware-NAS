import sys, os
from pprint import pprint
import numpy as np
from time import perf_counter 
import inspect
import warnings


# local import
import CostModel.cnn as cnn
import CostModel.common as common 
from CostModel.capacitor import cap_energy, cal_cap_recharge_time_custom
from DNNDumper.cnn_types import Mat
from DNNDumper.file_utils import json_dump, json_load





# Hardware-aware Design Space Explorer
# exploring : 
# - Execution Design Space (tile sizes: Tr Tc Tm Tn, loop order)
def explore_full_param_sweep_contpow(layer, plat_settings, plat_cost_profile, report_topN=0.5, best_selection='first'):
    
    R = layer['OFM'].h; C = layer['OFM'].w; M = layer['OFM'].ch; N = layer['IFM'].ch
    H = layer['IFM'].h; W = layer['IFM'].w
    Kh = layer['K'].h; Kw = layer['K'].w
    stride = layer['stride']

    # get search space
    tr_lst, tc_lst, tm_lst, tn_lst = common.filter_legal_tilesizes(None, None, None, None, H, W, R, C, M, N, layer_type = layer['type'])
    inter_tile_order = common.filter_legal_reuseschems(layer_type = layer['type'])
    #pprint(tr_lst); pprint(tc_lst); pprint(tm_lst); pprint(tn_lst)
    #sys.exit()

    result_pass = []
    result_fail = []    
    search_space_size = 0

    # -- all tile size permutations
    for Tr in tr_lst:
        for Tc in tc_lst:
            Tri, Tci = common._calc_conv_ifm_tile_size(Tr, Tc, Kh, Kw)
            for Tm in tm_lst:
                for Tn in tn_lst:

                    # -- all loop orders
                    for inter_lo in inter_tile_order:                        
                        #print (R, C, M, N, Tr, Tc, Tm, Tn, inter_lo)
                        
                            search_space_size+=1

                            # -- check if passes the initial constraints ?                                                        
                            params_exec = {'tile_size': [Kh, Kw, Tri, Tci, Tr, Tc, Tm, Tn], 'inter_lo': inter_lo}
                            params_pres = {'backup_batch_size': 1} # using S=1 for constant power
                                                      
                            res_cons_c0 = cnn.pass_constraint_spatial(layer, plat_settings, params_exec, params_pres); common.check_infnan(res_cons_c0)  
                            npc, npc_n0, npc_ngt0 = cnn.est_npc_layer_intpow(layer, params_exec, params_pres) # estmate the number of power cycles

                            if (res_cons_c0[0]):
                                lay_E, lay_L = cnn.est_cost_layer_contpow(layer, params_exec, plat_settings, plat_cost_profile); common.check_infnan([lay_E, lay_L])      
                                #rb_E, rb_L = cnn.est_cost_onetime_reboot() # one time reboot cost (only once per network model) 
                                
                                result_pass.append({
                                        'params' : common.to_string_params_all(params_exec, params_pres),                                                                                
                                        'Epc': [lay_E, lay_E], 'Le2e': lay_L, 
                                        'Lpc': [None, None], 'Lrc': [None, None], 'Eu' : None, 'npc' : [npc, npc_n0, npc_ngt0],
                                        'vm' : res_cons_c0[2]
                                })

                            else:
                                result_fail.append({
                                    'params' : common.to_string_params_all(params_exec, None),                                                                                
                                    'reason': 'FAILED_C0',
                                    'Epc': [lay_E, lay_E], 'Le2e': lay_L,
                                    'npc' : [npc, npc_n0, npc_ngt0],                                                            
                                    'vm' : res_cons_c0[2]
                                })                              
                                
    
    #print("Layer [%s] eval. complete. PASS= %d/%d = %.1f" % (layer['name'], len(result_pass), search_space_size, (len(result_pass)/search_space_size)*100.0 ))

    if (len(result_pass) > 0):
        # -- find best solution (lowest latency)  
        min_lat = np.min([r['Le2e'] for r in result_pass])
        all_best_sols = [r for r in result_pass if r['Le2e'] == min_lat]
        best_solution = sorted(all_best_sols, key = lambda i: i['vm'])

        sorted_result_pass = sorted(result_pass, key = lambda i: i['Le2e'])
        
        # top N% solutions
        nperc = report_topN
        nnum = int(np.ceil(nperc* len(sorted_result_pass)))
        pass_topN = sorted_result_pass[0:nnum]

        # sort and save the top N% failed solutions    
        sorted_results_fail_c0 = sorted([f for f in result_fail if f['reason'] == 'FAILED_C0'], key = lambda i: i['vm'])
        nnum = int(np.ceil(nperc * len(sorted_results_fail_c0)))
        sorted_results_fail_c0 = sorted_results_fail_c0[0:nnum]
        sorted_results_fail_c1 = []

        return best_solution, result_pass, sorted_results_fail_c0, sorted_results_fail_c1, pass_topN
    
    else:

        warnings.warn("WARNING: Layer [%s] - unable to find a solution" % (layer['name']))
        best_solution = None
        result_pass = []
        sorted_results_fail_c0 = []
        sorted_results_fail_c1 = []
        pass_topN = []
        
        return best_solution, result_pass, sorted_results_fail_c0, sorted_results_fail_c1, pass_topN


