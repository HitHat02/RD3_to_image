import os
import numpy as np

def readRd3(self):
    gpr = np.frombuffer(self.data, dtype=np.short)
    return gpr