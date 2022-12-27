# **QUALITY CHECK OF DATA FROM WEATHER STATIONS**
The quality check algorithm is composed by a list of consecutive tests.
Quality tests considered are **self-based**, that is quality tests are computed internally for the weather station.

The algorithm works with pandas.DataFrame objects, in which each **row** corresponds to a different **time** (set as index) while data from different **variables** are placed in **columns**. Tests are computed for each row (e.g. for each time step). All rows are flassged according to test passed, and classified in four classes accordignly.
The quality tests considered are the following:
- **complete test**: this test checks if all variables needed are present in each row. If test fails, the row is flagged and classified as **incomplete**;
- **internal consistency_test**: this test checks data consistency, e.g. if two variables are both zero or non-zero. If the test fails, the row is flagged and classified as **incomplete**;
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
- wind direction [deg]
- precipitation [mm/DT] (DT: time step of data acquisition)
The time step of data acqusition for the RISICO LIVE network is **10 minutes**. The sliding window considered for the time persistence test is *2 hours*.

### References
1. Zahumenský, I. (2004). Guidelines on quality control procedures for data from automatic weather stations. World Meteorological Organization, 955, 2–6. http://www.wmo.int/pages/prog/www/IMOP/publications/IOM-82-TECO_2005/Papers/3(14)_Slovakia_2_Zahumensky.pdf
2. Estévez, J., Gavilán, P., & Giráldez, J. V. (2011). Guidelines on validation procedures for meteorological data from automatic weather stations. Journal of Hydrology, 402(1–2), 144–154.https://doi.org/10.1016/j.jhydrol.2011.02.031
3. Capozzi, V., Cotroneo, Y., Castagno, P., De Vivo, C., & Budillon, G. (2020). Rescue and quality control of sub-daily meteorological data collected at Montevergine Observatory (Southern Apennines), 1884-1963. Earth System Science Data, 12(2), 1467–1487. https://doi.org/10.5194/essd-12-1467-2020
4. WMO, Guidelines on Surface Station Data Quality Control and Quality Assurance for Climate Applications (2021), ISBN 978-92-63-11269-9
5. M. Bratu, A. Toreti, M. Zampieri, and A. Ceglar (2022), Quality Checks of meteorological data - QuackMe, Publications Office of the European Union, Luxembourg, ISBN 978-92-76-46870-7, doi:10.2760/96559, JRC128152.