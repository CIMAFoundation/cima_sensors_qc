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
    - incomplete (QC=0/QC=1): complete or consistency tests not passed
    - wrong (QC=2): range test non passed
    - suspicious (QC=3/QC=4): step or time persistence tests non passed
    - good (QC=5): all tests are passed

    Keyword arguments:
    QC -- value to check
    """
    if (qc==0) or (qc==1):
        label = QualityLabel.INCOMPLETE
    elif (qc==2):
        label = QualityLabel.WRONG
    elif (qc==3) or (qc==4):
        label = QualityLabel.SUSPICIOUS
    elif (qc==5):
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
