import numpy
import pandas as pd
from numpy import mean, corrcoef, zeros
from niralysis.utils.consts import *
from niralysis.utils.data_menipulation import set_data_by_areas


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
            n_channels: number of channels.
            sampling_rate: sampling rate in seconds. Used to divide the time series to 5 seconds bins.

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
    def ISC_by_events(events_table: pd.DataFrame, df_A: pd.DataFrame, df_B: pd.DataFrame, sampling_rate: float = 0.02,
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

                n_channels: number of channels.
                sampling_rate: sampling rate in seconds. Used to divide the time series to 5 seconds bins.

                output_path: a pth to csv file, if given the function will save the returned data frame in to the
                given path.



            Returns:
                pd.DataFrame: table of ISC values, each row is an ISC values of each channel at a certain event.

        """

        if df_A.shape[1] != df_B.shape[1]:
            raise ValueError('df_A and df_B does not contain the same channels')

        if by_areas is not None:
            df_A = set_data_by_areas(df_A, by_areas)
            df_B = set_data_by_areas(df_B, by_areas)

        events_labels = events_table[EVENT_COLUMN].tolist()
        ISC_table = pd.DataFrame(index=events_labels, columns=df_A.columns[1:])

        for i in range(len(events_labels)):
            starting_time = events_table[START_COLUMN][i]
            ending_time = events_table[END_COLUMN][i]
            A_event = df_A[(df_A[TIME_COLUMN] >= starting_time) & (df_A[TIME_COLUMN] <= ending_time)]
            B_event = df_B[(df_A[TIME_COLUMN] >= starting_time) & (df_B[TIME_COLUMN] <= ending_time)]

            ISC_table.iloc[i] = ISC.ISC(A_event, B_event, sampling_rate)

        if output_path is not None:
            if not output_path.endswith('.csv'):
                raise ValueError('Output path must end with .csv')
            ISC_table.to_csv(output_path)

        return ISC_table
