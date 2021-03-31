import enum

#######################
# Enums
#######################
class LAYERTYPES(int, enum.Enum):
   LAYER_CONV     = 1
   LAYER_FC       = 2
   LAYER_MAXPOOL  = 3

class CONVTYPE(int, enum.Enum):
   VIA_1D      = 1
   VIA_MATMUL  = 2
   VIA_MAC     = 3

class FCTYPE(int, enum.Enum):
   VIA_MAC     = 1
   VIA_MATMUL  = 2
   
class CONV_TASK_TYPE(int, enum.Enum):    
    # task types related to convolution using 1D conv (FIR)
    TASK_CONVBY1D_1DCONV    = 1    # DMA + LEA FIR + DMA
    TASK_CONVBY1D_MADD_1    = 2    # DMA + MADD (1D conv results) + DMA
    TASK_CONVBY1D_MADD_2_BR = 3    # DMA + MADD (add channels to get single IFM) + BIAS + RELU + DMA

class FC_TASK_TYPE(int, enum.Enum):
   # task types related to convolution using 1D conv (FIR)
   TASK_CONVBY1D_1DCONV    = 1    # DMA + LEA FIR + DMA
   TASK_CONVBY1D_MADD_1    = 2    # DMA + MADD (1D conv results) + DMA
   TASK_CONVBY1D_MADD_2_BR = 3    # DMA + MADD (add channels to get single IFM) + BIAS + RELU + DMA


#######################
# Data types
#######################
# Objects - primarily used for holding text labels (not values)
# @TODO: rename to differentiate text objects and value objects

class CNNModel:
  def __init__(self, name, layers, num_layers):
    self.name = name
    self.layers = layers
    self.num_layers = num_layers

class CNNLayer:
  def __init__(self, lid, name, func, weights, bias, ifm, ofm, s=1, p=0, params_exec=None, params_pres=None):
    self.lid = lid
    self.name = name
    self.func = func
    self.weights = weights
    self.bias = bias
    self.ifm = ifm
    self.ofm = ofm

    # execution params
    if params_exec != None:
      inter_lo = params_exec['inter_lo']    
      Kh, Kw, Tri, Tci, Tr, Tc, Tm, Tn = params_exec['tile_size']
      self.Tn = Tn; self.Tm = Tm; self.Tr = Tr; self.Tc = Tc      
      self.lpOdr = self._get_lpodr_lbl(inter_lo)
    else:
      self.Tn = -1; self.Tm = -1; self.Tr = -1; self.Tc = -1      
      self.lpOdr = 'None'

    self.str= s; self.pad= p

    # preservation params
    if params_pres != None:
      self.preSz = params_pres['backup_batch_size']
    else:
      self.preSz = -1
    
    # buffer index (double buffering)
    self.idxBuf = 0

  
  # lpord as specified in msp430 code
  def _get_lpodr_lbl(self,inter_lo):
    lbl = {
      'reuse_I' : "IFM_ORIENTED",
      'reuse_W' : "WEIGHT_ORIENTED",
      'reuse_O' : "OFM_ORIENTED",
    }
    return lbl[inter_lo]
   

class Mat:
    def __init__(self, data, n, ch, h, w):
        self.data = data
        self.n = n
        self.ch = ch
        self.h = h
        self.w = w

    def __repr__(self):
        s = "MAT(data = []" +  \
              ", n = " + str(self.n) + \
              ", ch = " + str(self.ch) + \
              ", h = " + str(self.h) + \
              ", w = " + str(self.w) + ")\n"
        return s
