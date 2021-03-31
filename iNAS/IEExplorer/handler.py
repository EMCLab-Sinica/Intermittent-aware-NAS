import sys, os
from pprint import pprint
import numpy as np
from time import perf_counter 
import inspect

sys.path.append('..')
import CostModel.common as common 
from IEExplorer.explore_intpow import explore_full_param_sweep_intpow, get_le2e_fixed_params_intpow, get_data_access_layer_intpow
from IEExplorer.explore_contpow import explore_full_param_sweep_contpow


## -- Intermittent-aware Design Space Explorer (handler module) --


############################################################################
# HELPERS
############################################################################
class IEErrorCodes():
    IE_ERRORCODE_NONE = None
    IE_ERRORCODE_SPATIAL_C0 = 11
    IE_ERRORCODE_ATOMICITY_C1 = 12
    IE_ERRORCODE_UNKNOWN = -1
    
    

# check what the exec design error is 
def _check_error(fail_solutions_c0, fail_solutions_c1):
    if (len(fail_solutions_c1) > 0):
        return IEErrorCodes.IE_ERRORCODE_ATOMICITY_C1    
    elif (len(fail_solutions_c0) > 0):
        return IEErrorCodes.IE_ERRORCODE_SPATIAL_C0    
    else:
        return IEErrorCodes.IE_ERRORCODE_UNKNOWN



# check if the layer dimensions are valid
def _check_layer(layer):
    if layer['type'] == "CONV":
        if not common.check_conv(layer):
            sys.exit(inspect.currentframe().f_code.co_name+"::Error - CONV dimensions incorrect")
    elif (layer['type'] == "POOL") or (layer['type'] == "GAVGPOOL"):
        if not common.check_pool(layer):
            sys.exit(inspect.currentframe().f_code.co_name+"::Error - POOL dimensions incorrect")
    elif layer['type'] == "FC":
        if not common.check_fc(layer):   # assumes the FC layer is formulated as a CONV layer                
            sys.exit(inspect.currentframe().f_code.co_name+"::Error - FC dimensions incorrect")
    else:
        sys.exit(inspect.currentframe().f_code.co_name+"::Error - unknown layer type")



############################################################################
# Query E2E latency / cost
############################################################################
# given a specific exec + pres solution, find end-to-end latency
def find_layer_cost_fixed_solution(layer, solution, plat_settings, plat_cost_profile, power_type='INT'):
    cost_stats_per_layer = None    
        
    #print ("------- Finding Lat E2E for : %s" % layer['name'])
    _check_layer(layer)
    if solution['params'] != None:
        # find parameters of the solution
        Kh = layer['K'].h; Kw = layer['K'].w
        stride = layer['stride']
        Tr, Tc, Tm, Tn, reuse_sch, S = common.string_to_params_all(solution['params'])
        Tri, Tci = common._calc_conv_ifm_tile_size(Tr, Tc, Kh, Kw)
        params_exec = {'tile_size': [Kh, Kw, Tri, Tci, Tr, Tc, Tm, Tn], 'inter_lo': reuse_sch}    
        params_pres = {'backup_batch_size': S}   

        # find cost stats
        if power_type == 'INT':
            cost_stats = get_le2e_fixed_params_intpow(layer, params_exec, params_pres, plat_settings, plat_cost_profile)              
        else:
            sys.exit(inspect.currentframe().f_code.co_name+"::Error - unknown power_type")
        
        return cost_stats
        
    else:
        sys.exit(inspect.currentframe().f_code.co_name+"::Error - solution is None")
    



def get_layer_data_access_cost(layer, solution, plat_settings, plat_cost_profile, power_type='INT'):
    cost_per_layer = {}    
    _check_layer(layer)
    if solution['params'] != None:
        Kh = layer['K'].h; Kw = layer['K'].w
        stride = layer['stride']
        Tr, Tc, Tm, Tn, reuse_sch, S = common.string_to_params_all(solution['params'])
        Tri, Tci = common._calc_conv_ifm_tile_size(Tr, Tc, Kh, Kw)
        params_exec = {'tile_size': [Kh, Kw, Tri, Tci, Tr, Tc, Tm, Tn], 'inter_lo': reuse_sch}
        params_pres = {'backup_batch_size': S}

        tot_data_rd_cost_L, tot_data_wr_cost_L, tot_data_rd_cost_E, tot_data_wr_cost_E = get_data_access_layer_intpow(layer, params_exec, params_pres, plat_settings, plat_cost_profile)

        return tot_data_rd_cost_L, tot_data_wr_cost_L, tot_data_rd_cost_E, tot_data_wr_cost_E
    
    else:
        sys.exit(inspect.currentframe().f_code.co_name+"::Error - solution is None")


        

        



############################################################################
# Explorer Handler
############################################################################

# find best execution solution (intermittent or constinuos pow)
def find_best_solution(network, plat_settings, plat_cost_profile, power_type='INT'):
    sol_per_layer = {}    
    for each_layer in network: 
        #print ("------- Exploring : %s" % each_layer['name'])
        _check_layer(each_layer)

        best_solution=None; pass_solutions=None; fail_solutions=None
        if power_type == 'INT':
            best_solution, pass_solutions, fail_solutions_c0, fail_solutions_c1, pass_topN = explore_full_param_sweep_intpow(each_layer, plat_settings, plat_cost_profile)                
        elif power_type == 'CONT':
            best_solution, pass_solutions, fail_solutions_c0, fail_solutions_c1, pass_topN = explore_full_param_sweep_contpow(each_layer, plat_settings, plat_cost_profile)                
                
        if best_solution == None:   # no solution found                        
            sol_per_layer[each_layer['name']] = {
                'best_sol': best_solution,            
                #'pass_sols': pass_solutions,
                'pass_topN' : pass_topN,
                'fail_c0_topN': fail_solutions_c0,
                'fail_c1_topN': fail_solutions_c1,
                'error_code' : _check_error(fail_solutions_c0, fail_solutions_c1),
            }
            #print(each_layer['name'])
            return sol_per_layer
        else:
            sol_per_layer[each_layer['name']] = {
                'best_sol': best_solution,
                #'pass_sols': pass_solutions,
                'pass_topN' : pass_topN,
                'fail_c0_topN': fail_solutions_c0,
                'fail_c1_topN': fail_solutions_c1,
                'error_code' : None,
            }
    
    return sol_per_layer



