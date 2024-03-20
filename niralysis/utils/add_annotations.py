import mne
import os
import pandas as pd
import numpy as np
import datetime
from niralysis.utils.consts import *
from datetime import timezone




def get_rec_start_time(raw_data) -> datetime.datetime:
    """
    @return: time when the recording began
    """
    return raw_data.info['meas_date']

def get_exp_start_time(psychopy_path) -> int:
    """
    @param psychopy_path: path to the Psychopy file
    @return: time when the experiment began
    """
    # The time when the file was last modified (for psychopy files that have not been modified, it is the time when the experiment ended)
    final_time = os.path.getmtime(psychopy_path)
    psychopy = pd.read_csv(psychopy_path)
    # The amount of seconds that the experiment took
    amount_of_secs = psychopy["image_3.started"].max() + psychopy["key_resp_4.rt"].max()

    return datetime.datetime.fromtimestamp(final_time - amount_of_secs)

def get_delay(begin_rec: datetime, begin_exp: datetime) -> int:
    """
    @param start_rec: time when the recording began
    @param start_exp: time when the experiment began
    @return: delay between the start of the recording and the start of the experiment
    """
    begin_rec = begin_rec.replace(tzinfo=timezone.utc)
    begin_exp = begin_exp.replace(tzinfo=timezone.utc)
    delay = begin_rec - begin_exp
    return float(delay.total_seconds())

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
                row = np.where(psychopy["report.started"].notna())[0][0]
                onset = psychopy["report.started"][row]
            elif event_name == 'A' or event_name == 'B':
                row = np.where(psychopy["turn"] == event_name)[0][0]
                onset = psychopy["sound_1.started"][row]

    return onset - delay
    
def set_events_from_psychopy_table(snirf_path,psychopy_path): 
    """
    @param snief_path: path to the SNIRF file
    @param psychopy_path: path to the Psychopy file

    The method sets the events in the SNIRF file according to the Psychopy file
    """
    snirf = mne.io.read_raw_snirf(snirf_path, preload=True)
    psychopy = pd.read_csv(psychopy_path)
    delay = get_delay(get_rec_start_time(snirf), get_exp_start_time(psychopy_path))  #datetime.datetime.fromtimestamp(psychopy['StartTime'][0])
    snirf.annotations.description = np.array(EVENTS)
    snirf.annotations.onset = np.array([get_event_info(event, delay, psychopy, idx) for idx, event in enumerate(EVENTS)], dtype=float)
    return snirf

def set_events_from_rec_delay(subject_A_path, subject_B_path):

    snirf_a = mne.io.read_raw_snirf(subject_A_path, preload=True)
    snirf_b = mne.io.read_raw_snirf(subject_B_path, preload=True)
    delay = get_delay(get_rec_start_time(snirf_a), get_rec_start_time(snirf_b))
    if delay < 0:
        snirf_b.annotations.onset = snirf_a.annotations.onset - abs(delay)
    else:
        snirf_b.annotations.onset = snirf_a.annotations.onset + abs(delay)
    
    return snirf_b

    

