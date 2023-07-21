import pandas as pd
import pytest
from niralysis.niralysis import *
from niralysis.Events_to_label import events_to_labels 

# Define fixture

@pytest.fixture
def example_data():
    # Load example data from a CSV file or create a DataFrame here for testing
    return pd.read_csv('tests/csv4test/example_head_data.csv')

@pytest.fixture
def expected_change_in_position_per_frame():
    # Load expected change in position per frame data from a CSV file or create a DataFrame here for testing
    return pd.read_csv('tests/csv4test/truth_diff_frames.csv')

@pytest.fixture
def expected_change_in_distance():
    # Load expected change in position per frame data from a CSV file or create a DataFrame here for testing
    return pd.read_csv('tests/csv4test/truth_table_distance_diff_frames.csv')

# Test functions

def test_calculate_change_in_distance(example_data, expected_change_in_distance):
    """
    Test the calculate_change_in_distance function.
    """
    change_in_distance_table = Niralysis.calculate_change_in_distance(example_data).astype(float).round(3)
    assert change_in_distance_table[:4].equals(expected_change_in_distance.astype(float).round(3))

def test_calculate_change_in_position_per_frame(example_data, expected_change_in_position_per_frame):
    """
    Test the calculate_change_in_position_per_frame function.
    """
    change_in_position_table = Niralysis.calculate_change_in_position_per_frame(example_data).astype(float).round(3)
    assert change_in_position_table[:5].equals(expected_change_in_position_per_frame.astype(float).round(3))


def test_dataframe_with_no_timestamp_column():
    # Create a test DataFrame without the 'timestamp' column
    data = {
        'Col0': [1, 2, 3],
        'Col1': [4, 5, 6],
        'Col': [7, 8, 9]
    }
    df = pd.DataFrame(data)

    # Ensure that the function raises a KeyError when 'timestamp' column is missing
    with pytest.raises(KeyError):
        events_to_labels(df) 

