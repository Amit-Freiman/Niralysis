from niralysis.Niralysis import Niralysis


class Subject:
    def __init__(self, path: str, areas: dict = None):
        self.path = path
        self.name = path.split('\\')[-1].replace('.snirf', '')
        self.subject = Niralysis(path)
        self.subject.set_hbo_data(None, False, high_pass_freq=0.4)
        self.subject.events_handler.set_continuous_events_frame()
        self.events_table = self.subject.events_handler.get_continuous_events_frame()
        if areas is not None:
            self.subject.hbo_data.set_data_by_areas(areas)
            self.data_by_ares = self.subject.hbo_data.get_hbo_data_by_areas()

