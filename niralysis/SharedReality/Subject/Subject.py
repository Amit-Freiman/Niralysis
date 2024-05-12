from typing import Optional

from niralysis.Niralysis import Niralysis
from niralysis.SharedReality.Event.Event import Event
from niralysis.SharedReality.Subject.PreprocessingInstructions import PreprocessingInstructions
from niralysis.SharedReality.consts import *
from niralysis.utils.consts import *
from niralysis.HbOData.HbOData import HbOData
import pandas as pd
import mne

class Subject:
    def __init__(self, path: str, areas: dict = None, preprocess_by_events: bool = False,
                 preprocessing_instructions: PreprocessingInstructions = None):
        self.preprocessing_instructions = preprocessing_instructions
        if not path:
            self.events_data = None
        else:
            self.path = path
            self.name = path.split('\\')[-1].replace('.snirf', '')
            self.subject = Niralysis(path)
            self.subject.events_handler.set_continuous_events_frame()
            self.events_table = self.subject.events_handler.get_continuous_events_frame()
            self.events_data = None
            self.preprocess_by_events = preprocess_by_events
            if not self.preprocess_by_events:
                self.subject.set_full_hbo_data(None, False, high_pass_freq=0.4)
            else:
                self.subject.hbo_data.raw_data = 0
            self.set_events_data(areas, preprocessing_instructions)

            self.data_by_ares = areas is not None

            

    def get_hbo_data(self):
        if self.data_by_ares:
            return self.subject.hbo_data.get_hbo_data_by_areas()
        return self.subject.hbo_data.get_hbo_data()

    def set_hbo_data_columns(self, columns):
        self.subject.hbo_data.columns = columns

    def set_events_data(self, areas: dict=None, preprocessing_instructions: PreprocessingInstructions=None):
        events_data = {FIRST_WATCH: {}, DISCUSSIONS: {}, SECOND_WATCH: {}}
        for index, event in self.events_table.iterrows():
            event_instance = self.get_event_data(event, preprocessing_instructions)
            if areas is not None:
                event_instance.set_by_areas(areas)
            events_data[EVENTS_CATEGORY[index]][event[EVENT_COLUMN]] = event_instance

        self.events_data = events_data

    def get_event_data(self, event: pd.Series, preprocessing_instructions: PreprocessingInstructions=None) -> Event:
        if not self.preprocess_by_events:
            data = self.get_hbo_data()
            event_data = data[(data[TIME_COLUMN] >= event[START_COLUMN]) & (data[TIME_COLUMN] <= event[END_COLUMN])]
            event_data.reset_index(drop=True, inplace=True)
            event = Event(event[EVENT_COLUMN], data_frame=event_data)
        else:
            raw_data = mne.io.read_raw_snirf(self.path, preload=True)
            raw_data.crop(event[START_COLUMN], event[END_COLUMN])
            event = Event(event[EVENT_COLUMN], raw_data=raw_data)
            event.preprocess(preprocessing_instructions)
        return event

    def get_event_data_table(self, index, name):
        category = self.events_data[EVENTS_CATEGORY[index]]
        if category is None:
            return None
        return category.get(name).get_data_by_areas()
    

