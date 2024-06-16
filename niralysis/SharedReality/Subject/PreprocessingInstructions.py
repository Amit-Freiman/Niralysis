from typing import Optional

from niralysis.SharedReality.consts import *


class PreprocessingInstructions:
    def __init__(self, areas_dict: dict = None, channels: Optional[int] = None, with_storm: bool = False,
                 low_freq: float = DEFAULT_LOW_FREQ,
                 high_freq: float = DEFAULT_HIGH_FREQ,
                 path_length_factor: float = DEFAULT_PATH_LENGTH_FACTOR, scale: float = DEFAULT_SCALE,
                 invalid_source_thresh: int = DEFAULT_INVALID_SOURCE_THRESH,
                 invalid_detectors_thresh: int = DEFAULT_INVALID_DETECTORS_THRESH,
                 bad_channels: [str] = []):
        self.channels = channels
        self.with_storm = with_storm
        self.low_freq, self.high_freq = low_freq, high_freq
        self.path_length_factor = path_length_factor
        self.scale = scale
        self.invalid_source_thresh = invalid_source_thresh
        self.invalid_detectors_thresh = invalid_detectors_thresh
        self.areas_dict = areas_dict
        self.bad_channels = bad_channels