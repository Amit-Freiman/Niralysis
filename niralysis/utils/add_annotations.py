import mne
import pandas as pd
import numpy as np
import datetime
from niralysis.utils.consts import *
from datetime import timezone




def get_start_time(raw_data) -> datetime.datetime:
    """
    @return: time when the recording began
    """
    return raw_data.info['meas_date']

def add_internal_delay(delay: int) -> int:
    """
    @param delay: delay to add (in seconds)

    """
    return delay

def get_delay(begin_rec: datetime, begin_exp: datetime) -> int:
    """
    @param start_rec: time when the recording began
    @param start_exp: time when the experiment began
    @return: delay between the start of the recording and the start of the experiment
    """
    begin_rec = begin_rec.replace(tzinfo=timezone.utc)
    begin_exp = begin_exp.replace(tzinfo=timezone.utc)
    delay = begin_rec - begin_exp
    return int(delay.total_seconds() + add_internal_delay(20)) # Change 20 to the calculated delay (first event from A through LSL, minus the same event from A through psychopy)

def get_event_info(event, delay, psychopy, idx) -> tuple:
    """
    @param event: event's name
    @param delay: delay between the start of the recording and the start of the experiment
    @return: event's name, start time, end time, duration
    """
    if event.find(' ') != -1:
        event_name = event.split(' ')[1] if event.split(' ')[1] == 'open' else event.split(':')[1]
        event_type = event.split(' ')[0]
    elif event.find(':') != -1:
        event_name = event.split(':')[1]
        event_type = event.split(':')[0]


    if event_type == EVENT_BEGIN:
        if event_name in CANDIDATES:
            if idx < 11:
                row = np.where(psychopy["candidate"] == event_name)[0][0]
            else:
                row = np.where(psychopy["candidate"] == event_name)[0][1]
            onset = psychopy["image.started"][row]
        elif event_name in DISCUSSION:
            if event_name == 'open':
                # Find the row that has a value
                row = np.where(psychopy["open.started"].notna())[0][0]
                onset = psychopy["open.started"][row]
            elif event_name == 'A' or event_name == 'B':
                row = np.where(psychopy["turn"] == event_name)[0][0]
                onset = psychopy["turn_2.started"][row]
    else:
        if event_name in CANDIDATES:
            if idx < 11:
                row = np.where(psychopy["candidate"] == event_name)[0][0]
            else:
                row = np.where(psychopy["candidate"] == event_name)[0][1]
            onset = psychopy["image_7.started"][row]
        elif event_name in DISCUSSION:
            if event_name == 'open':
                # Find the row that has a value
                row = np.where(psychopy["report.started"].notna())[0][0]
                onset = psychopy["report.started"][row]
            elif event_name == 'A' or event_name == 'B':
                row = np.where(psychopy["turn"] == event_name)[0][0]
                onset = psychopy["sound_1.started"][row]

    return onset - delay
    
def set_events_from_psychopy_table(snirf_path,psychopy_path) -> None:
    """
    @param snief_path: path to the SNIRF file
    @param psychopy_path: path to the Psychopy file

    The method sets the events in the SNIRF file according to the Psychopy file
    """
    snirf = mne.io.read_raw_snirf(snirf_path, preload=True)
    psychopy = pd.read_csv(psychopy_path)
    delay = get_delay(get_start_time(snirf), datetime.datetime.fromtimestamp(psychopy['StartTime'][0]))
    snirf.annotations.description = np.array(EVENTS)
    snirf.annotations.onset = np.array([get_event_info(event, delay, psychopy, idx) for idx, event in enumerate(EVENTS)], dtype=float)

    

    

