import pandas as pd
from jsonOrganizer import process_json_files
from calculate_differences import get_table_of_deltas_between_time_stamps_in_all_kps
from calculate_pairwise_distance import calculate_pairwise_distance



class Niralysis:
    """Class for fNIR analysis of OpenPose"""

    FRAMES_PER_SECOND = 30  # number of frames in a group for analysis of movement
    HEAD_KP = [0,1,2,5,15,16,17,18]
    ARM_KP = [1,2,3,4,5,6,7,8]

    def __init__(self):
        """
        Initialize the class
        Args:
            fname (str): path to .snirf file
        """
        # Add Nina and Naama's init code here

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
        
        # Set key_points_according_to_column_headers
        column_names = self.data.columns
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

    def generate_open_pose(self, path_to_open_pose_output_folder: str, beginning_of_recording: list = 0, key_points_to_extract: list = HEAD_KP):
        """Generates attribute file.motionlabels (Timestamps for certain motion labels from video)
        Args:
            path_to_open_pose_output_folder (str): path to open pose output folder (folder containing all json files)
            beginning_of_recording (list): list of lists of the beginning of the recording
            key_points_to_extract (list): list of key points to extract
        Returns:
            open_pose_data (list): list of lists of open pose data
        """
        self.data = self.get_csv(path_to_open_pose_output_folder)
        df_extracted = self.extract_key_point(key_points_to_extract)
        df_filtered = Niralysis.filter_confidence(df_extracted)
        self.change_in_position = Niralysis.calculate_change_in_position_per_frame(df_filtered)
        self.change_in_distance = Niralysis.calculate_change_in_distance(df_filtered)

    def filter_labels(self):
        """Filter data using timestamps of motion labels"""
        pass

    def check_key_point_input(self):
        """"""
        pass
