import pandas as pd
import pathlib 
import numpy as np
from snirf import Snirf

from niralysis.HbOData.HbOData import HbOData
from niralysis.EventsHandler.EventsHandler import EventsHandler
from niralysis.utils.jsonOrganizer import process_json_files
from niralysis.calculators.calculate_differences import get_table_of_deltas_between_time_stamps_in_all_kps, get_table_of_summed_distances_for_kp_over_time
from niralysis.calculators.calculate_pairwise_distance import calculate_pairwise_distance
from niralysis.utils.Events_to_label import events_to_labels
import mne



class Niralysis:

    """
    Initialize a Niralysis object with a SNIRF file.

    Parameters:
        snirf_fname (str): The file path of the SNIRF file.
    
    Methods:
        storm: Update SNIRF probe locations with STORM data.
            Functions and methods used in storm:
                set_storm_file: Set the STORM file for STORM analysis.
                read_storm_to_DF: Read the STORM data from the provided STORM.txt file and return it as a pandas DataFrame.
                storm_prob: Extract the STORM source and detector optode locations from the STORM data.
                is_storm_valid: Validate the STORM data to ensure it contains valid source and detector optode locations.
                snirf_with_storm_prob: Update the SNIRF data with STORM optode locations and save the modified data back to the original SNIRF file.
                get_old_probe_locations: Get the original probe locations before updating with STORM data.
        invalid_sourc: Identify the source optode locations that have a Euclidean distance greater than or equal to the specified threshold
            from the original source optode locations.
        invalid_detec: Identify the detector optode locations that have a Euclidean distance greater than or equal to the specified threshold
            from the original detector optode locations.
            Functions and methods used in invalid_sourc and invalid_detec:
                euclidean_dist: Calculate the Euclidean distance between the optode locations before and after the STORM data update.
        
        generate_open_pose: General function to analyse open pose data for head movements and arm movements and save the results as motion labels with corresponding timestamps.
            Functions and methods used in generate_open_pose:    
                get_csv: Convert folder containing json files to csv file.
                extract_key_point: Extract the data from the data frame, according to the key points given.
                filter_confidence: Filter data based on confidence, if confidence is less than 0.5 in a specific key point and time frame, then
                    the data in this time frame is set to 0 so as to exclude it from further analysis.
                calculate_change_in_distance: Calculate the change in distance between two key points (for all key points).
                    Then calculate the change between consecutive time frames in the calculated data.
                calculate_change_in_position_per_frame: Calculate the change in position between consecutive time frames for all key points.
        

    Attributes:
        snirf_fname (pathlib.Path): The file path of the SNIRF file.
        snirf_data (Snirf): The loaded SNIRF data.
        storm_fname (pathlib.Path or None): The file path of the STORM file, if set.
        old_sourc_loc (numpy.ndarray or None): The original source optode locations.
        old_detc_loc (numpy.ndarray or None): The original detector optode locations.
        invalid_sourc(numpy.ndarray): the source optode locations that are off-place and invalid.
        invalid_detec(numpy.ndarray):the detector optode locations that are off-place and invalid.
        data (pd.DataFrame): data frame of the json file combined
        changed_frames (pd.DataFrame): data frame of the change in distance and position for each keypoint
            between consecutive time frames for each key point
        motion_label (pd.DataFrame): data frame of the motion labels for each timestamp
        """ 

    FRAMES_PER_SECOND = 30  # number of frames in a group for analysis of movement
    HEAD_KP = [0,1,2,5,15,16,17,18]
    ARM_KP = [1,2,3,4,5,6,7,8]


    def __init__(self, snirf_fname: str):

        if type(snirf_fname) == pathlib.WindowsPath:
            snirf_fname = str(snirf_fname)
        # check if snirf_fname is a string
        if type(snirf_fname) != str:
            raise TypeError("snirf_fname must be a string")
        # check if snirf_fname is empty
        if len(snirf_fname) == 0:
            raise ValueError("snirf_fname cannot be empty")
        # check if snirf_fname is a path
        # check if snirf_fname is a snirf file
        if not snirf_fname.endswith('.snirf'):
            raise ValueError("Not a snirf file.")
        # check if snirf_fname exists
        if not pathlib.Path(snirf_fname).exists():
            raise ValueError("snirf_fname does not exist")
            
        self.snirf_fname = pathlib.Path(snirf_fname)

        # Intialized the attributes
              
        self.old_sourc_loc = None
        self.old_detc_loc = None
        self.storm_fname = None
        self.hbo_data = HbOData(snirf_fname)
        self.events_handler = EventsHandler(snirf_fname)



    ######## HbO ########

    def set_hbo_data(self, channels: [int], with_storm: bool, low_pass_freq=0.01, high_pass_freq=0.5, path_length_factor=0.6):
        self.hbo_data.preprocess(channels, with_storm, low_pass_freq, high_pass_freq, path_length_factor)

        
    ######## STORM ########

    def storm(self,storm_fname,user_input : int = 0):
        """
    Update SNIRF probe locations with STORM data.
    If the STORM data is valid and the update is successful, the method prints a confirmation message.

    Parameters:
        storm_fname (str): The file path of the STORM.txt file.
        user_input (int): The user can choose to view the updated source and detector optode locations or they can skip the preview . Default is set to 0.

    Raises:
        ValueError: If the STORM file does not exist.

    Updates:
        snirf_detc_loc (numpy.ndarray): Updates the detector optode locations with the STORM data.
        snirf_sourc_loc (numpy.ndarray): Updates the source optode locations with the STORM data.
        old_detc_loc (numpy.ndarray): Stores the original detector optode locations if not already stored.
        old_sourc_loc (numpy.ndarray): Stores the original source optode locations if not already stored.
        """
        # check if storm_fname is a path
        if type(storm_fname) == pathlib.WindowsPath:
            storm_fname = str(storm_fname)
        # check if storm_fname is a string
        if type(storm_fname) != str:
            raise TypeError("storm_fname must be a string")
        # check if storm_fname is a txt file
        if not storm_fname.endswith('.txt'):
            raise ValueError("Not a txt file.")
        # check if storm_fname exists
        if not pathlib.Path(storm_fname).exists():
            raise ValueError("storm_fname does not exist")
        # check if storm_fname is empty
        if storm_fname is None:
            raise ValueError("storm_fname cannot be empty")
        # check if user_input is an integer
        if type(user_input) != int:
            raise TypeError("user_input must be an integer")
        # check if user_input is 0 or 1
        if user_input != 0 and user_input != 1:
            raise ValueError("user_input must be either 0 or 1")
        # check if user_input is empty
        if user_input is None:
            raise ValueError("user_input cannot be empty")
       
        try:
                data = Snirf(rf'{self.snirf_fname}', 'r+')
                data_backup = data
                self.snirf_detc_loc = data.nirs[0].probe.detectorPos3D[:,:]
                self.snirf_sourc_loc = data.nirs[0].probe.sourcePos3D[:,:]
                self.set_storm_file(storm_fname)
                self.snirf_with_storm_prob(data)

                print("Your snirf file has been updated.")

                if user_input == str(1):
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
            ValueError: If the STORM file does not exist.
            ValueError: If the STORM file is not in a txt format.
            ValueError: If the STORM file is empty.
            TypeError: If the STORM file is not a string or path Object.
            
        Updates:
            storm_fname (pathlib.Path): The file path of the STORM.txt file.
        """
        # check if storm_fname is a path
        if type(storm_fname) == pathlib.WindowsPath:
            storm_fname = str(storm_fname)
        # check if storm_fname is a string
        if type(storm_fname) != str:
            raise TypeError("storm_fname must be a string")
        # check if storm_fname is a txt file
        if not storm_fname.endswith('.txt'):
            raise ValueError("Not a txt file.")
        # check if storm_fname exists
        if not pathlib.Path(storm_fname).exists():
            raise ValueError("storm_fname does not exist")
        # check if storm_fname is empty
        if storm_fname is None:
            raise ValueError("storm_fname cannot be empty")
        
        self.storm_fname = pathlib.Path(storm_fname)
        self.storm_data = Niralysis.read_storm_to_DF(storm_fname)
    
    
    def read_storm_to_DF(storm_fname):
        """ 
        Read the STORM data from the provided STORM.txt file and return it as a pandas DataFrame.

        Parameters:
            storm_fname (str): The file path of the STORM.txt file.

        Raises:
            ValueError: If the STORM file does not exist.
            ValueError: If the STORM file is not in a txt format.
            ValueError: If the STORM file is empty.
            TypeError: If the STORM file is not a string or Path object.

        Returns:
            pd.DataFrame: The STORM data loaded from the file.
        """
        # check if storm_fname is a path
        if type(storm_fname) == pathlib.WindowsPath:
            storm_fname = str(storm_fname)
        # check if storm_fname is a string
        if type(storm_fname) != str:
            raise TypeError("storm_fname must be a string")
        # check if storm_fname is a txt file
        if not storm_fname.endswith('.txt'):
            raise ValueError("Not a txt file.")
        # check if storm_fname exists
        if not pathlib.Path(storm_fname).exists():
            raise ValueError("storm_fname does not exist")
        # check if storm_fname is empty
        if storm_fname is None:
            raise ValueError("storm_fname cannot be empty")

        
        storm_data = pd.read_csv(storm_fname,delim_whitespace=True, index_col=0, header=None)
        storm_data.index.name = None
        return storm_data
    

    ###### Processing STORM file ######

    def storm_prob(self):
        """
        Extract the STORM source and detector optode locations from the STORM data.

        Returns:
            Tuple[pandas.DataFrame, pandas.DataFrame]: A tuple containing the STORM source and detector optode locations as pandas DataFrames.
        
        Raises:
            ValueError: If the STORM data does not contain valid source or detector optode locations.
        """


        # Extract the STORM source and detector optode locations based on the index pattern

        storm_sourc_loc = self.storm_data[self.storm_data.index.astype(str).str.contains(r'^s\d+$')]
        storm_detc_loc = self.storm_data[self.storm_data.index.astype(str).str.contains(r'^d\d+$')]

        # Check if the extracted STORM data contains valid source and detector optode locations

        if len(storm_sourc_loc) == 0 or len(storm_detc_loc) == 0:
            raise ValueError("Invalid STORM data. Check your STORM file.")

        return storm_sourc_loc, storm_detc_loc
    

    ###### validation STORM file ######

    def is_storm_valid(self):
        """
        Validate the STORM data to ensure it contains valid source and detector optode locations.

        Raises:
            ValueError: If the STORM data contains NaN values or any integer columns, or if the number of STORM source or detector optode locations
                    does not match the number of optode locations in the SNIRF data."""
        
        # Get the STORM source and detector optode locations

        storm_sourc_loc, storm_detc_loc = self.storm_prob()

        # Check if the STORM data contains NaN values

        if storm_sourc_loc.isnull().values.any() or storm_detc_loc.isnull().values.any():
            raise ValueError("Invalid STORM data. Check your STORM file.")
        

        # Check if any column in the STORM data is of integer data type

        if any(storm_sourc_loc.dtypes == int or storm_detc_loc.dtypes ==int):
            raise ValueError("STORM data contains integer column(s). All columns should have float data type.")
        
         # Check if the number of STORM source or detector optode locations matches the number in the SNIRF data
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

        Updates:
            data (Snirf): The updated SNIRF data.
        """
        # Validate the STORM data
        try:
            self.is_storm_valid()
        except ValueError as error:
            print(error)
        # check if data is a Snirf object
        if type(data) != Snirf:
            raise TypeError("data must be a Snirf object")
        # check if data is empty
        if data is None:
            raise ValueError("data cannot be empty")

        
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
            Tuple[numpy.ndarray or None, numpy.ndarray or None]: A tuple containing the original source and detector optode locations.
        """

        return self.old_sourc_loc, self.old_detc_loc
    

    def euclidean_dist(self):
        """
        Calculate the Euclidean distance between the optode locations before and after the STORM data update.

        Returns:
            Tuple[numpy.ndarray, numpy.ndarray]: A tuple containing the Euclidean distances between the updated and original
                source optode locations and the updated and original detector optode locations."""
        
        # Retrieve the original source and detector optode locations
        self.old_sourc_loc, self.old_detc_loc = self.get_old_probe_locations()

        # Retrieve the current STORM source and detector optode locations
        storm_sourc_loc, storm_detc_loc = self.storm_prob()

        # Compute the Euclidean distances between the updated and original optode locations
        sourc_euclidean_dist = np.linalg.norm(storm_sourc_loc - self.old_sourc_loc, axis=1)
        detc_euclidean_dist = np.linalg.norm(storm_detc_loc - self.old_detc_loc, axis=1)

        return sourc_euclidean_dist, detc_euclidean_dist

    
    def invalid_sourc(self,thresh : int = 20):
        """
        Identify the source optode locations that have a Euclidean distance greater than or equal to the specified threshold
        from the original source optode locations.

        Parameters:
            thresh (float): The threshold value for the Euclidean distance. Default is set to 20 mm.

        Returns:
            numpy.ndarray: A NumPy array containing the source optode locations that crossed the Euclidean distance threshold, and therefore are off-place and invalid.
            """
        # check if thresh is an integer
        if type(thresh) != int:
            raise TypeError("thresh must be an integer")
        # check if thresh is positive
        if thresh < 0:
            raise ValueError("thresh must be a positive integer")
        # check if thresh is greater than 30 (the maximum distance between two optodes) if so, give a warning
        if thresh > 30:
            print("Warning: thresh is greater than 30 mm. This is the maximum distance between two adjacent optodes. Please check your input.")

        # Obtain the STORM source optode locations and the Euclidean distances
        storm_sourc_loc = self.storm_prob()[0]
        sourc_euclidean_dist = self.euclidean_dist()[0]
        sourc_euclidean_dist = np.array(sourc_euclidean_dist)

        # Filter the STORM source optode locations based on the Euclidean distance threshold
        invalid_sourc = storm_sourc_loc[sourc_euclidean_dist >= thresh]

        return invalid_sourc
    

    def invalid_detec(self,thresh : int = 20):
        """
        Identify the detector optode locations that have a Euclidean distance greater than or equal to the specified threshold
        from the original detector optode locations.

        Parameters:
            thresh (float): The threshold value for the Euclidean distance. Default is set to 10.

        Returns:
            numpy.ndarray: A NumPy array containing the detector optode locations that crossed the Euclidean
              distance threshold, and are therefore off-place and invalid.
        """
        # check if thresh is an integer
        if type(thresh) != int:
            raise TypeError("thresh must be an integer")
        # check if thresh is positive
        if thresh < 0:
            raise ValueError("thresh must be a positive integer")
        # check if thresh is greater than 30 (the maximum distance between two optodes) if so, give a warning
        if thresh > 30:
            print("Warning: thresh is greater than 30 mm. This is the maximum distance between two adjacent optodes. Please check your input.")
        
        # Obtain the STORM detector optode locations and the Euclidean distances
        storm_detc_loc = self.storm_prob()[1]
        detc_euclidean_dist = self.euclidean_dist()[1]
        detc_euclidean_dist = np.array(detc_euclidean_dist)

        # Filter the STORM detector optode locations based on the Euclidean distance threshold
        invalid_detec = storm_detc_loc[detc_euclidean_dist >= thresh]
        return invalid_detec

    
    ######## Openpose ########
    
    def get_csv(self, json_folder):
        """
        Convert folder containing json files to csv file.

        Args:
            json_folder (str): path to folder cotaining all json files of the recording
            
        Returns:
            data (pd.DataFrame): data frame of the json files combined and organized
            """
        # check if json_folder is a string
        if type(json_folder) != str:
            raise TypeError("json_folder must be a string")
        # check if json_folder is empty
        if len(json_folder) == 0:
            raise ValueError("json_folder cannot be empty")
        # check if json_folder is a path
        if type(json_folder) == pathlib.WindowsPath:
            json_folder = str(json_folder)
        
        return process_json_files(json_folder)

    def extract_key_point(self, key_points: list) -> pd.DataFrame:

        """
        Extract the data from the data frame, according to the key points given.

        Args:
            key_points (list): list of key points to extract

        Returns:
            filtered_key_point_data (pd.DataFrame): filtered data frame containing only the key points given
            """

        # check if key_points is a list
        if type(key_points) != list:
            raise TypeError("key_points must be a list")
        # check if key_points is empty
        if len(key_points) == 0:
            raise ValueError("key_points cannot be empty")
        # check if key_points contains only integers
        for key_point in key_points:
            if type(key_point) != int:
                raise TypeError("key_points must contain only integers")
        # check if key_points contains only integers between 0 and 24
        for key_point in key_points:
            if key_point < 0 or key_point > 24:
                raise ValueError("key_points must contain only integers between 0 and 24")
        
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

        """
        Filter data based on confidence, if confidence is less than 0.5 in a specific key point and time frame, then
        the data in this time frame is set to 0 so as to exclude it from further analysis. 
        If you wish to include all data, set confidence_threshold to 0.

        The columns are organized as follows: KP_1_x, KP_1_y, KP_1_confidence, KP_2_x, KP_2_y, KP_2_confidence, etc.

        Args:
            confidence_threshold (float): confidence threshold (default = 0.5) 
                defining the minimum confidence required for the data to be included in the analysis
            """
        
        #### Add case if filtered_key_point_data is the same as self.data
        # check if confidence_threshold is a float
        if type(confidence_threshold) != float:
            raise TypeError("confidence_threshold must be a float")
        # check if confidence_threshold is between 0 and 1
        if confidence_threshold < 0 or confidence_threshold > 1:
            raise ValueError("confidence_threshold must be between 0 and 1")
        # check if filtered_key_point_data is a pandas DataFrame
        if type(filtered_key_point_data) != pd.DataFrame:
            raise TypeError("filtered_key_point_data must be a pandas DataFrame")
        # check if filtered_key_point_data is empty
        if filtered_key_point_data.empty:
            raise ValueError("filtered_key_point_data cannot be empty")
        
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
        """    
        Calculate the change in distance between two key points (for all key points).
        Then calculate the change between consecutive time frames in the calculated data.

        Parameters:
            data (pd.DataFrame): The input data containing key points' coordinates at different time frames.

        Returns:
            pd.DataFrame: A DataFrame containing the change in distance between consecutive time frames for each pair of key points.
        """
        # check if data is empty
        if data.empty:
            raise ValueError("data cannot be empty")
        # check if data is a pandas DataFrame
        if type(data) != pd.DataFrame:
            raise TypeError("data must be a pandas DataFrame")
        
        distance_table = calculate_pairwise_distance(data)
        change_in_distance_table = Niralysis.calculate_change_in_position_per_frame(distance_table)
        return change_in_distance_table
        

    def calculate_change_in_position_per_frame(data):
        """    
        Calculate the change in position between consecutive time frames for all key points.

        Parameters:
            data (pd.DataFrame): The input data containing key points' coordinates at different time frames.

        Returns:
            pd.DataFrame: A DataFrame containing the change in position between consecutive time frames for all key points.
        """
        # check if data is empty
        if data.empty:
            raise ValueError("data cannot be empty")
        # check if data is a pandas DataFrame
        if type(data) != pd.DataFrame:
            raise TypeError("data must be a pandas DataFrame")
        
        change_in_position_table = get_table_of_deltas_between_time_stamps_in_all_kps(data)
        return change_in_position_table

    def generate_open_pose(self, path_to_open_pose_output_folder: str, key_points_to_extract: int = 0, beginning_of_recording: int = 0):

        """
        General function to analyse open pose data for head movements and arm movements
        and save the results as motion labels with corresponding timestamps. 

        Args:
            path_to_open_pose_output_folder (str): path to open pose output folder (folder containing all json files)
            beginning_of_recording (int): starting time of the recording to transform the timestamps (as frames) to seconds (FUNCTIONALITY NOT AVAILABLE YET)
            key_points_to_extract (list): 0 (defualt) to extract only head key points, 1 to extract head and arms key points

        Adds to self:
            data (pd.DataFrame): data frame of the json file combined
            changed_frames (pd.DataFrame): data frame of the change in distance and position for each keypoint
              between consecutive time frames for each key point
            motion_label (pd.DataFrame): data frame of the motion labels for each timestamp
            """
        
        if type(key_points_to_extract) != int:
            raise TypeError("key_points_to_extract must be an integer")
        if key_points_to_extract > 1 or key_points_to_extract < 0:
            raise ValueError("key_points_to_extract must be 0 (Just head) or 1 (Head and arms))")
        if type(path_to_open_pose_output_folder) == pathlib.WindowsPath:
            path_to_open_pose_output_folder = str(path_to_open_pose_output_folder)
        if type(path_to_open_pose_output_folder) != str:
            raise TypeError("path_to_open_pose_output_folder must be a string")
        if type(beginning_of_recording) != int:
            raise TypeError("beginning_of_recording must be an integer (time in seconds)")
        if beginning_of_recording < 0:
            raise ValueError("beginning_of_recording must be a positive integer")
        
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
        self.motion_label = events_to_labels(self.changed_frames)




            


    






