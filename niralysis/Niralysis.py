import pathlib

from niralysis.SharedReality.Subject.PreprocessingInstructions import PreprocessingInstructions
from niralysis.Storm.Storm import Storm
from niralysis.OpenPose.OpenPose import OpenPose
from niralysis.HbOData.HbOData import HbOData
from niralysis.EventsHandler.EventsHandler import EventsHandler
from niralysis.utils.consts import HEAD_KP, ARM_KP
from niralysis.calculators.calculate_differences import get_table_of_summed_distances_for_kp_over_time
from niralysis.utils.Events_to_label import events_to_labels



class Niralysis:

    """
    Initialize a Niralysis object with a SNIRF file.

    Parameters:

        snirf_fname (str): The file path of the SNIRF file.
    
    Methods:

        set_hbo_data: Set the HbO data for the SNIRF file.

        update_probe_loc_storm : Update SNIRF probe locations with STORM data.
            Functions and methods used in update_probe_loc_storm:
                storm: Load the STORM data.
                invalid_sourc: Identify the source optode locations that have a Euclidean distance greater than or equal to the specified threshold
                    from the original source optode locations.
                invalid_detec: Identify the detector optode locations that have a Euclidean distance greater than or equal to the specified threshold
                    from the original detector optode locations.
        
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
        snirf_fname (str): The file path of the SNIRF file.
        old_sourc_loc (pd.DataFrame): The original source optode locations.
        old_detc_loc (pd.DataFrame): The original detector optode locations.
        storm_fname (str): The file path of the STORM file.
        hbo_data (HbOData): HbOData object.
        events_handler (EventsHandler): EventsHandler object.
        invalid_optodes (list): The source and detector optode locations that are off-place and therefor invalid.

    
        """ 


    def __init__(self, snirf_fname: str, preprocessing_instructions = PreprocessingInstructions()):

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
        self.preprocessing_instructions = preprocessing_instructions


    ######## HbO ########

    def set_full_hbo_data(self, preprocess=False):
        if preprocess:
            self.hbo_data.preprocess(channels=self.preprocessing_instructions.channels,
                                     with_storm=self.preprocessing_instructions.with_storm,
                                     low_freq=self.preprocessing_instructions.low_freq,
                                     high_freq=self.preprocessing_instructions.high_freq,
                                     path_length_factor=self.preprocessing_instructions.path_length_factor,
                                     bad_channels=self.preprocessing_instructions.bad_channels)
        else:
            self.hbo_data.set_data_frame(self.preprocessing_instructions.bad_channels)


    ######## STORM ########
        
    def update_probe_loc_storm(self, storm_fname: str, print_prob_loc: bool = False, invalid_optodes: bool = False, distance_threshold: int = 20):
        """
        Update SNIRF probe locations with STORM data.

        Args:
            storm_fname (str): The file path of the STORM file.
            print_prob_loc (bool): Print the updated source and detector optode locations.
            invalid_optodes (bool): Identify the source and detector optode locations that have a Euclidean distance greater than or equal to the specified threshold
                from the original source and detector optode locations.
            distance_threshold (int): The Euclidean distance threshold

        Updates:
            invalid_optodes (list): The source and detector optode locations that are off-place and therefor invalid.

        Returns:
            None
        """
        storm = Storm(self.snirf_fname)
        storm.storm(storm_fname, print_prob_loc)
        in_source = storm.invalid_sourc(distance_threshold)
        in_detector = storm.invalid_detec(distance_threshold)
        self.invalid_optodes = [in_source, in_detector]


    ######## Openpose ########

    def generate_open_pose(self, path_to_open_pose_output_folder: str, key_points_to_extract: int = 0, beginning_of_recording: int = 0):

        """
        General function to analyse open pose data for head movements and arm movements
        and save the results as motion labels with corresponding timestamps. 

        Args:
            path_to_open_pose_output_folder (str): path to open pose output folder (folder containing all json files)
            beginning_of_recording (int): starting time of the recording to transform the timestamps (as frames) to seconds (FUNCTIONALITY NOT AVAILABLE YET)
            key_points_to_extract (list): 0 (defualt) to extract only head key points, 1 to extract head and arms key points

        Updates:
            data (pd.DataFrame): data frame of the json file combined
            changed_frames (pd.DataFrame): data frame of the change in distance and position for each keypoint
                between consecutive time frames for each key point
            motion_label (pd.DataFrame): data frame of the motion labels for each timestamp
            
        Returns:
            op_data (OpenPose): OpenPose object with the updated data, changed_frames and motion_label
        
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
            key_points_to_extract = HEAD_KP
        else:
            key_points_to_extract = ARM_KP + HEAD_KP
        
        op_data = OpenPose(path_to_open_pose_output_folder)
        op_data.data = op_data.get_csv(path_to_open_pose_output_folder)
        df_extracted = op_data.extract_key_point(key_points_to_extract)
        df_filtered = OpenPose.filter_confidence(df_extracted)
        change_in_position = OpenPose.calculate_change_in_position_per_frame(df_filtered)
        change_in_distance = OpenPose.calculate_change_in_distance(df_filtered)
        op_data.changed_frames = get_table_of_summed_distances_for_kp_over_time(change_in_position, change_in_distance, 50)
        op_data.motion_label = events_to_labels(op_data.changed_frames)

        return op_data



            


    






