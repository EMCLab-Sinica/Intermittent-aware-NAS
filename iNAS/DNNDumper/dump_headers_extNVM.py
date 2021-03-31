import sys, os
from pprint import pprint
import warnings
import numpy as np
from datetime import datetime, date


# local imports
sys.path.append('.')
from misc import _get_dims, _get_dim_k, _get_dim_ifm
from cnn_types import CNNModel, CNNLayer, Mat


#################################################################
#           HELPERS
#################################################################
def _get_text_mat(data_loc, n, ch, h, w, dtype='int'):
    if dtype == 'str':
        m = Mat( data = data_loc, n = str(n), ch = str(ch), h = str(h), w = str(w) )
    else:
        m = Mat( data = data_loc, n = n, ch = ch, h = h, w = w )
    return m


#################################################################
#           COMMON
#################################################################
def _write_file_top_datafile(fc, fname):
    fc.write('#ifndef %s_H_\n' % fname.upper())
    fc.write('#define %s_H_\n\n' % fname.upper())
    fc.write('#include "DSPLib.h"\n\n')       


#################################################################
#  OUTPUT MODEL ARCHITECTURE
#################################################################
def _get_layer_text(layer):

    s = "{\n"
    
    s += "\t.lix = %d,\n" % layer.lid
    s += "\t.fun = %s,\n" % layer.func

    # -- weights --
    s += "\t.weights = (Mat_t){\n"
    s += "\t\t.data = %d,\n" % (layer.weights.data)
    s += "\t\t.n = %d,\n" % (layer.weights.n)
    s += "\t\t.ch = %d,\n" % (layer.weights.ch)
    s += "\t\t.h = %d,\n" % (layer.weights.h)
    s += "\t\t.w = %d\n" % (layer.weights.w)
    s += "\t},\n"

    # -- bias --
    s += "\t.bias = (Mat_t){\n"
    s += "\t\t.data = %d,\n" % (layer.bias.data)
    s += "\t\t.n = %d,\n" % (layer.bias.n)
    s += "\t\t.ch = %d,\n" % (layer.bias.ch)
    s += "\t\t.h = %d,\n" % (layer.bias.h)
    s += "\t\t.w = %d\n" % (layer.bias.w)
    s += "\t},\n"

    # -- ifm --
    s += "\t.ifm = (Mat_t){\n"
    s += "\t\t.data = %d,\n" % (layer.ifm.data)
    s += "\t\t.n = %d,\n" % (layer.ifm.n)
    s += "\t\t.ch = %d,\n" % (layer.ifm.ch)
    s += "\t\t.h = %d,\n" % (layer.ifm.h)
    s += "\t\t.w = %d\n" % (layer.ifm.w)
    s += "\t},\n"

    # -- ofm --
    s += "\t.ofm = (Mat_t){\n"
    s += "\t\t.data = %d,\n" % (layer.ofm.data)
    s += "\t\t.n = %d,\n" % (layer.ofm.n)
    s += "\t\t.ch = %d,\n" % (layer.ofm.ch)
    s += "\t\t.h = %d,\n" % (layer.ofm.h)
    s += "\t\t.w = %d\n" % (layer.ofm.w)
    s += "\t},\n"


    # -- execution parameters --
    s += "\t.parE = (ExeParams_t){\n"    
    s += "\t\t.Tn = %d,\n" % (layer.Tn)
    s += "\t\t.Tm = %d,\n" % (layer.Tm)
    s += "\t\t.Tr = %d,\n" % (layer.Tr)
    s += "\t\t.Tc = %d,\n" % (layer.Tc)
    s += "\t\t.str = %d,\n" % (layer.str)
    s += "\t\t.pad = %d,\n" % (layer.pad)
    s += "\t\t.lpOdr = %s\n" % (layer.lpOdr)
    s += "\t},\n"


    # -- preservation parameters --
    s += "\t.parP = (PreParams_t){\n"
    s += "\t\t.preSz = %d,\n" % (layer.preSz)    
    s += "\t},\n"


    # -- double buffer index --
    s += "\t.idxBuf = 0\n"

    s += "}"

    return s


def _write_file_top_modelfile(fc, fname_dev, fname):
    dtstr = datetime.now().strftime("%m/%d/%y,%H:%M:%S")

    fc.write("/* \n" +
              "* %s.h \n" % fname +
              "* (Auto-generated)\n" +               
              "* Created on: %s \n" % dtstr +
              "* Label : %s \n" % fname_dev +
              "*/\n\n")  
    
    fc.write('#ifndef %s_H_\n' % fname.upper())
    fc.write('#define %s_H_\n\n' % fname.upper())
        
    fc.write('#include "../cnn/cnn_types.h"\n')           
    fc.write('#include "../cnn/cnn_conv_tiled_std.h"\n')   
    fc.write('#include "../cnn/cnn_fc.h"\n')       
    fc.write('#include "../cnn/cnn_pool.h"\n\n\n')       


def write_model_header(dir, fname_dev, fname, model: CNNModel):
    
    # Create and write file
    with open('%s/%s.h' % (dir, fname_dev.lower()), 'w') as fc:

        _write_file_top_modelfile(fc, fname_dev, fname)
                
        fc.write("\n")    

        # -- write out each layer in the model --
        fc.write("#pragma PERSISTENT(%s)\n" % model.name)
        fc.write("CNNLayer_t %s[%d] = {\n" % (model.name, model.num_layers))
        for lix, each_layer in enumerate(model.layers):
            s = _get_layer_text(each_layer)
            fc.write(s)
            if (lix < (model.num_layers-1)):
                fc.write(",\n")
        
        fc.write("\n};\n\n")
          
        # -- write out the network model instance --
        fc.write("#pragma PERSISTENT(network)\n" + 
                 "CNNModel_t network={\n" +             
                 "\t.Layers       = %s,\n" % model.name + 
                 "\t.numLayers = %d,\n" % model.num_layers + 
                 "\t.name = \"%s\"\n" % model.name + 
                 "};\n\n")

        fc.write('#endif /* %s_H_ */\n' % fname.upper())
        

    print ("Written out - ", dir,"/",fname_dev)











