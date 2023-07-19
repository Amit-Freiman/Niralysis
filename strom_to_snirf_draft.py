import pandas as pd
import pathlib 
import pysnirf2
from snirf import Snirf
import numpy as np
from typing import Union


class Niralysis:

    def __init__(self, snirf_fname: Union[pathlib.Path, str]):
        self.snirf_fname = pathlib.Path(snirf_fname)
        if not self.snirf_fname.exists():
            raise ValueError("File does not exsist.") 
        
    
    def read_snirf(self):
        self.snirf = Snirf(self.snirf_fname, 'r+')


snirf_file = Snirf(r'C:\\Users\\User\\Python for Neurosceince\\Hackathon\\Niralysis\\sub_demo.snirf', 'r+')       
snirf_detectors_loc = snirf_file.nirs[0].probe.detectorPos3D[:,:]
snirf_sourcers_loc = snirf_file.nirs[0].probe.sourcePos3D[:,:]
num_snirf_sourcers_loc = np.shape(snirf_sourcers_loc)[0]
num_snirf_detectors_loc = np.shape(snirf_detectors_loc)[0]
