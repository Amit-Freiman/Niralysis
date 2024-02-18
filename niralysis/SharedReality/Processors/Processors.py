import os
import pandas as pd
from niralysis.SharedReality.SharedReality import SharedReality
from niralysis.SharedReality.Subject.Subject import Subject
from niralysis.ISC.ISC import ISC
from ..consts import *


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
            print(path_A)
            subject_A = Subject(path_A)
            subjects.append(subject_A)
            data_frames.append(subject_A.subject.hbo_data.get_hbo_data())
            print(path_B)
            subject_B = Subject(path_B)
            subjects.append(subject_B)
            data_frames.append(subject_A.subject.hbo_data.get_hbo_data())

    sum_subjects_data = sum(data_frames)

    ISC_tables = []
    for i, subject in enumerate(subjects):
        sum_subjects_exclude_i = (sum_subjects_data - data_frames[i]) / (len(data_frames) -1)
        ISC_tables.append(ISC.ISC_by_events(subject.events_table, subject.subject.hbo_data.get_hbo_data(),
                                      sum_subjects_exclude_i, by_areas=old_area_dict))


    return sum(ISC_tables) / len(ISC_tables)
