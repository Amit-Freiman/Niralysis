from niralysis.Niralysis import Niralysis
from niralysis.SharedReality.consts import *
from niralysis.utils.consts import *


class Subject:
    def __init__(self, path: str, areas: dict = None):
        if not path:
            self.events_data = None
        else:
            self.path = path
            self.name = path.split('\\')[-1].replace('.snirf', '')
            self.subject = Niralysis(path)
            self.subject.set_hbo_data(None, False, high_pass_freq=0.4)
            self.subject.events_handler.set_continuous_events_frame()
            self.events_table = self.subject.events_handler.get_continuous_events_frame()
            self.events_data = None
            self.data_by_ares = False
            if areas is not None:
                self.subject.hbo_data.set_data_by_areas(areas)
                self.data_by_ares = True
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
            events_data[EVENTS_CATEGORY[index]][event[EVENT_COLUMN]] = self.get_event_data(event)
        self.events_data = events_data

    def get_event_data(self, event):
        data = self.get_hbo_data()
        event_data = data[(data[TIME_COLUMN] >= event[START_COLUMN]) & (data[TIME_COLUMN] <= event[END_COLUMN])]
        event_data.reset_index(drop=True, inplace=True)
        return event_data

    def get_event_data_table(self, index, name):
        category = self.events_data[EVENTS_CATEGORY[index]]
        if category is None:
            return None
        return category.get(name)
    

