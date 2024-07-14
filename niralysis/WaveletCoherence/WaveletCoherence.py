from __future__ import division
import numpy
from matplotlib import pyplot

import pycwt as wavelet
from pycwt.helpers import find


class WaveletCoherence:
    def __init__(self, x, y, scale=0.05, wavelet_type='cmor'):
        self.x = x
        self.y = y
        self.scale = scale
        self.wavelet_type = wavelet_type

    def plot(self):
        pass
