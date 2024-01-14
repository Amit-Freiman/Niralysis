import mne
import pandas as pd
import pathlib
import numpy as np
class HbOData:

    """
    HbOData is a class to handle the HbO data of g given snirf file.


    It holds the events frame - a table in witch every row is an event with columns=['event', 'time', 'duration']

    """

    def __init__(self, path: str):
        self.raw_data = mne.io.read_raw_snirf(path, preload=True)
        self.data = self.raw_data.get_data()
        self.events = None
        self.concentrated_data = None
        self.set_events_frame()
        self.data_frame = None

    def set_events_frame(self) -> None:
        if self.raw_data.annotations is None:
            self.events = None

        events = pd.DataFrame(columns=['event', 'time', 'duration'])
        events['event'] = self.raw_data.annotations.description
        events['time'] = self.raw_data.annotations.onset
        events['duration'] = self.raw_data.annotations.duration
        self.events = events

    def get_events_frame(self) -> pd.DataFrame | None:
        return self.events

    def preprocess(self, channels: [int], low_pass_freq, high_pass_freq, path_length_factor):

        processed_data = mne.preprocessing.nirs.optical_density(self.raw_data)
        processed_data = processed_data.filter(l_freq=low_pass_freq, h_freq=high_pass_freq)
        concentrated_data = mne.preprocessing.nirs.beer_lambert_law(processed_data, path_length_factor)
        channels_to_drop = [concentrated_data.ch_names[i] for i, ch_type in
                            enumerate(concentrated_data.get_channel_types()) if ch_type != 'hbo']
        concentrated_data = concentrated_data.drop_channels(channels_to_drop)
        data_frame = pd.DataFrame(concentrated_data.get_data().T, columns=concentrated_data.ch_names)
        data_frame.insert(0, 'time', concentrated_data.times)
        self.data_frame = 0.1 * data_frame
