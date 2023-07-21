import pathlib
import pytest
import pandas as pd
from niralysis.niralysis import *


 ######## Testing the Niralysis class ########

### Testing the init function
def test_valid_input():
    """Testing if the file name as a path is valid """
    fname = pathlib.Path("demo_data/60_001.snirf") 
    q = Niralysis(fname)
    assert fname == q.snirf_fname

def test_str_input():
    """Testing if the file name as a string is valid """
    q = Niralysis("demo_data/60_001.snirf")
    assert pathlib.Path("demo_data/60_001.snirf") == q.snirf_fname


def test_not_snirf_input():
    """Testing if the file type is snirf """
    fname = pathlib.Path('wrongfileformat.txt')
    with pytest.raises(ValueError):
        Niralysis(fname)


def test_missing_file():
    """Testing a case if file is missing in the reposetory"""
    fname = pathlib.Path('nofilefound.snirf')
    with pytest.raises(ValueError):
       Niralysis(fname)

def test_empty_input():
    """Testing if the file name is empty """
    fname = pathlib.Path('')
    with pytest.raises(ValueError):
        q = Niralysis(fname)

### Testing the storm function
def test_storm_path_input():
    """Testing if the storm file is valid as a path"""
    fname = pathlib.Path('demo_data/60_001.snirf')
    storm_name = pathlib.Path('demo_data/STORM_demo.txt')
    q = Niralysis(fname)
    q.storm(storm_name)
    assert storm_name == q.storm_fname

def test_storm_str_input():
    """Testing if string input is valid """
    fname = pathlib.Path('demo_data/60_001.snirf')
    storm_name = 'demo_data/STORM_demo.txt'
    q = Niralysis(fname)
    q.storm(storm_name)
    assert pathlib.Path(storm_name) == q.storm_fname
    
def test_storm_not_txt_input():
    """Testing if the storm file isnt text"""
    fname = pathlib.Path('demo_data/60_001.snirf')
    storm_name = 'demo_data/STORM_demo.csv'
    with pytest.raises(ValueError):
        q = Niralysis(fname)
        q.storm(storm_name)

def test_storm_missing_file():
    """Testing a case if file is missing in the reposetory"""
    fname = pathlib.Path('demo_data/60_001.snirf')
    storm_name = 'demo_data/stormnotfound.txt'
    with pytest.raises(ValueError):
        q = Niralysis(fname)
        q.storm(storm_name)

def test_storm_empty_input():
    """Testing if the file name is empty """
    fname = 'demo_data/60_001.snirf'
    storm_name = pathlib.Path('')
    with pytest.raises(ValueError):
        q = Niralysis(fname)
        q.storm(storm_name)

def test_storm_valid_1():
    """Testing if the storm file is valid by adding storm file with missing detector"""
    fname = pathlib.Path('demo_data/60_001.snirf')
    storm_name = 'tests/txt4test/STORM_demo_missing_detector.txt'
    with pytest.raises(ValueError):
        q = Niralysis(fname)
        q.storm(storm_name)

def test_storm_valid_2():
    """Testing if the storm file is valid by adding storm file with missing value (which will result in NaN)"""
    fname = pathlib.Path('demo_data/60_001.snirf')
    storm_name = 'tests/txt4test/STORM_demo_missing_value.txt'
    with pytest.raises(ValueError):
        q = Niralysis(fname)
        q.storm(storm_name)

def test_source_locations_changed():
    """Testing if the source locations are changed after storm file is added"""
    fname = pathlib.Path('demo_data/60_001.snirf')
    storm_name = 'demo_data/STORM_demo.txt'
    q = Niralysis(fname)
    q.storm(storm_name)
    storm_sourc_loc, storm_detc_loc = q.storm_prob()
    assert np.array_equal(q.snirf_sourc_loc, storm_sourc_loc[[1,2,3]].values)

def test_detector_locations_changed():
    """Testing if the detector locations are changed after storm file is added"""
    fname = pathlib.Path('demo_data/60_001.snirf')
    storm_name = 'demo_data/STORM_demo.txt'
    q = Niralysis(fname)
    q.storm(storm_name)
    storm_sourc_loc, storm_detc_loc = q.storm_prob()
    assert np.array_equal(q.snirf_detc_loc, storm_detc_loc[[1,2,3]].values)
    