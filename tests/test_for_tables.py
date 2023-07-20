import pandas as pd
import pytest
from niralysis.niralysis import Niralysis
# Test functions
def test_calculate_change_in_distance():
    """
    Test the calculate_change_in_distance function.

    This test case reads data from example_data, calculates the change in distance
    using the calculate_change_in_distance function, and compares the result with the
    expected_change_in_distance fixture.
    """
    example_data=pd.read_csv('example_head_data.csv')
    expected_change_in_distance=pd.read_csv('truth_table_distance_diff_frames.csv')
    change_in_distance_table = Niralysis.calculate_change_in_distance(example_data)
    assert change_in_distance_table[:4].equals(expected_change_in_distance)

def test_calculate_change_in_position_per_frame(example_data, expected_change_in_position_per_frame):
    """
    Test the calculate_change_in_position_per_frame function.

    This test case reads data from example_data, calculates the change in position per frame
    using the calculate_change_in_position_per_frame function, and compares the result with the
    expected_change_in_position_per_frame fixture.
    """
    example_data=pd.read_csv('example_head_data.csv')
    expected_change_in_position_per_frame=pd.read_csv('truth_diff_frames.csv')
    change_in_position_table = Niralysis.calculate_change_in_position_per_frame(example_data)
    assert change_in_position_table[:5].equals(expected_change_in_position_per_frame)