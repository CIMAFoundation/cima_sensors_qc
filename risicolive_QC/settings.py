KEY_STATION = 'station_id'

################################################################################
# TEST 1
VALUES_CHECK = ['t', 'h', 'p', 'ws'] # variables checked by complete_test
# TEST 3
RANGES = {  # Physical range [min, max] used by range_test
    't':  [-30, 50],    # temperature [C°]         -> ref: 1
    'h':  [0, 100],     # relative humidity [.]    -> ref: 3
    'p':  [0, 400],     # precipitation [mm/10min] -> ref: 2
    'ws': [0, 75],      # wind speed [m/s]         -> ref: 2
    'wd': [0, 360],     # wind direction [deg]
}
# TEST 4
STEPS = {  # Steps accepted in 10min -> ref: 2
    't':  2,         # temperature [C]
    'h':  10,        # relative humidity [.]
    'ws': 10,        # wind speed [m/s]
}
# TEST 5
VARIATIONS = { # Minimum variation -> variations less than this value are considered as zero-variations
    # Structure:
    # - list with 1 value: this value is considered as minimum variation for the entire range
    # - list with 3 values: the third value is the minum variation checked in the range specified by the first and second value
    # E.g. : for the relative humidity, variations less than 0.5% are null-variations in the range [0%, 95%]
    't':  [0.01],         # temperature [C]
    'h':  [0, 95, 0.1],   # relative humidity [.]
    'ws': [0.1, 75, 0.1], # wind speed [m/s]
}
