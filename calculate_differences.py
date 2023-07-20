import pandas as pd


def get_distance_of_coordinate_between_two_time_stamps(coordinate1, coordinate2) -> float:
    """Calculate the distance between two points in space"""
    return coordinate2 - coordinate1


def get_table_of_deltas_between_time_stamps_in_all_kps(x_y_data: pd.DataFrame) -> pd.DataFrame:
    """Calculate the difference between the coordinates of the key points in two consecutive time stamps
    Args:
        x_y_data (pd.DataFrame): data frame of values for every key point (column) and time stamp (row)
    Vars:
        counter_of_all_zeros_in_a_row_for_all_kps (dict): dictionary of dictionaries that are counters of consecutive
                                                            zeros in a row for all key points
    Returns:
        deltas (df): data frame of deltas between each 2 consecutive time stamps (0-1, 1-2, 2-3, etc.)
                        Each row corresponds to the difference between two consecutive time stamps.
    Algorithm:
        If the value in the time stamp is 0, then the value in the delta is 0.
        If the value in the time stamp is not 0, then the value in the delta is the difference between the value in the
        time stamp and the value in the previous time stamp, that is not 0.

    """
    if x_y_data.empty:
        raise ValueError("The input DataFrame is empty.")

    counter_of_all_zeros_in_a_row_for_all_kps = dict()
    deltas = pd.DataFrame(columns=x_y_data.columns, index=range(len(x_y_data) - 1))

    for kp in x_y_data.columns:
        counter_of_all_zeros_in_a_row_for_all_kps[kp] = dict()
        loc_of_last_timestamp_before_zero = 0
        counter_of_zeros_in_a_row = 0
        for time_stamp in range(x_y_data.shape[0]-1):
            if x_y_data[kp][time_stamp] > 0 and x_y_data[kp][time_stamp+1] > 0:
                deltas.at[time_stamp, kp] = x_y_data[kp][time_stamp + 1] - x_y_data[kp][time_stamp]
            elif x_y_data[kp][time_stamp] == 0 and x_y_data[kp][time_stamp+1] > 0:
                loc_of_time_stamp = loc_of_last_timestamp_before_zero
                this_time_stamp_value = x_y_data[kp][loc_of_time_stamp]  # last value before zero values
                next_time_stamp_value = x_y_data[kp][time_stamp+1]
                deltas.at[time_stamp, kp] = next_time_stamp_value - this_time_stamp_value
                counter_of_all_zeros_in_a_row_for_all_kps[kp][time_stamp] = counter_of_zeros_in_a_row
                counter_of_zeros_in_a_row = 0
            elif x_y_data[kp][time_stamp] == 0 and x_y_data[kp][time_stamp+1] == 0:
                counter_of_zeros_in_a_row += 1
                deltas.at[time_stamp, kp] = 0
            elif x_y_data[kp][time_stamp] > 0 and x_y_data[kp][time_stamp+1] == 0:
                loc_of_last_timestamp_before_zero = time_stamp
                deltas.at[time_stamp, kp] = 0
                counter_of_zeros_in_a_row = 1
    return deltas


# def get_table_of_summed_distances_for_kp_over_time(deltas_table: pd.DataFrame, threshold: float) -> pd.DataFrame:
#     """Calculate the summed distance of a key point over time
#     Sums the deltas in the nose kp, until sum reaches the threshold.
#     When sum reaches threshold, sums the deltas in the corresponding rows for every kp in table.
#
#     Args:
#         deltas_table (pd.DataFrame): data frame of deltas between each 2 consecutive time stamps (0-1, 1-2, 2-3, etc.)
#                                         Each row corresponds to the difference between two consecutive time stamps.
#         threshold (float): threshold of summed distance of nose kp over time
#     Returns:
#         summed_distances (pd.DataFrame): data frame of summed distances of every kp over time.
#                                             Each row corresponds to the summed distance of every kp over time
#                                             until threshold is reached.
#
#     Algorithm: Sum nose columns values until threshold is reached, if threshold is reached, sum all columns values and
#     continue summing until threshold is reached again, etc., until the end of the table.
#     Keep track of the time stamps until threshold is reached, and the time stamps after threshold is reached, and save
#     them in a column in the sums table.
#     """
#
#     sums = pd.DataFrame(columns=deltas_table.columns)
#     nose_columns_names = deltas_table.columns["KP_0_x", "KP_0_y"]
#     timestamps = ['0']  # list of starting time stamps of every sum
#     running_timestamp = 0  # Current time stamp
#     sum_until_threshold_is_reached_x = 0  # Sum of nose x values until threshold is reached
#     sum_until_threshold_is_reached_y = 0  # Sum of nose y values until threshold is reached
#     number_of_thresholds_reached = 0  # Number of thresholds reached
#     timestamps_of_thresholds = []  # List of time stamps of starting and ending of every sum
#
#     for time_stamp in range(deltas_table.shape[0]):
#         sum_until_threshold_is_reached_x += deltas_table[nose_columns_names[0]][time_stamp]
#         sum_until_threshold_is_reached_y += deltas_table[nose_columns_names[1]][time_stamp]
#         if sum_until_threshold_is_reached_x > threshold or sum_until_threshold_is_reached_y > threshold:
#             # Sum all columns values between last timestamp before threshold is reached and current timestamp.
#             # Add the sum to the sums table.
#             for kp in deltas_table.columns:
#                 # sum all columns values between last timestamp before threshold is reached and current timestamp for
#                 # every kp
#                 sums.at[number_of_thresholds_reached, kp] = deltas_table[kp][timestamps[-1]:time_stamp].sum()
#             # Reset the sum until threshold is reached
#             sum_until_threshold_is_reached_x = 0
#             number_of_thresholds_reached += 1
#             timestamps_of_thresholds.append(f"{timestamps[-1]}-{time_stamp}")
#             #####timestamps.append(timestamps_of_thresholds[-1])
#         running_timestamp += 1  # running_timestamp is the number of the current timestamp, starting from 0
#
#     # Add timestamps to sums table as a column
#     sums["timestamps"] = timestamps
#     return sums


def get_table_of_summed_distances_for_kp_over_time(deltas_table: pd.DataFrame, threshold: float) -> pd.DataFrame:
    """Calculate the summed distance of a key point over time
    Sums the deltas in the nose kp, until sum reaches the threshold.
    When sum reaches threshold, sums the deltas in the corresponding rows for every kp in table.

    Args:
        deltas_table (pd.DataFrame): data frame of deltas between each 2 consecutive time stamps (0-1, 1-2, 2-3, etc.)
                                        Each row corresponds to the difference between two consecutive time stamps.
        threshold (float): threshold of summed distance of nose kp over time
    Returns:
        sums (pd.DataFrame): Data frame of summed distances of every kp over time.
                            Each row corresponds to the summed distance of every kp over time
                            until threshold is reached.

    Algorithm:
    1. Use sum_until_threshold function to get a list of starting and ending time stamps of every sum, and a dict of the
    sums for every starting point.
    2. According to the list, sum all columns values in this area for every kp using sum_all_kp_for_range function.
    3. Add the sum to the sums table.
    """
    sums = pd.DataFrame(columns=deltas_table.columns)
    nose_columns_names = ["KP_0_x", "KP_0_y"]

    nose_x_list = list(deltas_table[nose_columns_names[0]])
    nose_y_list = list(deltas_table[nose_columns_names[1]])
    start_to_end_locations_tuple_list = sum_until_threshold(nose_x_list, nose_y_list, threshold)
    sums["timestamps"] = create_timestamps_column(start_to_end_locations_tuple_list)

    print(deltas_table.columns)
    for kp in deltas_table.columns:
        column_of_sums_per_kb = create_column_of_sum_for_kp_in_range(deltas_table[kp], start_to_end_locations_tuple_list)
        sums[kp] = column_of_sums_per_kb
    return sums


def create_timestamps_column(start_to_end_locations_tuple_list: list) -> pd.DataFrame:
    """Recieves a list of tuples of start and end locations of sums.
    Returns a data frame with a column of the start and end locations of the sums."""
    timestamps_column = pd.DataFrame(columns=["timestamps"])
    for i, j in start_to_end_locations_tuple_list:
        timestamps_column.at[i, "timestamps"] = f"{i}-{j}"
    return timestamps_column


def create_column_of_sum_for_kp_in_range(delta_kp_column: pd.DataFrame, ranges: list) -> pd.DataFrame:
    """Recieves a column of the kp, and a list of ranges.
    Sums the values in this range and return a row with the sums, as a data frame."""
    sum_rows = pd.DataFrame(columns=["sums"])
    for i, j in ranges:
        sum_rows.at[i, "sums"] = delta_kp_column[i:j].sum()
    return sum_rows


def sum_until_threshold(values_x: list, values_y: list, threshold: int) -> list:
    """Go over the sum of every 30 values in the list, and insert to a new list all the sums that are bigger than
    threshold.

    Args:
        values_x (list): list of values in x
        values_y (list): list of values in y
        threshold (int): threshold of summed distance of nose kp over time

    returns:
    start_to_end_locations_tuple_list: a list of tuples of start and end locations of sums that are bigger than
    threshold"""
    start_to_end_locations_tuple_list = []
    for i in range(len(values_x)):
        for j in range(30):
            if sum(values_x[i:i+j]) > threshold or sum(values_y[i:i+j]) > threshold:
                start_to_end_locations_tuple_list.append((i, i+j))
    return start_to_end_locations_tuple_list



















