import copy
import os
import pandas as pd
import matplotlib.pyplot as plt
from niralysis.SharedReality.SharedReality import SharedReality
from niralysis.SharedReality.Subject.Subject import Subject
from niralysis.ISC.ISC import ISC
from ..Event.Event import Event
from ..Subject.PreprocessingInstructions import PreprocessingInstructions
from ..consts import *
from ...EventsHandler.EventsHandler import EventsHandler
from ...Niralysis import Niralysis
from ...utils.add_annotations import set_events_from_psychopy_table
from ...utils.consts import TIME_COLUMN
from ...utils.data_manipulation import calculate_mean_table, count_nan_values, get_areas_dict
from ...utils.data_presentation import get_low_auditory_isc_plot


def process_ISC_by_coupels(folder_path):
    """
    Processes the ISC between A and B and subjects of all the run folders within the given path.
    @param folder_path:
    @return:
    """

    all_df = []
    all_df_dates = []

    # Iterate through all folders and subfolders
    for root, dirs, files in os.walk(folder_path):
        # Check if there are two snirf files, one ending with -A and the other ending with -B
        snirf_files = [file for file in files if file.endswith(".snirf")]
        snirf_files_A = [file for file in snirf_files if file.endswith("A.snirf")]
        snirf_files_B = [file for file in snirf_files if file.endswith("B.snirf")]

        # If both -A and -B files exist in the folder, call the run function
        if len(snirf_files_A) == 1 and len(snirf_files_B) == 1:
            path_A = os.path.join(root, snirf_files_A[0])
            path_B = os.path.join(root, snirf_files_B[0])
            date = root.split('\\')[-1]
            sharedReality = SharedReality(path_A, path_B)
            ISC_table = sharedReality.run(date)
            all_df.append(ISC_table)
            all_df_dates.append(date)

    main_table = pd.concat(all_df, keys=all_df_dates)
    return main_table





def process_ISC_between_all_subjects(folder_path, preprocess_by_event: bool):
    """s
    Processes the ISC between all subjects of all the run folders within the given path.
    For each subject calculates the isc between the subject and the means of al the rest subjects
    Presents the means of all isc calculations
    @param folder_path:
    @return:
    """
    subjects = []

    # Iterate through all folders and sub folders
    for root, dirs, files in os.walk(folder_path):
        # Check if there are two snirf files, one ending with -A and the other ending with -B
        snirf_files = [file for file in files if file.endswith(".snirf")]
        snirf_files_A = [file for file in snirf_files if file.endswith("A.snirf")]
        snirf_files_B = [file for file in snirf_files if file.endswith("B.snirf")]
        snirf_files_B_2 = [file for file in snirf_files if file.endswith("B_2.snirf")]



        # If -A or -B files exist in the folder, call the run function
        if len(snirf_files_A) >= 1:
            Subject.subject_handler(root, snirf_files_A[0], 0, subjects, preprocess_by_event)

        if len(snirf_files_B) >= 1:
            file_to_merge = snirf_files_B_2[0] if len(snirf_files_B_2) > 0 else None
            Subject.subject_handler(root, snirf_files_B[0], 1, subjects, preprocess_by_event,  file_to_merge=file_to_merge)

    merged_data, factor = merge_event_data_table(subjects, preprocess_by_event)

    ISC_tables = []
    for i, subject in enumerate(subjects):
        sum_subjects_exclude_i = mean_event_data_table(subject, merged_data, factor if not preprocess_by_event else None)
        mean_subject = Subject("")
        mean_subject.events_data = sum_subjects_exclude_i
        isc_score = ISC.subjects_ISC_by_events(subject, mean_subject, use_default_events=True, preprocess_by_event=preprocess_by_event)
        get_low_auditory_isc_plot(isc_score, subject, mean_subject)
        ISC_tables.append(isc_score)

    main = calculate_mean_table(ISC_tables, factor)
    # main.drop(['discussion:A', 'discussion:B', 'open discussion'], axis=0, inplace=True)

    return main, ISC_tables


def process_ISC_between_all_subjects_opposed_events(folder_path, preprocess_by_event: bool):
    """
    Processes the ISC between all subjects of all the run folders within the given path.
    For each subject calculates the isc between the subject event all the other events of the means of al the rest subjects
    Presents the means of all isc calculations
    @param folder_path:
    @return:
    """
    subjects = []

    # Iterate through all folders and sub folders
    for root, dirs, files in os.walk(folder_path):
        # Check if there are two snirf files, one ending with -A and the other ending with -B
        snirf_files = [file for file in files if file.endswith(".snirf")]
        snirf_files_A = [file for file in snirf_files if file.endswith("A.snirf")]
        snirf_files_B = [file for file in snirf_files if file.endswith("B.snirf")]

        # If  -A or -B files exist in the folder, call the run function
        if len(snirf_files_A) >= 1:
            Subject.subject_handler(root, snirf_files_A[0], 0, subjects, preprocess_by_event)

        if len(snirf_files_B) >= 1:
            Subject.subject_handler(root, snirf_files_B[0], 1, subjects, preprocess_by_event)

    merged_data, factor = merge_event_data_table(subjects, preprocess_by_event)

    ISC_tables = []
    tables_title = []
    for i, subject in enumerate(subjects):
        sum_subjects_exclude_i = mean_event_data_table(subject, merged_data, factor if not preprocess_by_event else None)
        new_subject = Subject("")
        new_subject.events_data = sum_subjects_exclude_i
        first_watch = ISC.subjects_ISC_by_oposed_events(subject.events_data[FIRST_WATCH],
                                                        new_subject.events_data[FIRST_WATCH])
        second_watch = ISC.subjects_ISC_by_oposed_events(subject.events_data[SECOND_WATCH],
                                                         new_subject.events_data[SECOND_WATCH])
        ISC_tables.append(first_watch)
        tables_title.append(f"{subject.name} {FIRST_WATCH}")
        ISC_tables.append(second_watch)
        tables_title.append(f"{subject.name} {SECOND_WATCH}")


    main_table = pd.concat(ISC_tables, keys=tables_title)
    return main_table

def visualize_ISC_tables(ISC_tables):
    # Extract brain areas from the columns (excluding the first column)
    brain_areas = ['Primary Auditory Cortex']

    # Initialize two plots for first view and second view
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8))

    # Define a color map for different ISC tables
    color_map = {0: 'red', 1: 'blue', 2: 'green', 3: 'yellow', 4: 'purple', 5: 'orange', 6: 'cyan',
                  7: 'magenta', 8: 'lime', 9: 'pink', 10: 'teal', 11: 'lavender', 12: 'brown', 13: 'gold',
                    14: 'navy', 15: 'olive', 16: 'maroon', 17: 'aqua', 18: 'coral', 19: 'indigo',
                      20: 'silver', 21: 'orchid', 22: 'salmon', 23: 'turquoise', 24: 'tan'} 

    # Iterate over the ISC tables and plot each one
    for i, isc_table in enumerate(ISC_tables):
        # Extract the events/subjects (assuming the first column contains these)
        isc_table.drop(['discussion:A', 'discussion:B', 'open discussion'], axis=0, inplace=True)
        
        for brain_area in brain_areas:
            # Extract ISC values for the current brain area
            isc_values = isc_table[brain_area]
            
            ax1.scatter(isc_values.index[:4], isc_values[:4], label=f'{brain_area} (Subject_{i})', color=color_map[i], alpha=0.7, marker='o', linewidths=0)
            ax2.scatter(isc_values.index[4:], isc_values[4:], label=f'{brain_area} (Subject_{i})', color=color_map[i], alpha=0.7, marker='o', linewidths=0)

    # Set plot labels and title for first view
    ax1.set_xlabel('Events')
    ax1.set_ylabel('ISC Values')
    ax1.set_title('First View')

    # Set plot labels and title for second view
    ax2.set_xlabel('Events')
    ax2.set_ylabel('ISC Values')
    ax2.set_title('Second View')

    # Create a legend to show which color represents which ISC table
    legend_labels = [f'Subject_{i}' for i in range(len(ISC_tables))]
    legend_handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color_map[i], markersize=10) for i in range(len(ISC_tables))]
    ax1.legend(legend_handles, legend_labels, loc='center left', bbox_to_anchor=(1, 0.5))
    ax2.legend(legend_handles, legend_labels, loc='center left', bbox_to_anchor=(1, 0.5))

    # Adjust the spacing between subplots
    plt.tight_layout()

    # Show the plots
    plt.show()

def process_diff_between_snirf_and_psychopy(folder_path: str) -> pd.DataFrame:
    """

    @param folder_path:
    @return: table of differences between event duration in snirf and psychopy timetables
    """

    duration_diff_df = {}

    # Iterate through all folders and subfolders.
    for root, dirs, files in os.walk(folder_path):
        # Check if there are two snirf files, one ending with -A and the other ending with -B

        try:
            snirf_files = [file for file in files if file.endswith(".snirf")]
            snirf_files_A = [file for file in snirf_files if file.endswith("A.snirf")]
            psyco_path = [file for file in files if file.endswith(".csv")]

            if len(snirf_files_A) == 1 and len(psyco_path) == 1:
                snirf_path = os.path.join(root, snirf_files_A[0])
                psyco_path = os.path.join(root, psyco_path[0])

                # creates timetable according to data from snirf file
                subject_snirf = Niralysis(snirf_path)
                subject_snirf.events_handler.set_continuous_events_frame()
                snirf_event_table = subject_snirf.events_handler.get_continuous_events_frame()

                # creates timetable according to data from snirf file
                psyco_snirf = set_events_from_psychopy_table(snirf_path, psyco_path)
                subject_psyco = EventsHandler(snirf_path)
                subject_psyco.raw_data = psyco_snirf
                subject_psyco.set_continuous_events_frame()
                psyco_event_table = subject_psyco.get_continuous_events_frame()

                duration_diff = psyco_event_table['Duration'] - snirf_event_table['Duration']
                duration_diff_df[snirf_files_A[0]] = duration_diff.values
        except:
            continue

    return pd.DataFrame(duration_diff_df)


def merge_event_data_table(subjects, preprocess_by_event: bool = False):
    merged_data = {FIRST_WATCH: {}, DISCUSSIONS: {}, SECOND_WATCH: {}}
    factor = pd.DataFrame(index=EVENTS_TABLE_NAMES, columns=subjects[0].get_event_data_table(0, EVENTS_TABLE_NAMES[0]).columns)

    for index, event in enumerate(EVENTS_TABLE_NAMES):
        data = subjects[0].get_event_data_table(index, event).fillna(0)
        for subject in subjects[1:]:
            data = data.add(subject.get_event_data_table(index, event).fillna(0))

        merged_data[EVENTS_CATEGORY[index]][event] = Event(event, data_by_area=data.fillna(0))
        factor.iloc[index] = data.loc[AREA_VALIDATION] if preprocess_by_event else None
    factor.drop(columns=[TIME_COLUMN], inplace=True)
    return merged_data, factor if preprocess_by_event else get_subjects_factor(subjects)

def get_subjects_factor(subjects: [Subject]):
    subjects_factor = subjects[0].get_hbo_data().loc[AREA_VALIDATION]
    for subject in subjects[1:]:
        subjects_factor += subject.get_hbo_data().loc[AREA_VALIDATION]
    return subjects_factor

def mean_event_data_table(subject, event_data_table, factor =None):
    mean_data = copy.deepcopy(event_data_table)
    for index, event in enumerate(EVENTS_TABLE_NAMES):
        factor = factor if factor is not None else mean_data[EVENTS_CATEGORY[index]][event].get_data_by_areas().loc[AREA_VALIDATION]
        mean_data[EVENTS_CATEGORY[index]][event].data.data_by_areas -= subject.get_event_data_table(index, event).fillna(0)
        mean_data[EVENTS_CATEGORY[index]][event].data.data_by_areas /= factor

    return mean_data


def process_nan_values(folder_path):
    """
    Processes the ISC between A and B and subjects of all the run folders within the given path.
    @param folder_path:
    @return:
    """
    subjects = {}
    data_frames = []

    # Iterate through all folders and sub folders
    for root, dirs, files in os.walk(folder_path):
        # Check if there are two snirf files, one ending with -A and the other ending with -B
        snirf_files = [file for file in files if file.endswith(".snirf")]
        snirf_files_A = [file for file in snirf_files if file.endswith("A.snirf")]
        snirf_files_B = [file for file in snirf_files if file.endswith("B.snirf")]

        # If both -A and -B files exist in the folder, call the run function
        if len(snirf_files_A) == 1 and len(snirf_files_B) == 1:
            path_A = os.path.join(root, snirf_files_A[0])
            path_B = os.path.join(root, snirf_files_B[0])
            subject_A = Subject(path_A, old_area_dict)
            subjects[subject_A.name] = count_nan_values(subject_A.get_hbo_data())
            subject_B = Subject(path_B, old_area_dict)
            subjects[subject_B.name] = count_nan_values(subject_B.get_hbo_data())

    return subjects


def create_all_heatmaps(folder_path, save_images_path, candidate_choices_path):
    # Iterate through all folders and subfolders
    for root, dirs, files in os.walk(folder_path):
        # Check if there are two snirf files, one ending with -A and the other ending with -B
        snirf_files = [file for file in files if file.endswith(".snirf")]
        snirf_files_A = [file for file in snirf_files if file.endswith("A.snirf")]
        snirf_files_B = [file for file in snirf_files if file.endswith("B.snirf")]

        # If both -A and -B files exist in the folder, call the run function
        if len(snirf_files_A) == 1 and len(snirf_files_B) == 1:
            path_A = os.path.join(root, snirf_files_A[0])
            path_B = os.path.join(root, snirf_files_B[0])
            sharedReality = SharedReality(path_A, path_B)
            sharedReality.get_wavelet_coherence_maps(save_images_path, candidate_choices_path)


