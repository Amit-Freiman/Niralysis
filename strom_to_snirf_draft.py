import pandas as pd
import pathlib 
import numpy as np
import re
from snirf import Snirf
import math
from scipy.spatial import distance




class Niralysis:


    def __init__(self, snirf_fname: str):
        """
    Initialize a Niralysis object with a SNIRF file.

    Parameters:
        snirf_fname (str): The file path of the SNIRF file.

    Raises:
        ValueError: If the SNIRF file does not exist or has an invalid extension.

    Attributes:
        snirf_fname (pathlib.Path): The file path of the SNIRF file.
        snirf_data (Snirf): The loaded SNIRF data.
        snirf_sourc_loc (numpy.ndarray): Source optode locations from the SNIRF data.
        snirf_detc_loc (numpy.ndarray): Detector optode locations from the SNIRF data.
        old_sourc_loc (numpy.ndarray or None): The original source optode locations.
        old_detc_loc (numpy.ndarray or None): The original detector optode locations.
        storm_fname (pathlib.Path or None): The file path of the STORM file, if set.
    """         
            
        self.snirf_fname = pathlib.Path(snirf_fname)
        if not self.snirf_fname.exists():
            raise ValueError("snirf file does not exsist.") 
        
        if not str(self.snirf_fname).endswith('.snirf'):
            raise ValueError("Not a snirf file.") 
        

        self.old_sourc_loc = None
        self.old_detc_loc = None
        self.storm_fname = None


     ###### Read other files ######

    def storm(self,storm_fname):
        """
    Switching the snirf original probe locations with the STORM probe locations. 

    Parameters:
        storm_fname (str): The file path of the STORM.txt file.

    Raises:
        ValueError: If the STORM file does not exist.

    Updates:
        snirf_detc_loc (numpy.ndarray): Updates the detector optode locations with the STORM data.
        snirf_sourc_loc (numpy.ndarray): Updates the source optode locations with the STORM data.
        old_detc_loc (numpy.ndarray): Stores the original detector optode locations if not already stored.
        old_sourc_loc (numpy.ndarray): Stores the original source optode locations if not already stored.
    """

        data = Snirf(rf'{self.snirf_fname}', 'r+')
        self.snirf_detc_loc = data.nirs[0].probe.detectorPos3D[:,:]
        self.snirf_sourc_loc = data.nirs[0].probe.sourcePos3D[:,:]
        self.set_storm_file(storm_fname)
        self.snirf_with_storm_prob(data)


    
    def set_storm_file(self, storm_fname: str):
        """   
    Set the STORM file for STORM analysis.

    Parameters:
        storm_fname (str): The file path of the STORM.txt file.

    Raises:
        ValueError: If the STORM.txt file does not exist.

    Updates:
        storm_fname (pathlib.Path): The file path of the STORM.txt file."""
        
        self.storm_fname = pathlib.Path(storm_fname)
        if not self.storm_fname.exists():
            raise ValueError("storm file not found!")
        self.storm_data = Niralysis.read_storm_to_DF(storm_fname)
    
    
    def read_storm_to_DF(storm_fname):
        """ 
    Read the STORM data from the provided STORM.txt file and return it as a pandas DataFrame.

    Parameters:
        storm_fname (str): The file path of the STORM.txt file.

    Raises:
        ValueError: If the STORM file path is None.

    Returns:
        pd.DataFrame: The STORM data loaded from the file."""
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

        """
    Update the SNIRF data with STORM optode locations and save the modified data back to the original SNIRF file.

    Parameters:
        data (Snirf): The SNIRF data to be updated with STORM optode locations.

    Raises:
        ValueError: If there is an issue with the STORM data or SNIRF data.

    Updates:
        snirf_detc_loc (numpy.ndarray): Updates the detector optode locations with the STORM data.
        snirf_sourc_loc (numpy.ndarray): Updates the source optode locations with the STORM data.
        old_detc_loc (numpy.ndarray): Stores the original detector optode locations if not already stored.
        old_sourc_loc (numpy.ndarray): Stores the original source optode locations if not already stored."""
        
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
        """    
    Get the original probe locations before updating with STORM data.

    Returns:
        Tuple[numpy.ndarray or None, numpy.ndarray or None]: A tuple containing the original source and detector optode locations."""
        return self.old_sourc_loc, self.old_detc_loc
    
    def euclidean_dist(storm_loc, snirf_loc, cols=None):
        return np.linalg.norm(storm_loc - snirf_loc, axis=1)
    
    def delta_dist(self, storm_loc, snirf_loc, cols=None, thresh = 30):
        df_dist = self.euclidean_dist(storm_loc, snirf_loc, cols=None)
        invalid_prob_indices = []
        for i, prob in enumerate(df_dist.shape[0]): #looping on the optode rows, adding the indices of invalid optode to a list
            if prob <=thresh:
                continue
            invalid_prob_indices.append(i)
        invalid_prob = storm_loc[invalid_prob_indices]
        return invalid_prob
  
    def dist_source(self):
        self.old_sourc_loc = self.get_old_probe_locations()[0]
        storm_sourc_loc = self.storm_prob()[0]
        invalid_source = self.delta_dist(self.old_sourc_loc,storm_sourc_loc)
        return invalid_source
    
    def dist_detec(self):
        self.old_detc_loc = self.get_old_probe_locations()[1]
        storm_detc_loc = self.storm_prob()[1]
        invalid_detector = self.delta_dist(self.old_detc_loc,storm_detc_loc)
        return invalid_detector

       
#####Testing the code ####



file = Niralysis('sub_demo.snirf')
file.storm('STORM_demo.txt')



            


    






