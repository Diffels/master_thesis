'''
File that computes the rNTC ratio used as exogeneous variable in the model.
Use data and code given by Tareen Muhammad UMAIR from thermodynamics lab, @t Uliege.

October 2024
'''

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 24 15:46:42 2024
"""

import pandas as pd
import pypsa


def extracting_ac_interconnections_max_transfer_capacities(n):
  """ Extracting the data for max transfer capacity on AC interconnections """
  data_ac = n.lines
  new_index_ac = data_ac['bus0'].str[:2] + ' --> ' + data_ac['bus1'].str[:2]
  multi_index_ac = pd.MultiIndex.from_arrays([data_ac.index, new_index_ac], names=('Line', 'Connection'))
  empty_df_ac = pd.DataFrame(index=multi_index_ac).T
  time_series_ac = n.lines_t.p1
  for column in time_series_ac.columns:
    if column in empty_df_ac.columns.get_level_values('Line'):
        empty_df_ac[column] = time_series_ac[column].values

  empty_df_ac = empty_df_ac.loc[:, (empty_df_ac != 0).any(axis=0)]
  empty_df_ac = empty_df_ac.abs()
  #max values on each transmission line
  max_values_ac = empty_df_ac.max().rename("Max_transfer_capacity [MW]")
  return max_values_ac


def extracting_dc_interconnections_max_transfer_capacities(n):
  """ Extracting the data for max transfer capacity on DC interconnections """
  data_dc = n.links
  data_dc = data_dc[data_dc['carrier'] == 'DC']
  data_dc = data_dc[~data_dc.index.str.contains('reversed')]
  data_dc = data_dc[data_dc['bus0'].str[:2] != data_dc['bus1'].str[:2]]
  new_index_dc = data_dc['bus0'].str[:2] + ' --> ' + data_dc['bus1'].str[:2]
  multi_index_dc = pd.MultiIndex.from_arrays([data_dc.index, new_index_dc], names=('Link', 'Connection'))
  empty_df_dc = pd.DataFrame(index=multi_index_dc).T
  time_series_dc = n.links_t.p1
  for column in time_series_dc.columns:
    if column in empty_df_dc.columns.get_level_values('Link'):
        empty_df_dc[column] = time_series_dc[column].values

  empty_df_dc = empty_df_dc.loc[:, (empty_df_dc != 0).any(axis=0)]
  empty_df_dc = empty_df_dc.abs()
  #max values on each transmission line
  max_values_dc = empty_df_dc.max().rename("Max_transfer_capacity [MW]")
  return max_values_dc


def extracting_peak_load(n):
  """ Extracting data for Peak load """
  data_load = n.loads_t.p
  drop_columns = ['H2', 'heat', 'gas', 'process', 'fuel cell', 'oil', 'aviation', 'shipping', 'naphtha', 'biomass']
  data_load_filtered = data_load[data_load.columns[~data_load.columns.str.contains('|'.join(drop_columns))]]
  data_load_grouped = data_load_filtered.groupby(data_load_filtered.columns.str[:2], axis=1).sum()
  if year != "2020":
    data_load_grouped = data_load_grouped.drop(columns=['EU'])
  # Extracting the peak load value
  max_values_load = data_load_grouped.max().rename("Peak load [MW]")
  return max_values_load


def extracting_battery_data(n):
 """ Extracting data for Stationary batteries installed energy capacities (MWh) on EU level """

 data_battery_energy = n.stores
 data_battery_energy = data_battery_energy[data_battery_energy['carrier'] == 'Li ion']
 battery_energy_capacity = data_battery_energy.e_nom_opt.sum()

 """ Extracting the power capacity (MW) of data based on max power supplied at any hour to the grid
    from battery storage and then combining them as there is no direct way to get the power capacity of 
    batteries in pypsa. If we counter check the energy to power capacity ratio its around 5 """
 data_power_battery = n.stores_t.p
 data_power_battery_filtered = data_power_battery.filter(regex='battery storage', axis=1)
 data_power_battery_filtered = data_power_battery_filtered.abs()
 battery_power_capacity = data_power_battery_filtered.max().sum()

 power_energy_capacity_ratio = battery_energy_capacity/battery_power_capacity
 
 return battery_energy_capacity,battery_power_capacity,power_energy_capacity_ratio


def compute_rNTC(max_values_ac, max_values_dc, max_values_load, disp=False):
  # Step 1: Convert max_values_ac and max_values_dc to DataFrames to extract source zones
  data_ac = max_values_ac.reset_index()
  data_ac.columns = ['Line', 'Connection', 'Max_transfer_capacity [MW]']  # Renaming columns for easier access
  data_ac['Source Zone'] = data_ac['Connection'].str.split(' --> ').str[0]  # Extract the source zone

  data_dc = max_values_dc.reset_index()
  data_dc.columns = ['Link', 'Connection', 'Max_transfer_capacity [MW]']  # Renaming columns for easier access
  data_dc['Source Zone'] = data_dc['Connection'].str.split(' --> ').str[0]  # Extract the source zone

  # Step 2: Combine AC and DC data
  combined_data = pd.concat([data_ac, data_dc], ignore_index=True)

  # Step 3: Calculate NTC_z for each zone by summing up the Max_transfer_capacity for each Source Zone
  ntc_z_combined = combined_data.groupby('Source Zone')['Max_transfer_capacity [MW]'].sum()

  # Step 4: Calculate the sum of peak loads from max_values_load
  sum_peak_loads = max_values_load.sum()

  # Step 5: Calculate the sum of all NTC_z_combined values
  sum_ntc_z_combined = ntc_z_combined.sum()

  # Step 6: Calculate rNTC according to Equation 3.9
  rNTC = sum_ntc_z_combined / sum_peak_loads

  if disp:
    # Print results
    print("NTC values for each zone (NTC_z_combined):")
    for zone, ntc in ntc_z_combined.items():
        print(f"{zone}: {ntc} MW")

    print("\nSum of Peak Loads:", sum_peak_loads, "MW")
    print("Sum of Combined NTC_z values (AC + DC):", sum_ntc_z_combined, "MW")
    print("Ratio NTC (rNTC):", rNTC)

  return rNTC, sum_ntc_z_combined, sum_peak_loads

if __name__ == '__main__':

  years = ["2020", "2030", "2040", "2050"]
  dir_path = r"C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\pymedeas2_models\models\europe\modules_pymedeas_eu\surr_model\pypsa\rNTC\data_extract\extract_rNTC.csv"
  countries= ['AT', 'BE', 'BG', 'CH', 'CZ', 'DE', 'DK', 'EE', 'ES', 'FI', 'FR', 'GB', 'GR', 'HR', 'HU', 'IE', 'IT', 'LT', 'LU', 'LV', 'NL', 'NO', 'PL', 'PT', 'SE', 'SI', 'SK', 'RO']

  output = pd.DataFrame(index=years)

  for year in years:
    net_path = r"C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\Umair\rNTC\Code_data 1\Code_data\elec_s_32_lvopt_EQ0.70c_1H-T-H-B-I-A-dist1_"+year+".nc"
    n=pypsa.Network(net_path)

    max_values_ac = extracting_ac_interconnections_max_transfer_capacities(n)
    max_values_dc = extracting_dc_interconnections_max_transfer_capacities(n)
    max_values_load = extracting_peak_load(n)
    # battery_energy_capacity, battery_power_capacity, power_energy_capacity_ratio =  extracting_battery_data(n)

    rNTC, sum_rNTC_z, sum_peak_loads = compute_rNTC(max_values_ac, max_values_dc, max_values_load, disp=False)

    output.loc[year, 'rNTC [-]'] = rNTC
    output.loc[year, 'sum_rNTC_z [MW]'] = sum_rNTC_z
    output.loc[year, 'sum_peak_loads [MW]'] = sum_peak_loads

  print(output)
  output.to_csv(dir_path, index_label='Years')