import os
from typing import Optional

from niralysis.Niralysis import Niralysis
from niralysis.SharedReality.Event.Event import Event
from niralysis.SharedReality.Subject.PreprocessingInstructions import PreprocessingInstructions
from niralysis.SharedReality.consts import *
from niralysis.utils.consts import *
import pandas as pd
import mne

from niralysis.utils.data_manipulation import set_data_by_areas, get_areas_dict


class Subject:
    def __init__(self, path: str, preprocess_by_events: bool = False,
                 preprocessing_instructions: PreprocessingInstructions = None):
        self.preprocessing_instructions = preprocessing_instructions
        if not path:
            self.events_data = None
        else:
            self.path = path
            self.name = path.split('\\')[-1].replace('.snirf', '')
            self.subject = Niralysis(path, preprocessing_instructions)
            self.subject.events_handler.set_continuous_events_frame()
            self.events_table = self.subject.events_handler.get_continuous_events_frame()
            self.events_data = None
            self.preprocess_by_events = preprocess_by_events
            self.data_by_ares = False
            print(f"creating subject {self.name} data")
            if not self.preprocess_by_events:
                self.subject.set_full_hbo_data()
                self.set_data_by_areas()
                self.set_events_data()
            else:
                self.subject.hbo_data.raw_data = 0
                self.set_events_data()



    def get_hbo_data(self):
        if self.data_by_ares:
            return self.subject.hbo_data.get_hbo_data_by_areas()
        return self.subject.hbo_data.get_hbo_data()

    def set_hbo_data_columns(self, columns):
        self.subject.hbo_data.columns = columns

    def set_events_data(self):
        events_data = {FIRST_WATCH: {}, DISCUSSIONS: {}, SECOND_WATCH: {}}
        for index, event in self.events_table.iterrows():
            event_instance = self.get_event_data(event, self.preprocessing_instructions)
            if self.preprocess_by_events:
                event_instance.set_by_areas(self.preprocessing_instructions.areas_dict)
            events_data[EVENTS_CATEGORY[index]][event[EVENT_COLUMN]] = event_instance

        self.events_data = events_data

    def get_event_data(self, event_details: pd.Series, preprocessing_instructions: PreprocessingInstructions = None) -> Event:
        if not self.preprocess_by_events:
            data = self.get_hbo_data()
            event_data = data[(data[TIME_COLUMN] >= event_details[START_COLUMN]) & (data[TIME_COLUMN] <= event_details[END_COLUMN])]
            event_data.reset_index(drop=True, inplace=True)
            event = Event(event_details[EVENT_COLUMN], data_by_area=event_data)
        else:
            raw_data = mne.io.read_raw_snirf(self.path, preload=True)
            raw_data = mne.preprocessing.nirs.optical_density(raw_data)
            raw_data = raw_data.filter(l_freq=0.01, h_freq=0.5)
            raw_data.crop(event_details[START_COLUMN], event_details[END_COLUMN])
            event = Event(event_details[EVENT_COLUMN], raw_data=raw_data)
            event.preprocess(preprocessing_instructions)
        return event

    def get_event_data_table(self, index, name):
        category = self.events_data[EVENTS_CATEGORY[index]]
        if category is None:
            return None
        return category.get(name).get_data_by_areas()

    def set_data_by_areas(self):
        areas = self.preprocessing_instructions.areas_dict
        self.data_by_ares = areas is not None
        if areas is None:
            return

        self.subject.hbo_data.data_by_areas = set_data_by_areas(self.subject.hbo_data.get_hbo_data(), areas)

    @staticmethod
    def get_subjects_preprocessing_instructions(path: str) -> (str, PreprocessingInstructions):
        table_path = path.replace('.snirf', '.xlsx')
        if not os.path.exists(table_path):
            return

        df = pd.read_excel(table_path)
        template = df[CAP_SIZE][0]
        bad_channels = df[BAD_CHANNELS].dropna()
        low_freq = df[LOW_FREQ][0] if not df[LOW_FREQ].dropna().empty else DEFAULT_LOW_FREQ
        high_freq = df[HIGH_FREQ][0] if not df[HIGH_FREQ].dropna().empty else DEFAULT_HIGH_FREQ
        areas_dict = get_areas_dict(template)
        return PreprocessingInstructions(areas_dict=areas_dict, bad_channels=bad_channels, low_freq=low_freq,
                                         high_freq=high_freq)

