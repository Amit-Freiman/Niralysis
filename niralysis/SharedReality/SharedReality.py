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
UNIQUE_COMBINATION = "S1_D1"




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
    
    def check_device_order(self, unique_combination : str = UNIQUE_COMBINATION) -> bool:
        """
        Checks if the device order is correct (Old Brite, 20488/24302 and then the New Brite, 24053/24048)
        Verify by checking the channel combinations for one that is unique to this order
        
        @param unique_combination: A unique channel combination. Only if the devices are in the correct order will this combination be found
        @return: True if the devices are in the correct order, False otherwise
        """
        for channel in self.subject_A.hbo_data.get_hbo_data().columns:
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
        if subject == "A":
            data = self.subject_A.hbo_data.get_hbo_data()
        elif subject == "B":
            data = self.subject_B.hbo_data.get_hbo_data()
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
        
        if subject == "A":
            self.subject_A.hbo_data.columns = flipped_columns
        elif subject == "B":
            self.subject_B.hbo_data.columns = flipped_columns

    def run(self, date) -> pd.DataFrame:
        self.subject_A = Niralysis(self.subject_A_path)
        self.subject_B = Niralysis(self.subject_B_path)
        self.subject_A.set_hbo_data(None, False, high_pass_freq=0.4)
        if not self.check_device_order():
            self.flip_device_order("A")
        self.subject_B.set_hbo_data(None, False, high_pass_freq=0.4)
        if not self.check_device_order():
            self.flip_device_order("B")
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
