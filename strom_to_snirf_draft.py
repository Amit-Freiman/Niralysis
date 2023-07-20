import pandas as pd
import pathlib 
import numpy as np
from typing import Union
import re
from snirf import Snirf



class Niralysis:

     ###### Defining snirf's attributes and reading snirf file ######

    def __init__(self, snirf_fname: str):
            
        self.snirf_fname = pathlib.Path(snirf_fname)
        if not self.snirf_fname.exists():
            raise ValueError("snirf file does not exsist.") 
        
        if not str(self.snirf_fname).endswith('.snirf'):
            raise ValueError("Not a snirf file.") 
        
        #self.read_snirf()
        

        self.old_sourc_loc = None
        self.old_detc_loc = None
        self.storm_fname = None
    


                  
     ###### Read other files ######

    def storm(self,storm_fname):
        data = Snirf(rf'{self.snirf_fname}', 'r+')
        self.snirf_detc_loc = data.nirs[0].probe.detectorPos3D[:,:]
        self.snirf_sourc_loc = data.nirs[0].probe.sourcePos3D[:,:]
        self.set_storm_file(storm_fname)
        self.snirf_with_storm_prob(data)


    
    def set_storm_file(self, storm_fname: str):
        self.storm_fname = pathlib.Path(storm_fname)
        if not self.storm_fname.exists():
            raise ValueError("storm file not found!")
        self.storm_data = Niralysis.read_storm_to_DF(storm_fname)
    
    
    def read_storm_to_DF(storm_fname):
        """Reads the txt file located in self.data_fname, to
        the attribute self.data.
        """
        if storm_fname is None:
            raise ValueError("No storm file set. Use 'set_storm_file' to provide a file path.")
        
        storm_data = pd.read_csv(storm_fname,delim_whitespace=True, index_col=0, header=None)
        storm_data.index.name = None
        return storm_data
    

    ###### Processing STORM file ######

    def storm_prob(self):
        ### need to add validation: if there isn't "s" or "d" indexes

        storm_sourc_loc = self.storm_data[self.storm_data.index.astype(str).str.contains(r'^s\d+$')]
        storm_detc_loc = self.storm_data[self.storm_data.index.astype(str).str.contains(r'^d\d+$')]
        
        if len(storm_sourc_loc) == 0 or len(storm_detc_loc) == 0:
            raise ValueError("Invalid STORM data. Check your STORM file.")


        return storm_sourc_loc, storm_detc_loc
    

    def snirf_with_storm_prob(self,data):
        storm_sourc_loc, storm_detc_loc = self.storm_prob()

        # Store the old optode locations if not already stored
        if self.old_sourc_loc is None:
            self.old_sourc_loc = np.copy(data.nirs[0].probe.sourcePos3D)
        if self.old_detc_loc is None:
            self.old_detc_loc = np.copy(data.nirs[0].probe.detectorPos3D)

        # Update the SNIRF file with the STORM data
        data.nirs[0].probe.sourcePos3D[:, :] = storm_sourc_loc
        data.nirs[0].probe.detectorPos3D[:, :] = storm_detc_loc

        data.save(rf'{self.snirf_fname}')


    def is_same_dim(self):
        num_snirf_sourc = np.shape(self.snirf_sourc_loc)[0]
        num_snirf_detc = np.shape(self.snirf_detc_loc)[0]
        storm_sourc_loc, storm_detc_loc = self.storm_prob()
        num_storm_sourc = np.shape(storm_sourc_loc)
        num_storm_detc = np.shape(storm_detc_loc)
        if num_snirf_sourc != num_storm_sourc or num_snirf_detc != num_storm_detc:
            raise ValueError("File does not exist.")


    def get_old_probe_locations(self):
        """Returns the old probe locations."""
        return self.old_sourc_loc, self.old_detc_loc
    



#####Testing the code ####



file = Niralysis('sub_demo.snirf')
file.storm('STORM_demo.txt')



            


    






