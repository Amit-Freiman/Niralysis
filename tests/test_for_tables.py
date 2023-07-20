import os
import sys
import pytest
import csv
from Niralysis_openpose import calculate_change_in_distance, calculate_change_in_position_per_frame

# Define path names for test data
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'csv4test')
EXAMPLE_HEAD_DATA_CSV = os.path.join(TEST_DATA_DIR, 'example_head_data.csv')
TRUTH_TABLE_DISTANCE_DIFF_FRAMES_CSV = os.path.join(TEST_DATA_DIR, 'truth_table_distance_diff_frames.csv')
TRUTH_DIFF_FRAMES_CSV = os.path.join(TEST_DATA_DIR, 'truth_diff_frames.csv')

def read_csv(file_path):
    with open(file_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip the header
        data = [list(map(float, row)) for row in reader]
    return data

@pytest.fixture
def expected_change_in_distance():
    return read_csv(TRUTH_TABLE_DISTANCE_DIFF_FRAMES_CSV)[:4]

@pytest.fixture
def expected_change_in_position_per_frame():
    return read_csv(TRUTH_DIFF_FRAMES_CSV)[:5]

def test_calculate_change_in_distance(expected_change_in_distance):
    data = read_csv(EXAMPLE_HEAD_DATA_CSV)
    change_in_distance_table = calculate_change_in_distance(data)
    assert change_in_distance_table[:4] == expected_change_in_distance

def test_calculate_change_in_position_per_frame(expected_change_in_position_per_frame):
    data = read_csv(EXAMPLE_HEAD_DATA_CSV)
    change_in_position_table = calculate_change_in_position_per_frame(data)
    assert change_in_position_table[:5] == expected_change_in_position_per_frame
