import pandas as pd
import pathlib 
import numpy as np
from typing import Union
import re
from snirf import Snirf
# from mne.io import read_raw_snirf


class Niralysis:

     ###### Defining snirf's attributes and reading snirf file ######

    def __init__(self, snirf_fname: str):
            
        self.snirf_fname = pathlib.Path(snirf_fname)
        if not self.snirf_fname.exists():
            raise ValueError("snirf file does not exsist.") 
        
        if not str(self.snirf_fname).endswith('.snirf'):
            raise ValueError("Not a snirf file.") 
        
        self.read_snirf()
        self.snirf_detc_loc = self.snirf_data.nirs[0].probe.detectorPos3D[:,:]
        self.snirf_sourc_loc = self.snirf_data.nirs[0].probe.sourcePos3D[:,:]

        self.old_sourc_loc = None
        self.old_detc_loc = None
        self.storm_fname = None
                  
        
    def read_snirf(self):
        self.snirf_data = Snirf(rf'{self.snirf_fname}', 'r+')


     ###### Read other files ######

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
    

    ###### Processing STORM file ######

    def storm_prob(self):
        ### need to add validation: if there isn't "s" or "d" indexes

        storm_data = self.read_storm_to_DF()
        storm_sourc_loc = storm_data[storm_data.index.astype(str).str.contains(r'^s\d+$')]
        storm_detc_loc = storm_data[storm_data.index.astype(str).str.contains(r'^d\d+$')]
        
        if len(storm_sourc_loc) == 0 or len(storm_detc_loc) == 0:
            raise ValueError("Invalid STORM data. Check your STORM file.")


        return storm_sourc_loc, storm_detc_loc
    

    
    
    def snirf_with_storm_prob(self):
        storm_sourc_loc, storm_detc_loc = self.storm_prob()

        # Store the old optode locations
        self.old_sourc_loc = np.copy(self.snirf_data.nirs[0].probe.sourcePos3D)
        self.old_detc_loc = np.copy(self.snirf_data.nirs[0].probe.detectorPos3D)

        # Update the SNIRF file with the STORM data
        self.snirf_data.nirs[0].probe.sourcePos3D[:, :] = storm_sourc_loc
        self.snirf_data.nirs[0].probe.detectorPos3D[:, :] = storm_detc_loc

        return self.snirf_data
    

    def is_same_dim(self): 
        #### validate if the number of the optodes is the same between the storm and the snirf files ###
        num_snirf_sourc = np.shape(self.snirf_sourc_loc)[0]
        num_snirf_detc = np.shape(self.snirf_detc_loc)[0]
        storm_sourc_loc, storm_detc_loc = self.storm_prob()
        num_storm_sourc = np.shape(storm_sourc_loc)
        num_storm_detc = np.shape(storm_detc_loc)
        if num_snirf_sourc !=num_storm_sourc or num_snirf_detc !=num_storm_detc:
            raise ValueError("File does not exsist.")
        


#####Testing the code ####


# Example usage

file = Niralysis('sub_demo.snirf')
file.set_storm_file('STORM_demo.txt')
file.read_snirf()
file.read_storm_to_DF()

storm_sourc_loc, storm_detc_loc = file.storm_prob()
print("Storm Source Positions:")
print(storm_sourc_loc)
print("\nStorm Detector Positions:")
print(storm_detc_loc)

# Call the method to update SNIRF file with STORM data
file.snirf_with_storm_prob()


# Access new optode location in a snirf file
new_snirf_source_loc = file.snirf_sourc_loc
new_snirf_detector_loc = file.snirf_detc_loc
print("\nNew Source Locations in snirf file:")
print(new_snirf_source_loc)
print("\nNew Detector Locations in snirf file:")
print(new_snirf_detector_loc)


# Access old optode locations
old_source_locations = file.old_sourc_loc
old_detector_locations = file.old_detc_loc

print("\nOld Source Locations:")
print(old_source_locations)
print("\nOld Detector Locations:")
print(old_detector_locations)








            


    






