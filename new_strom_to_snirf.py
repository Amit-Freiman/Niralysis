import pandas as pd
import pathlib 
import numpy as np
from typing import Union
import re
from snirf import Snirf



class Niralysis:

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
    def __init__(self, snirf_fname: str):
            
        self.snirf_fname = pathlib.Path(snirf_fname)
        if not self.snirf_fname.exists():
            raise ValueError("snirf file does not exsist.") 
        
        if not str(self.snirf_fname).endswith('.snirf'):
            raise ValueError("Not a snirf file.") 
        
        

        self.old_sourc_loc = None
        self.old_detc_loc = None
        self.storm_fname = None
        
    

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
        try:
                data = Snirf(rf'{self.snirf_fname}', 'r+')
                data_backup = data
                self.snirf_detc_loc = data.nirs[0].probe.detectorPos3D[:,:]
                self.snirf_sourc_loc = data.nirs[0].probe.sourcePos3D[:,:]
                self.set_storm_file(storm_fname)
                self.snirf_with_storm_prob(data)

                print("Your snirf file has been updated.")
                a = input("If you want to see the updated sources and detectors locations, press 1. Else, press 0")
                if a == str(1):
                    place = Snirf(rf'{self.snirf_fname}', 'r+')
                    print("The updated sourcs' locaions: \n")
                    print(place.nirs[0].probe.sourcePos3D[:,:])
                    print("The updated detectors' locaions: \n")
                    print(place.nirs[0].probe.detectorPos3D[:,:])
                else:
                    pass
        except OSError as error:
            print(error) 
            data_backup.save(rf'{self.snirf_fname}')
            print('We took care of it, please try again')
            
            


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
    
    ###validation STOM file###
    def is_storm_valid(self):
        storm_sourc_loc, storm_detc_loc = self.storm_prob()

        if storm_sourc_loc.isnull().values.any() or storm_detc_loc.isnull().values.any():
            raise ValueError("Invalid STORM data. Check your STORM file.")
        
        if any(storm_sourc_loc.dtypes == int or storm_detc_loc.dtypes ==int):
            raise ValueError("STORM data contains integer column(s). All columns should have float data type.")
 
        num_storm_sourc = np.shape(storm_sourc_loc)
        num_storm_detc = np.shape(storm_detc_loc)
        
        num_snirf_sourc = np.shape(self.snirf_sourc_loc)[0]
        num_snirf_detc = np.shape(self.snirf_detc_loc)[0]

        if num_snirf_sourc != num_storm_sourc or num_snirf_detc != num_storm_detc:
            raise ValueError("Invalid STORM data. Check your STORM file.")
        


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
        data.close()

        
    def get_old_probe_locations(self):
        """    
    Get the original probe locations before updating with STORM data.

    Returns:
        Tuple[numpy.ndarray or None, numpy.ndarray or None]: A tuple containing the original source and detector optode locations."""
        return self.old_sourc_loc, self.old_detc_loc
    

    def euclidean_dist(self):
        self.old_sourc_loc, self.old_detc_loc = self.get_old_probe_locations()
        storm_sourc_loc, storm_detc_loc = self.storm_prob()

        sourc_euclidean_dist = np.linalg.norm(storm_sourc_loc - self.old_sourc_loc, axis=1)
        detc_euclidean_dist = np.linalg.norm(storm_detc_loc - self.old_detc_loc, axis=1)

        return sourc_euclidean_dist, detc_euclidean_dist

    
    def invalid_sourc(self,thresh=10):
        storm_sourc_loc = self.storm_prob()[0]
        sourc_euclidean_dist = self.euclidean_dist()[0]
        sourc_euclidean_dist = np.array(sourc_euclidean_dist)
        invalid_sourc = storm_sourc_loc[sourc_euclidean_dist >= thresh]
        return invalid_sourc
    
    def invalid_detec(self,thresh=10):
        storm_detc_loc = self.storm_prob()[1]
        detc_euclidean_dist = self.euclidean_dist()[1]
        detc_euclidean_dist = np.array(detc_euclidean_dist)
        invalid_detec = storm_detc_loc[detc_euclidean_dist >= thresh]
        return invalid_detec



#####Testing the code ####



head = Niralysis('sub_demo.snirf')
head.storm('STORM_demo.txt')



            


    






