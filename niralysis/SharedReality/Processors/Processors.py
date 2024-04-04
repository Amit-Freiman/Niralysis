import os
import pandas as pd
from niralysis.SharedReality.SharedReality import SharedReality
from niralysis.SharedReality.Subject.Subject import Subject
from niralysis.ISC.ISC import ISC
from ..consts import *
from ...EventsHandler.EventsHandler import EventsHandler
from ...Niralysis import Niralysis
from ...utils.add_annotations import set_events_from_psychopy_table


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


def process_ISC_between_all_subjects(folder_path):
    """
    Processes the ISC between A and B and subjects of all the run folders within the given path.
    @param folder_path:
    @return:
    """
    subjects = []
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
            subject_A = Subject(path_A)
            subject_A.set_events_data()
            subjects.append(subject_A)
            data_frames.append(subject_A.get_hbo_data())
            subject_B = Subject(path_B)
            subject_B.set_events_data()
            subjects.append(subject_B)
            data_frames.append(subject_A.get_hbo_data())

    sum_subjects_data = sum(data_frames)

    ISC_tables = []
    for i, subject in enumerate(subjects):
        sum_subjects_exclude_i = (sum_subjects_data - data_frames[i]) / (len(data_frames) - 1)
        ISC_tables.append(ISC.ISC_by_events(subject.events_table, subject.events_table, subject.get_hbo_data(),
                                      sum_subjects_exclude_i, by_areas=old_all_sizes))


    return sum(ISC_tables) / len(ISC_tables)


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
