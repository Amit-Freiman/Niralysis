import pandas as pd
import pathlib 
import numpy as np
from typing import Union
import re
from snirf import Snirf
from niralysis.jsonOrganizer import process_json_files
from niralysis.calculate_differences import get_table_of_deltas_between_time_stamps_in_all_kps, get_table_of_summed_distances_for_kp_over_time
from niralysis.calculate_pairwise_distance import calculate_pairwise_distance
from niralysis.Events_to_label import events_to_labels 


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

    FRAMES_PER_SECOND = 30  # number of frames in a group for analysis of movement
    HEAD_KP = [0,1,2,5,15,16,17,18]
    ARM_KP = [1,2,3,4,5,6,7,8]


    def __init__(self, snirf_fname: str):
            
        self.snirf_fname = pathlib.Path(snirf_fname)
        if not self.snirf_fname.exists():
            raise ValueError("snirf file does not exsist.") 
        
        if not str(self.snirf_fname).endswith('.snirf'):
            raise ValueError("Not a snirf file.") 
        
        

        self.old_sourc_loc = None
        self.old_detc_loc = None
        self.storm_fname = None
        
    ### STORM ###

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

    
    ### Openpose ###
    
    def get_csv(self, json_folder):
        """Convert json to csv
        Args:
            json_folder (str): path to folder cotaining all json files of the recording
        Returns:
            daqta (pd.DataFrame): data frame of the json file combined
        """
        return process_json_files(json_folder)

    def extract_key_point(self, key_points: list) -> pd.DataFrame:
        """Extract the data from the data frame, according to the key points given.
        Args:
            key_points (list): list of key points to extract
        Returns:
            filtered_key_point_data (pd.DataFrame): filtered data frame containing only the key points given
        """
        # check if key points are valid
        #self.check_key_point_input(key_points)
        # Find the key points in the column headers

        columns_to_include = []
        for key_point in key_points:
            key_point_names = ["KP_" + str(key_point) + "_x", "KP_" + str(key_point) + "_y", "KP_" + str(key_point) + "_confidence"]
            for header in key_point_names: 
                columns_to_include.append(header)

        # extract key points
        filtered_key_point_data = self.data[columns_to_include]
        return filtered_key_point_data

    def filter_confidence(filtered_key_point_data, confidence_threshold: float = 0.5):
        """Filter data based on confidence, if confidence  rmdir /s /q E:\testis less than 0.5 in a specific key point and time frame, then
        the data in this time frame is set to 0.
        The columns are organized as follows: KP_1_x, KP_1_y, KP_1_confidence, KP_2_x, KP_2_y, KP_2_confidence, etc.
        Args:
            confidence_threshold (float): confidence threshold
        """
        # Add case if filtered_key_point_data is the same as self.data
        for column in filtered_key_point_data.columns:
            if "confidence" in column:
                for index, confidence_per_time_stamp in enumerate(filtered_key_point_data[column]):
                    # If confidence is less than TH, set the data in this time frame to 0 in both x and y coordinates
                    if confidence_per_time_stamp < confidence_threshold:
                        # set the values in the x and y rows in this key point to 0
                        # find the index of the confidence column
                        index_of_confidence_column = filtered_key_point_data.columns.get_loc(column)
                        # find the index of the x and y columns in this key point
                        x_column = filtered_key_point_data.columns[index_of_confidence_column - 2]
                        y_column = filtered_key_point_data.columns[index_of_confidence_column - 1]
                        # set the values in the x and y rows in this key point to 0
                        filtered_key_point_data.loc[index,x_column] = 0
                        filtered_key_point_data.loc[index,y_column] = 0

        return filtered_key_point_data[filtered_key_point_data.columns.drop(list(filtered_key_point_data.filter(regex='confidence')))]

    def calculate_change_in_distance(data):
        distance_table = calculate_pairwise_distance(data)
        change_in_distance_table = Niralysis.calculate_change_in_position_per_frame(distance_table)
        return change_in_distance_table
        

    def calculate_change_in_position_per_frame(data):
        """"""
        change_in_position_table = get_table_of_deltas_between_time_stamps_in_all_kps(data)
        return change_in_position_table

    def generate_motion_labels_by_change(self):
        """Generate motion labels per time stamp according to change in x and y coordinates"""
        self.motion_label = events_to_labels(self.changed_frames, 3)

    def generate_open_pose(self, path_to_open_pose_output_folder: str, key_points_to_extract: int = 0, beginning_of_recording: list = 0):
        """Generates attribute file.motionlabels (Timestamps for certain motion labels from video)
        Args:
            path_to_open_pose_output_folder (str): path to open pose output folder (folder containing all json files)
            beginning_of_recording (list): list of lists of the beginning of the recording
            key_points_to_extract (list): list of key points to extract
        Returns:
            open_pose_data (list): list of lists of open pose data
        """
        if type(key_points_to_extract) != int:
            raise TypeError("key_points_to_extract must be an integer")
        if key_points_to_extract > 1 or key_points_to_extract < 0:
            raise ValueError("key_points_to_extract must be 0 (Just head) or 1 (Head and arms))")
        if type(path_to_open_pose_output_folder) == pathlib.WindowsPath:
            path_to_open_pose_output_folder = str(path_to_open_pose_output_folder)
        if type(path_to_open_pose_output_folder) != str:
            raise TypeError("path_to_open_pose_output_folder must be a string")
        if key_points_to_extract == 0:
            key_points_to_extract = Niralysis.HEAD_KP
        else:
            key_points_to_extract = Niralysis.ARM_KP + Niralysis.HEAD_KP
        self.data = self.get_csv(path_to_open_pose_output_folder)
        df_extracted = self.extract_key_point(key_points_to_extract)
        df_filtered = Niralysis.filter_confidence(df_extracted)
        change_in_position = Niralysis.calculate_change_in_position_per_frame(df_filtered)
        change_in_distance = Niralysis.calculate_change_in_distance(df_filtered)
        self.changed_frames = get_table_of_summed_distances_for_kp_over_time(change_in_position, change_in_distance, 50)



#####Testing the code ####



# head = Niralysis('sub_demo.snirf')
# head.storm('STORM_demo.txt')



            


    






