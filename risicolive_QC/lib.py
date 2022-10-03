import pandas as pd
from enum import Enum
from .tests import *
from .settings import *

class QualityLabel(Enum):
    """
    Enum for the quality label
    """
    INCOMPLETE = 3
    WRONG = 2
    SUSPICIOUS = 1
    GOOD = 0

TEST_COMPLETE = (FLAGS.OK_COMPLETE.value | FLAGS.OK_CONSISTENT.value)
TEST_RANGE_OK = FLAGS.OK_RANGE.value
TEST_NOT_SUSPICIOUS = (
    FLAGS.OK_NO_STEPS.value | FLAGS.OK_NO_PERSISTENCE.value
)
TEST_GOOD = (
    FLAGS.OK_COMPLETE.value | FLAGS.OK_CONSISTENT.value |
    FLAGS.OK_RANGE.value | FLAGS.OK_NO_STEPS.value |
    FLAGS.OK_NO_PERSISTENCE.value
)


################################################################################
def quality_label(qc_val):
    """
    This function assigns the quality label:
    - good: all tests are passed
    - suspicious: step or time persistence tests non passed
    - wrong: range test non passed
    - incomplete: complete or consistency tests not passed

    Keyword arguments:
    qc_val -- value to check
    """   
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
def quality_check(df_station: pd.DataFrame, settings: Dict=DEFAULT):
    """
    This function compute all the tests sequentially for the single station

    Keyword arguments:
    df_station -- pandas.dataframe with data for a single station [rows:times, columns:variables]
    settings   -- dictionary with config info for all tests
    """
    df_check = pd.DataFrame(index=df_station.index, columns=['QC', 'QC_LABEL'])

    internal_check = InternalCheck(settings)
    df_check.loc[:, 'QC'] = internal_check.all_test(df_station)
    df_check.loc[:, 'QC_LABEL'] = df_check['QC'].apply(lambda qc_val: quality_label(qc_val))

    return df_check
