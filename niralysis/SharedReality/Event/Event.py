from typing import Optional

from niralysis.HbOData.HbOData import HbOData
from niralysis.SharedReality.Subject.PreprocessingInstructions import PreprocessingInstructions
from niralysis.utils.data_manipulation import set_data_by_areas


class Event:
    def __init__(self, name, raw_data=None, data_frame=None, data_by_area=None):
        self.name = name
        self.data = HbOData('', raw_data, data_frame, data_by_area)

    def preprocess(self, instructions: PreprocessingInstructions):
        self.data.preprocess(instructions.channels, with_storm=instructions.with_storm, low_freq=instructions.low_freq,
                             high_freq=instructions.high_freq,
                             path_length_factor=instructions.path_length_factor, scale=instructions.scale,
                             bad_channels=instructions.bad_channels,
                             with_optical_density=False)

    def get_data(self):
        return self.data.get_hbo_data()

    def set_by_areas(self, areas: dict):
        self.data.data_by_areas = set_data_by_areas(self.data.user_data_frame, areas)

    def get_data_by_areas(self):
        return self.data.get_hbo_data_by_areas()
