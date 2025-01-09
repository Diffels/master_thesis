import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
from scipy.interpolate import PchipInterpolator
import os 
current_path = os.getcwd()


path_rNTC = r'C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\pymedeas2_models\models\europe\modules_pymedeas_eu\surr_model\pypsa\rNTC\data_extract\extract_rNTC.csv'
path_invest = r"C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\pymedeas2_models\models\europe\modules_pymedeas_eu\surr_model\pypsa\capa and invest\data_extract\inputs\investments.csv" 

# Given data
time = np.array([2020, 2030, 2040, 2050])
df = pd.read_csv(path_rNTC, index_col='Years')
rNTC = df['rNTC [-]']
peak_loads = df['sum_peak_loads [MW]']/1e6 # To make in TW


dfinvest = pd.read_csv(
    r"C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\pymedeas2_models\models\europe\modules_pymedeas_eu\surr_model\pypsa\capa and invest\data_extract\inputs\investments.csv", 
    index_col=1)

# Define the years and extract rows for AC and DC
years = ["2020", "2030", "2040", "2050"]
AC = dfinvest.loc['AC', years]
DC = dfinvest.loc['DC', years]
DISTRIB = dfinvest.loc['electricity distribution grid', years]

# Create a new DataFrame with AC and DC data for each year
df2 = pd.DataFrame({
    'Investments [€]': AC.values+DC.values+DISTRIB.values}, index=years)

invest = np.array(df2['Investments [€]'])

print(invest)
# Translation 2020€->1995-USD

# Convert 2020-EUR to 2020-USD. Source: https://data.ecb.europa.eu/data/datasets/EXR/EXR.D.USD.EUR.SP00.A (Accessed on 29 December 2024)
USD_2020 = invest * 1.1193
print(USD_2020)

# Convert 2020-USD to 1995-USD. Source: https://www.measuringworth.com/datasets/usgdp/result.php (Accessed on 29 December 2024)
USD_1995 = USD_2020 * (66.93/105.36)

invest = USD_1995
print(invest)

""" rNTC interpolation """
# Create interpolation function
rNTC[1995] = 0.01
rNTC = rNTC.sort_index(ascending=True)
new_time = np.insert(time, 0, 1995)
# interpolation_func_rNTC = interp1d(new_time, rNTC, kind='cubic', fill_value="extrapolate")
interpolation_func_rNTC = PchipInterpolator(new_time, rNTC, extrapolate=True)

# Generate new time range from 1995 to 2050 with 1-year steps
time_extrapolated = np.arange(1995, 2051, 1)
rNTC_extrapolated = interpolation_func_rNTC(time_extrapolated)

# Replace negative values with zero
rNTC_extrapolated = np.maximum(rNTC_extrapolated, 0.01)

print(rNTC_extrapolated)
# Plot to visualize the extrapolated data
plt.figure(figsize=(10, 6))
plt.plot(time, rNTC[1:], 'o', label="PyPSA Data Points", color="tab:blue")
plt.plot(time_extrapolated[25:], rNTC_extrapolated[25:], '-', label="Interpolated Data", color="darkorange")

plt.plot(1995, rNTC_extrapolated[0], 'o', label="Assumption", color="darkorange")
plt.plot(time_extrapolated[:26], rNTC_extrapolated[:26], '--', label="Extrapolated Data", color="darkorange")
plt.xlabel("Year", fontsize=14)
plt.ylabel("rNTC [-]", fontsize=14)
plt.legend()
plt.grid(True)
file_path = os.path.join(current_path, "Figures", "interp_rNTC.pdf")
plt.savefig(file_path)
plt.show()


""" Investments interpolation """
# Create interpolation function
interpolation_func_invest = interp1d(time, invest, kind='linear', fill_value="extrapolate")

invest_extrapolated = interpolation_func_invest(time_extrapolated)

# Replace negative values with zero
invest_extrapolated = np.maximum(invest_extrapolated, 0)

# Plot to visualize the extrapolated data
plt.figure(figsize=(10, 6))
plt.plot(time, invest, 'o', label="Original Data Points", color="blue")
plt.plot(time_extrapolated, invest_extrapolated, '-', label="Extrapolated Data", color="orange")
plt.xlabel("Year")
plt.ylabel("Investment in USD")
plt.title("Extrapolatedinvestments from 1995 to 2050 (No Negative Values, from PyPSA-EUR)")
plt.legend()
plt.grid(True)
plt.show()

""" Peak loads interpolation """
# Create interpolation function
interpolation_func_peak_load = interp1d(time, peak_loads, kind='cubic', fill_value="extrapolate")

peak_loads_extrapolated = interpolation_func_peak_load(time_extrapolated)

# Replace negative values with zero
peak_loads_extrapolated = np.maximum(peak_loads_extrapolated, 0)

# Plot to visualize the extrapolated data
plt.figure(figsize=(10, 6))
plt.plot(time, peak_loads, 'o', label="Original Data Points", color="blue")
plt.plot(time_extrapolated, peak_loads_extrapolated, '-', label="Extrapolated Data", color="orange")
plt.xlabel("Year")
plt.ylabel("Peak Loads TW")
plt.title("Extrapolated peak loads from 1995 to 2050 (No Negative Values, from PyPSA-EUR)")
plt.legend()
plt.grid(True)
plt.show()

# Save to CSV
df = pd.DataFrame({'Year': time_extrapolated, 'rNTC': rNTC_extrapolated})
df["sum_peak_loads [TW]"] = peak_loads_extrapolated
df["Investments [1995-USD]"] = invest_extrapolated

print(df)
df.to_csv(r"C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\pymedeas2_models\models\europe\modules_pymedeas_eu\surr_model\pypsa\rNTC\interp_rNTC.csv", index=False)
