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


    def all_test(self, df_station: pd.DataFrame) -> pd.DataFrame:
        """This function compute all the tests"""
        df_check = pd.Series(index=df_station.index, name='internal_check')

        test_1 = self.complete_test(df_station)
        df_check.loc[test_1[~test_1].index] = 0

        test_2 = self.consistency_test(df_station[test_1])
        df_check.loc[test_2[~test_2].index] = 1

        test_3 = self.range_test(df_station[test_1][test_2])
        df_check.loc[test_3[~test_3].index] = 2

        test_4 = self.step_test(df_station)
        df_check.loc[test_4[(test_1) & (test_2) & (test_3) & (~test_4)].index] = 3

        test_5 = self.persistence_test(df_station)
        df_check.loc[test_5[(test_1) & (test_2) & (test_3) & (test_4) & (~test_5)].index] = 4

        df_check.loc[test_5[(test_1) & (test_2) & (test_3) & (test_4) & (test_5)].index] = 5

        return df_check


    def complete_test(self, df: pd.DataFrame) -> pd.Series:
        """
        The function checks whether all data for the specified variables are present for each time instant
        self.settings['VARS_CHECK'] -- variables to check

        Keyword arguments:
        df-- pandas.dataframe with data for a single station [rows:times, columns:variables]
        """
        return df[self.settings['VARS_CHECK']].apply(lambda row: self.complete_check(row), axis=1)

    def consistency_test(self, df: pd.DataFrame) -> pd.Series:
        """
        The function checks data consistency for two variables A and B in each time instant: they must be both zero or non-zero.
        self.settings['VARS_CHECK'] -- variables A, B to check

        Keyword arguments:
        df -- pandas.dataframe with data for a single station [rows:times, columns:variables]
        """
        return df[self.settings['VARS_CONS']].apply(lambda row: self.consistency_check(row), axis=1)

    def range_test(self, df: pd.DataFrame) -> pd.Series:
        """
        The function checks if values for each variables are in a certain range
        It return false if at least one istant presents at least one variable out of the range
        self.settings['RANGES'] -- dictionary with ranges for each variable to check

        Keyword arguments:
        df -- pandas.dataframe with data for a single station [rows:times, columns:variables]
        """
        vars = self.settings['RANGES'].keys()
        mins = [self.settings['RANGES'][v][0] for v in vars]
        maxs = [self.settings['RANGES'][v][1] for v in vars]
        return df[vars].apply(lambda row: self.range_check(row, mins, maxs), axis=1).all(axis=1)

    def step_test(self, df: pd.DataFrame) -> pd.Series:
        """
        The function checks if non-physical steps are present
        It return False if at least one istant presents non-physical step in at least one variable
        self.settings['STEPS'] -- dictionary with physically-accepted step for each variable

        Keyword arguments:
        df -- pandas.dataframe with data for a single station [rows:times, columns:variables]
        """
        df_check = pd.DataFrame(index=df.index, columns=self.settings['STEPS'].keys())
        for vv in self.settings['STEPS'].keys():
            df_check.loc[:, vv] = df[vv].rolling(2).apply(lambda ww: self.step_check(ww, self.settings['STEPS'][vv]), raw=True)
        return df_check.all(axis=1)

    def persistence_test(self, df: pd.DataFrame) -> pd.Series:
        """
        The function checks if data can be considered time fixed
        It returns False if at least one data is time fixed in the time window considered
        self.settings['VARIATIONS'] -- dictionary with minimum variations accepted for each variable, for a certain range [structure: [min_var, min, max]]
        self.settings['WINDOW']     -- sliding window
        Keyword arguments:
        df -- pandas.dataframe with data for a single station [rows:times, columns:variables]
        """
        df_check = pd.DataFrame(index=df.index, columns=self.settings['VARIATIONS'].keys())
        for vv in self.settings['VARIATIONS'].keys():
            df_check.loc[:, vv] = df[vv].rolling(self.settings['WINDOW']).apply(lambda ww: self.persistence_check(ww, self.settings['VARIATIONS'][vv][0], self.settings['VARIATIONS'][vv][1], self.settings['VARIATIONS'][vv][2]), raw=True)
        return df_check.all(axis=1)


    def complete_check(self, array: np.array) -> bool:
        """This function checks if NaN values are present in array"""
        return np.count_nonzero(np.isnan(array))==0

    def consistency_check(self, array: np.array) -> bool:
        """This function checks if the first element is zero when the second element is NaN"""
        return (array[1]!=np.nan) or ((array[1]==np.nan) & (array[1]==0))

    def range_check(self, array: np.array, a: np.array, b: np.array) -> bool:
        """This function check if elements are in the range"""
        return (array>=a) & (array<=b)

    def step_check(self, array: np.array, step: float) -> bool:
        """This function checks if there are not step in a 2-d array"""
        return (np.abs(array[1]-array[0])<=step)

    def persistence_check(self, array: np.array, var: float, a: float, b: float) -> bool:
        """This function checks if elements are considered constants"""
        return not ((np.count_nonzero((array>=a)&(array<=b))==array.shape[0]) & (np.count_nonzero(np.abs(np.ediff1d(array))<var)==(array.shape[0]-1)))
