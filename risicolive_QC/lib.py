import pandas as pd
from .tests import *
from .settings import *

def quality(x):
    """
    This function assigns the quality label:
    - incoherent (QC=0/QC=1): complete or consistency tests not passed
    - wrong (QC=2): range test non passed
    - suspicious (QC=3/QC=4): step or time persistence tests non passed
    - good (QC=5): all tests are passed
    """
    if (x==0) or (x==1):
        label = 'incoherent'
    elif (x==2):
        label = 'wrong'
    elif (x==3) or (x==4):
        label = 'suspicious'
    elif (x==5):
        label = 'good'
    return label


def all_tests(df_station: pd.DataFrame):
    """
    This function compute all the tests sequentially for the single station

    Keyword arguments:
    df_station   -- pandas.dataframe with data for a single station, for a certain time interval [rows:times, columns:variables]
    """
    QC = -1
    if not complete_test(df_station):
        QC = 0
    elif not internal_consistency_test(df_station):
        QC = 1
    elif not range_test(df_station):
        QC = 2
    elif not step_test(df_station):
        QC = 3
    elif not time_persistence_test(df_station):
        QC = 4
    else:
        QC = 5
    return QC

################################################################################
def check_allStations(df_stations: pd.DataFrame):
    """
    This function compute the tests check for each station

    Keyword arguments:
    df_stations   -- pandas.dataframe with data for all stations, for a certain time interval [rows:times, columns:variables]
    """
    stations_tests = df_stations.groupby(KEY_STATION).apply(lambda station: all_tests(station)).reset_index().rename(columns={0:'QC'})
    stations_tests['QC_label'] = stations_tests['QC'].apply(lambda x: quality(x))
    return stations_tests
