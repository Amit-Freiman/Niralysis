from typing import Optional


class PreprocessingInstructions:
    def __init__(self, channels: Optional[int]=None, with_storm: bool = True, low_freq: float = 0.01,
                   high_freq: float = 0.5,
                   path_length_factor: float = 0.6, scale: float = 0.1, invalid_source_thresh: int = 20,
                   invalid_detectors_thresh: int = 20):
        self.channels = channels
        self.with_storm = with_storm
        self.low_freq, self.high_freq = low_freq, high_freq
        self.path_length_factor = path_length_factor
        self.scale = scale
        self.invalid_source_thresh = invalid_source_thresh
        self.invalid_detectors_thresh = invalid_detectors_thresh
