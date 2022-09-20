import pandas as pd
import risicolive_QC as qc

def main():
    df = pd.read_csv('test/hours/12.csv')
    ss = qc.lib.check_allStations(df)
    ss.loc[:, 'date'] = df.date.iloc[0]
    ss[['date', qc.settings.KEY_STATION, 'QC', 'QC_label']].to_csv('test/hours/12_QC.csv', index=False)
    return

if __name__=='__main__':
    main()
