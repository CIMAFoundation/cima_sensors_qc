import pandas as pd
import numpy as np
from typing import List, Any, Union, Dict, Tuple
from dataclasses import dataclass, field
from .settings import *

################################################################################
### QUALITY CHECK TESTS ########################################################
################################################################################
@dataclass
class InternalCheck():
    settings: Dict = field(default_factory=lambda: DEFAULT, init=True)

    def __post_init__(self):
        """Complete the settings"""
        for kk in DEFAULT.keys():
            if not (kk in self.settings.keys()):
                self.settings[kk] = DEFAULT[kk]

    def complete_test(self, df_station: pd.DataFrame) -> bool:
        """
        The function checks whether all data for the specified variables are present for each time instant
        It returns False if at least one istant is not complete.
        This test can be computed on the single row (e.g. for each time)
        self.vars_check -- variables to check

        Keyword arguments:
        df_station -- pandas.dataframe with data for a single station [rows:times, columns:variables]
        """
        df_flagged = df_station.copy()
        vars = self.settings['VARS_CHECK']
        df_flagged['FLAG_NaN'] = df_flagged[vars].isnull().any(axis='columns')
        result = not df_flagged['FLAG_NaN'].any()
        return result


    def consistency_test(self, df_station: pd.DataFrame) -> bool:
        """
        The function checks data consistency for two variables A and B in each time instant:
        if both A and B are not NaN, they must be both zero or non-zero.
        It return False if at least one istant is not consistent
        This test can be computed on the single row (e.g. for each time)
        self.vars_cons -- variables A, B to check

        Keyword arguments:
        df_station -- pandas.dataframe with data for a single station [rows:times, columns:variables]
        """
        df_flagged = df_station.copy()
        vars = self.settings['VARS_CONS']
        idx = ~((df_flagged[vars[0]].isna()) & (df_flagged[vars[1]].isna()))
        df_flagged.loc[idx, 'FLAG_CONSISTENCY'] = df_flagged[idx].apply(lambda row: np.where(((row[vars[0]]==0) & (row[vars[1]]!=0)) | ((row[vars[0]]!=0) & (row[vars[1]]==0)), True, False), axis=1)
        result = not df_flagged['FLAG_CONSISTENCY'].any()
        return result


    def range_test(self, df_station: pd.DataFrame) -> bool:
        """
        The function checks if values for each variables are in a certain range
        It return false if at least one istant presents at least one variable out of the range
        This test can be computed on the single row (e.g. for each time)
        self.ranges -- dictionary with ranges for each variable to check

        Keyword arguments:
        df_station -- pandas.dataframe with data for a single station [rows:times, columns:variables]
        """
        df_flagged = df_station.copy()
        ranges = self.settings['RANGES']
        for kk in ranges.keys():
            df_flagged.loc[:, 'CHECK_RANGE_{}'.format(kk)] = df_flagged.apply(lambda row: np.where( ( (row[kk]>=ranges[kk][0]) & (row[kk]<=ranges[kk][1]) ) | (np.isnan(row[kk])), False, True), axis=1)
        df_flagged['FLAG_RANGE'] = df_flagged[['CHECK_RANGE_{}'.format(kk) for kk in ranges.keys()]].any(axis='columns')
        result = not df_flagged['FLAG_RANGE'].any()
        return result


    def step_test(self, df_station: pd.DataFrame) -> bool:
        """
        The function checks if non-physical steps are present
        It return False if at least one istant presents non-physical step in at least one variable
        This test must be computed on at least two rows (e.g. for two consecutive times)
        self.steps -- dictionary with physically-accepted step for each variable

        Keyword arguments:
        df_station -- pandas.dataframe with data for a single station [rows:times, columns:variables]
        """
        df_flagged = df_station.copy()
        steps = self.settings['STEPS']
        for kk in steps.keys():
            df_flagged.loc[:,'diff_backward_{}'.format(kk)] = np.abs(df_flagged[kk].diff(periods=1))
            df_flagged.loc[:, 'CHECK_STEP_{}'.format(kk)] = df_flagged.apply(lambda row: np.where(row['diff_backward_{}'.format(kk)]>=steps[kk], True, False), axis=1)
        df_flagged['FLAG_STEP'] = df_flagged[['CHECK_STEP_{}'.format(kk) for kk in steps.keys()]].any(axis='columns')
        result = not df_flagged['FLAG_STEP'].any()
        return result


    def time_persistence_test(self, df_station: pd.DataFrame) -> bool:
        """
        The function checks if data can be considered time fixed
        It returns False if at least one data is time fixed in the time window considered
        This test must be computed on at least two rows (e.g. for two consecutive times)
        self.variations -- dictionary with minimum variations accepted for each variable, for a certain range [structure: [min_var, min, max]]

        Keyword arguments:
        df_station -- pandas.dataframe with data for a single station [rows:times, columns:variables]
        """
        df_flagged = df_station.copy()
        flags = dict()
        variations = self.settings['VARIATIONS']
        for kk in variations.keys():
            df_flagged.loc[:, 'diff_backward_{}'.format(kk)] = np.abs(df_flagged.loc[:, kk].diff(periods=1))
            df_flagged.loc[:, 'CHECK_PERSISTENCE_{}'.format(kk)] = df_flagged.apply(lambda row: np.where((row['diff_backward_{}'.format(kk)]<variations[kk][0]) & (row[kk]>=variations[kk][1]) & (row[kk]<=variations[kk][2]) , True, False), axis=1)
            flags['FLAG_PERSISTENCE_{}'.format(kk)] = [df_flagged['CHECK_PERSISTENCE_{}'.format(kk)].iloc[1:].all().item()]
            result = not pd.DataFrame(flags).any(axis='columns').item()
        return result

################################################################################
