"""
Run file to interpolate ratios_EUR_MW.xlsx and tech_shares.xlsx from [2020, 2030, 2040, 2050] to
[1995, 1996, ..., 2050], saved in interp_tech_shares.csv and interp_ratios_EUR_MW.csv. 

Wrote by Noe Diffels
November 2024
"""

import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt

# ratios = pd.read_csv(r"C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\pymedeas2_models\models\europe\modules_pymedeas_eu\surr_model\pypsa\capa and invest\data_extract\outputs\ratios_EUR_MW.csv")
shares_ls = pd.read_csv(r"C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\pymedeas2_models\models\europe\modules_pymedeas_eu\surr_model\pypsa\capa and invest\data_extract\outputs\tech_shares_ls.csv")
shares_curt = pd.read_csv(r"C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\pymedeas2_models\models\europe\modules_pymedeas_eu\surr_model\pypsa\capa and invest\data_extract\outputs\tech_shares_curt.csv")
prices = pd.read_csv(r'C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\pymedeas2_models\prices_1995USD_W.csv')
# print(shares_curt)
print(prices)

years = [2020, 2030, 2040, 2050]

# Ensure dataframes are correctly structured
shares_ls.set_index(shares_ls.columns[0], inplace=True)  # First column becomes the index
shares_curt.set_index(shares_curt.columns[0], inplace=True)  # First column becomes the index

prices.set_index(prices.columns[0], inplace=True)  # First column becomes the index
# prices = prices.T  # Transpose so years are columns

# Generate new time range from 1995 to 2050 with 1-year steps
time_extrapolated = np.arange(1995, 2051, 1)
time_extrapolated2 = np.arange(2020, 2051, 1)
print(len(time_extrapolated2))

# Interpolate each row in shares and ratios
def interpolate_dataframe(df, time_columns, new_time_range):
    """
    Interpolates the rows of a dataframe over a new time range.

    :param df: Original DataFrame with columns as time points
    :param time_columns: List of time points in the original DataFrame
    :param new_time_range: New time range for interpolation
    :return: DataFrame interpolated over the new time range
    """
    interpolated_data = {}
    for row in df.index:
        interpolation_func = interp1d(time_columns, df.loc[row], kind='linear', fill_value="extrapolate")
        interpolated_data[row] = interpolation_func(new_time_range)
    return pd.DataFrame(interpolated_data, index=new_time_range)

# Interpolate shares and ratios
shares_interpolated_ls = interpolate_dataframe(shares_ls, years, time_extrapolated)
shares_interpolated_curt = interpolate_dataframe(shares_curt, years, time_extrapolated)

pricesinterpolated = interpolate_dataframe(prices, years, time_extrapolated)

for row in shares_interpolated_ls.columns:
    shares_interpolated_ls[row] = shares_interpolated_ls[row].clip(lower=0) # Set minimum total investment to 0. For a sake of correctness.
    
for row in shares_interpolated_curt.columns:
    shares_interpolated_curt[row] = shares_interpolated_curt[row].clip(lower=0) # Set minimum total investment to 0. For a sake of correctness.

# # Plot to visualize the interpolation for Shares
# plt.figure(figsize=(12, 6))
# for row in shares_interpolated.columns:
#     if row != "Total [EUR]":
#         plt.plot(time_extrapolated, shares_interpolated[row], label=row)
# plt.xlabel("Year")
# plt.ylabel("Shares")
# plt.title("Interpolated Shares from 1995 to 2050")
# plt.legend()
# plt.grid(True)
# plt.show()

# Plot to visualize the interpolation for Ratios
# plt.figure(figsize=(12, 6))
# for row in pricesinterpolated.columns:
#     plt.plot(time_extrapolated2, pricesinterpolated[row], label=row)
# plt.xlabel("Year")
# plt.ylabel("Annualized Prices (EUR/W)")
# plt.title("Interpolated Prices from 2020 to 2050")
# plt.legend()
# plt.grid(True)
# plt.show()

# Save interpolated dataframes to CSV
# shares_interpolated_ls.to_csv(r"C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\pymedeas2_models\models\europe\modules_pymedeas_eu\surr_model\pypsa\capa and invest\interpolation\outputs\interp_tech_shares_ls.csv", index_label="Year")
# shares_interpolated_curt.to_csv(r"C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\pymedeas2_models\models\europe\modules_pymedeas_eu\surr_model\pypsa\capa and invest\interpolation\outputs\interp_tech_shares_curt.csv", index_label="Year")
# ratios_interpolated.to_csv(r"C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\pymedeas2_models\models\europe\modules_pymedeas_eu\surr_model\pypsa\capa and invest\interpolation\outputs\interp_ratios_EUR_MW.csv", index_label="Year")

pricesinterpolated.to_csv("interp_prices_1995USD_W.csv", index_label="Year")