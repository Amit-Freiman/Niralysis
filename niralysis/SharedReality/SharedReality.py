import pandas as pd

from .Subject.Subject import Subject
from .consts import *
from niralysis.ISC.ISC import ISC
from niralysis.Niralysis import Niralysis
from ..WaveletCoherence.WaveletCoherence import WaveletCoherence


class SharedReality:
    def __init__(self, root, name):
        self.date = name
        self.subject_A_path = root + f"\\{name + "_A.snir"}"
        self.subject_B_path = root + name + f"\\{name + "_B.snir"}"
        self.subject_A = Subject.subject_handler(root, name + "_A.snirf",0)
        self.subject_B = Subject.subject_handler(root, name + "_B.snirf", 1)
        self.ISC_table = None
        self.wavelet_coherence = {}


    def candidates_handler(self, date):
        choices = {'31012024_0900': ('Roy', 'Roy', 'Sahar', 'Yael'),
                   '24012024_1400': ('Roy', 'Alon', 'Roy', 'Sahar'),
                   '01022024_1610': ('Alon', 'Roy', 'Sahar', 'Yael'),
                   '06022024_1400': ('Alon', 'Roy', 'Alon', 'Sahar'),
                   '07022024_1600': ('Roy', 'Yael', 'Roy', 'Sahar'),
                   '01022024_1000': ('Roy', 'Sahar', 'Roy', 'Yael'),
                   '31012024_1600': ('Roy', 'Alon', 'Roy', 'Yael'),
                   '01042024_1210': ('Roy', 'Alon', 'Roy', 'Sahar'),
                   '04032024_1200': ('Roy', 'Alon', 'Roy', 'Sahar'),
                   '06032024_1600': ('Roy', 'Roy', 'Yael', 'Sahar'),
                   '07032024_1000': ('Roy', 'Alon', 'Roy', 'Yael'),
                   '08022024_1400': ('Alon', 'Alon', 'Roy', 'Yael'),
                   '11032024_1145': ('Roy', 'Roy', 'Alon', 'Yael'),
                   '12032024_1410': ('Roy', 'Yael', 'Roy', 'Sahar'),
                   }
        return choices[date]
    
    def check_device_order(self, subject: str, unique_combination : str = UNIQUE_COMBINATION) -> bool:
        """
        Checks if the device order is correct (Old Brite, 20488/24302 and then the New Brite, 24053/24048)
        Verify by checking the channel combinations for one that is unique to this order
        
        @param unique_combination: A unique channel combination. Only if the devices are in the correct order will this combination be found
        @return: True if the devices are in the correct order, False otherwise
        """
        if subject == SUBJECT_A:
            columns = self.subject_A.get_hbo_data().columns
        elif subject == SUBJECT_B:
            columns = self.subject_B.get_hbo_data().columns
        else:
            raise ValueError("Invalid subject")
        for channel in columns:
            if unique_combination in channel:
                return True
        return False
    
    def flip_device_order(self, subject):
        """
        Flips the order of the devices in the data (for a specific subject) - changes the names of the columns but keeps the data intact
        Example for the first device (S1-S10,D1-D8)
        S1_D1 -> S11_D9
        S2_D2 -> S12_D10
        Example for the second device (S11-S20,D9-D16)
        S11_D9 -> S1_D1
        S12_D10 -> S2_D2
        """
        if subject == SUBJECT_A:
            data = self.subject_A.get_hbo_data()
        elif subject == SUBJECT_B:
            data = self.subject_B.get_hbo_data()
        else:
            raise ValueError("Invalid subject")

        # Get the column names (Remove first column - "Time" column)
        columns = data.columns[1:]

        # Split the columns into two halves: S1-S10 and D1-D8 (first device), and S11-S20 and D9-D16 (second device)
        first_device_columns = [col for col in columns if int(col[1:col.index("_")]) < 11]
        second_device_columns = [col for col in columns if int(col[1:col.index("_")]) >= 11]

        # Perform addition for the first device columns and subtraction for the second device columns
        flipped_first_device_columns = [f"S{int(col[1:col.index('_')]) + 10}_D{int(col[col.index('D')+1:col.index(' ')]) + 8}" for col in first_device_columns]
        flipped_second_device_columns = [f"S{int(col[1:col.index('_')]) - 10}_D{int(col[col.index('D')+1:col.index(' ')]) - 8}" for col in second_device_columns]

        # Combine the flipped columns
        flipped_columns = flipped_first_device_columns + flipped_second_device_columns

        # Add the time column back to the columns list
        flipped_columns = ["Time"] + flipped_columns

        # Rename the columns in the original data
        data.columns = flipped_columns
        
        if subject == SUBJECT_A:
            self.subject_A.set_hbo_data_columns(flipped_columns)
        elif subject == SUBJECT_B:
            self.subject_B.set_hbo_data_columns(flipped_columns)

    def run(self, date) -> pd.DataFrame:

        if not self.check_device_order(SUBJECT_A):
            self.flip_device_order(SUBJECT_A)
        if not self.check_device_order(SUBJECT_B):
            self.flip_device_order(SUBJECT_B)

        self.ISC_table = ISC.ISC_by_events(self.subject_A.events_table, self.subject_B.events_table,
                                           self.subject_A.get_hbo_data(), self.subject_B.get_hbo_data(),
                                           by_areas=old_area_dict)

        A_pre_choice, B_pre_choice, post_choice, control = self.candidates_handler(date)
        df = pd.DataFrame(index=TABLE_ROWS, columns=self.ISC_table.columns)

        for i, candidate in enumerate([A_pre_choice, B_pre_choice, post_choice, control]):
            df.loc[TABLE_ROWS[i * 2]] = self.ISC_table.loc[candidate].iloc[0]
            df.loc[TABLE_ROWS[i * 2 + 1]] = self.ISC_table.loc[candidate].iloc[1]

        return df

    def get_wavelet_coherence_maps(self, path_to_save_maps = None, path_to_candidate_choices = None):
        for i, event in enumerate(CANDIDATE_EVENTS_TABLE_NAMES):
            table_A = self.subject_A.get_event_data_table(i, event)
            table_B = self.subject_B.get_event_data_table(i, event)
            watch = 1 if i < 4 else 2
            number_of_rows = min(table_A.shape[0], table_B.shape[0])
            wavelet_coherence = WaveletCoherence(table_A.head(number_of_rows), table_B.head(number_of_rows),
                                                 path_to_save_maps, path_to_candidate_choices)
            name = wavelet_coherence.get_map_name(self.date, event, watch)
            wavelet_coherence.set_wavelet_coherence()
            wavelet_coherence.get_coherence_heatmap(name)
            self.wavelet_coherence[name] = wavelet_coherence



