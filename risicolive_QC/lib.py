import pandas as pd
from .tests import *
from .settings import *

################################################################################
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

################################################################################
def check_allStations(df_stations: pd.DataFrame):
    """
    This function compute the tests check for each station
    The time window in which check are computed corresponds to the times of the dataset

    Keyword arguments:
    df_stations   -- pandas.dataframe with data for ALL stations, for a certain time interval [rows:times, columns:variables]
    """
    stations_tests = df_stations.groupby(KEY_STATION).apply(lambda station: InternalCheck.all_tests(station)).reset_index().rename(columns={0:'QC'})
    stations_tests['QC_label'] = stations_tests['QC'].apply(lambda x: quality(x))
    return stations_tests
