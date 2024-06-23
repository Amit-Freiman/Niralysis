import matplotlib.pyplot as plt
import pandas as pd

from niralysis.SharedReality.Subject.Subject import Subject

def get_low_auditory_isc_plot(isc_table: pd.DataFrame, subject: Subject, mean: Subject):
    index = -1
    for event_name, event in isc_table.iterrows():
        index += 1
        if event_name in ['discussion:A', 'discussion:B', 'open discussion']:
            continue

        if event["Primary Auditory Cortex"] < 0.1:
            subject_event_data_table = subject.get_event_data_table(index, event_name)
            mean_event_data_table = mean.get_event_data_table(index, event_name)
            y_subject = subject_event_data_table["Primary Auditory Cortex"]
            y_mean = mean_event_data_table["Primary Auditory Cortex"]

            if len(y_subject) <= len(y_mean):
                time = subject_event_data_table["Time"] - subject_event_data_table["Time"][0]
                y_mean = y_mean[:len(time)]
            else:
                time = mean_event_data_table["Time"] - mean_event_data_table["Time"][0]
                y_subject = y_subject[:len(time)]

            watch = "first" if index < 4 else "second"
            plt.figure(figsize=(15, 10))
            plt.plot(time, y_subject, linewidth=1.5, color='green', label="Subject")
            plt.plot(time, y_mean, linewidth=1.5, color='red', label="Mean", alpha=1)
            plt.xlabel('Time', fontsize=22)
            plt.ylabel('Hbo', fontsize=22)
            plt.yticks(fontsize=18)
            plt.xticks(fontsize=18)
            plt.title(f"{subject.name}, {event_name}, {watch} watch Primary Auditory Cortex", fontsize=26)
            plt.legend()
            plt.grid(True)
            plt.show()
