import pandas as pd

from .consts import *
from niralysis.ISC.ISC import ISC
from niralysis.Niralysis import Niralysis

A_PRE_CHOICE_1 = "A pre-choice first watch"
A_PRE_CHOICE_2 = "A pre-choice second watch"
B_PRE_CHOICE_1 = "B pre-choice first watch"
B_PRE_CHOICE_2 = "B pre-choice second watch"
POST_CHOICE_1 = "post-choice first watch"
POST_CHOICE_2 = "post-choice second watch"
CONTROL_1 = "control first watch"
CONTROL_2 = "control second watch"
TABLE_ROWS = [A_PRE_CHOICE_1, A_PRE_CHOICE_2, B_PRE_CHOICE_1, B_PRE_CHOICE_2, POST_CHOICE_1, POST_CHOICE_2, CONTROL_1,
              CONTROL_2]




class SharedReality:
    def __init__(self, subject_A_path, subject_B_path):
        self.subject_A_path = subject_A_path
        self.subject_B_path = subject_B_path
        self.subject_A = None
        self.subject_B = None
        self.events_table = None
        self.ISC_table = None

    def candidates_handler(self, date):
        choices = {'26062023_1100': ('Roy', 'Sahar', 'Roy', 'Yael'),
                   '19062023_1200': ('Roy', 'Alon', 'Roy', 'Sahar'),
                   '08062023_1400': ('Roy', 'Yael', 'Alon', 'Sahar'),
                   '05062023_1200': ('Roy', 'Alon', 'Alon', 'Sahar'),
                   '29052023_0800': ('Roy', 'Alon', 'Alon', 'Sahar'),
                   '11052023_1530': ('Roy', 'Yael', 'Alon', 'Sahar'),
                   '29062023_1615': ('Sahar', 'Roy', 'Alon', 'Yael'),

                   }
        return choices[date]

    def run(self, date) -> pd.DataFrame:
        self.subject_A = Niralysis(self.subject_A_path)
        self.subject_B = Niralysis(self.subject_B_path)

        self.subject_A.set_hbo_data(None, False, high_pass_freq=0.4)
        self.subject_B.set_hbo_data(None, False, high_pass_freq=0.4)
        self.subject_A.events_handler.set_continuous_events_frame()
        self.events_table = self.subject_A.events_handler.get_continuous_events_frame()

        self.ISC_table = ISC.ISC_by_events(self.events_table, self.subject_A.hbo_data.get_hbo_data(),
                                           self.subject_B.hbo_data.get_hbo_data(), by_areas=old_area_dict)

        A_pre_choice, B_pre_choice, post_choice, control = self.candidates_handler(date)
        df = pd.DataFrame(index=TABLE_ROWS, columns=self.ISC_table.columns)

        for i, candidate in enumerate([A_pre_choice, B_pre_choice, post_choice, control]):
            df.loc[TABLE_ROWS[i * 2]] = self.ISC_table.loc[candidate].iloc[0]
            df.loc[TABLE_ROWS[i * 2 + 1]] = self.ISC_table.loc[candidate].iloc[1]

        return df
