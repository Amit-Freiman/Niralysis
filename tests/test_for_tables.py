import pandas as pd
import pytest
from niralysis.niralysis import *
# Define fixture

@pytest.fixture
def example_data():
    # Load example data from a CSV file or create a DataFrame here for testing
    return pd.read_csv('example_head_data.csv')

@pytest.fixture
def expected_change_in_position_per_frame():
    # Load expected change in position per frame data from a CSV file or create a DataFrame here for testing
    return pd.read_csv('truth_diff_frames.csv')

@pytest.fixture
def expected_change_in_distance():
    # Load expected change in position per frame data from a CSV file or create a DataFrame here for testing
    return pd.read_csv('truth_table_distance_diff_frames.csv')

# Test functions

def test_calculate_change_in_distance(example_data, expected_change_in_distance):
    """
    Test the calculate_change_in_distance function.
    """
    change_in_distance_table = Niralysis.calculate_change_in_distance(example_data)
    assert change_in_distance_table[:4].equals(expected_change_in_distance)

def test_calculate_change_in_position_per_frame(example_data, expected_change_in_position_per_frame):
    """
    Test the calculate_change_in_position_per_frame function.
    """
    change_in_position_table = Niralysis.calculate_change_in_position_per_frame(example_data)
    assert change_in_position_table[:5].equals(expected_change_in_position_per_frame)
