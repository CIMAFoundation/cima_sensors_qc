# **QUALITY CHECK OF DATA FROM WEATHER STATIONS**
The quality check algorithm is composed by a list of consecutive tests.
Quality tests are computed internally for the weather station.

The algorithm works with pandas.DataFrame objects, in which each **row** corresponds to a different **time** (set as index) while data from different **variables** are placed in **columns**. Tests are computed for each row (e.g. for each time step). All rows are flagged according to test passed, and classified in four classes accordingly.
The quality tests considered are the following:
- **complete test**: this test checks if all variables needed are present in each row. If test fails, the row is flagged and classified as **incomplete**;
- **range test**: this test checks if values for each variables are in a certain range. If the test fails, the weather station is flagged and classified as **wrong**;
- **step test**: this test checks if non-physical steps are present. If the test fails, the row is flagged and classified as **suspicious**;
- **time persistence test**: this test checks if data can be considered time fixed. This test work on a **sliding window**. If the test fails, the row is flagged and classified as **suspicious**.
- if all tests are passed, the row is flagged and classified as **good**.

See the **example_notebook.ipynb** for examples.


---
## Quality check of weather stations for RISICO LIVE network
DEFAULT configuration is setted for the quality check of data from weather stations used for the RISICO LIVE network.
RISICO LIVE network is the network of weather stations in which RISICO model is implemented.
In order to use these data for the implementation of RISICO model, the following variables are considered:
- temperature [C°]
- relative humidity [.]
- wind speed [m/s]
- precipitation [mm]
The time step of data acqusition for the RISICO LIVE network is **10 minutes**. The sliding window considered for the time persistence test is *2 hours*.
