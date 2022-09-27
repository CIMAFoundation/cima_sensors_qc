import pandas as pd
from .tests import *
from .settings import *

################################################################################
def quality(qc):
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
        label = 'none'
    return label

################################################################################
def complete_config(config=None):
    """This function complete the config file"""
    if config is None:
        config = DEFAULT['TEST']
    else:
        for kk in ['WINDOW', 'VARS_CHECK', 'VARS_CONS', 'RANGES', 'STEPS', 'VARIATIONS']:
            if not (kk in config.keys()):
                config[kk] = DEFAULT['TEST'][kk]
    return config

################################################################################
def all_tests(df_station: pd.DataFrame, config=None):
    """
    This function compute all the tests sequentially for the single station
    complete/consistency/range tests -> computed at each time separately
    step test -> computed in a 2-time window
    time persistence test -> computed in a sliding window

    Keyword arguments:
    df_station -- pandas.dataframe with data for a single station [rows:times, columns:variables]
    config     -- dictionary with config info for all tests
    """
    if config is None:
        return 'ERROR'

    window = config['WINDOW']
    WW = window-1
    df_station_check = df_station.copy()
    for idx in df_station.index[WW:]:
        if not complete_test(df_station.loc[idx:idx], config['VARS_CHECK']):
            df_station_check.loc[idx, 'QC'] = 0
        elif not consistency_test(df_station.loc[idx:idx], config['VARS_CONS']):
            df_station_check.loc[idx, 'QC'] = 1
        elif not range_test(df_station.loc[idx:idx], config['RANGES']):
            df_station_check.loc[idx, 'QC'] = 2
        elif not step_test(df_station.loc[idx-1:idx], config['STEPS']):
            df_station_check.loc[idx, 'QC'] = 3
        elif not time_persistence_test(df_station.loc[idx-WW:idx], config['VARIATIONS']):
            df_station_check.loc[idx, 'QC'] = 4
        else:
            df_station_check.loc[idx, 'QC'] = 5
    df_station_check.loc[:, 'QC_label'] = df_station_check['QC'].apply(lambda qc: quality(qc))
    return df_station_check

################################################################################
def check_stations(df_stations: pd.DataFrame, key_station: str=None, config=None):
    """
    This function compute the tests check for each station

    Keyword arguments:
    df_stations -- pandas.dataframe with data for different stations, for a certain time interval [rows:times, columns:variables]
    key_station -- unique identifier for stations
    config      -- dictionary with config info for all tests [defaul: in parames.json file]
    """
    config = complete_config(config)

    if key_station is None:
        key_station = DEFAULT['INFO']['KEY_STATION']
    stations_tests = df_stations.groupby(key_station, group_keys=False).apply(lambda station: allTests(station, config))
    return stations_tests
