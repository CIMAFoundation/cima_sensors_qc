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
    if not((qc_val & FLAGS.OK_COMPLETE.value) and (qc_val & FLAGS.OK_CONSISTENT.value)):
        label = QualityLabel.INCOMPLETE
    elif not (qc_val & FLAGS.OK_RANGE.value):
        label = QualityLabel.WRONG
    elif not((qc_val & FLAGS.OK_NO_STEPS.value) and (qc_val & FLAGS.OK_NO_PERSISTENCE.value)):
        label = QualityLabel.SUSPICIOUS
    elif (qc_val & FLAGS.OK_COMPLETE.value) and (qc_val & FLAGS.OK_CONSISTENT.value) and (qc_val & FLAGS.OK_RANGE.value) and (qc_val & FLAGS.OK_NO_STEPS.value) and (qc_val & FLAGS.OK_NO_PERSISTENCE.value):
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
