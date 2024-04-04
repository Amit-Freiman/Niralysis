from niralysis.Niralysis import Niralysis
from niralysis.utils.consts import *


class Subject:
    def __init__(self, path: str, areas: dict = None):
        self.path = path
        self.name = path.split('\\')[-1].replace('.snirf', '')
        self.subject = Niralysis(path)
        self.subject.set_hbo_data(None, False, high_pass_freq=0.4)
        self.subject.events_handler.set_continuous_events_frame()
        self.events_table = self.subject.events_handler.get_continuous_events_frame()
        self.events_data = None
        if areas is not None:
            self.subject.hbo_data.set_data_by_areas(areas)
            self.data_by_ares = self.subject.hbo_data.get_hbo_data_by_areas()

    def get_hbo_data(self):
        return self.subject.hbo_data.get_hbo_data()

    def set_hbo_data_columns(self, columns):
        self.subject.hbo_data.columns = columns

    def set_events_data(self):
        events_data = {}
        for index, event in self.events_table.iterrows():
            events_data[event[EVENT_COLUMN]] = self.get_event_data(event)
        self.events_data = events_data

    def get_event_data(self, event):
        data = self.get_hbo_data()
        return data[(data[TIME_COLUMN] >= event[START_COLUMN]) & (data[TIME_COLUMN] <= event[END_COLUMN])]



    


