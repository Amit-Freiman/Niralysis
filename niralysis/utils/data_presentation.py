import matplotlib.pyplot as plt
import pandas as pd

from niralysis.SharedReality.Subject.Subject import Subject

def get_low_auditory_isc_plot(isc_table: pd.DataFrame, subject: Subject, mean: Subject):
    index = -1
    for event_name, event in isc_table.iterrows():
        index += 1
        if event_name in ['discussion:A', 'discussion:B', 'open discussion']:
            continue

        if event["Primary Auditory Cortex"] <= 0.2:
            subject_event_data_table = subject.get_event_data_table(index, event_name)
            mean_event_data_table = mean.get_event_data_table(index, event_name)
            subject_hbo_values = subject_event_data_table["Primary Auditory Cortex"]
            mean_hbo_values = mean_event_data_table["Primary Auditory Cortex"]
            if len(subject_hbo_values) <= len(mean_hbo_values):
                time = subject_event_data_table["Time"] - subject_event_data_table["Time"][0]
                mean_hbo_values = mean_hbo_values[:len(time)]
            else:
                time = mean_event_data_table["Time"] - mean_event_data_table["Time"][0]
                subject_hbo_values = subject_hbo_values[:len(time)]
            if "area validation" in subject_hbo_values:
                subject_hbo_values.drop("area validation", inplace=True)
            if "valid channels" in subject_hbo_values:
                subject_hbo_values.drop("valid channels", inplace=True)
            if "area validation" in mean_hbo_values:
                mean_hbo_values.drop("area validation", inplace=True)
            if "valid channels" in mean_hbo_values:
                mean_hbo_values.drop("valid channels", inplace=True)
            if "area validation" in time:
                time.drop("area validation", inplace=True)
            if "valid channels" in time:
                time.drop("valid channels", inplace=True)
            # If last values in mean_hbo_values or subject_hbo_values is NaN, remove it
            mean_hbo_values = mean_hbo_values.dropna()
            subject_hbo_values = subject_hbo_values.dropna()

            
            watch = "first" if index < 4 else "second"
            plt.figure(figsize=(15, 10))
            plt.plot(time, subject_hbo_values, linewidth=1.5, color='green', label="Subject")
            plt.plot(time, mean_hbo_values, linewidth=1.5, color='red', label="Mean", alpha=1)
            plt.xlabel('Time', fontsize=22)
            plt.ylabel('Hbo', fontsize=22)
            plt.yticks(fontsize=18)
            plt.xticks(fontsize=18)
            plt.title(f"{subject.name}, {event_name}, {watch} watch Primary Auditory Cortex", fontsize=26)
            plt.text(0.5, -0.11, f"Correlation: {event['Primary Auditory Cortex']}", fontsize=18, transform=plt.gca().transAxes, ha='center')
            plt.legend()
            plt.grid(True)
            plt.show()
