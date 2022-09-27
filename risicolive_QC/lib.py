import pandas as pd
from .tests import *
from .settings import *

################################################################################
def quality_label(qc):
    """
    This function assigns the quality label:
    - incomplete (QC=0/QC=1): complete or consistency tests not passed
    - wrong (QC=2): range test non passed
    - suspicious (QC=3/QC=4): step or time persistence tests non passed
    - good (QC=5): all tests are passed

    Keyword arguments:
    QC -- value to check
    """
    if (qc==0) or (qc==1):
        label = 'incomplete'
    elif (qc==2):
        label = 'wrong'
    elif (qc==3) or (qc==4):
        label = 'suspicious'
    elif (qc==5):
        label = 'good'
    else:
        label = None
    return label

################################################################################
def quality_test(df_station: pd.DataFrame, settings: Dict=DEFAULT):
    """
    This function compute all the tests sequentially for the single station
    complete/consistency/range tests -> computed at each time separately
    step test                        -> computed in a 2-time window
    time persistence test            -> computed in a sliding window

    Keyword arguments:
    df_station -- pandas.dataframe with data for a single station [rows:times, columns:variables]
    settings   -- dictionary with config info for all tests
    """
    check = InternalCheck(settings)

    window = check.settings['WINDOW']
    WW = window-1
    df_station_check = df_station.copy()
    df_station_check.loc[:, 'QC'] = None
    for idx in range(WW, len(df_station)):
        if not check.complete_test(df_station.iloc[idx:idx+1]):
            df_station_check.iloc[(idx, -1)] = 0
        elif not check.consistency_test(df_station.iloc[idx:idx+1]):
            df_station_check.iloc[(idx, -1)] = 1
        elif not check.range_test(df_station.iloc[idx:idx+1]):
            df_station_check.iloc[(idx, -1)] = 2
        elif not check.step_test(df_station.iloc[idx-1:idx+1]):
            df_station_check.iloc[(idx, -1)] = 3
        elif not check.time_persistence_test(df_station.iloc[idx-WW:idx+1]):
            df_station_check.iloc[(idx, -1)] = 4
        else:
            df_station_check.iloc[(idx, -1)] = 5
    df_station_check.loc[:, 'QC_label'] = df_station_check['QC'].apply(lambda qc: quality_label(qc))
    return df_station_check
