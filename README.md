# **QUALITY CHECK OF DATA FROM WEATHER STATIONS**
This package compute the quality check of data.
The quality check algorithm is composed by a list of consecutive tests, in which the use of the following test depends on the result from the previous test.
Quality tests considered are **self-based**, that is quality tests are computed internally for each weather station.

The algorithm works with pandas.DataFrame objects, in which each **row** corresponds to a different **time** while data from different **variables** are placed in **columns**. Tests are computed for each row.
The quality tests considered are the following:
- **complete_test**: this test checks if all variables needed are present in each row. If test fails, the row is flagged QC=0. If the test is passed, the following test is computed;
- **internal_consistency_test**: this test checks data consistency, e.g. if two variables are both zero or non-zero. If the test fails, the row is flagged QC=1. If the test is passed, the following test is computed;
- **range_test**: this test checks if values for each variables are in a certain range. If the test fails, the weather station is flagged QC=2. If the test is passed, the following test is computed;
- **step_test**: this test checks if non-physical steps are present. This test work on a **sliding window**. If the test fails, the row is flagged QC=3. If the test is passed, the following test is computed;
- **time_persistence_test**: this test checks if data can be considered time fixed. This test work on a **sliding window**. If the test fails, the row is flagged QC=4.
- if all tests are passed, the row is flagged QC=5.

Then, rows are categorized in 4 classes (referred to as QC_label):
    1. incomplete: with QC=0 o QC=1
    2. wrong: weather with QC=2
    3. suspicious: with QC=3 o QC=4
    4. good: with QC=5

See the **example_notebook.ipynb** for examples.

---
## Quality check of weather stations for RISICO LIVE network
DEFAULT configuration is setted for the quality check of data from weather stations used for the RISICO LIVE network.
RISICO LIVE network is the network of weather stations in which RISICO model is implemented.
In order to use these data for the implementation of RISICO model, the following variables are considered:
- temperature [C°]
- relative humidity [.]
- wind speed [m/s]
- wind direction [deg]
- precipitation [mm/DT] (DT: time step of data acquisition)
The time step of data acqusition for the RISICO LIVE network is **10 minutes**. All information needed for each test is contained in the **config.json** file.

### References
1. Guidelines on validation procedures for meteorological data from automatic weather stations, Estévez J., Gavilán P., Giráldez J. V. (2011)
2. Guidelines on quality control procedures for data from automatic weather stations, Igor Zahumenský (2004)
3. Rescue and quality control of sub-daily meteorological data collected at Montevergine Observatory (Southern Apennines), 1884-1963, Capozzi V., Cotroneo Y., Castagno P., De Vivo C., Budillon G. (2020)
4. Quality Checks of meteorological data - QuackMe, M. Bratu, A. Toreti, M. Zampieri, and A. Ceglar (2022)
