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
def quality_label(qc):
    """
    This function assigns the quality label:
    - incomplete: complete or consistency tests not passed
    - wrong: range test non passed
    - suspicious: step or time persistence tests non passed
    - good: all tests are passed

    Keyword arguments:
    qc -- value to check
    """
    if  (~(qc & FLAGS.OK_COMPLETE.value)) | (~(qc & FLAGS.OK_CONSISTENT.value)):
        label = QualityLabel.INCOMPLETE
    elif ~(qc & FLAGS.OK_RANGE.value):
        label = QualityLabel.WRONG
    elif (~(qc & FLAGS.OK_NO_STEPS.value)) | (~(qc & FLAGS.OK_NO_PERSISTENCE.value)):
        label = QualityLabel.SUSPICIOUS
    elif qc & (FLAGS.OK_COMPLETE.value  | FLAGS.OK_CONSISTENT.value  | FLAGS.OK_RANGE.value  | FLAGS.OK_NO_STEPS.value  | FLAGS.OK_NO_PERSISTENCE.value):
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
    df_check.loc[:, 'QC_LABEL'] = df_check['QC'].apply(lambda qc: quality_label(qc))

    return df_check
