import matplotlib.pyplot as plt
import pandas as pd

from niralysis.SharedReality.Subject.Subject import Subject

def get_low_auditory_isc_plot(isc_table: pd.DataFrame, subject: Subject):
    index = -1
    for event_name, event in isc_table.iterrows():
        index += 1
        if event_name in ['discussion:A', 'discussion:B', 'open discussion']:
            continue

        if event["Primary Auditory Cortex"] < 0.1:
            event_data_table = subject.get_event_data_table(index, event_name)
            watch = "first" if index < 4 else "second"
            x = event_data_table["Time"]
            y = event_data_table["Primary Auditory Cortex"]
            plt.figure(figsize=(15, 10))
            plt.plot(x, y, linewidth=1.5, color='green')
            plt.xlabel('Time', fontsize=22)
            plt.ylabel('Hbo', fontsize=22)
            plt.yticks(fontsize=18)
            plt.xticks(fontsize=18)
            plt.title(f"{subject.name}, {event_name}, {watch} watch Primary Auditory Cortex", fontsize=26)
            plt.legend()
            plt.show()
            return