import pandas as pd

from niralysis.utils.consts import TIME_COLUMN


def set_data_by_areas(df: pd.DataFrame, areas: dict) -> pd.DataFrame:
    data_by_area = pd.DataFrame()
    data_by_area[TIME_COLUMN] = df[TIME_COLUMN]
    for area in areas.keys():
        data_by_area[area] = df.iloc[:, areas[area]].mean(axis=1)

    return data_by_area


def set_before_and_after_difference_table(ISC_table: pd.DataFrame, events: [str]):
    difference_table = pd.DataFrame()

    for event in events:
        difference_table.append(ISC_table.loc[event].iloc[0] - ISC_table.loc[event].iloc[1], index=event)



##
