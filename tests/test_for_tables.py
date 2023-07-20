import os
import pytest
import csv
from Niralysis_openpose import calculate_change_in_distance, calculate_change_in_position_per_frame

def read_csv(file_path):
    with open(file_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip the header
        data = [list(map(float, row)) for row in reader]
    return data

@pytest.fixture
def expected_change_in_distance():
    file_path = os.path.join('tests', 'csv4test', 'truth_table_distance_diff_frames.csv')
    return read_csv(file_path)[:4]

@pytest.fixture
def expected_change_in_position_per_frame():
    file_path = os.path.join('tests', 'csv4test', 'truth_diff_frames.csv')
    return read_csv(file_path)[:5]

def test_calculate_change_in_distance(expected_change_in_distance):
    file_path = os.path.join('tests', 'csv4test', 'example_head_data.csv')
    data = read_csv(file_path)
    change_in_distance_table = calculate_change_in_distance(data)
    assert change_in_distance_table[:4] == expected_change_in_distance

def test_calculate_change_in_position_per_frame(expected_change_in_position_per_frame):
    file_path = os.path.join('tests', 'csv4test', 'example_head_data.csv')
    data = read_csv(file_path)
    change_in_position_table = calculate_change_in_position_per_frame(data)
    assert change_in_position_table[:5] == expected_change_in_position_per_frame
