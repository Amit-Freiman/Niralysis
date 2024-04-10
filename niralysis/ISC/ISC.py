import numpy
import pandas as pd
from numpy import mean, corrcoef, zeros

from niralysis.SharedReality.Subject.Subject import Subject
from niralysis.SharedReality.consts import EVENTS_TABLE_NAMES
from niralysis.utils.consts import *
from niralysis.utils.data_manipulation import set_data_by_areas


class ISC:

    @staticmethod
    def get_binned_signals(df: pd.DataFrame, timepoints_per_bin: int):
        n_bins = round(df.shape[0] / timepoints_per_bin)
        df = df.drop(columns=TIME_COLUMN)
        binned_signal = []

        for i in range(n_bins - 1):
            start_row = i * timepoints_per_bin
            end_row = start_row + timepoints_per_bin
            binned_data = mean(df.iloc[start_row:end_row, :], axis=0)
            binned_signal.append(binned_data)

        return pd.DataFrame(binned_signal)

    @staticmethod
    def ISC(df_A: pd.DataFrame, df_B: pd.DataFrame, sampling_rate: float, by_areas: dict = None) -> numpy.array:
        """
        Calculates the ISC - Inter subject correlation between two subjects fNIRS measures of a certain event.

        This function takes a two DataFrames containing HbO values coordinates and computes the person correlation
        between the subjects HbO values at each chanel.

        Parameters:
            df_A (pd.DataFrame): DataFrame containing HbO values coordinates from object A measurements.
                The DataFrame should have columns for 'Time' and channels, so each row represent the measured HbO values
                of each channel in a certain time.
            df_B (pd.DataFrame): DataFrame containing HbO values coordinates from object A measurements.
                The DataFrame should have columns for 'Time' and channels, so each row represent the measured HbO values
                of each channel in a certain time.
            sampling_rate: sampling rate in seconds. Used to divide the time series to 5 seconds bins.
            by_areas : A dict that maps channels to brain areas, if given the ISC will be calculated between the mean
                    HbO values of each brain's area channel, if None, the ISC will be calculated between each channel.
                     key: brain area name, value: list of channels name, S<number>_D<number>
        Returns:
            pd.DataFrame: vector of ISC values for each channel
        """
        if by_areas is not None:
            df_A = set_data_by_areas(df_A, by_areas)
            df_B = set_data_by_areas(df_B, by_areas)

        n_channels = df_A.shape[1] - 1

        timepoints_per_bin = 5 / sampling_rate
        A_binned_signal = ISC.get_binned_signals(df_A, int(timepoints_per_bin))
        B_binned_signal = ISC.get_binned_signals(df_B, int(timepoints_per_bin))

        if (A_binned_signal.shape[0] != B_binned_signal.shape[0]):
            min_timepoints = min(A_binned_signal.shape[0], B_binned_signal.shape[0])
            A_binned_signal = A_binned_signal.iloc[:min_timepoints, :]
            B_binned_signal = B_binned_signal.iloc[:min_timepoints, :]

        channels_corr = zeros(n_channels)

        # Pearson's correlation coefficient of each channel
        for channel in range(n_channels):
            channels_corr[channel] = corrcoef(A_binned_signal.iloc[:, channel], B_binned_signal.iloc[:, channel])[0, 1]

        return channels_corr

    @staticmethod
    def ISC_by_events(A_events_table: pd.DataFrame, B_events_table: pd.DataFrame, df_A: pd.DataFrame, df_B: pd.DataFrame, sampling_rate: float = 0.02,
                      by_areas: dict = None,
                      output_path=None):
        """
            Function to compute correlation between fNIRS measures of two objects, while attending a series of events,
            Parameters:
                events_table_path (str): path to the table of events, csv file. Table must be as formatted as follow:
                 each row represents an event. Table must have the following columns:
                        Event - the name of the event
                        Start - time stamp (in seconds) of the event's starting time
                        End - time stamp (in seconds) of the event's end

                df_A (pd.DataFrame): DataFrame containing HbO values coordinates from object A measurements..
                    The DataFrame should have columns for 'Time' and channels, so each row represent the measured HbO values
                    of each channel in a certain time.

                df_B (pd.DataFrame): DataFrame containing HbO values coordinates from object A measurements..
                    The DataFrame should have columns for 'Time' and channels, so each row represent the measured
                    HbO values of each channel in a certain time.

                sampling_rate: sampling rate in seconds. Used to divide the time series to 5 seconds bins.
                by_areas : A dict that maps channels to brain areas, if given the ISC will be calculated between the mean
                        HbO values of each brain's area channel, if None, the ISC will be calculated between each channel.
                         key: brain area name, value: list of channels name, S<number>_D<number>
                output_path: a pth to csv file, if given the function will save the returned data frame in to the
                given path.



            Returns:
                pd.DataFrame: table of ISC values, each row is an ISC values of each channel at a certain event.

        """

        if by_areas is None and df_A.shape[1] != df_B.shape[1]:
            raise ValueError('df_A and df_B does not contain the same channels')

        if not A_events_table[EVENT_COLUMN].equals(B_events_table[EVENT_COLUMN]):
            raise ValueError('A_events_table and B_events_table does not contain the same events')

        if by_areas is not None:
            df_A = set_data_by_areas(df_A, by_areas)
            df_B = set_data_by_areas(df_B, by_areas)

        events_labels = A_events_table[EVENT_COLUMN].tolist()
        ISC_table = pd.DataFrame(index=events_labels, columns=df_A.columns[1:])

        for i in range(len(events_labels)): # to fix watching order is not necessarily the same, event index in a is
            # not the same as in be (candidates videos)
            A_starting_time = A_events_table[START_COLUMN][i]
            A_ending_time = A_events_table[END_COLUMN][i]
            A_event = df_A[(df_A[TIME_COLUMN] >= A_starting_time) & (df_A[TIME_COLUMN] <= A_ending_time)]

            B_starting_time = B_events_table[START_COLUMN][i]
            B_ending_time = B_events_table[END_COLUMN][i]
            B_event = df_B[(df_B[TIME_COLUMN] >= B_starting_time) & (df_B[TIME_COLUMN] <= B_ending_time)]

            ISC_table.iloc[i] = ISC.ISC(A_event, B_event, sampling_rate)

        if output_path is not None:
            if not output_path.endswith('.csv'):
                raise ValueError('Output path must end with .csv')
            ISC_table.to_csv(output_path)

        return ISC_table


    @staticmethod
    def subjects_ISC_by_events(subject_A: Subject, subject_B: Subject, sampling_rate: float = 0.02, output_path=None,
                               use_default_events: bool = False):
        """
            Function to compute correlation between fNIRS measures of two Subject Class instances', while attending
            a series of events,
            Parameters:
                subject_A (Subject):

                subject_B (Subject): instance of Subject with contains subject's B data

                sampling_rate: sampling rate in seconds. Used to divide the time series to 5 seconds bins.
                by_areas : A dict that maps channels to brain areas, if given the ISC will be calculated between the mean
                        HbO values of each brain's area channel, if None, the ISC will be calculated between each channel.
                         key: brain area name, value: list of channels name, S<number>_D<number>
                output_path: a pth to csv file, if given the function will save the returned data frame in to the
                given path.

            Returns:
                pd.DataFrame: table of ISC values, each row is an ISC values of each channel at a certain event.

        """
        df_A = subject_A.get_hbo_data()

        if use_default_events:
            events_labels = EVENTS_TABLE_NAMES
        else:
            events_labels = subject_A.events_table[EVENT_COLUMN].tolist()
        ISC_table = pd.DataFrame(index=events_labels, columns=df_A.columns[1:])

        for index, event_name in enumerate(events_labels):
            A_event = subject_A.get_event_data_table(index, event_name)
            B_event = subject_B.get_event_data_table(index, event_name)
            if A_event is None:
                raise ValueError(f'subject A does not have the event {event_name}')
            if B_event is None:
                raise ValueError(f'subject B does not have the event {event_name}')


            ISC_table.iloc[index] = ISC.ISC(A_event, B_event, sampling_rate)

        if output_path is not None:
            if not output_path.endswith('.csv'):
                raise ValueError('Output path must end with .csv')
            ISC_table.to_csv(output_path)

        return ISC_table