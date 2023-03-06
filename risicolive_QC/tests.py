################################################################################
# Copyright 2023, Nicolò Perello, Mirko D'Andrea
################################################################################
#This file is part of risicolive_QC.
#
#risicolive_QC is free software: you can redistribute it and/or modify it under
#the terms of the GNU General Public License as published by the
#Free Software Foundation, either version 3 of the License,
#or (at your option) any later version.
#
#risicolive_QC is distributed in the hope that it will be useful, but WITHOUT
#ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License along with
#risicolive_QC. If not, see <https://www.gnu.org/licenses/>.
################################################################################

import pandas as pd
import numpy as np
from typing import List, Any, Union, Dict, Tuple
from enum import Enum
from dataclasses import dataclass, field
from .config import *

class FLAGS(Enum):
    """
    Enum for the quality flags
    """
    ALL_NO            = np.uint16(0b0000000000000000) # none of the tests are passed
    OK_COMPLETE       = np.uint16(0b0000000000000001) # complete test is passed
    OK_CONSISTENT     = np.uint16(0b0000000000000010) # consistency test is passed
    OK_RANGE          = np.uint16(0b0000000000000100) # range test is passed
    OK_NO_STEPS       = np.uint16(0b0000000000001000) # step test is passed
    OK_NO_PERSISTENCE = np.uint16(0b0000000000010000) # persistence test is passed

class QualityLabel(Enum):
    """
    Enum for the quality label
    """
    INCOMPLETE = 3
    WRONG      = 2
    SUSPICIOUS = 1
    GOOD       = 0

## labels classification
TEST_COMPLETE = (
    FLAGS.OK_COMPLETE.value | FLAGS.OK_CONSISTENT.value
)
TEST_RANGE_OK = FLAGS.OK_RANGE.value
TEST_NOT_SUSPICIOUS = (
    FLAGS.OK_NO_STEPS.value | FLAGS.OK_NO_PERSISTENCE.value
)
TEST_GOOD = (
    FLAGS.OK_COMPLETE.value | FLAGS.OK_RANGE.value |
    FLAGS.OK_NO_STEPS.value | FLAGS.OK_NO_PERSISTENCE.value
)


################################################################################
### FUNCTIONS ##################################################################
################################################################################
def quality_check(df_station: pd.DataFrame, settings: Dict=DEFAULT):
    """
    This function compute the tests for the single station and add the label
    df_station -- pandas.dataframe with data for a single station [rows:times, columns:variables]
    settings   -- dictionary with config info for all tests
    """
    df_check = pd.DataFrame(index=df_station.index, columns=['QC', 'QC_LABEL'])
    internal_check = InternalCheck(settings)
    df_check['QC'] = internal_check.all_test(df_station)
    df_check['QC_LABEL'] = df_check['QC'].apply(lambda qc_val: quality_label(qc_val))
    return df_check

def quality_label(qc_val):
    """
    This function assigns the quality label:
    - incomplete: complete test is not passed
    - wrong:      range test is non passed
    - suspicious: step or time persistence tests are non passed
    - good:       all tests are passed
    qc_val -- value to check
    """
    # cast qc_val to int before comparing
    qc_val = np.uint16(qc_val)
    if (qc_val & TEST_COMPLETE) != TEST_COMPLETE:
        label = QualityLabel.INCOMPLETE
    elif (qc_val & TEST_RANGE_OK) != TEST_RANGE_OK:
        label = QualityLabel.WRONG
    elif (qc_val & TEST_NOT_SUSPICIOUS) != TEST_NOT_SUSPICIOUS:
        label = QualityLabel.SUSPICIOUS
    elif (qc_val & TEST_GOOD) == TEST_GOOD:
        label = QualityLabel.GOOD
    else:
        label = None
    return label.name if label else None


################################################################################
### QUALITY CHECK TESTS ########################################################
################################################################################
@dataclass
class InternalCheck():
    settings: Dict = field(default_factory=lambda: DEFAULT, init=True)

    def __post_init__(self):
        """Complete the settings"""
        which_tests = {'complete':False, 'range':False, 'step':False, 'persistence':False}
        if 'VARS_CHECK' in self.settings.keys(): # check complete_test
            which_tests['complete'] = True
        if 'RANGES' in self.settings.keys(): # check range_test
            which_tests['range'] = True
        if 'STEPS' in self.settings.keys():
            which_tests['step'] = True # check step_test
        if ('WINDOW' in self.settings.keys()) and ('VARIATIONS' in self.settings.keys()): #check persistence_test
            which_tests['persistence'] = True
        self.which_tests = which_tests


    def all_test(self, df_station: pd.DataFrame) -> pd.DataFrame:
        """This function compute all the tests consecutively"""
        df_check = pd.Series(index=df_station.index, name='internal_check', dtype='uint16')
        df_check.loc[:] = FLAGS.ALL_NO.value

        if self.which_tests['complete']:
            index_complete = self.complete_test(df_station)
        else:
            index_complete = df_check.index
        df_check.loc[index_complete] += FLAGS.OK_COMPLETE.value

        df_check.loc[:] += FLAGS.OK_CONSISTENT.value ## ALL ARE CONSISTENT - consistency_test DEPRECATED

        if self.which_tests['range']:
            index_range = self.range_test(df_station)
        else:
            index_range = df_check.index
        df_check.loc[index_range] += FLAGS.OK_RANGE.value

        if self.which_tests['step']:
            index_step = self.step_test(df_station)
        else:
            index_step = df_check.index
        df_check.loc[index_step] += FLAGS.OK_NO_STEPS.value

        if self.which_tests['persistence']:
            index_persistence = self.persistence_test(df_station)
        else:
            index_persistence = df_check.index
        df_check.loc[index_persistence] += FLAGS.OK_NO_PERSISTENCE.value

        df_check = df_check.astype('uint16')
        return df_check


    def complete_test(self, df: pd.DataFrame) -> pd.Series:
        """
        The function returns True if all data for the variables to check are present
        This check is done for each time step (e.g. for each row of the dataset)
        self.settings['VARS_CHECK'] -- variables to check
        df                          -- pandas.dataframe with data for a single station [rows:times, columns:variables]
        """
        return df[self.settings['VARS_CHECK']].notna().all(axis=1, bool_only=True)

    def range_test(self, df: pd.DataFrame) -> pd.Series:
        """
        The function checks if values for each variables are in a specified range. This check is done for each time step (e.g. for each row of the dataset)
        It return False if at least one variable is out of the range
        NOTE: NaN values are considered out of range
        self.settings['RANGES'] -- dictionary with ranges for each variable to check
        df                      -- pandas.dataframe with data for a single station [rows:times, columns:variables]
        """
        variables = list(self.settings['RANGES'].keys())
        mins = [self.settings['RANGES'][v][0] for v in self.settings['RANGES'].keys()]
        maxs = [self.settings['RANGES'][v][1] for v in self.settings['RANGES'].keys()]
        return df[variables].apply(lambda vars_check: self.range_check(vars_check=vars_check, min_vals=mins, max_vals=maxs), axis=1).all(axis=1, bool_only=True)

    def step_test(self, df: pd.DataFrame) -> pd.Series:
        """
        The function checks if non-physical steps are present between two consecutive time steps (e.g. two consecutive rows)
        It return False if at least one variable presents non-physical step
        If the test can not be performed (e.g. presence of NaN values), it returns False
        self.settings['STEPS'] -- dictionary with physically-accepted step for each variable
        df                     -- pandas.dataframe with data for a single station [rows:times, columns:variables]
        """
        variables = list(self.settings['STEPS'].keys())
        steps = [self.settings['STEPS'][v] for v in self.settings['STEPS'].keys()]
        return df[variables].diff(periods=1).abs().apply(lambda vars_check: self.range_check(vars_check=vars_check, min_vals=0, max_vals=steps), axis=1).all(axis=1, bool_only=True)

    def persistence_test(self, df: pd.DataFrame) -> pd.Series:
        """
        The function checks if data can be considered time fixed
        It returns False if at least one variable is fixed in the time window considered
        If the test cannot be performed (e.g. presence of NaN values), it returns True
        self.settings['VARIATIONS'] -- dictionary with minimum variations accepted for each variable, for a certain range [structure: [min_var, min, max]]
        self.settings['WINDOW']     -- sliding window (e.g. time interval for persistence check)
        df                          -- pandas.dataframe with data for a single station [rows:times, columns:variables]
        """
        df_test = pd.DataFrame(index=df.index, columns=self.settings['VARIATIONS'].keys())
        for var in self.settings['VARIATIONS'].keys():
            min_variation = self.settings['VARIATIONS'][var][0]
            min_val  = self.settings['VARIATIONS'][var][1]
            max_val  = self.settings['VARIATIONS'][var][2]
            df_test[var] = df[var].rolling(self.settings['WINDOW']).apply(lambda var_check: self.no_persistence_check(var_check=var_check, min_variation=min_variation, min_val=min_val, max_val=max_val), raw=True)
        df_test = df_test.fillna(1)
        return df_test.all(axis=1)


    def range_check(self, vars_check: np.array, min_vals: np.array, max_vals: np.array) -> bool:
        """This function returns True if element are in the range"""
        return (vars_check>=min_vals) & (vars_check<=max_vals)

    def no_persistence_check(self, var_check: np.array, min_variation: float, min_val: float, max_val: float) -> bool:
        """This function returns True if elements are not constants"""
        persistence = np.all((var_check>=min_val)&(var_check<=max_val)) and (np.abs(np.max(var_check)-np.min(var_check))<min_variation)
        return not persistence

    ####### DEPRECATED #########################################################
    #def consistency_test(self, df: pd.DataFrame) -> pd.Series:
    #    """
    #    The function checks data consistency for two variables A and B in each time instant:
    #    when A is NaN, B must be zero or NaN; when A is not NaN, B must be not NaN
    #    This check is done for each time step (e.g. for each row of the dataset)
    #    self.settings['VARS_CHECK'] -- variables A-B to check (WITH THIS ORDER)
    #    df                          -- pandas.dataframe with data for a single station [rows:times, columns:variables]
    #    """
    #    return df[self.settings['VARS_CONS']].apply(lambda row: self.consistency_check(row), axis=1)

    #def consistency_check(self, array: np.array) -> bool:
    #    """This function returns True if the first element is zero or NaN when the second element is NaN"""
    #    a = array[0]
    #    b = array[1]
    #    return return ((not np.isnan(a)) & (not np.isnan(b))) or ( np.isnan(a) & ((b==0) | (np.isnan(b))))
