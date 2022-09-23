import pandas as pd
import numpy as np
from typing import List, Any, Union, Dict, Tuple
from .settings import *

################################################################################
### QUALITY CHECK TESTS ########################################################
################################################################################
class InternalCheck():
    """
    Class for self-based tests, e.g. computed within the single station
    """

    @staticmethod
    def complete_test(df_station: pd.DataFrame, variables: List[str]) -> bool:
        """
        The function checks whether all data for the specified variables are present for each time instant
        It returns False if at least one istant is not complete.
        This test can be computed on the single row (e.g. for each time)

        Keyword arguments:
        df_station -- pandas.dataframe with data for a single station [rows:times, columns:variables]
        variables  -- list of variables to check
        """
        df_flagged = df_station.copy()
        df_flagged['FLAG_NaN'] = df_flagged[variables].isnull().any(axis='columns')
        result = not df_flagged['FLAG_NaN'].any()
        return result


    @staticmethod
    def consistency_test(df_station: pd.DataFrame, variables: List[str]) -> bool:
        """
        The function checks data consistency for two variables A and B in each time instant:
        if both A and B are not NaN, they must be both zero or non-zero.
        It return False if at least one istant is not consistent
        This test can be computed on the single row (e.g. for each time)

        Keyword arguments:
        df_station -- pandas.dataframe with data for a single station [rows:times, columns:variables]
        variables  -- variables A, B to check
        """
        df_flagged = df_station.copy()
        idx = ~((df_flagged[variables[0]].isna()) & (df_flagged[variables[1]].isna()))
        df_flagged.loc[idx, 'FLAG_CONSISTENCY'] = df_flagged[idx].apply(lambda row: np.where(((row[variables[0]]==0) & (row[variables[1]]!=0)) | ((row[variables[0]]!=0) & (row[variables[1]]==0)), True, False), axis=1)
        result = not df_flagged['FLAG_CONSISTENCY'].any()
        return result


    @staticmethod
    def range_test(df_station: pd.DataFrame, ranges: Dict[str, List[float]]) -> bool:
        """
        The function checks if values for each variables are in a certain range
        It return false if at least one istant presents at least one variable out of the range
        This test can be computed on the single row (e.g. for each time)

        Keyword arguments:
        df_station -- pandas.dataframe with data for a single station [rows:times, columns:variables]
        ranges     -- dictionary with ranges for each variable to check
        """
        df_flagged = df_station.copy()
        for kk in ranges.keys():
            df_flagged.loc[:, 'CHECK_RANGE_{}'.format(kk)] = df_flagged.apply(lambda row: np.where( ( (row[kk]>=ranges[kk][0]) & (row[kk]<=ranges[kk][1]) ) | (np.isnan(row[kk])), False, True), axis=1)
        df_flagged['FLAG_RANGE'] = df_flagged[['CHECK_RANGE_{}'.format(kk) for kk in ranges.keys()]].any(axis='columns')
        result = not df_flagged['FLAG_RANGE'].any()
        return result


    @staticmethod
    def step_test(df_station: pd.DataFrame, steps: Dict[str, float]) -> bool:
        """
        The function checks if non-physical steps are present
        It return False if at least one istant presents non-physical step in at least one variable
        This test must be computed on at least two rows (e.g. for two consecutive times)

        Keyword arguments:
        df_station -- pandas.dataframe with data for a single station [rows:times, columns:variables]
        steps      -- dictionary with physically-accepted step for each variable
        """
        df_flagged = df_station.copy()
        if len(df_flagged)<2:
            return NODATAVAL
        for kk in steps.keys():
            df_flagged.loc[:,'diff_backward_{}'.format(kk)] = np.abs(df_flagged[kk].diff(periods=1))
            df_flagged.loc[:, 'CHECK_STEP_{}'.format(kk)] = df_flagged.apply(lambda row: np.where(row['diff_backward_{}'.format(kk)]>=steps[kk], True, False), axis=1)
        df_flagged['FLAG_STEP'] = df_flagged[['CHECK_STEP_{}'.format(kk) for kk in steps.keys()]].any(axis='columns')
        result = not df_flagged['FLAG_STEP'].any()
        return result


    @staticmethod
    def time_persistence_test(df_station: pd.DataFrame, variations: Dict[str, List[float]]) -> bool:
        """
        The function checks if data can be considered time fixed
        It returns False if at least one data is time fixed in the time window considered
        This test must be computed on at least two rows (e.g. for two consecutive times)

        Keyword arguments:
        df_station -- pandas.dataframe with data for a single station [rows:times, columns:variables]
        variations -- dictionary with minimum variations accepted for each variable
        """
        df_flagged = df_station.copy()
        flags = dict()
        for kk in variations.keys():
            df_flagged.loc[:, 'diff_backward_{}'.format(kk)] = np.abs(df_flagged.loc[:, kk].diff(periods=1))
            df_flagged.loc[:, 'CHECK_PERSISTENCE_{}'.format(kk)] = df_flagged.apply(lambda row: np.where(row['diff_backward_{}'.format(kk)]<variations[kk], True, False), axis=1)
            flags['FLAG_PERSISTENCE_{}'.format(kk)] = [df_flagged['CHECK_PERSISTENCE_{}'.format(kk)].all().item()]
        result = not pd.DataFrame(flags).any(axis='columns').item()
        return result

################################################################################
