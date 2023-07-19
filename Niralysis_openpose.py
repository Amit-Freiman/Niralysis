
class Niralysis:
    """Class for fNIR analysis of OpenPose"""
    def __init__(self, json_file):
        self.data = self.get_csv(json_file)
        self.frames_per_second = 30  # number of frames in a group for analysis of movement

    def get_csv(self, json_file):
        """Convert json to csv
        Args:
            json_file (str): path to json file
        Returns:
            csv (list): list of lists
        """
        pass

    def extract_key_point(self, key_points: list):
        """"""
        pass

    def filter_confidence(self):
        """"""
        pass

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
            path_to_open_pose_output_folder (str): path to open pose output folder
            beginning_of_recording (list): list of lists of the beginning of the recording
            key_points_to_extract (list): list of key points to extract
        Returns:
            open_pose_data (list): list of lists of open pose data
        """
        pass

    def filter_labels(self):
        """Filter data using timestamps of motion labels"""
        pass

    def check_key_point_input(self):
        """"""
        pass
