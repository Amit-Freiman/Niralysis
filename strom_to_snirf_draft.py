import pandas as pd
import pathlib 
import numpy as np
from typing import Union
import re
import mne


class Niralysis:

    def __init__(self, snirf_fname: str):
            
        self.snirf_fname = pathlib.Path(snirf_fname)
        if not self.snirf_fname.exists():
            raise ValueError("snirf file does not exsist.") 
        
        if not str(self.snirf_fname).endswith('.snirf'):
            raise ValueError("Not a snirf file.") 
        
        self.read_snirf()
        self.snirf_dtc_loc = self.snirf_file.nirs[0].probe.detectorPos3D[:,:]
        self.snirf_src_loc = self.snirf_file.nirs[0].probe.sourcePos3D[:,:]

        self.storm_fname = None
                  
     ### Read files ###
        
    def read_snirf(self):
        self.snirf_file = mne.io.read_raw_snirf(self.snirf_fname)


    def set_storm_file(self, storm_fname: str):
        self.storm_fname = pathlib.Path(storm_fname)
        if not self.storm_fname.exists():
            raise ValueError("storm file not found!")
    
    
    def read_storm_to_DF(self):
        """Reads the txt file located in self.data_fname, to
        the attribute self.data.
        """
        if self.storm_fname is None:
            raise ValueError("No storm file set. Use 'set_storm_file' to provide a file path.")
        
        self.storm_data = pd.read_csv(self.storm_fname,delim_whitespace=True, index_col=0, header=None)
        self.storm_data.index.name = None
        return self.storm_data
    

    ### Processing STORM file ###

    def storm_prob(self):
        storm_data = self.read_storm_to_DF()
        storm_src = storm_data[storm_data.index.astype(str).str.contains(r'^s\d+$')]
        storm_dtc = storm_data[storm_data.index.astype(str).str.contains(r'^d\d+$')]
        return storm_src, storm_dtc
    

    def snirf_with_storm_prob(self):
        snirf_file_copy = self.snirf_file.copy()
        self.snirf_file.close()
        storm_src, storm_dtc = self.storm_prob()
        snirf_file_copy.nirs[0].probe.sourcePos3D[:, :] = storm_src[:, :]
        snirf_file_copy.nirs[0].probe.detectorPos3D[:, :] = storm_dtc[:, :]
        snirf_file_copy.save()
        return snirf_file_copy
       

    def is_same_dim(self):
        num_snirf_src_loc = np.shape(self.snirf_src_loc)[0]
        num_snirf_dtc_loc = np.shape(self.snirf_dtc_loc)[0]
        num_storm_dtc = 23
        num_storm_src = 16
        if num_snirf_src_loc !=num_storm_src or num_snirf_dtc_loc !=num_storm_dtc:
            raise ValueError("File does not exsist.")
        

file = Niralysis('sub_demo.snirf')
file.read_snirf()  
file.set_storm_file('STORM_demo.txt')
file.read_storm_to_DF()
storm_src, storm_dtc = file.storm_prob()
print("Storm Source Positions:")
print(storm_src)
print("\nStorm Detector Positions:")
print(storm_dtc)

new = file.snirf_with_storm_prob()
print("\nModified Detector Positions in New Snirf File:")
print(new.nirs[0].probe.detectorPos3D[:, :])


    






            


    






