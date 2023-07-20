import pathlib
import pytest
import pandas as pd
from niralysis.niralysis import *


"""testing file object"""
def test_valid_input():
    """Testing if the file name as a path is valid """
    fname = pathlib.Path(__file__) 
    q = Niralysis(fname)
    assert fname == q.snirf_fname


def test_str_input():
    """Testing if the file name as a string is valid """
    q = Niralysis(__file__)
    assert pathlib.Path(__file__) == q.snirf_fname


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


def test_wrong_input_type():
    """Testing if format is wrong"""
    fname = 2
    with pytest.raises(TypeError):
        q = Niralysis(pathlib.Path(fname))

