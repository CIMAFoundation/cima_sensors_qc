import pandas as pd
import numpy as np
from datetime import timedelta, datetime
import os
import glob
from typing import List, Any, Union, Dict, Tuple
from .settings import *

################################################################################
### QUALITY CHECK TESTS ########################################################
################################################################################
class InternalCheck():
    """
    Class for self-based tests
    """
    def __init__(self):
        pass

    @staticmethod
    def all_tests(df_station: pd.DataFrame):
        """
        This function compute all the tests sequentially for the single station

        Keyword arguments:
        df_station   -- pandas.dataframe with data for a single station, for a certain time interval [rows:times, columns:variables]
        """
        QC = -1
        if not InternalCheck.complete_test(df_station):
            QC = 0
        elif not InternalCheck.internal_consistency_test(df_station):
            QC = 1
        elif not InternalCheck.range_test(df_station):
            QC = 2
        elif not InternalCheck.step_test(df_station):
            QC = 3
        elif not InternalCheck.time_persistence_test(df_station):
            QC = 4
        else:
            QC = 5
        return QC


    @staticmethod
    def complete_test(df_station: pd.DataFrame) -> bool:
        """
        The function checks whether all data required to reconstruct RISICO are present for each time instant
        It returns False if at least one istant is not complete

        Keyword arguments:
        df_station   -- pandas.dataframe with data for a single station, for a certain time interval [rows:times, columns:variables]
        """
        df_flagged = df_station.copy()
        df_flagged['FLAG_NaN'] = df_flagged[VALUES_CHECK].isnull().any(axis='columns')
        result = not df_flagged['FLAG_NaN'].any()
        return result


    @staticmethod
    def internal_consistency_test(df_station: pd.DataFrame) -> bool:
        """
        The function checks data consistency for wind in each time instant:
        - if wind speed is zero when wind direciton is NaN
        - if both wind direction and wind speed are non-zero, or zero
        It return False if at least one istant is not consistent

        Keyword arguments:
        df_station   -- pandas.dataframe with data for a single station, for a certain time interval [rows:times, columns:variables]
        """
        df_flagged = df_station.copy()
        df_flagged.loc[df_flagged.wd.isna(), 'FLAG_CONSISTENCY'] = df_flagged[df_flagged.wd.isna()].apply(lambda row: np.where(row['ws']!=0, True, False), axis=1)
        df_flagged.loc[~df_flagged.wd.isna(), 'FLAG_CONSISTENCY'] = df_flagged[~df_flagged.wd.isna()].apply(lambda row: np.where(((row['ws']==0) & (row['wd']!=0)) | ((row['ws']!=0) & (row['wd']==0)), True, False), axis=1)
        result = not df_flagged['FLAG_CONSISTENCY'].any()
        return result


    @staticmethod
    def range_test(df_station: pd.DataFrame) -> bool:
        """
        The function checks if values for each variables are in a certain range
        It return false if at least one istant presents at least one variable out of the range

        Keyword arguments:
        df_station   -- pandas.dataframe with data for a single station, for a certain time interval [rows:times, columns:variables]
        """
        df_flagged = df_station.copy()
        for kk in RANGES.keys():
            df_flagged.loc[:, 'CHECK_RANGE_{}'.format(kk)] = df_flagged.apply(lambda row: np.where( ( (row[kk]>=RANGES[kk][0]) & (row[kk]<=RANGES[kk][1]) ) | (np.isnan(row[kk])), False, True), axis=1)
        df_flagged['FLAG_RANGE'] = df_flagged[['CHECK_RANGE_{}'.format(kk) for kk in RANGES.keys()]].any(axis='columns')
        result = not df_flagged['FLAG_RANGE'].any()
        return result


    @staticmethod
    def step_test(df_station: pd.DataFrame) -> bool:
        """
        The function checks if non-physical steps are present
        It return False if at least one istant presents non-physical step in at least one variable

        Keyword arguments:
        df_station   -- pandas.dataframe with data for a single station, for a certain time interval [rows:times, columns:variables]
        """
        df_flagged = df_station.copy()
        for kk in STEPS.keys():
            df_flagged.loc[:,'diff_backward_{}'.format(kk)] = np.abs(df_flagged[kk].diff(periods=1))
            df_flagged.loc[:, 'diff_forward_{}'.format(kk)]  = np.abs(df_flagged[kk].diff(periods=-1))
            df_flagged.loc[:, 'CHECK_STEP_{}'.format(kk)] = df_flagged.apply(lambda row: np.where((row['diff_backward_{}'.format(kk)]>=STEPS[kk]) | (row['diff_forward_{}'.format(kk)]>=STEPS[kk]), True, False), axis=1)
        df_flagged['FLAG_STEP'] = df_flagged[['CHECK_STEP_{}'.format(kk) for kk in STEPS.keys()]].any(axis='columns')
        df_flagged['FLAG_STEP'] = df_flagged[['CHECK_STEP_{}'.format(kk) for kk in STEPS.keys()]].any(axis='columns')
        result = not df_flagged['FLAG_STEP'].any()
        return result


    @staticmethod
    def time_persistence_test(df_station: pd.DataFrame) -> bool:
        """
        The function checks if data can be considered time fixed
        It returns False if at least one data is time fixed in the time window considered

        Keyword arguments:
        df_station   -- pandas.dataframe with data for a single station, for a certain time interval [rows:times, columns:variables]
        """
        df_flagged = df_station.copy()
        flags = dict()
        for kk in VARIATIONS.keys():
            df_flagged.loc[:, 'diff_backward_{}'.format(kk)] = np.abs(df_flagged.loc[:, kk].diff(periods=1))
            df_flagged.loc[:, 'diff_forward_{}'.format(kk)]  = np.abs(df_flagged.loc[:, kk].diff(periods=-1))
            if len(VARIATIONS[kk])==1:
                df_flagged.loc[:, 'CHECK_PERSISTENCE_{}'.format(kk)] = df_flagged.apply(lambda row: np.where((row['diff_backward_{}'.format(kk)]<VARIATIONS[kk][0]) | (row['diff_forward_{}'.format(kk)]<VARIATIONS[kk][0]), True, False), axis=1)
            else:
                df_flagged.loc[:, 'CHECK_PERSISTENCE_{}'.format(kk)] = df_flagged.apply(lambda row: np.where(((row['diff_backward_{}'.format(kk)]<VARIATIONS[kk][2]) | (row['diff_forward_{}'.format(kk)]<VARIATIONS[kk][2])) & (row[kk]>=VARIATIONS[kk][0]) & (row[kk]<=VARIATIONS[kk][1]), True, False), axis=1)
            flags['FLAG_PERSISTENCE_{}'.format(kk)] = [df_flagged['CHECK_PERSISTENCE_{}'.format(kk)].all().item()]
        result = not pd.DataFrame(flags).any(axis='columns').item()
        return result, df_flagged

################################################################################
