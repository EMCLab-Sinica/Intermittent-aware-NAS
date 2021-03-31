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



# get end-to-end latency for a specific fixed param
def get_le2e_fixed_params_intpow(layer, params_exec, params_pres, plat_settings, plat_cost_profile):
    result = {}
    res_cons_c0 = cnn.pass_constraint_spatial(layer, plat_settings, params_exec, params_pres)
    if (res_cons_c0[0]):
        Epc_max, Lpc_max, Epc_min, Lpc_min = cnn.est_cost_layer_intpow(layer, params_exec, params_pres, plat_settings, plat_cost_profile)
                                        
        res_cons_c1 = cnn.pass_constraint_atomicity(Epc_max, plat_settings)
        Eav = res_cons_c1[1]

        if (res_cons_c1[0]):
            L_e2e, npc, npc_n0, npc_ngt0, L_rc_min, L_rc_max = cnn.est_latency_e2e_layer_intpow(layer, Epc_max, Lpc_max, Epc_min, Lpc_min, plat_settings, params_exec, params_pres)
            result = {
                'params' : common.to_string_params_all(params_exec, params_pres),                                                                                
                'Epc': [Epc_max, Epc_min], 'Le2e': L_e2e, 'Lpc': [Lpc_max, Lpc_min], 'Lrc': [L_rc_min, L_rc_max],
                'Eu' : (Epc_max / Eav) * 100.0,
                'npc' : [npc, npc_n0, npc_ngt0],
                'vm' : res_cons_c0[2]
            }
            #print(result['Lpc'], result['Lrc'])
        else:
            npc, npc_n0, npc_ngt0 = cnn.est_npc_layer_intpow(layer, params_exec, params_pres)
            result = {
                'params' : common.to_string_params_all(params_exec, params_pres),                                        
                'reason': 'FAILED_C1',
                'Epc': [Epc_max, Epc_min], 'Le2e': None, 'Lpc': [None, None],
                'Eu' : (Epc_max / Eav) * 100.0, 'Eav' : Eav,
                'npc' : [npc, npc_n0, npc_ngt0],
                'vm' : res_cons_c0[2]
            }
    else:
        result = {
                'params' : common.to_string_params_all(params_exec, params_pres),                                        
                'reason': 'FAILED_C0',
                'Epc': [None, None], 'Le2e': None, 'Lpc': [None, None],
                'npc' : [None, None, None],
                'vm' : res_cons_c0[2]
            }

    return result



# Intermittent-aware Design Space Explorer
# exploring : 
# - Execution Design Space (tile sizes: Tr Tc Tm Tn, loop order)
# - Preservation Design Space (preservation batch size :S)

def explore_full_param_sweep_intpow(layer, plat_settings, plat_cost_profile, report_topN=0.5, best_selection='first'):
    
    R = layer['OFM'].h; C = layer['OFM'].w; M = layer['OFM'].ch; N = layer['IFM'].ch
    H = layer['IFM'].h; W = layer['IFM'].w
    Kh = layer['K'].h; Kw = layer['K'].w
    stride = layer['stride']

    # get search space
    tr_lst, tc_lst, tm_lst, tn_lst = common.filter_legal_tilesizes(None, None, None, None, H, W, R, C, M, N, layer_type = layer['type'])
    inter_tile_order = common.filter_legal_reuseschems(layer_type = layer['type'])
    
    #pprint(layer)
    #pprint(tr_lst); pprint(tc_lst); pprint(tm_lst); pprint(tn_lst)
    
    result_pass = []
    result_fail = []    
    search_space_size = 0

    # -- all tile size permutations
    for Tr in tr_lst:
        for Tc in tc_lst:
            Tri, Tci = common._calc_conv_ifm_tile_size(Tr, Tc, Kh, Kw, layer_type = layer['type'])
            for Tm in tm_lst:
                for Tn in tn_lst:

                    # -- all loop orders
                    for inter_lo in inter_tile_order:
                        
                        S_lst = common.filter_legal_pressizes(None, H, W, R, C, M, N, Tr, Tc, Tm, Tn, inter_lo, layer_type = layer['type'])
                        #print (R, C, M, N, Tr, Tc, Tm, Tn, inter_lo, S_lst)

                        # -- all S values
                        for S in S_lst:
                            search_space_size+=1

                            # -- check if passes the initial constraints ?                                                        
                            params_exec = {'tile_size': [Kh, Kw, Tri, Tci, Tr, Tc, Tm, Tn], 'inter_lo': inter_lo}
                            params_pres = {'backup_batch_size': S}
                                                      
                            res_cons_c0 = cnn.pass_constraint_spatial(layer, plat_settings, params_exec, params_pres); common.check_infnan(res_cons_c0)
                            
                            if (res_cons_c0[0]):

                                Epc_max, Lpc_max, Epc_min, Lpc_min = cnn.est_cost_layer_intpow(layer, params_exec, params_pres, plat_settings, plat_cost_profile)
                                common.check_infnan([Epc_max, Lpc_max, Epc_min, Lpc_min])
                                #pprint([Lpc_max, Lpc_min])
                                                         
                                
                                res_cons_c1 = cnn.pass_constraint_atomicity(Epc_max, plat_settings); common.check_infnan(res_cons_c1)
                                Eav = res_cons_c1[1]   

                                #pprint([Epc_max, Eav]);sys.exit()

                                if (res_cons_c1[0]):                                  
                                    
                                    L_e2e, npc, npc_n0, npc_ngt0, L_rc_min, L_rc_max = cnn.est_latency_e2e_layer_intpow(layer, Epc_max, Lpc_max, Epc_min, Lpc_min, plat_settings, params_exec, params_pres)
                                    common.check_infnan([L_e2e, npc, npc_n0, npc_ngt0, L_rc_min, L_rc_max])

                                    if L_e2e == np.inf: sys.exit('inf')

                                    #pprint(L_e2e)
                                    result_pass.append({
                                        'params' : common.to_string_params_all(params_exec, params_pres),                                                                                
                                        'Epc': [Epc_max, Epc_min], 'Le2e': L_e2e, 'Lpc': [Lpc_max, Lpc_min], 'Lrc': [L_rc_min, L_rc_max],
                                        'Eu' : (Epc_max / Eav) * 100.0,
                                        'npc' : [npc, npc_n0, npc_ngt0],
                                        'vm' : res_cons_c0[2]
                                    })
                                else:
                                    result_fail.append({
                                        'params' : common.to_string_params_all(params_exec, params_pres),                                        
                                        'reason': 'FAILED_C1',
                                        'Epc': [Epc_max, Epc_min], 'Le2e': None, 'Lpc': [None, None],
                                        'Eu' : (Epc_max / Eav) * 100.0,
                                        'npc' : [None, None, None],
                                        'vm' : res_cons_c0[2]
                                    })             
                            else:
                                result_fail.append({
                                        'params' : common.to_string_params_all(params_exec, params_pres),                                        
                                        'reason': 'FAILED_C0',
                                        'Epc': [None, None], 'Le2e': None, 'Lpc': [None, None],
                                        'npc' : [None, None, None],
                                        'vm' : res_cons_c0[2]
                                    })                              
                                
    
    #print("IEExplorer::EXPLORE_INTPOW: Layer [%s] eval. complete. PASS= %d/%d = %.1f" % (layer['name'], len(result_pass), search_space_size, (len(result_pass)/search_space_size)*100.0 ))
    
    if (len(result_pass) > 0):

        # -- find best solution (lowest E2E latency)  
        min_le2e = np.min([r['Le2e'] for r in result_pass])
        all_best_sols = [r for r in result_pass if r['Le2e'] == min_le2e]
        best_solution = sorted(all_best_sols, key = lambda i: i['vm'])

        sorted_result_pass = sorted(result_pass, key = lambda i: i['Le2e'])        
        # best_solution = sorted_result_pass[0]
        #pprint(best_solution)

        # top N% solutions
        nperc = report_topN
        nnum = int(np.ceil(nperc* len(sorted_result_pass)))
        pass_topN = sorted_result_pass[0:nnum]

        # sort and save the top N% failed solutions    
        sorted_results_fail_c0 = sorted([f for f in result_fail if f['reason'] == 'FAILED_C0'], key = lambda i: i['vm'])
        nnum = int(np.ceil(nperc * len(sorted_results_fail_c0)))
        sorted_results_fail_c0 = sorted_results_fail_c0[0:nnum]

        sorted_results_fail_c1 = sorted([f for f in result_fail if f['reason'] == 'FAILED_C1'], key = lambda i: i['Epc'][0])
        nnum = int(np.ceil(nperc * len(sorted_results_fail_c1)))
        sorted_results_fail_c1 = sorted_results_fail_c1[0:nnum]

        return best_solution, result_pass, sorted_results_fail_c0, sorted_results_fail_c1, pass_topN
    
    else:
        #pprint(result_fail)
        
        warnings.warn("WARNING: Layer [%s] - unable to find a solution" % (layer['name']))
        best_solution = None
        result_pass = []
        sorted_results_fail_c0 = []
        sorted_results_fail_c1 = []
        pass_topN = []
        
        return best_solution, result_pass, sorted_results_fail_c0, sorted_results_fail_c1, pass_topN





def get_data_access_layer_intpow(layer, params_exec, params_pres, plat_settings, plat_cost_profile):
    total_nvm_read_cost_L, total_nvm_write_cost_L, total_nvm_read_cost_E, total_nvm_write_cost_E = cnn.est_data_access_layer_intpow(layer, params_exec, params_pres, plat_settings, plat_cost_profile)
    return total_nvm_read_cost_L, total_nvm_write_cost_L, total_nvm_read_cost_E, total_nvm_write_cost_E