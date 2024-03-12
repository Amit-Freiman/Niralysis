import mne
import pandas as pd
import datetime
from niralysis.utils.consts import *



def get_start_time(raw_data) -> datetime.datetime:
    """
    @return: time when the recording began
    """
    return raw_data.info['meas_date']

def get_delay(begin_rec: datetime, begin_exp: datetime) -> int:
    """
    @param start_rec: time when the recording began
    @param start_exp: time when the experiment began
    @return: delay between the start of the recording and the start of the experiment
    """
    delay = begin_exp - begin_rec
    return int(delay.total_seconds())

def set_events_from_psychopy_table(snirf_path,psychopy_path) -> None:
    """
    @param snief_path: path to the SNIRF file
    @param psychopy_path: path to the Psychopy file

    The method sets the events in the SNIRF file according to the Psychopy file
    """
    snirf = mne.io.read_raw_snirf(snirf_path, preload=True)
    psychopy = pd.read_csv(psychopy_path)
    delay = get_delay(get_start_time(snirf), datetime.datetime.fromtimestamp(psychopy['StartTime'][0]))
    events = pd.DataFrame(columns=[EVENT_COLUMN, START_COLUMN, END_COLUMN, DURATION_COLUMN])
    

    

