"""
Conversion file from interp_ratios_EUR_MW.csv to interp_ratios_USD_MW.csv
Wrote by Noe Diffels
November 2024

Two phenomena could be taken into account: 
    1. Exchange trade rate EUR-USD
    2. Domestic inflation (through CPI indicator)

[References] 
Both phenoma are computed for each year from 1995 to 2050. To do so,

    1. Historical Data is taken:

    (Exch Rate) European Central Bank Website. (Years 1999-2024) https://data.ecb.europa.eu/data/datasets/EXR/EXR.D.USD.EUR.SP00.A (Accessed on 19th November 2024)
    (CPI) Our World in data Website (Years 1995-2022) https://ourworldindata.org/grapher/consumer-price-index?tab=table (assessed on 19th November 2024)

    2. Prevision metrics
    
    (Exch Rate) Coin Codex Website (2025 and 2030) https://coincodex.com/forex/usd-eur/forecast/ (Accessed on 19th November 2024)

    3. Cubic Spline Interpolation

    Both use cubic spline interpolation from scipy.interpolate (interp1d, kind='cubic') in order to assess future or past unkown values.

[Assumptions]
It is important to note that the conversion EUR-USD does not really make any sense before 1999 since this year is when EUR was introduce on the market.
However in this work we consider exchange rate values constants from 1995 until the first known EUR value in 1999, for a sake of simplicity. 

"""
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d


# Files paths: 
# xml_file = r"C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\pymedeas2_models\models\europe\modules_pymedeas_eu\surr_model\pypsa\capa and invest\usd_conversion\inputs\usd.xml"
# cpi_file = r"C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\pymedeas2_models\models\europe\modules_pymedeas_eu\surr_model\pypsa\capa and invest\usd_conversion\inputs\consumer-price-index.csv"

EUR_data_path = r"C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\pymedeas2_models\models\europe\modules_pymedeas_eu\surr_model\pypsa\capa and invest\data_extract\outputs\ratios_EUR_MW.csv"
out_path = r"C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\pymedeas2_models\models\europe\modules_pymedeas_eu\surr_model\pypsa\capa and invest\usd_conversion\output"


EUR_2020 = pd.read_csv(EUR_data_path, index_col='RES_type')
print(EUR_2020)

# Convert 2020-EUR to 2020-USD. Source: https://data.ecb.europa.eu/data/datasets/EXR/EXR.D.USD.EUR.SP00.A (Accessed on 29 December 2024)
USD_2020 = EUR_2020.apply(lambda row: row * 1.1193, axis=1)
print(USD_2020)

# COnvert 2020-USD to 1995-USD. Source: https://www.measuringworth.com/datasets/usgdp/result.php (Accessed on 29 December 2024)
USD_1995 = USD_2020.apply(lambda row: row * (66.93/105.36), axis=1)
print(USD_1995)
USD_1995_W = USD_1995/1e6
USD_1995_W.to_csv("prices_1995USD_W.csv")




# def xml_extract(): 
#     # Load the XML file
#     tree = ET.parse(xml_file)
#     root = tree.getroot()

#     # Define the namespace to parse the XML
#     namespace = {'ns': 'http://www.ecb.europa.eu/vocabulary/stats/exr/1'}

#     # Extract daily exchange rate data
#     daily_data = []
#     for obs in root.findall(".//ns:Obs", namespace):
#         time_period = obs.attrib.get("TIME_PERIOD")
#         obs_value = obs.attrib.get("OBS_VALUE")
#         if time_period and obs_value:
#             daily_data.append({
#                 "Date": time_period,
#                 "Rate": float(obs_value)
#             })

#     # Convert to DataFrame
#     df_daily = pd.DataFrame(daily_data)

#     # Convert 'Date' to datetime and extract the year
#     df_daily['Date'] = pd.to_datetime(df_daily['Date'])
#     df_daily['Year'] = df_daily['Date'].dt.year

#     # Calculate yearly average exchange rates
#     yearly_rates = df_daily.groupby('Year')['Rate'].mean()

#     # Display the yearly rates
#     # print("Yearly Average Exchange Rates (USD/EUR):")
#     # print(yearly_rates)
#     return yearly_rates

# def extrapolation(known_years, known_values, all_years, plot=True, var=""):
#     """
#     Cubic Spline Extrapolation
#     """
#     # Fit a linear regression for trend extrapolation
#     coeffs = np.polyfit(known_years, known_values, deg=1)  # Linear fit
#     trend_func = np.poly1d(coeffs)

#     # Interpolate known data using cubic splines for a smooth curve
#     spline_interp = interp1d(known_years, known_values, kind='cubic', fill_value='extrapolate')

#     # Combine spline interpolation (1995–2030) with trend extrapolation (2030+)
#     combined_values = []
#     for year in all_years:
#         if year < min(known_years):
#             combined_values.append(known_values[0])
#         elif year >= min(known_years) and year <= max(known_years):  # Use spline interpolation for known range
#             combined_values.append(spline_interp(year).item())
#         else:  # Use trend line for extrapolation beyond known data
#             combined_values.append(trend_func(year))

#     # Create a new dictionary with the full range
#     full_data = dict(zip(all_years, combined_values))

#     if plot:
#         # Plot for visualization
#         plt.figure(figsize=(10, 6))
#         plt.plot(all_years[4:36], combined_values[4:36], color='tab:orange', label='Interpolated Data')  # Fitted curve
#         plt.plot(all_years[:5], combined_values[:5], '--' , color='tab:orange', label='Extrapolated Data')  # Fitted curve
#         plt.plot(all_years[35:], combined_values[35:], '--' , color='tab:orange')  # Fitted curve
#         plt.scatter(known_years, known_values, color='tab:blue', marker='o', label='Known Data (ECB)')  # Known points
#         plt.scatter([2025, 2030], [1.135914, 1.224872], color="tab:green", marker='o', label='Prevision Data (CC)')
#         plt.xlabel('Year [-]', fontsize=14)
#         plt.ylabel(var, fontsize=14)
#         plt.legend()
#         plt.grid(True)
#         plt.savefig("exch_rates.pdf")
#         plt.show()

#     return full_data

# """
# Exchange rates USD/EUR
# """
# # Historical data from European Central Bank Website. (1999-2024)
# # https://data.ecb.europa.eu/data/datasets/EXR/EXR.D.USD.EUR.SP00.A (Accessed on 19th November 2024)

# exchange_rates = xml_extract()

# # Prediction (2025, 2030) from https://coincodex.com/forex/usd-eur/forecast/ (Accessed on 19th November 2024)
# exchange_rates[2025] = 1.135914
# exchange_rates[2030] = 1.224872

# # Extract years and values from the dataframe
# known_years = np.array(exchange_rates.index)
# known_values = np.array(exchange_rates.values)

# # Create a range of years from 1995 to 2050
# all_years = np.arange(1995, 2051)

# exchange_rates = extrapolation(known_years, known_values, all_years, plot=True, var="Exchange Rates (USD/EUR)")

# """
# Inflation index: Consumer Prixe Index (CPI)
# """
# # Historical data from https://ourworldindata.org/grapher/consumer-price-index?tab=table (assessed on 19th November 2024)

# cpi = pd.read_csv(cpi_file, index_col='Year')
# cpi = cpi['Consumer price index (2010 = 100)']
# cpi.name = 'CPI'
# cpi = cpi.loc[cpi.index.isin(all_years)]

# # Extract years and values from the dataframe
# known_years = np.array(cpi.index)
# known_values = np.array(cpi.values)

# # cpi = extrapolation(known_years, known_values, all_years, plot=True, var="CPI [$]")

# print(exchange_rates)
# # print(cpi)

# """
# Modification of the data: EUR->1995-USD
# """
# EUR_data = pd.read_csv(EUR_data_path, index_col='Year')
# print(EUR_data)
# # Convert EUR to USD for each year
# USD_data = EUR_data.apply(lambda row: row * exchange_rates[row.name], axis=1)

# # Adjust to 1995 USD using CPI
# base_cpi = cpi[1995]
# #USD_data = USD_data.apply(lambda row: row * (cpi[row.name]/base_cpi), axis=1) # All pypsa costs are annualized. More information such as annuity factor available here: https://pypsa-eur.readthedocs.io/en/latest/costs.html.

# print(USD_data)
# USD_data.to_csv(out_path+"\interp_ratios_USD1995_MW.csv", index_label="Year")
# print(exchange_rates)
# df_exch_rates = pd.DataFrame(list(exchange_rates.items()), columns=['Year', 'Value'])
# df_exch_rates.set_index('Year', inplace=True)
# df_exch_rates.to_csv(out_path+"\exchange_rates.csv")

