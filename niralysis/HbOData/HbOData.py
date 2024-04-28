from typing import Optional
import re
import mne
import pandas as pd
from niralysis.Storm.Storm import Storm
from niralysis.utils.consts import *
from itertools import compress

from niralysis.utils.data_manipulation import set_data_by_areas


class HbOData:
    """
    Class to handle HbO date
     Args:
        path (string): Path to the SNIRF file.

     Methods:
        Preprocess - Preprocess HbO measurements from a raw fNIRS  signals within a SNIRF, across all channels.
        Preprocessing includes:
            drops channels from invalid source and invalid detectors by storm
            convert intensity to optical density
            filter low and high frequency bands
            convert from optical density to concentration difference
            convert to micro molar by given scale

    """

    def __init__(self, path: str):
        self.user_data_frame = None
        self.all_data_frame = None
        self.raw_data = mne.io.read_raw_snirf(path, preload=True)
        self.data = self.raw_data.get_data()
        self.concentrated_data = None
        self.storm_path = None
        self.storm = Storm(path)
        self.invalid_sourc = None
        self.invalid_detec = None
        self.bad_channels = None
        self.data_by_areas = None


    def set_storm_path(self, storm_path: str):
        """
         Set the storm's file's path
        @param storm_path:
        """
        self.storm.check_storm_fname(storm_path)
        self.storm_path = storm_path

    def preprocess(self, channels: Optional[int], with_storm: bool = True, low_freq: float = 0.01,
                   high_freq: float = 0.5,
                   path_length_factor: float = 0.6, scale: float = 0.1, invalid_source_thresh: int = 20,
                   invalid_detectors_thresh: int = 20):
        """
        Preprocess HbO measurements from a raw fNIRS signals within a SNIRF, across all channels.
        Preprocessing includes:
            drops channels from invalid source and invalid detectors by storm
            convert intensity to optical density
            filter low and high frequency bands
            convert from optical density to concentration difference
            convert to micro molar by given scale

        Creates a data Frame with column - 'time', ...relevant valid channels
        Each raw represents the processed measurements of the HbO values at a certain time in each channel.
        saves data frame in 'self.all_data_frame'

        If a list of channels is provided creates the above frame only with the listed valid channels, saves
        data frame in 'self.user_data_frame'

        @param channels:  [int], A list of channels indexes to focus
        @param with_storm: if True, drops channels with invalid source or detectors, requires to set a storm file path
                           by method - "set_storm_path(storm_path)"
        @param low_freq: method will filter values beneath low_freq
        @param high_freq: method will filter values above low_freq
        @param path_length_factor: The partial pathlength factor for beer lambert law
        @param scale: scale to convert to micro molar
        @param invalid_source_thresh: The threshold value for the Euclidean distance
        @param invalid_detectors_thresh: The threshold value for the Euclidean distance.
        @return: data Frame with column - 'time', ...relevant valid channels
                Each raw represents the processed measurements of the HbO values at a certain time in each channel.
                If a list of channels is provided returns only the valid listed channels.
        """

        # if storm - drop channels from invalid_sourc and invalid_detector
        if with_storm:
            if self.storm_path is None:
                raise Exception('Could not find a storm\'s path.\n Please set a storm file path by method '
                                '- "set_storm_path(storm_path)"')
            self.storm.set_storm_file(self.storm_path)
            self.invalid_sourc = self.storm.invalid_sourc(invalid_source_thresh)
            self.invalid_detec = self.storm.invalid_detec(invalid_detectors_thresh)

        # convert intensity to optical density
        processed_data = mne.preprocessing.nirs.optical_density(self.raw_data)

        # evaluate the quality of the data using a scalp coupling index (SCI)
        sci = mne.preprocessing.nirs.scalp_coupling_index(processed_data)
        self.bad_channels = list(compress(processed_data.ch_names, sci < 0.7))
        processed_data = processed_data.drop_channels(self.bad_channels)

        # apply temporal derivative distribution repair (tddr) to remove motion artifacts
        processed_data = mne.preprocessing.nirs.tddr(processed_data)

        # filter low and high frequency bands
        filtered_data = processed_data.filter(l_freq=low_freq, h_freq=high_freq)  # N-EQ

        # convert from optical density to concentration difference
        concentrated_data = mne.preprocessing.nirs.beer_lambert_law(filtered_data, path_length_factor)

        # extract HbO measurements and drops invalid channels
        channels_to_drop = [concentrated_data.ch_names[i] for i, ch_type in
                            enumerate(concentrated_data.get_channel_types()) if ch_type != 'hbo' or
                            self.is_storm_invalid_channel(concentrated_data.ch_names[i], with_storm)]
        concentrated_data = concentrated_data.drop_channels(channels_to_drop)
        # Add channel names dropped to "bad_channels" attribute
        self.bad_channels += channels_to_drop

        data_frame = pd.DataFrame(concentrated_data.get_data().T, columns=concentrated_data.ch_names)

        # convert to micro molar
        data_frame = scale * data_frame
        data_frame.insert(0, TIME_COLUMN, concentrated_data.times)
        self.all_data_frame = data_frame
        self.user_data_frame = data_frame.iloc[:, channels] if channels else data_frame  # set given channels to focus

        return self.user_data_frame

    def is_storm_invalid_channel(self, channel_name: str, with_storm: bool) -> bool:
        """
        Checks if a channel should be filtered out do to invalid source or detectors locations
        @param channel_name:
        @param with_storm: True to check if a channel should be filtered out by storm
        @return: True if a channel should be filtered
        """
        if with_storm:
            source, detector, type = re.split(r"[ _]", channel_name)
            return (source.lower() in self.invalid_sourc.index.tolist() or detector.lower() in
                    self.invalid_detec.index.tolist())
        return False

    def get_hbo_data(self):
        if self.user_data_frame is None:
            raise Exception("No Data Frame is available, make sure to create data frame by the preprocess function")
        return self.user_data_frame

    def set_data_by_areas(self, areas: dict):
        if self.user_data_frame is None:
            raise Exception("No Data Frame is available, make sure to create data frame by the preprocess function")

        self.data_by_areas = set_data_by_areas(self.user_data_frame, areas)

    def get_hbo_data_by_areas(self):
        if self.data_by_areas is None:
            raise Exception("No Data Frame is available, make sure to create data frame by the set_data_by_areas "
                            "function")
        return self.data_by_areas
