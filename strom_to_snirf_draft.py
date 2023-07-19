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
        
        self.read_snirf()
        self.snirf_dtc_loc = self.snirf_file.nirs[0].probe.detectorPos3D[:,:]
        self.snirf_src_loc = self.snirf_file.nirs[0].probe.sourcePos3D[:,:]

        
    
    def read_snirf(self):
        self.snirf_file = Snirf(self.snirf_fname, 'r+')

    def read_storm(self):
        pass


    def is_same_dim(self):
        num_snirf_src_loc = np.shape(self.snirf_src_loc)[0]
        num_snirf_dtc_loc = np.shape(self.snirf_dtc_loc)[0]
        num_storm_dtc = 23
        num_storm_src = 16

        if num_snirf_src_loc !=num_storm_src or num_snirf_dtc_loc !=num_storm_dtc:
            raise ValueError("File does not exsist.")
        


    








