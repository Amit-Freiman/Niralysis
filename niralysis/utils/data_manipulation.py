import pandas as pd

from niralysis.utils.consts import TIME_COLUMN


def set_data_by_areas(df: pd.DataFrame, areas: dict) -> pd.DataFrame:
    """
    Function re set the data from representing channels measurements to represent brain area's measurements.
    Each area will be a mean value of all the channels that are associated with the channel according to areas
    dictionary.


    @param df: HbO values data table, first column - 'Time', each other column is a certain channel's measurements
            values. Each row is the value of all the channels in a given time
    @param areas: dictionary that associate brain areas and channels - keys: brain area name, value: a list of
            channels names.
    @return: HbO values data table, first column - 'Time', each other column is a certain brain's area measurements
            values. Each row is the value of all the brain's area in a given time

    """
    data_by_area = pd.DataFrame()
    data_by_area[TIME_COLUMN] = df[TIME_COLUMN]
    for area in areas.keys():
        valid_channels = [f"{channel} hbo" for channel in areas[area] if f"{channel} hbo" in df.columns]
        data_by_area[area] =df[valid_channels].mean(axis=1)

    return data_by_area


def set_before_and_after_difference_table(ISC_table: pd.DataFrame, events: [str]):
    """
    Function calculates the difference between the score of event in its first appearance and its second appearance
    @param events_score_table: each row of the dataframe is an event and its score in the different channels /
            brain areas.
    @param events: list of events to calculate the difference between their double appearance
    @return: data table, each row of the dataframe is an event from the given list of events. Each row of the dataframe
             is the difference between the score of event in its first appearance and its second appearance in the
             different channels / brain areas.
    """

    difference_table = pd.DataFrame()

    for event in events:
        difference_table.append(ISC_table.loc[event].iloc[0] - ISC_table.loc[event].iloc[1], index=event)



def calculate_mean_table(data_tables: [pd.DataFrame]):
    """
    Function creates a data table witch the value of every cell is the mean value of the same cell in all the given
    data tables.

    @param data_tables: A list of data frames, all with the same structure (columns and indexes)
    @return: A single data frame
    """

    mean_table = data_tables[0]
    for data_table in data_tables[1:]:
        mean_table += data_table

    return mean_table / len(data_tables)

def count_nan_values(df):
    """
    Count the number of NaN values in each column of the DataFrame.

    Parameters:
    df (DataFrame): The input DataFrame.

    Returns:
    dict: A dictionary where keys are column names and values are the count of NaN values in each column.
    """
    nan_counts = df.isnull().sum()  # Count NaN values in each column
    nan_counts_dict = nan_counts.to_dict()  # Convert Series to dictionary
    return nan_counts_dict