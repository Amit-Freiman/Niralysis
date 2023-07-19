import pandas as pd


def get_distance_of_coordinate_between_two_time_stamps(coordinate1, coordinate2) -> float:
    """Calculate the distance between two points in space"""
    return coordinate2 - coordinate1


def get_table_of_deltas_between_time_stamps_in_all_kps(x_y_data: pd.DataFrame) -> pd.DataFrame:
    """Calculate the difference between the coordinates of the key points in two consecutive time stamps
    Args:
        x_y_data (pd.DataFrame): data frame of values for every key point (column) and time stamp (row)
    Returns:
        deltas (df): data frame of deltas between each 2 consecutive time stamps (0-1, 1-2, 2-3, etc.)
    """
    deltas = pd.DataFrame(columns=x_y_data.columns)
    rows_in_deltas = []

    for kp in x_y_data.columns:
        loc_of_last_timestamp_before_zero = 0
        for time_stamp in range(len(x_y_data)-1):
            if x_y_data[kp][time_stamp] == 0 and x_y_data[kp][time_stamp+1] != 0:
                loc_of_time_stamp = loc_of_last_timestamp_before_zero
                this_time_stamp_value = x_y_data[kp][loc_of_time_stamp]  # last value before zero values
                next_time_stamp_value = x_y_data[kp][time_stamp+1]
                deltas[kp][time_stamp] = get_distance_of_coordinate_between_two_time_stamps(this_time_stamp_value,
                                                                                            next_time_stamp_value)
                rows_in_deltas.append(f"{time_stamp}-{time_stamp + 1}")
                continue
            if x_y_data[kp][time_stamp] == 0 and x_y_data[kp][time_stamp+1] == 0:
                continue
            if x_y_data[kp][time_stamp] != 0 and x_y_data[kp][time_stamp+1] == 0:
                loc_of_last_timestamp_before_zero = time_stamp
                continue