################################################################################
# Copyright 2023, Nicolò Perello, Mirko D'Andrea
################################################################################
#This file is part of cima_sensors_qc.
#
#cima_sensors_qc is free software: you can redistribute it and/or modify it under
#the terms of the GNU General Public License as published by the
#Free Software Foundation, either version 3 of the License,
#or (at your option) any later version.
#
#cima_sensors_qc is distributed in the hope that it will be useful, but WITHOUT
#ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License along with
#cima_sensors_qc. If not, see <https://www.gnu.org/licenses/>.
################################################################################

import pandas as pd
import numpy as np
import sys 
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from cima_sensors_qc import InternalCheck, quality_check

###
settings = {
    'VARS_CHECK': ['a', 'b'],
    'RANGES': {
        'a': [0,2],
        'b':[0,2]
        },
    'STEPS': {
        'a': 1,
        'b': 2
    },
    "WINDOW": 3,
    "VARIATIONS": {
            "a":  [1.1, 1, 3],
            "b":  [2.1, 5, 7],
    }
}


def main():

    print('* InternalCheck tests:')
    IC = InternalCheck(settings)

    print('   - single tests')
    # COMPLETE CHECK
    print('       - complete test...', end='')
    df_complete = pd.read_csv('test_complete.csv', index_col=0)
    df_complete.loc[:, 'result'] = IC.complete_test(df_complete)
    print(df_complete.result.equals(df_complete.check))

    # RANGE CHECK
    print('       - range test...')
    df_range = pd.read_csv('test_range.csv', index_col=0)
    ## check single variables
    print('             single variables: ')
    for var in settings['RANGES'].keys():
        print('                 {}: '.format(var), end='')
        mins = settings['RANGES'][var][0]
        maxs = settings['RANGES'][var][1]
        df_tmp = df_range[var].apply(lambda vars_check: IC.range_check(vars_check=vars_check, min_vals=mins, max_vals=maxs))
        print(df_range['{}_check'.format(var)].equals(df_tmp))
    df_range.loc[:, 'result'] = IC.range_test(df_range)
    print('             all variables: ', df_range.result.equals(df_range.check))

    # STEP CHECK
    print('       - step test...')
    df_step = pd.read_csv('test_step.csv', index_col=0)
    ## check single variables
    print('             single variables: ')
    for var in settings['STEPS'].keys():
        print('                 {}: '.format(var), end='')
        step = settings['STEPS'][var]
        df_tmp = df_step[var].diff(periods=1).abs().apply(lambda vars_check: IC.range_check(vars_check=vars_check, min_vals=0, max_vals=step))
        print(df_step['{}_check'.format(var)].equals(df_tmp))
    df_step.loc[:, 'result'] = IC.step_test(df_step)
    print('             all variables: ', df_step.result.equals(df_step.check))

    # PERSISTENCE CHECK
    print('       - persistence test...')
    df_persistence = pd.read_csv('test_persistence.csv', index_col=0)
    ## check single variables
    print('             single variables: ')
    for var in settings['VARIATIONS'].keys():
        print('                 {}: '.format(var), end='')
        min_variation = settings['VARIATIONS'][var][0]
        min_val  = settings['VARIATIONS'][var][1]
        max_val  = settings['VARIATIONS'][var][2]
        df_tmp = df_persistence[var].rolling(settings['WINDOW']).apply(lambda var_check: IC.no_persistence_check(var_check=var_check, min_variation=min_variation, min_val=min_val, max_val=max_val), raw=True)
        df_tmp = df_tmp.fillna(True)
        df_tmp = df_tmp.apply(lambda x: x>0)
        print(df_persistence['{}_check'.format(var)].equals(df_tmp))
    df_persistence.loc[:, 'result'] = IC.persistence_test(df_persistence)
    print('             all variables: ', df_persistence.result.equals(df_persistence.check))

    ## COMPLETE TESTS
    df_all = pd.read_csv('test_ALL.csv', index_col=0)
    df_all['check'] = df_all['check'].astype('uint16')
    df_all_checked = quality_check(df_all, settings)
    print('   - all tests: ', df_all.check.equals(df_all_checked.QC))
    print('           complete: ', df_all.check_COMPLETE.equals(IC.complete_test(df_all)))
    print('           range: ', df_all.check_RANGE.equals(IC.range_test(df_all)))
    print('           step: ', df_all.check_STEP.equals(IC.step_test(df_all)))
    print('           persistence: ', df_all.check_PERSISTENCE.equals(IC.persistence_test(df_all)))
    print('     labels: ', df_all.check_LABEL.equals(df_all_checked.QC_LABEL))


if __name__=='__main__':
    main()
