import pandas as pd
import numpy as np
from typing import List, Any, Union, Dict, Tuple
from enum import Enum
from dataclasses import dataclass, field
from .settings import *

class FLAGS(Enum):
    """
    Enum for the quality flags
    """
    ALL_NO            = np.uint16(0b0000000000000000) # none of the tests are passed
    OK_COMPLETE       = np.uint16(0b0000000000000001) # complete test is passed
    #OK_CONSISTENT     = np.uint16(0b0000000000000010) # consistent test is passed
    OK_RANGE          = np.uint16(0b0000000000000100) # range test is passed
    OK_NO_STEPS       = np.uint16(0b0000000000001000) # step test is passed
    OK_NO_PERSISTENCE = np.uint16(0b0000000000010000) # persistence test is passed

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
        df_check = pd.Series(index=df_station.index, name='internal_check', dtype='int16')
        df_check.loc[:] = FLAGS.ALL_NO.value
        df_check.loc[self.complete_test(df_station)]    += FLAGS.OK_COMPLETE.value
        #df_check.loc[self.consistency_test(df_station)] += FLAGS.OK_CONSISTENT.value
        df_check.loc[self.range_test(df_station)]       += FLAGS.OK_RANGE.value
        df_check.loc[self.step_test(df_station)]        += FLAGS.OK_NO_STEPS.value
        df_check.loc[self.persistence_test(df_station)] += FLAGS.OK_NO_PERSISTENCE.value
        return df_check


    def complete_test(self, df: pd.DataFrame) -> pd.Series:
        """
        The function returns True if all data for the variables to check are present
        This check is done for each time step (e.g. for each row of the dataset)
        self.settings['VARS_CHECK'] -- variables to check
        df                          -- pandas.dataframe with data for a single station [rows:times, columns:variables]
        """
        return df[self.settings['VARS_CHECK']].notna().all(axis=1, bool_only=True)

    #def consistency_test(self, df: pd.DataFrame) -> pd.Series:
    #    """
    #    The function checks data consistency for two variables A and B in each time instant:
    #    when A is NaN, B must be zero or NaN; when A is not NaN, B must be not NaN
    #    This check is done for each time step (e.g. for each row of the dataset)
    #    self.settings['VARS_CHECK'] -- variables A-B to check (WITH THIS ORDER)
    #    df                          -- pandas.dataframe with data for a single station [rows:times, columns:variables]
    #    """
    #    return df[self.settings['VARS_CONS']].apply(lambda row: self.consistency_check(row), axis=1)

    def range_test(self, df: pd.DataFrame) -> pd.Series:
        """
        The function checks if values for each variables are in a specified range: it return False if at least one variable is out of the range
        NaN values are considered out of range
        This check is done for each time step (e.g. for each row of the dataset)
        self.settings['RANGES'] -- dictionary with ranges for each variable to check
        df                      -- pandas.dataframe with data for a single station [rows:times, columns:variables]
        """
        mins = [self.settings['RANGES'][v][0] for v in self.settings['RANGES'].keys()]
        maxs = [self.settings['RANGES'][v][1] for v in self.settings['RANGES'].keys()]
        return df[self.settings['RANGES'].keys()].apply(lambda row: self.range_check(row, mins, maxs), axis=1).all(axis=1)

    def step_test(self, df: pd.DataFrame) -> pd.Series:
        """
        The function checks if non-physical steps are present between two consecutive time steps (e.g. two consecutive rows)
        It return False if at least one variable presents non-physical step, OR if the test can not be performed
        self.settings['STEPS'] -- dictionary with physically-accepted step for each variable
        df                     -- pandas.dataframe with data for a single station [rows:times, columns:variables]
        """
        df_test = pd.DataFrame(index=df.index, columns=self.settings['STEPS'].keys())
        for vv in self.settings['STEPS'].keys():
            df_test.loc[:, vv] = df[vv].rolling(2).apply(lambda ww: self.no_step_check(ww, self.settings['STEPS'][vv]), raw=True)
        df_test = df_test.fillna(False)
        return df_test.all(axis=1)

    def persistence_test(self, df: pd.DataFrame) -> pd.Series:
        """
        The function checks if data can be considered time fixed
        It returns False if at least one variable is fixed in the time window considered, or if the test can not be performed
        self.settings['VARIATIONS'] -- dictionary with minimum variations accepted for each variable, for a certain range [structure: [min_var, min, max]]
        self.settings['WINDOW']     -- sliding window (e.g. time interval for persistence check)
        df                          -- pandas.dataframe with data for a single station [rows:times, columns:variables]
        """
        df_test = pd.DataFrame(index=df.index, columns=self.settings['VARIATIONS'].keys())
        for vv in self.settings['VARIATIONS'].keys():
            df_test.loc[:, vv] = df[vv].rolling(self.settings['WINDOW']).apply(lambda ww: self.no_persistence_check(ww, self.settings['VARIATIONS'][vv][0], self.settings['VARIATIONS'][vv][1], self.settings['VARIATIONS'][vv][2]), raw=True)
        df_test = df_test.fillna(False)
        return df_test.all(axis=1)


    #def complete_check(self, array: np.array) -> bool:
    #    """This function returns True if the array does NOT contain NaN values"""
    #    return np.count_nonzero(np.isnan(array))==0

    #def consistency_check(self, array: np.array) -> bool:
    #    """This function returns True if the first element is zero or NaN when the second element is NaN"""
    #    a = array[0]
    #    b = array[1]
    #    return return ((not np.isnan(a)) & (not np.isnan(b))) or ( np.isnan(a) & ((b==0) | (np.isnan(b))))

    def range_check(self, array: np.array, a: np.array, b: np.array) -> bool:
        """This function returns True if element are in the range"""
        return (array>=a) & (array<=b)

    def no_step_check(self, array: np.array, step: float) -> bool:
        """This function returns True if there are no step in a 2-d array"""
        return (np.abs(array[1]-array[0])<=step)

    def no_persistence_check(self, array: np.array, var: float, a: float, b: float) -> bool:
        """This function returns True if elements are not constants"""
        return not ((np.count_nonzero((array>=a)&(array<=b))==array.shape[0]) & (np.count_nonzero(np.abs(np.ediff1d(array))<var)==(array.shape[0]-1)))
