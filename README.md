# Quality check of weather stations for RISICO LIVE network
The following package computes the quality check of data from weather stations used for the RISICO LIVE network.
RISICO LIVE network is the network of weather stations in which RISICO model is implemented.
In order to use these data for the implementation of RISICO model, the following variables are considered:
- temperature [C°]
- relative humidity [.]
- wind speed [m/s]
- wind direction [deg]
- precipitation [mm/DT] (DT: time step of data acquisition)
The time step of data acqusition for the RISICO LIVE network is **10 minutes**.

### Quality tests
Data from stations are checked every 1 hour. The quality check algorithm is composed by a list of consecutive tests, in which the use of the following test depends on the result from the previous test.
Quality tests considered are **self-based**, that is quality tests are computed internally for each weather station.

The quality tests considered are the following:
- **complete_test**: this test checks if all variables needed are present (in particular: temperature, relative humidity, wind speed, precipitation). The test is considered failed if at least one istant is not complete, and then the weather station is flagged QC=0. If the test is passed, the following test is computed;
- **internal_consistency_test**: this test checks data consistency for wind in each time instant: if wind speed is zero when wind direciton is NaN; if both wind direction and wind speed are non-zero, or zero. The test is considered failed if at least one istant is not consistent, and then the weather station is flagged QC=1. If the test is passed, the following test is computed;
- **range_test**: this test checks if values for each variables are in a certain range. The test is considered failed if at least one istant presents at least one variable out of the range, and then the weather station is flagged QC=2. If the test is passed, the following test is computed;
- **step_test**: this test checks if non-physical steps are present. The test is considered failed if at least one istant presents non-physical step in at least one variable, and then the weather station is flagged QC=3. If the test is passed, the following test is computed;
- **time_persistence_test**: this test checks if data can be considered time fixed. The test is considered failed if at least one data is time fixed in the time window considered, and then the weather station is flagged QC=4.
- if all tests are passed, the weather station is flagged QC=5.

Then, weather stations are categorized in 4 classes (referred to as QC_label):
    1. incoherent: weather stations with QC=0 o QC=1
    2. wrong: weather station with QC=2
    3. suspicious: weather station with QC=3 o QC=4
    4. good: weather station with QC=5

The algorithm works with pandas.DataFrame objects.

### References
1. Guidelines on validation procedures for meteorological data from automatic weather stations, Estévez J., Gavilán P., Giráldez J. V. (2011)
2. Guidelines on quality control procedures for data from automatic weather stations, Igor Zahumenský (2004)
3. Rescue and quality control of sub-daily meteorological data collected at Montevergine Observatory (Southern Apennines), 1884-1963, Capozzi V., Cotroneo Y., Castagno P., De Vivo C., Budillon G. (2020)
4. Quality Checks of meteorological data - QuackMe, M. Bratu, A. Toreti, M. Zampieri, and A. Ceglar (2022)

