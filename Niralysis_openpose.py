import pandas as pd
from jsonOrganizer import process_json_files


class Niralysis:
    """Class for fNIR analysis of OpenPose"""

    FRAMES_PER_SECOND = 30  # number of frames in a group for analysis of movement

    def __init__(self, fname: str):
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
        self.check_key_point_input()
        # Set key_points_according_to_column_headers
        columns_to_include = ["frame"]
        for key_point in key_points:
            for header in self.data.columns[0]:
                if key_point in header:
                    columns_to_include.append(header)

        # extract key points
        filtered_key_point_data = self.data[columns_to_include]
        return filtered_key_point_data

    def filter_confidence(self, confidence_threshold: float = 0.5):
        """Filter data based on confidence, if confidence is less than 0.5 in a specific key point and time frame, then
        the data in this time frame is set to 0.
        The columns are organized as follows: KP_1_x, KP_1_y, KP_1_confidence, KP_2_x, KP_2_y, KP_2_confidence, etc.
        Args:
            confidence_threshold (float): confidence threshold
        """
        for column in self.data.columns:
            if "confidence" in column:
                for confidence_per_time_stamp in self.data[column]:
                    # If confidence is less than TH, set the data in this time frame to 0 in both x and y coordinates
                    if confidence_per_time_stamp < confidence_threshold:
                        # set the values in the x and y rows in this key point to 0
                        self.data[column - 2] = 0
                        self.data[column - 1] = 0

    def check_movement(self):
        """"""
        pass

    def calculate_change_in_position_per_frame(self):
        """"""
        pass

    def generate_motion_labels_by_change(self):
        """Generate motion labels per time stamp according to change in x and y coordinates"""

    def generate_open_pose(self, path_to_open_pose_output_folder: str, beginning_of_recording: list, key_points_to_extract: list):
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
        self.filter_confidence()


    def filter_labels(self):
        """Filter data using timestamps of motion labels"""
        pass

    def check_key_point_input(self):
        """"""
        pass
