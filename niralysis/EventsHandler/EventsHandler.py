import re
import mne
import pandas as pd
from niralysis.utils.consts import *
from niralysis.utils.add_annotations import set_events_from_rec_delay, set_events_from_original_file


class EventsHandler:
    """
     Handles the events in the SNIRF file

     Args:
         path (string): Path to the SNIRF file.

     Methods:
         set_spotted_events_frame - sets events frame, treat each spotted event as a singular event
         set_continuous_events_frame - sets events frame, looks for continuous events and calculates its duration
         get_spotted_events_frame - spotted events getter
         get_continuous_events_frame - continuous events getter
    """


    def __init__(self, path: str):
        self.raw_data = mne.io.read_raw_snirf(path, preload=True)
        self.path = path
        self.continuous_events = None
        self.spotted_events = None

    def set_spotted_events_frame(self) -> None:
        """
        creates a dataframe with columns - 'event', 'time', 'duration'
        Each event in the SNIRF file is a raw in the frame
        """
        if self.raw_data.annotations is None:
            self.spotted_events = None

        events = pd.DataFrame(columns=[END_COLUMN, TIME_COLUMN, DURATION_COLUMN])
        events[END_COLUMN] = self.raw_data.annotations.description
        events[TIME_COLUMN] = self.raw_data.annotations.onset
        events[DURATION_COLUMN] = self.raw_data.annotations.duration
        self.spotted_events = events

    def set_continuous_events_frame(self) -> None:
        """
        creates a dataframe with columns - 'event', 'start', 'end', 'duration'
        A continuous event in the SNIRF file should be set in the SNRIF file as follows:
            An SNIRF event with the name 'begin<:|-| ><event's name>' marks the starting point of a continuous event
            An SNIRF event with the name 'end<:|-| ><event's name>' marks the ending point of a continuous event
        The method adds a row for each <event's name>
        An event without a 'begin' or 'end' mark will be treated as a spotted event
        """
        if self.raw_data.annotations is None:
            self.spotted_events = None
        
        if self.path.endswith("A.snirf") or self.path.endswith("A.snirf.gz"):
            self.raw_data = set_events_from_original_file(self.path, self.path.replace("_A", "_events_file"))
        # If snirf is B file, we need to take the A file and set the events
        if self.path.endswith("B.snirf") or self.path.endswith("B.snirf.gz"):
        # if self.raw_data.annotations.description.size == 0:
            # Take the path and change the B to A
            path_a = self.path.replace("B", "events_file")
            self.raw_data = set_events_from_rec_delay(path_a, self.path)

        events = pd.DataFrame(columns=[EVENT_COLUMN, START_COLUMN, END_COLUMN, DURATION_COLUMN])

        events_index = {}
        ind = 0
        for i, event in enumerate(self.raw_data.annotations.description):
            if event.startswith(EVENT_BEGIN):
                name = re.split(r"[: -]", event, 1)[1].strip()
                events_index[name] = ind
                events.at[ind, EVENT_COLUMN] = name
                events.at[ind, START_COLUMN] = self.raw_data.annotations.onset[i]
                ind += 1
            elif event.startswith(EVENT_END):
                name = re.split(r"[: -]", event, 1)[1].strip()
                event_ind = events_index[name]
                events.at[event_ind, END_COLUMN] = self.raw_data.annotations.onset[i]
                events.at[event_ind, DURATION_COLUMN] = (self.raw_data.annotations.onset[i] -
                                                         events.at[event_ind, START_COLUMN])
            else:
                # a spotted event
                events.at[ind, EVENT_COLUMN] = event
                events.at[ind, START_COLUMN] = self.raw_data.annotations.onset[i]
                events.at[ind, END_COLUMN] = self.raw_data.annotations.onset[i] + self.raw_data.annotations.duration[i]
                events[ind, DURATION_COLUMN] = self.raw_data.annotations.duration[i]
                ind += 1

        self.continuous_events = events

    def get_spotted_events_frame(self) -> pd.DataFrame | None:
        """
        @return: spotted events data frame
        """
        return self.spotted_events

    def get_continuous_events_frame(self) -> pd.DataFrame | None:
        """
        @return: continuous events data frame
        """
        return self.continuous_events
