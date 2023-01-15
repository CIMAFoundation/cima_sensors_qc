import pandas as pd
import numpy as np
from risicolive_QC import InternalCheck

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
    }
}


def main():

    print('* InternalCheck tests:')
    IC = InternalCheck(settings)

    print('   - single tests')
    # COMPLETE CHECK
    print('       - complete test...', end='')
    df_complete = pd.read_csv('test/test_complete.csv', index_col=0)
    df_complete.loc[:, 'result'] = IC.complete_test(df_complete)
    print(df_complete.result.equals(df_complete.check))

    # RANGE CHECK
    print('       - range test...', end='')
    df_range = pd.read_csv('test/test_range.csv', index_col=0)
    df_range.loc[:, 'result'] = IC.range_test(df_range)
    print(df_range.result.equals(df_range.check))

    # STEP CHECK
    print('       - step test...', end='')
    df_step = pd.read_csv('test/test_step.csv', index_col=0)
    df_step.loc[:, 'result'] = IC.step_test(df_step)
    print(df_step.result.equals(df_step.check))

if __name__=='__main__':
    main()
