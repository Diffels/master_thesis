import pandas as pd
import os
file_dir = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(file_dir+'\dataset.csv')
df_filtered = df[df['GAMS_error'] != 2]
ds = df_filtered[['CapacityRatio', 'ShareFlex', 'ShareStorage', 'ShareWind', 'SharePV','rNTC','Curtailment_[TWh]', 'Shedding_[MWh]', 'CurtailmentToRESGeneration_[%]']]
correlation_matrix = ds.corr()
Corr_curtail = correlation_matrix['Curtailment_[TWh]']

print(Corr_curtail)
