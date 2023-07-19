import pandas as pd
import pathlib 
import pysnirf2
from snirf import Snirf
import numpy as np
from typing import Union


# class Niralysis:

#     def __init__(self, snirf_fname: Union[pathlib.Path, str]):
#         self.snirf_fname = pathlib.Path(snirf_fname)
#         if not self.snirf_fname.exists():
#             raise ValueError("File does not exsist.") 
        
    
    # def read_snirf(self):
    #     self.snirf = Snirf(self.snirf_fname, 'r+')


snirf_file = Snirf(r'C:\\Users\\User\\Python for Neurosceince\\Hackathon\\Niralysis\\sub_demo.snirf', 'r+')       
snirf_detectors = snirf_file.nirs[0].probe.detectorPos3D[:,:]
snirf_sourcers = snirf_file.nirs[0].probe.sourcePos3D[:,:]
num_sourcers = np.shape(snirf_sourcers)[0]
num_detectors = np.shape(snirf_detectors)[0]
