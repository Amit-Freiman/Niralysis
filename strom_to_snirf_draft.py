import pandas as pd
import pathlib 
import pysnirf2
from snirf import Snirf
import numpy as np
from typing import Union


class Niralysis:

def __init__(self, snirf_fname: Union[pathlib.Path, str], storm_fname: Union[pathlib.Path, str]):
        
        self.snirf_fname = pathlib.Path(snirf_fname)
        if not self.snirf_fname.exists():
            raise ValueError("snirf file does not exsist.") 
        
        self.storm_fname = pathlib.Path(storm_fname)
        if not self.storm_fname.exists():
            raise ValueError("storm file not found!")
               
    
    def read_snirf(self.snirf_fname):
        self.snirf_file = Snirf(self.snirf_fname, 'r+')


    def read_storm_to_DF(self.storm_fname)-> pd.DataFrame:
        """Reads the txt file located in self.data_fname, to
        the attribute self.data.
        """
        self.storm_file = pd.read_csv(self.storm_fname)
        self.storm_data = pd.DataFrame(self.storm_file)
        return self.storm_data
        


    def is_same_dim(self):
        snirf_dtc_loc = self.snirf_file.nirs[0].probe.detectorPos3D[:,:]
        snirf_src_loc = self.snirf_file.nirs[0].probe.sourcePos3D[:,:]
        num_snirf_src_loc = np.shape(snirf_src_loc)[0]
        num_snirf_dtc_loc = np.shape(snirf_dtc_loc)[0]
        num_storm_dtc = 23
        num_storm_src = 16

        if num_snirf_src_loc !=num_storm_src or num_snirf_dtc_loc !=num_storm_dtc:
            raise ValueError("File does not exsist.")







