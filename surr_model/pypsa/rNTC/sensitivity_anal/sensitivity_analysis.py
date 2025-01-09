"""
Sensitive Analysis related to the behaviour of rNTC with grid related investements.

Wrote by Noe Diffels, from pypsa data obtained.
November 2024
"""
import pandas as pd
import numpy as np
from scipy.interpolate import interp1d


"""
Files Paths
"""
rNTC_path = r"C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\pymedeas2_models\models\europe\modules_pymedeas_eu\surr_model\pypsa\rNTC\interp_rNTC.csv"
capacity_path = r"C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\pymedeas2_models\models\europe\modules_pymedeas_eu\surr_model\pypsa\rNTC\sensitivity_anal\inputs\capacities.csv"
out_path = r"C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\pymedeas2_models\models\europe\modules_pymedeas_eu\surr_model\pypsa\rNTC\sensitivity_anal\output\ratio_rNTC_TW.csv"

"""
Data extraction
"""
rNTC = pd.read_csv(rNTC_path, index_col=0)
capacities = pd.read_csv(capacity_path, index_col=1)

grid_distribution_capacity = capacities.loc[capacities.index.str.contains('electricity distribution grid')]
AC_lines_capacity = capacities.loc[capacities.index.str.contains('AC')]
DC_lines_capacity = capacities.loc[capacities.index.str.contains('DC')]

# Initialize an empty DataFrame with years as the index
NTC_capacities = pd.DataFrame(index=[2020, 2030, 2040, 2050])
NTC_capacities.index.name = "Year"  # Add an index name
# Compute values for each year
for year in NTC_capacities.index:
    year_str = str(year)  # Ensure year is a string to match column names
    grid_value = grid_distribution_capacity.loc['electricity distribution grid', year_str]
    ac_value = AC_lines_capacity.loc['AC', year_str]
    dc_value = DC_lines_capacity.loc['DC', year_str]

    NTC_capacities.loc[year, 'Distrib Grid'] = grid_value
    NTC_capacities.loc[year, 'AC Lines'] = ac_value
    NTC_capacities.loc[year, 'DC Lines'] = dc_value
    #NTC_capacities.loc[year, 'Total'] = grid_value + ac_value + dc_value
NTC_capacities = NTC_capacities.T
print(NTC_capacities)

"""
Data Interpolation
"""
all_years = np.arange(1995, 2051, 1)
known_years = [2020, 2030, 2040, 2050]

interpolated_data = {}
for row in NTC_capacities.index:
    interpolation_func = interp1d(known_years, NTC_capacities.loc[row], kind='linear', fill_value="extrapolate")
    interpolated_values = interpolation_func(all_years)
    interpolated_values[interpolated_values < 0] = 0  # Replace negative values with 0
    interpolated_data[row] = interpolated_values

dfNTC = pd.DataFrame(interpolated_data, index=all_years)
dfNTC['Total'] = dfNTC.sum(axis=1)

ratio_rNTC_MW = rNTC["rNTC"]/dfNTC['Total']
ratio_rNTC_TW = ratio_rNTC_MW * 1e6 # pb here

ratio_rNTC_TW.name = "Ratio"

print(ratio_rNTC_TW)
ratio_rNTC_TW.to_csv(out_path, index_label='Year')

import matplotlib.pyplot as plt
plt.figure(figsize=(10, 6))
plt.plot(ratio_rNTC_TW.index, ratio_rNTC_TW.values)
plt.show()