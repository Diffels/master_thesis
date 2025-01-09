"""
File to display the plots used in Noe Diffels' master thesis report.

Wrote by Noe Diffels
November 2024
"""

# Import necessary libraries
import netCDF4 as nc
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import math
import seaborn as sns
current_path = os.getcwd()

bounds = [(0.4, 1.3), (0.25, 0.9), (0, 3), (0, 0.55), (0, 0.35), (0, 0.75), (0, 1), (0, 1)] # Upper bound for storage limited to 60% instead 300%, cfr. report.


# Function to plot with bounds
def plot_with_bounds(years, data, label, color, bounds, legend=[], alpha=1, flag=True, style='-'):
    lower_bound, upper_bound = bounds
    out_of_bounds = (data < lower_bound) | (data >= upper_bound)

    if not flag and out_of_bounds.any():
        out_of_ds_line, = plt.plot(years[out_of_bounds], data[out_of_bounds], 'x', color="red", label='Out of DS')
        legend.insert(0, out_of_ds_line)  # Ensure "Out of DS" is always the first in the legend
        flag = True  # Update flag
    else:
        plt.plot(years[out_of_bounds], data[out_of_bounds], 'x', color="red")

    line, = plt.plot(years, data, label=label, color=color, alpha=alpha, linestyle=style)
    legend.append(line)

    return flag

def plot_sm(dataset, features=True, targets=True, ylim=False, save=True, flag=True):
    legend = []

    # Extract variables
    share_flex = dataset.variables['share_flex'][:]
    cap_ratio = dataset.variables['cap_ratio'][:]
    share_pv = dataset.variables['share_pv'][:]
    share_wind = dataset.variables['share_wind'][:]
    share_sto = dataset.variables['share_sto'][:]
    rNTC = dataset.variables['rNTC'][:]

    curtailment = dataset.variables['curtailment'][:]
    load_shed = dataset.variables['load_shedding'][:]

    years = np.arange(1995, 2051)

    plt.figure(figsize=(10, 6))

    # Plot features
    if features:
        flag = plot_with_bounds(years, cap_ratio, 'cap_ratio', 'tab:red', bounds[0], legend, flag=flag)
        flag = plot_with_bounds(years, share_flex, 'share_flex', 'tab:blue', bounds[1], legend, flag=flag)
        flag = plot_with_bounds(years, share_sto, 'share_sto', 'tab:purple', bounds[2], legend, flag=flag)
        flag = plot_with_bounds(years, share_wind, 'share_wind', 'tab:orange', bounds[3], legend, flag=flag)
        flag = plot_with_bounds(years, share_pv, 'share_pv', 'tab:green', bounds[4], legend, flag=flag)
        flag = plot_with_bounds(years, rNTC, 'rNTC', 'teal', bounds[5], legend, flag=flag)

    # Plot targets
    if targets:
        flag = plot_with_bounds(years, curtailment, 'curtailment', 'gold', bounds[6], legend, flag=flag)
        flag = plot_with_bounds(years, load_shed, 'load_shed', 'tab:pink', bounds[7], legend, flag=flag)

    plt.legend(handles=legend, loc='upper left')
    plt.xlabel('Years [-]', fontsize=14)
    plt.ylabel('Dmnl [-]', fontsize=14)
    if ylim:
        plt.ylim([0, 0.1])
    plt.tick_params(axis='both', which='major', labelsize=12)
    plt.grid(True)
    if save:
        if features and targets:
            file_path = os.path.join(current_path, "Figures", "features_targets.svg")
        elif features:
            file_path = os.path.join(current_path, "Figures", "features.pdf")
        elif targets:
            file_path = os.path.join(current_path, "Figures", "targets.pdf")
        else:
            raise ValueError('Neither Targets or Values was selected.')
        plt.savefig(file_path)
    plt.show()

def plot_investments_2ds(ds1, ds2):

    # Start from 96' to avoid the consideration of previously installed capacity.
    res_invest1 = np.cumsum(ds1.variables['tot_investments_res'][1:])
    res_invest2 = np.cumsum(ds2.variables['tot_investments_res'][1:])
    sto_invest1 = np.cumsum(ds1.variables['tot_investments_storage'][1:])
    sto_invest2 = np.cumsum(ds2.variables['tot_investments_storage'][1:])
    ntc_invest1 = np.cumsum(ds1.variables['tot_investments_ntc'][1:])
    ntc_invest2 = np.cumsum(ds2.variables['tot_investments_ntc'][1:])

    years = np.arange(1996, 2051)

    # plt.figure(figsize=(10, 6))
    # plot_with_bounds(years, tot_invest1, 'Total Investments without PID', 'orange', (-math.inf, math.inf), alpha=0.3)
    # plot_with_bounds(years, tot_invest2, 'Total Investments with PID', 'tab:orange', (-math.inf, math.inf))
    # plt.legend()
    # plt.xlabel('Years [-]', fontsize=14)
    # plt.ylabel('Investments [$]', fontsize=14)
    # plt.tick_params(axis='both', which='major', labelsize=12)  # Change 12 to your desired size
    # plt.grid(True)
    # file_path = os.path.join(current_path, "Figures/investments", "invest_comparison.pdf")
    # plt.savefig(file_path)
    # plt.show()

    # plt.figure(figsize=(10, 6))
    # year2= np.arange(1995, 2051)
    # rNTC1 = ds1.variables['rNTC'][:]
    # rNTC2 = ds2.variables['rNTC'][:]
    # plt.plot(year2, rNTC1, label='rNTC target without feedback', color='teal',  alpha=0.3)
    # plt.plot(year2, rNTC2, label='rNTC target with feedback', color='teal')
    # plt.legend()
    # plt.xlabel('Years [-]', fontsize=14)
    # plt.ylabel('Dmnl [-]', fontsize=14)
    # plt.tick_params(axis='both', which='major', labelsize=12)  # Change 12 to your desired size
    # plt.grid(True)
    # file_path = os.path.join(current_path, "Figures/investments", "rNTC_comparison.pdf")
    # plt.savefig(file_path)
    # plt.show()

    plt.close() # Close plot

    plt.figure(figsize=(10, 6))
    plot_with_bounds(years, res_invest1, 'RES Investments without feedback', 'g', (-math.inf, math.inf), alpha=0.3)
    plot_with_bounds(years, res_invest2, 'RES Investments with feedback', 'g', (-math.inf, math.inf))
    plt.legend()
    plt.xlabel('Years [-]', fontsize=14)
    plt.ylabel('Investments in RES deployment [T$]', fontsize=14)
    plt.tick_params(axis='both', which='major', labelsize=12)  # Change 12 to your desired size
    plt.grid(True)
    file_path = os.path.join(current_path, "Figures/investments", "res_invest_comparison.pdf")
    plt.savefig(file_path)
    plt.show()

    plt.close() # Close plot
    
    plt.figure(figsize=(10, 6))
    plot_with_bounds(years, sto_invest1, 'Storage Investments without feedback', 'tab:purple', (-math.inf, math.inf), alpha=0.3)
    plot_with_bounds(years, sto_invest2, 'Storage Investments with feedback', 'tab:purple', (-math.inf, math.inf))
    plot_with_bounds(years, ntc_invest1, 'NTC Investments without feedback', 'teal', (-math.inf, math.inf), alpha=0.3)
    plot_with_bounds(years, ntc_invest2, 'NTC Investments with feedback', 'teal', (-math.inf, math.inf))
    plt.legend()
    plt.xlabel('Years [-]', fontsize=14)
    plt.ylabel('Investments [T$]', fontsize=14)
    plt.tick_params(axis='both', which='major', labelsize=12)  # Change 12 to your desired size
    plt.grid(True)
    file_path = os.path.join(current_path, "Figures/investments", "sto_ntc_invest_comparison.pdf")
    plt.savefig(file_path)
    plt.show()

    plt.close() # Close plot

    plt.figure(figsize=(10, 6))
    plot_with_bounds(years, res_invest1, 'RES Investments without feedback', 'g', (-math.inf, math.inf), alpha=0.3)
    plot_with_bounds(years, res_invest2, 'RES Investments with feedback', 'g', (-math.inf, math.inf))
    plot_with_bounds(years, sto_invest1, 'Storage Investments without feedback', 'tab:purple', (-math.inf, math.inf), alpha=0.3)
    plot_with_bounds(years, sto_invest2, 'Storage Investments with feedback', 'tab:purple', (-math.inf, math.inf))
    plot_with_bounds(years, ntc_invest1, 'NTC Investments without feedback', 'teal', (-math.inf, math.inf), alpha=0.3)
    plot_with_bounds(years, ntc_invest2, 'NTC Investments with feedback', 'teal', (-math.inf, math.inf))
    plt.legend()
    plt.xlabel('Years [-]', fontsize=14)
    plt.ylabel('Investments [T$]', fontsize=14)
    plt.tick_params(axis='both', which='major', labelsize=12)  # Change 12 to your desired size
    plt.grid(True)
    file_path = os.path.join(current_path, "Figures/investments", "all_invest_comparison.pdf")
    plt.savefig(file_path)
    plt.show()

def plot_MLP_RF(dataset, ylim=False, save=True, flag=True):
    legend = []

    mlp_curtailment = dataset.variables['curtailment'][:]
    mlp_load_shed = dataset.variables['load_shedding'][:]

    rf_curtailment = dataset.variables['RF_curtailment'][:]
    rf_load_shed = dataset.variables['RF_load_shedding'][:]

    years = np.arange(1995, 2051)

    plt.figure(figsize=(10, 6))

    flag = plot_with_bounds(years, mlp_curtailment, 'Curtailment MLP', 'gold', bounds[6], legend, flag=flag)
    flag = plot_with_bounds(years, mlp_load_shed, 'Load Shedding - MLP', 'tab:pink', bounds[7], legend, flag=flag)

    flag = plot_with_bounds(years, rf_curtailment, 'Curtailment - RF', 'gold', bounds[6], legend, flag=flag, style=':')
    flag = plot_with_bounds(years, rf_load_shed, 'Load Shedding - RF', 'tab:pink', bounds[7], legend, flag=flag, style=':')

    plt.legend(handles=legend, loc='upper left')
    plt.xlabel('Years [-]', fontsize=14)
    plt.ylabel('Dmnl [-]', fontsize=14)
    if ylim:
        plt.ylim([0, 0.1])
    plt.tick_params(axis='both', which='major', labelsize=12)
    plt.grid(True)
    if save:
        file_path = os.path.join(current_path, "Figures", "MLP_RF.pdf")
        plt.savefig(file_path)
    plt.show()

def plot_2_sm(ds1, ds2):
    """
    ds1: without PID
    ds2: with PID
    """
    plt.figure(figsize=(10, 6))
    
    curtailment_1 = ds1.variables['curtailment'][:]
    load_shed_1 = ds1.variables['load_shedding'][:]
    grid_invest1 = ds1.variables['TOT_investments'][:]

    curtailment_2 = ds2.variables['curtailment'][:]
    load_shed_2 = ds2.variables['load_shedding'][:]
    grid_invest2 = ds2.variables['TOT_investments'][:]

    

    years = np.arange(1995, 2051)

    plot_with_bounds(years, curtailment_1, 'curtailment without feedback', 'gold', bounds[6], alpha=1, style='-')   
    plot_with_bounds(years, curtailment_2, 'curtailment with feedback', 'goldenrod', bounds[6])
    plt.legend()
    plt.xlabel('Years [-]', fontsize=14)
    plt.ylabel('Dmnl [-]', fontsize=14)
    plt.tick_params(axis='both', which='major', labelsize=12)  # Change 12 to your desired size
    plt.grid(True)
    file_path = os.path.join(current_path, "Figures", "curt_comparison.pdf")
    plt.savefig(file_path)
    plt.show()

    plt.close() # Close plot
    plt.figure(figsize=(10, 6))

    plot_with_bounds(years, load_shed_1, 'load_shed without feedback', 'tab:pink', bounds[7], alpha=1, style='-')
    plot_with_bounds(years, load_shed_2, 'load_shed with feedback', 'darkorchid', bounds[7])
    plt.legend()
    plt.xlabel('Years [-]', fontsize=14)
    plt.ylabel('Dmnl [-]', fontsize=14)
    plt.tick_params(axis='both', which='major', labelsize=12)  # Change 12 to your desired size
    plt.grid(True)
    file_path = os.path.join(current_path, "Figures", "ls_comparison.pdf")
    plt.savefig(file_path)
    plt.show()

def plot_investments_1ds(ds):

    # tot_invest = ds.variables['TOT_investments'][:]
    res_invest = ds.variables['tot_investments_res'][25:]
    grid_invest = ds.variables['tot_investments_ntc'][25:]
    storage_invest = ds.variables['tot_investments_storage'][25:]

    res_invest = np.cumsum(res_invest)
    grid_invest = np.cumsum(grid_invest)
    storage_invest = np.cumsum(storage_invest)

    years = np.arange(2020, 2051)

    plt.figure(figsize=(10, 6))

    plt.plot(years, res_invest, label='Cumulated Investments in RES deployment [T$]', color='tab:green')
    plt.xlabel('Years [-]', fontsize=14)
    plt.ylabel('Cumulated Investments in RES deployment [T$]', fontsize=14)
    plt.tick_params(axis='both', which='major', labelsize=12)  # Change 12 to your desired size
    plt.grid(True)
    file_path = os.path.join(current_path, "Figures", "investments", "res_invest.pdf")
    plt.savefig(file_path)
    plt.show()

    plt.close() # Close plot
    # plt.figure(figsize=(10, 6))

    # plt.plot(years, grid_invest, label='Transfer Capacity', color='teal')
    # plt.xlabel('Years [-]', fontsize=14)
    # plt.ylabel('Cum. Investments in Grid development [T$]', fontsize=14)
    # plt.tick_params(axis='both', which='major', labelsize=12)  # Change 12 to your desired size
    # plt.grid(True)
    # file_path = os.path.join(current_path, "Figures", "investments", "grid_invest.pdf")
    # plt.savefig(file_path)
    # plt.show()

    # plt.close() # Close plot
    plt.figure(figsize=(10, 6))

    plt.plot(years, storage_invest, label='Storage Capacity', color='tab:purple')
    plt.plot(years, grid_invest, label='Transfer Capacity', color='teal')
    plt.legend()
    plt.xlabel('Years [-]', fontsize=14)
    plt.ylabel('Cumulated Investments in Grid & Storage capacity [T$]', fontsize=14)
    plt.tick_params(axis='both', which='major', labelsize=12)  # Change 12 to your desired size
    plt.grid(True)
    file_path = os.path.join(current_path, "Figures", "investments", "sto_grid_invest.pdf")
    # plt.legend()
    plt.savefig(file_path)
    plt.show()

def plot_investments_combined(list_ds, name_scen, save=False):

    if len(list_ds) != len(name_scen):
        raise ValueError(f'List containing the datasets are not the same as given names. ({len(list_ds)} ds vs {len(name_scen)} names)')
    # Data extraction
    res_invests=[]
    storage_invests=[]
    for ds in list_ds:
        # tot_invest = ds.variables['TOT_investments'][:]
        res_invests.append(np.cumsum(ds.variables['tot_investments_res'][:]))
        # grid_invest = ds.variables['tot_investments_ntc'][:]
        storage_invests.append(np.cumsum(ds.variables['tot_investments_storage'][:]))

    years = np.arange(1995, 2051)
    styles = ('-', '--', '-.')


    # RES
    plt.figure(figsize=(12, 8))
    for i in range(len(list_ds)):
        plt.plot(years, res_invests[i], label=name_scen[i], linestyle=styles[i], color='tab:green')
    plt.grid()
    # Labels, legend, and title
    plt.xlabel('Years [-]', fontsize=14)
    plt.ylabel('Cumulated Investments [T$]', fontsize=14)
    plt.legend(fontsize=12, loc='upper left')
    plt.tick_params(axis='both', which='major', labelsize=12)
    if save:
        # Save and show
        file_path = os.path.join(current_path, "Figures", "case_study", "res_investments.pdf")
        plt.savefig(file_path)
    plt.show()

    # Storage
    plt.figure(figsize=(12, 8))
    for i in range(len(list_ds)):
        plt.plot(years, storage_invests[i], label=name_scen[i], linestyle=styles[i], color='tab:purple')
    plt.grid()
    # Labels, legend, and title
    plt.xlabel('Years [-]', fontsize=14)
    plt.ylabel('Cumulated Investments [T$]', fontsize=14)
    plt.legend(fontsize=12, loc='upper left')
    plt.tick_params(axis='both', which='major', labelsize=12)
    if save:
        # Save and show
        file_path = os.path.join(current_path, "Figures", "case_study", "storage_investments.pdf")
        plt.savefig(file_path)
    plt.show()   

def plot_variable(name_var: str, y_axis_label: str, color: str, save: bool):

    var = dataset.variables[name_var][:]
    years = np.arange(1995, 2051)

    plt.figure(figsize=(10, 6))
    plt.plot(years, var, label=name_var, color=color) # , marker='o', markerfacecolor='lightblue'
    plt.xlabel('Years [-]', fontsize=14)
    plt.ylabel(y_axis_label, fontsize=14)
    plt.tick_params(axis='both', which='major', labelsize=12)  # Change 12 to your desired size
    plt.grid(True)
    plt.legend()
    if save:
        file_path = os.path.join(current_path, "Figures", f"{name_var}.svg")
        plt.savefig(file_path)
    plt.show()

def plot_variable_nuc(ds1, ds2, ds3, hist_data_final_year, name_var: str, y_axis_label: str, color: str, save: bool):

    var = ds1.variables[name_var][:] # Nuclear
    var2 = ds2.variables[name_var][:] # No nuclear
    var3 = ds3.variables[name_var][:] # Decomissing

    years = np.arange(1995, 2051)

    hist_data = var[:(hist_data_final_year-1995)]
    plt.figure(figsize=(10, 6))
    plt.plot(years, var, color=color[0], label="Nuclear policy")
    plt.plot(years, var3, color=color[2], label="Decommissioning policy")
    plt.plot(years, var2, color=color[1], label="Phase-out policy")
    plt.plot(np.arange(1995, hist_data_final_year), hist_data, color='grey', label="Historical Data")
    plt.xlabel('Years [-]', fontsize=14)
    plt.ylabel(y_axis_label, fontsize=14)
    plt.tick_params(axis='both', which='major', labelsize=12)  # Change 12 to your desired size
    plt.grid(True)
    plt.legend()
    if save:
        file_path = os.path.join(current_path, "Figures\\Nuclear", f"{name_var}.pdf")
        plt.savefig(file_path)
    plt.show()

def plot_variable_bau(ds1, ds2, hist_data_final_year: int, name_var: str, y_axis_label: str, color: str, save: bool):

    var = ds1.variables[name_var][:] # NZP
    var2 = ds2.variables[name_var][:] # Business As Usual

    years = np.arange(1995, 2051)
    hist_data = var[:(hist_data_final_year-1995)]
    plt.figure(figsize=(10, 6))
    plt.plot(years, var, color=color[0], label="RES policy")
    plt.plot(years, var2, color=color[1], label="FF policy")
    plt.plot(np.arange(1995, hist_data_final_year), hist_data, color='grey', label="Before policy")
    plt.xlabel('Years [-]', fontsize=14)
    plt.ylabel(y_axis_label, fontsize=14)
    plt.tick_params(axis='both', which='major', labelsize=12)  # Change 12 to your desired size
    plt.grid(True)
    plt.legend()
    if save:
        file_path = os.path.join(current_path, "Figures\\BAU", f"{name_var}.pdf")
        plt.savefig(file_path)
    plt.show()

def plot_baseline_outcome(save=False):
    ds_path = r'C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\pymedeas2_models\models\world\results.nc'
    dataset = nc.Dataset(ds_path)

    population = dataset.variables['population'][:]/1e9
    gdp = dataset.variables['desired_gdppc'][:]
    res = dataset.variables['fe_tot_generation_all_res_elec_twh'][:]

    years = np.arange(1995, 2051)
    plt.figure(figsize=(10, 6))
    plt.plot(years, population, color='tab:blue')
    plt.xlabel('Years [-]', fontsize=20)
    plt.ylabel("Population [Billion pers.]", fontsize=20)
    plt.tick_params(axis='both', which='major', labelsize=15)  # Change 12 to your desired size
    plt.grid(True)
    if save:
        file_path = os.path.join(current_path, "Figures\\BAU", f"population.pdf")
        plt.savefig(file_path)
    plt.show()

    plt.figure(figsize=(10, 6))
    plt.plot(years, gdp, color='tab:blue')
    plt.xlabel('Years [-]', fontsize=20)
    plt.ylabel("Desired GDP per capita [$/pers.]", fontsize=20)
    plt.tick_params(axis='both', which='major', labelsize=15)  # Change 12 to your desired size
    plt.grid(True)
    if save:
        file_path = os.path.join(current_path, "Figures\\BAU", f"desired_gdppc.pdf")
        plt.savefig(file_path)
    plt.show()

    plt.figure(figsize=(10, 6))
    plt.plot(years, res, color='tab:blue')
    plt.xlabel('Years [-]', fontsize=20)
    plt.ylabel("FE Elec Generation from RES [TWh]", fontsize=20)
    plt.tick_params(axis='both', which='major', labelsize=15)  # Change 12 to your desired size
    plt.grid(True)
    if save:
        file_path = os.path.join(current_path, "Figures\\BAU", f"res_baseline.pdf")
        plt.savefig(file_path)
    plt.show()

def plot_group_subvar(ds, name_var: str, y_axis_label: str, sub_var: list, save: bool):
    var = ds.variables[name_var][:]
    # Each row : time step
    # Each column : sub-variable
    dfvar = pd.DataFrame(var, columns=sub_var)
    years = np.arange(1995, 2051)

    plt.figure(figsize=(10, 6))
    plt.plot(years, dfvar.values)
    plt.xlabel('Years [-]', fontsize=14)
    plt.ylabel(y_axis_label, fontsize=14)
    plt.tick_params(axis='both', which='major', labelsize=12)  # Change 12 to your desired size
    plt.grid(True)
    plt.legend(dfvar.columns)
    if save:
        file_path = os.path.join(current_path, "Figures", f"{name_var}.svg")
        plt.savefig(file_path)
    plt.show()

def plot_group_subvar_cp_curt(ds, name_var: str, y_axis_label: str, sub_var: list, save: bool):
    cp = ds.variables["real_cp_res_elec"][:]
    curt = ds.variables["curtailment_delayed"][:]
    
    # Each row : time step
    # Each column : sub-variable
    dfvar = pd.DataFrame(cp, columns=sub_var)
    years = np.arange(1995, 2051)

    # Create figure and axis objects
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Plot on the left y-axis (ax1)
    for col in dfvar.columns:
        if col in ("wind_onshore", "solar_PV"):
            ax1.plot(years, dfvar[col], label=col)
    
    ax1.set_xlabel('Years [-]', fontsize=14)
    ax1.set_ylabel(y_axis_label, fontsize=14)
    ax1.tick_params(axis='both', which='major', labelsize=12)
    ax1.grid(True)

    # Create a second y-axis (ax2) sharing the same x-axis
    ax2 = ax1.twinx()
    ax2.plot(years, curt, color='gold', label='Curtailment')
    ax2.set_ylabel('Curtailment [-]', fontsize=14)
    #ax2.set_ylim(0, 0.05)  # Set limits for the right y-axis

    # Add legends for both axes
    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left')

    # Save the figure if required
    if save:
        file_path = os.path.join("Figures", f"cp_curt.pdf")
        plt.savefig(file_path)

    plt.show()
    
def plot_ff_extraction(ds):
    extract = ds.variables["pes_fossil_fuel_extraction"][:]
    dfextract = pd.DataFrame(extract, columns=["liquids", "gases", "solids"])
    years = np.arange(1995, 2051)

    plt.figure(figsize=(10, 6))
    plt.plot(years, dfextract["liquids"], color='tab:red', linestyle="dotted", label="Oil")
    plt.plot(years, dfextract["gases"], color='tab:red', linestyle="dashed", label="Gas")
    plt.plot(years, dfextract["solids"], color='tab:red', linestyle="dashdot", label="Coal")
    plt.axvline(2020, color='tab:orange', alpha=0.5, label='Policy start')
    plt.xlabel('Years [-]', fontsize=14)
    plt.ylabel("Primary Energy Supply Fossil Fuels extraction [EJ]", fontsize=14)
    plt.tick_params(axis='both', which='major', labelsize=12)  # Change 12 to your desired size
    plt.grid(True)
    plt.legend(dfextract.columns)
    file_path = os.path.join(current_path, "Figures", "ff_extract.pdf")
    plt.savefig(file_path)
    plt.show()

def plot_wind_solar_assessment_investments(ds):
    extract = ds.variables["installed_capacity_res_elec"][:]
    dfvar = pd.DataFrame(extract, columns=["hydro","geot_elec","solid_bioE_elec","oceanic","wind_onshore","wind_offshore","solar_PV","CSP"])
    wind_on = dfvar["wind_onshore"][25:]
    wind_off = dfvar["wind_offshore"][25:]
    solar = dfvar["solar_PV"][25:]

    path = r"C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\pymedeas2_models\interp_prices_1995USD_W.csv"
    prices = pd.read_csv(path, index_col="Year")
    price_on = prices["Wind (Onshore)"][25:]
    price_off = prices["Wind (Offshore)"][25:]
    price_sol = prices["Solar"][25:]

    var_on = wind_on.values * price_on.values
    var_off = wind_off.values * price_off.values
    var_sol = solar.values * price_sol.values

    years = np.arange(2020, 2051)

    plt.figure(figsize=(10, 6))
    # plt.plot(years, var_on, label="Wind Onshore", color="tab:orange")
    # plt.plot(years, var_off, label="Wind Offshore", color="gold")
    plt.plot(years, var_on+var_off, label="Wind (Onshore & Offshore)", color="tab:orange")
    plt.plot(years, var_sol, label="Solar", color="tab:green")

    plt.xlabel('Years [-]', fontsize=14)
    plt.ylabel("Estimated Investments [T$]", fontsize=14)
    plt.tick_params(axis='both', which='major', labelsize=12)  # Change 12 to your desired size
    plt.grid(True)
    plt.legend()
    file_path = os.path.join(current_path, "Figures", "example_invest.pdf")
    plt.savefig(file_path)
    plt.show()

def plot_share_flex(): 
    years = np.arange(1995, 2051)
    m = 0.006625
    p = 0.251
    share_flex = m * (years - 1995) + p
    plt.figure(figsize=(10, 6))
    plt.plot(years, share_flex, label="share_flex", color="tab:blue")
    plt.xlabel('Years', fontsize=14)
    plt.ylabel("Dmnl [-]", fontsize=14)
    plt.tick_params(axis='both', which='major', labelsize=12)  # Change 12 to your desired size
    plt.grid(True)
    plt.legend()
    file_path = os.path.join(current_path, "Figures", "share_flex.pdf")
    plt.savefig(file_path)
    plt.show()

def plot_resmix(ds, save: bool):
    name_var='real_generation_res_elec_twh'
    # name_var='installed_capacity_res_elec'

    colors = ['tab:blue', 'tab:purple', 'tab:brown', 'teal', 'tab:orange', 'gold', 'tab:green', 'pink']
    sub_var = ["hydro","geot_elec","solid_bioE_elec","oceanic","wind_onshore","wind_offshore","solar_PV","CSP"]
    var = ds.variables[name_var][:]

    # Each row: time step
    # Each column: sub-variable
    dfvar = pd.DataFrame(var, columns=sub_var) 
    years = np.arange(1995, 2051)  # Adjusting the years based on the example plot
    # ls = ds.variables["load_shedding"][:]
    # demand_e_twh = ds.variables["fe_demand_elec_consum_twh"][:]
    
    
    # demand_e_twh = ds.variables["fe_demand_elec_consum"][:]
    demand_e_twh = ds.variables["total_fe_elec_demand_twh"][:]
    
    
    # ff = ds.variables[""][:]

    if name_var == 'real_generation_res_elec_twh' or name_var == 'potential_generation_res_elec_twh':
        y_axis_label='Electricity Generation or Demand [TWh]'

        biogas = ds.variables['fes_elec_from_biogas_twh'][:]
        dfvar['biogas'] = biogas
        colors.append('seagreen')
        sub_var.append('biogas')

        waste = ds.variables['fes_elec_from_waste'][:]
        dfvar['waste'] = waste
        colors.append('peru')
        sub_var.append('waste')

        # curtailed = ds.variables['energy_curtailed_twh'][:]
        # dfvar['curtailment'] = curtailed
        # colors.append('black')
        # sub_var.append('curtailment')

        # nuc = ds.variables['fe_nuclear_elec_generation_twh'][:]
        # ff = ds.variables['fe_elec_generation_from_fossil_fuels'][:]
        # dffossil = pd.DataFrame(ff, columns=['liquids', 'gases', 'solids'])
        # dfvar['nuclear'] = nuc
        # dfvar['FF-liquids'] = dffossil['liquids']
        # dfvar['FF-gases'] = dffossil['gases']
        # dfvar['FF-solids'] = dffossil['solids']
        # sub_var.append('Nuclear')
        # sub_var.append('FF-liquids')
        # sub_var.append('FF-gases')
        # sub_var.append('FF-solids')
        # colors.append('violet')
        # colors.append('darkkhaki')
        # colors.append('olive')
        # colors.append('grey')
        # print(dfvar)
        nre = ds.variables['fe_elec_generation_from_nre_twh'][:]
        dfvar['NRE'] = nre
        colors.append('darkkhaki')
        sub_var.append('NRE')

        # if 'curtailment' not in ds.variables:
        #     # dfvar['mismatch'] = dfvar.sum(axis=0) - demand_e_twh
        #     dfvar['mismatch'] = dfvar[["hydro","geot_elec","solid_bioE_elec","oceanic","wind_onshore","wind_offshore","solar_PV","CSP"]].sum(axis=1)
        #     colors.append('plum')
        #     sub_var.append('Mismatch')
        
    else:
        y_axis_label='Electricity Power Installed by source [TW]'

    plt.figure(figsize=(10, 6))
    if name_var == 'real_generation_res_elec_twh' or name_var == 'potential_generation_res_elec_twh':

        # newdf = pd.DataFrame([ds.variables['fe_tot_generation_all_res_elec_twh'][:], nre, waste], ["Res", "Nre", "Waste"])
        # print(newdf)
        # plt.stackplot(years, newdf, labels=sub_var, colors=colors)

        plt.stackplot(years, dfvar.T, labels=sub_var, colors=colors)  # Use stackplot for the area plot
        plt.plot(years, demand_e_twh, label="Elec Demand", color="grey")
    else:
        for i, col in enumerate(sub_var):
            plt.plot(years, dfvar[col], label=col, color=colors[i])
        plt.grid()

    plt.xlabel('Years [-]', fontsize=14)
    plt.ylabel(y_axis_label, fontsize=14)
    plt.tick_params(axis='both', which='major', labelsize=12)  # Adjust tick label size
    # if name_var == 'real_generation_res_elec_twh':
    plt.legend(bbox_to_anchor=(1, 1), ncol=1, fontsize=10)  # Position and size of legend
    plt.tight_layout()
    # else:
    #     plt.legend(loc='upper left', ncol=3, fontsize=10)  # Position and size of legend
    
    # if name_var == 'installed_capacity_res_elec':
    #     plt.ylim([0, 2])
    if save:
        if name_var == 'real_generation_res_elec_twh':
            if "curtailment" in ds.variables:
                file_type = 'new'
            else: 
                file_type = 'old'

            file_path = os.path.join(os.getcwd(), "Figures", "case_study", f"{file_type}_elecgen.pdf")
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            plt.savefig(file_path)
        else:
            file_path = os.path.join(os.getcwd(), "Figures", "case_study", f"{name_var}.pdf")
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            plt.savefig(file_path)
    plt.show()

def plot_resinstall(ds1, ds2, save=False):
    name_var = 'installed_capacity_res_elec'
    y_axis_label = 'RES Electricity Power Installed [TW]'
    sub_var = ["hydro", "geot_elec", "solid_bioE_elec", "oceanic", "wind_onshore", 
               "wind_offshore", "solar_PV", "CSP"]

    # Extract variables from datasets
    var1 = ds1.variables[name_var][:]
    var2 = ds2.variables[name_var][:]

    # Convert to DataFrames
    dfvar1 = pd.DataFrame(var1, columns=sub_var)
    dfvar2 = pd.DataFrame(var2, columns=sub_var)

    # Define years
    years = np.arange(1995, 2051)  # Adjusting the years based on the example plot

    # Create the plot
    plt.figure(figsize=(10, 6))

    colors = ('tab:blue', 'tab:purple', 'tab:brown', 'teal', 'tab:orange', 'gold', 'tab:green', 'pink')

    # Plot each column (each energy source) for both datasets
    for i, col in enumerate(sub_var):
            plt.plot(years, dfvar1[col], label=col, color=colors[i])  # Data from ds1
            plt.plot(years, dfvar2[col], linestyle="--", color=colors[i])  # Data from ds2 (dashed line)

    # Customize the plot
    plt.xlabel('Years [-]', fontsize=14)
    plt.ylabel(y_axis_label, fontsize=14)
    plt.tick_params(axis='both', which='major', labelsize=12)  # Adjust tick label size
    plt.legend(loc='upper left', ncol=3, fontsize=10)  # Position and size of legend
    plt.grid()
    # Save the plot if needed
    if save:
        file_path = os.path.join(os.getcwd(), "Figures", "analysis", "res_installed.pdf")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        plt.savefig(file_path)

    # Show the plot
    plt.show()

def analysis(ds1, ds2, cum, name_var, ylabel1, ylabel2, save=False): 

    flag1 = True
    flag2 = True


    if name_var in ds1.variables:
        var1 = ds1.variables[name_var][:]
    else:
        flag1 = False

    if name_var == 'invest_res_elec':
        dfvar = pd.DataFrame(var1, columns=["hydro","geot_elec","solid_bioE_elec","oceanic","wind_onshore","wind_offshore","solar_PV","CSP"])
        var1 = dfvar.sum(axis=1).values
        var2 = ds2.variables["tot_investments_res"][:]
    elif name_var == 'grid_reinforcement_costs_tdollar':
        var2 = ds2.variables["tot_investments_ntc"][:]
    elif name_var == 'extra_monet_invest_to_cope_with_variable_elec_res':
        var2 = ds2.variables["tot_investments_ntc"][:]
    elif name_var == 'total_monet_invest_res_for_elec_tdolar' or 'cumulated_total_monet_invest_res_for_elec':
        var2 = ds2.variables["tot_investments_ntc"][:] + ds2.variables["tot_investments_res"][:]
    elif name_var == 'res_elec_tot_overcapacity':
        var2 = ds2.variables["curtailment"][:]
    elif name_var in ds2.variables:
        var2 = ds2.variables[name_var][:]
    else:
        flag2 = False

    if cum: 
        var1 = np.cumsum(var1)
        var2 = np.cumsum(var2)

    print(var2)
    years = np.arange(1995, 2051)

    plt.figure(figsize=(10, 6))
    
    # Plot for the first variable on the left y-axis
    ax1 = plt.gca()  # Get the current axes
    if flag1:
        if name_var == 'res_elec_tot_overcapacity':
            label = "Initial version (overcapacity)"
        else:
            label="Initial version"
        ax1.plot(years, var1, label=label, color="tab:red") 
    ax1.set_xlabel('Years [-]', fontsize=14)
    ax1.set_ylabel(ylabel1, fontsize=14, color="tab:red")
    ax1.tick_params(axis='y', labelcolor="tab:red", labelsize=12)
    ax1.grid(True)

    # Create a second y-axis sharing the same x-axis
    ax2 = ax1.twinx()  # Create twin axes
    if flag2:
        ax2.plot(years, var2, label="Proposed version", color="tab:blue")
    ax2.set_ylabel(ylabel2, fontsize=14, color="tab:blue")
    ax2.tick_params(axis='y', labelcolor="tab:blue", labelsize=12)

    if name_var == 'grid_reinforcement_costs_tdollar':
        # ax1.set_ylim([0, 0.07])
        # ax2.set_ylim([0, 0.07])
        pass
    elif name_var == 'invest_res_elec':
        ax1.set_ylim([2, 5])
        ax2.set_ylim([2, 5])
        pass
    elif name_var == 'total_monet_invest_res_for_elec_tdolar':
        ax1.set_ylim([0, 4.5])
        ax2.set_ylim([0, 4.5])
    elif name_var == 'res_elec_tot_overcapacity':
        ax1.plot(years, [0.1]*len(years), label="Initial version (curtailment_res)", color='tab:red', linestyle="-.")
        ax1.set_ylim([-0.01, 1.5])
    

    # Add legends for both lines
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    plt.legend(lines1 + lines2, labels1 + labels2, fontsize=10, loc='upper left')
    
    # Save the figure if required
    if save:
        file_path = os.path.join(os.getcwd(), "Figures", "analysis", f"{name_var}.pdf")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        plt.savefig(file_path)

    plt.show()

def analysis2(ds1, ds2, cum, name_var, ylabel1, ylabel2, save=False): 

    var1 = ds1.variables['abundance_electricity'][:]

    var2 = ds2.variables[name_var][:]

    years = np.arange(1995, 2051)

    plt.figure(figsize=(10, 6))
    
    # Plot for the first variable on the left y-axis
    ax1 = plt.gca()  # Get the current axes
    label = "Loss of Load (initial version) [Twh]"
    ax1.plot(years, var1, label=label, color="tab:red") 
    ax1.set_xlabel('Years [-]', fontsize=14)
    ax1.set_ylabel(ylabel1, fontsize=14, color="tab:red")
    ax1.tick_params(axis='y', labelcolor="tab:red", labelsize=12)
    ax1.grid(True)

    # Create a second y-axis sharing the same x-axis
    ax2 = ax1.twinx()  # Create twin axes
    ax2.plot(years, var2, label="Loss of Load (proposed version)", color="tab:blue")
    ax2.set_ylabel(ylabel2, fontsize=14, color="tab:blue")
    ax2.tick_params(axis='y', labelcolor="tab:blue", labelsize=12)

    # ax1.plot(years, [0.1]*len(years), label="Initial version (curtailment_res)", color='tab:red', linestyle="-.")
    # ax1.set_ylim([-0.01, 1.5])
    

    # # Add legends for both lines
    # lines1, labels1 = ax1.get_legend_handles_labels()
    # lines2, labels2 = ax2.get_legend_handles_labels()
    # plt.legend(lines1 + lines2, labels1 + labels2, fontsize=10, loc='upper left')
    
    # Save the figure if required
    if save:
        file_path = os.path.join(os.getcwd(), "Figures", "analysis", f"{name_var}.pdf")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        plt.savefig(file_path)

    plt.show()

def plot_regression(save=False):
    # Historical data
    hist_years = np.arange(1, 23)
    hist_wind = [
        0.005215058, 0.006228103, 0.007437936, 0.008882783, 0.010608298, 0.012669,
        0.01725, 0.022878, 0.027683, 0.0336658, 0.0397158, 0.0467198, 0.0549608,
        0.0629078, 0.0730683, 0.08155, 0.090616, 0.1012695, 0.1110025, 0.1210705,
        0.1308269, 0.1412435
    ]
    hist_solar = [
        6.52293e-6, 1.26524e-5, 2.45417e-5, 4.7603e-5, 9.23347e-5, 0.0001791,
        0.0002781, 0.0003622, 0.0005993, 0.0013074, 0.0022976, 0.0032806, 0.005254,
        0.0104225, 0.0168315, 0.029538, 0.051672, 0.0691754, 0.0794704, 0.0868224,
        0.0948718, 0.0995754
    ]
    hist_wind_off = [
        5.83073e-6, 9.50153e-6, 1.54833e-5, 2.5231e-5, 4.11154e-5, 0.000067,
        0.000077, 0.000237, 0.000506, 0.0005962, 0.0006832, 0.0008822, 0.0011012, 
        0.0014792, 0.0021437, 0.003016, 0.003553, 0.0050505, 0.0070702, 0.0080162,
        0.0106562, 0.0124732
    ]

    # Extrapolated data
    years = np.arange(0, 56)
    extrap_wind = 0.0002 * years**2 + 0.0005 * years + 0.012
    extrap_wind_linear = 0.0067*years-0.0224
    extrap_solar = 0.0119 * years - 0.0109
    extrap_wind_off = 0.0018 * years + 0.0016
    plt.figure(figsize=(10, 6))

    # Extrapolated data
    plt.plot(years, extrap_wind, label='Extrap Wind onshore (polynomial)', color='tab:orange')
    plt.plot(years, extrap_wind_linear, label='Extrap Solar (linear)', color='tab:orange', alpha=0.7)
    plt.plot(hist_years, hist_wind, label='Historical Wind onshore', color='grey', marker='o', markersize=3)

    plt.text(32, 0.6, r'$y = 0.0002x^2 + 0.0005x + 0.0058$', fontsize=12, color='tab:orange')
    plt.text(32, 0.575, r'$R^2=0.9986$', fontsize=12, color='tab:orange')
    plt.text(40, 0.2, r'$y = 0.0067x - 0.0224$', fontsize=12, color='tab:orange', alpha=0.7)
    plt.text(40, 0.175, r'$R^2=0.9484$', fontsize=12, color='tab:orange', alpha=0.7)

    # Labels and legend
    plt.xlabel('Years [-]', fontsize=14)
    plt.ylabel('Power Installed [TW]', fontsize=14)
    plt.xticks(np.arange(5, 60, 10), np.arange(2000, 2060, 10))    
    plt.tick_params(axis='both', which='major', labelsize=12)
    plt.grid(True)
    plt.legend()
    # Save plot if required
    if save:
        current_path = os.getcwd()  # Get current working directory
        file_path = os.path.join(current_path, "Figures", "case_study", "RES_reg.pdf")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)  # Ensure directories exist
        plt.savefig(file_path)
    plt.show()


    plt.figure(figsize=(10, 6))

    # Extrapolated data
    plt.plot(years[12:], extrap_solar[:44], label='Extrap Solar PV (from 2007)', color='tab:green')
    plt.plot(hist_years, hist_solar, label='Historical Solar PV', color='tab:green', linestyle='--', marker='.', alpha=0.5)

    plt.plot(years[16:], extrap_wind_off[:40], label='Extrap Wind offshore (from 2011)', color='gold')
    plt.plot(hist_years, hist_wind_off, label='Historical Wind offshore', color='gold', linestyle='--', marker='.', alpha=0.5)

    plt.text(30, 0.425, r'$y = 0.0119x + 0.0109', fontsize=12, color='tab:green')
    plt.text(30, 0.4, r'$R^2=0.9704$', fontsize=12, color='tab:green')
    plt.text(35, 0.1, r'$y = 0.0018x + 0.0016$', fontsize=12, color='gold', alpha=0.7)
    plt.text(35, 0.075, r'$R^2=0.9891$', fontsize=12, color='gold', alpha=0.7)

    # Labels and legend
    plt.xlabel('Years [-]', fontsize=14)
    plt.ylabel('Power Installed [TW]', fontsize=14)
    plt.xticks(np.arange(5, 60, 10), np.arange(2000, 2060, 10))    
    plt.tick_params(axis='both', which='major', labelsize=12)
    plt.grid(True)
    plt.legend()


    # Save plot if required
    if save:
        current_path = os.getcwd()  # Get current working directory
        file_path = os.path.join(current_path, "Figures", "case_study", "wind_off_solar_reg.pdf")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)  # Ensure directories exist
        plt.savefig(file_path)

    # Show plot
    plt.show()

def plot_lim_wind(ds, save=False):

    # share_wind_ON = float(installed_capacity_res_elec().loc['wind_onshore']*cp_res_elec().loc['wind_onshore'])/peak_load()/0.736
    # share_wind_OFF = float(installed_capacity_res_elec().loc['wind_offshore']*cp_res_elec().loc['wind_offshore'])/peak_load()/0.736
    
    # share_wind = share_wind_ON+share_wind_OFF
    # bounds = (0, 0.55)

    years = np.arange(1995, 2051)   
    # peak_load = dataset.variables['peak_load'][:]
    # dfRES = pd.DataFrame(ds.variables["installed_capacity_res_elec"][:], columns=["hydro","geot_elec","solid_bioE_elec","oceanic","wind_onshore","wind_offshore","solar_PV","CSP"])
    # dfcpRES = pd.DataFrame(ds.variables["cp_res_elec"][:], columns=["hydro","geot_elec","solid_bioE_elec","oceanic","wind_onshore","wind_offshore","solar_PV","CSP"])

    # upper_bound = (0.55 * peak_load * 0.736)/(dfcpRES["wind_onshore"].values+dfcpRES["wind_offshore"].values)

    share_wind=dataset.variables['share_wind'][:]

    plt.figure(figsize=(10, 6))
    plt.plot(years, share_wind, label='share_wind', color='tab:orange') # , marker='o', markerfacecolor='lightblue'
    plt.plot(years, [0.55]*len(years), label='Upper bound', color='tab:red', linestyle='--')
    plt.xlabel('Years [-]', fontsize=14)
    plt.ylabel('Dmnl [-]', fontsize=14)
    plt.tick_params(axis='both', which='major', labelsize=12)  # Change 12 to your desired size
    plt.grid(True)
    plt.legend()
    if save:
        file_path = os.path.join(current_path, "Figures", "case_study", "limit_wind.pdf")
        plt.savefig(file_path)
    plt.show()

def cs_sm(FFF, BAU, OT, save=False):
    legend = []
    years = np.arange(1995, 2051)
    flag=True

    plt.figure(figsize=(10, 6))
    styles=('-', '--', '-.')
    names=('FFF', 'BAU', 'OT')
    i=0
    for dataset in (FFF, BAU, OT):
        
        # share_flex = dataset.variables['share_flex'][:]
        # cap_ratio = dataset.variables['cap_ratio'][:]
        share_pv = dataset.variables['share_pv'][:]
        share_wind = dataset.variables['share_wind'][:]
        # share_sto = dataset.variables['share_sto'][:]
        # rNTC = dataset.variables['rNTC'][:]
        # flag = plot_with_bounds(years, cap_ratio, 'cap_ratio - '+names[i], 'tab:red', bounds[0], legend, flag=flag, style=styles[i])
        # flag = plot_with_bounds(years, share_flex, 'share_flex', 'tab:blue', bounds[1], legend, flag=flag)
        # flag = plot_with_bounds(years, share_sto, 'share_sto - '+names[i], 'tab:purple', bounds[2], legend, flag=flag, style=styles[i])
        flag = plot_with_bounds(years, share_wind, 'share_wind - '+names[i], 'tab:orange', bounds[3], legend, flag=flag, style=styles[i])
        flag = plot_with_bounds(years, share_pv, 'share_pv - '+names[i], 'tab:green', bounds[4], legend, flag=flag, style=styles[i])
        # flag = plot_with_bounds(years, rNTC, 'rNTC', 'teal', bounds[5], legend, flag=flag)
        i+=1

    # line, = plt.plot(years, [0.55]*len(years), label='Upper Bound - Wind', color='tab:purple', linestyle='-')
    # legend.append(line)
    # line, = plt.plot(years, [0.35]*len(years), label='Upper Bound - Solar', color = 'pink', linestyle='-')
    # legend.append(line)
    plt.legend(handles=legend, loc='center left')
    plt.xlabel('Years [-]', fontsize=14)
    plt.ylabel('Dmnl [-]', fontsize=14)
    plt.tick_params(axis='both', which='major', labelsize=12)
    plt.grid(True)
    if save:
        file_path = os.path.join(current_path, "Figures", "case_study", "features.pdf")
        plt.savefig(file_path)
    plt.show()

    plt.figure(figsize=(10, 6))
    legend=[]
    i=0
    flag=False
    for dataset in (FFF, BAU, OT):
        cap_ratio = dataset.variables['cap_ratio'][:]
        share_sto = dataset.variables['share_sto'][:]
        flag = plot_with_bounds(years, cap_ratio, 'cap_ratio - '+names[i], 'tab:red', bounds[0], legend, flag=flag, style=styles[i])
        flag = plot_with_bounds(years, share_sto, 'share_sto - '+names[i], 'tab:purple', bounds[2], legend, flag=flag, style=styles[i])
        i+=1
    plt.legend(handles=legend, loc='center left')
    plt.xlabel('Years [-]', fontsize=14)
    plt.ylabel('Dmnl [-]', fontsize=14)
    plt.tick_params(axis='both', which='major', labelsize=12)
    plt.grid(True)
    if save:
        file_path = os.path.join(current_path, "Figures", "case_study", "features2.pdf")
        plt.savefig(file_path)
    plt.show()

    plt.figure(figsize=(10, 6))
    legend=[]
    i=0
    flag=False
    for dataset in (FFF, BAU, OT):
        load_shed = dataset.variables['load_shedding'][:]
        flag = plot_with_bounds(years, load_shed, names[i], 'tab:pink', bounds[7], legend, flag=flag, style=styles[i])
        i+=1
    plt.legend(handles=legend, loc='upper right')
    plt.xlabel('Years [-]', fontsize=14)
    plt.ylabel('Dmnl [-]', fontsize=14)
    plt.tick_params(axis='both', which='major', labelsize=12)
    plt.grid(True)
    if save:
        file_path = os.path.join(current_path, "Figures", "case_study", "load_shedding.pdf")
        plt.savefig(file_path)
    plt.show()

    plt.figure(figsize=(10, 6))
    legend=[]
    i=0
    flag=False
    for dataset in (FFF, BAU, OT):
        curt = dataset.variables['curtailment'][:]
        flag = plot_with_bounds(years, curt, names[i], 'gold', bounds[7], legend, flag=flag, style=styles[i])
        i+=1
    plt.legend(handles=legend, loc='upper left')
    plt.xlabel('Years [-]', fontsize=14)
    plt.ylabel('Dmnl [-]', fontsize=14)
    plt.tick_params(axis='both', which='major', labelsize=12)
    plt.grid(True)
    if save:
        file_path = os.path.join(current_path, "Figures", "case_study", "curtailment.pdf")
        plt.savefig(file_path)
    plt.show()

def cs_variable(FFF, BAU, OT, name_var, color, yaxis, save=False):

    if name_var == 'co2_emissions_per_fuel' or name_var == 'required_fed_by_fuel':
        FFFvar = FFF.variables[name_var][:]
        BAUvar = BAU.variables[name_var][:]
        OTvar = OT.variables[name_var][:]

        sub_var=["electricity","heat","liquids","gases","solids"]
        dfFFF = pd.DataFrame(FFFvar, columns=sub_var)
        dfBAU = pd.DataFrame(BAUvar, columns=sub_var)
        dfOT = pd.DataFrame(OTvar, columns=sub_var)

        FFFvar = dfFFF["electricity"]
        BAUvar = dfBAU["electricity"]
        OTvar = dfOT["electricity"]
    else:
        FFFvar = FFF.variables[name_var][:]
        BAUvar = BAU.variables[name_var][:]
        OTvar = OT.variables[name_var][:]
        
    years = np.arange(1995, 2051)

    plt.figure(figsize=(10, 6))
    plt.plot(years, FFFvar, label='FFF', linestyle='-', color=color)
    plt.plot(years, BAUvar, label='BAU', linestyle='--', color=color) 
    plt.plot(years, OTvar, label='OT', linestyle='-.', color=color) 

    plt.xlabel('Years [-]', fontsize=14)
    plt.ylabel(yaxis, fontsize=14)
    plt.tick_params(axis='both', which='major', labelsize=12)  # Change 12 to your desired size
    plt.grid(True)
    plt.legend()
    if save:
        file_path = os.path.join(current_path, "Figures", "case_study", f"{name_var}.pdf")
        plt.savefig(file_path)
    plt.show()

def plot_costs_pypsa():
    path = r'C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\pymedeas2_models\prices_1995USD_W.csv'

    df = pd.read_csv(path)
    df = df.T
    df.columns = df.iloc[0]  # Set the first row as header
    df = df[1:]  # Drop the first row since it is now the header
    df = df[['Solar', 'Wind (Onshore)', 'Wind (Offshore)']]
    print(df)

    MEDEAS_windon = np.array([0.82, 0.78, 0.74, 0.73])/20
    MEDEAS_windoff = np.array([1.26, 1.2, 1.09, 1.07])/20
    MEDEAS_solar = np.array([1.45, 0.84, 0.64, 0.62])/25

    # Each row : time step
    # Each column : sub-variable
    plt.figure(figsize=(10, 6))
    plt.plot(df.index, df['Solar'], marker='o', color='tab:green', label='Solar - PyPSA')
    plt.plot(df.index, MEDEAS_solar, linestyle='--', marker='o', color='tab:green', label='Solar - MEDEAS')
    # plt.plot(df.index, df['Wind (Onshore)'], marker='o', color='tab:orange', label='Wind Onshore - PyPSA')
    # plt.plot(df.index, MEDEAS_windon, linestyle='--', marker='o', color='tab:orange', label='Wind Oshore - MEDEAS')
    plt.plot(df.index, df['Wind (Offshore)'], marker='o', color='gold', label='Wind Offshore - PyPSA')
    plt.plot(df.index, MEDEAS_windoff, linestyle='--', marker='o', color='gold', label='Wind Offshore - MEDEAS')
    plt.xlabel('Years [-]', fontsize=14)
    plt.ylabel('RES Annualized Costs [1995-USD/W]', fontsize=14)
    plt.tick_params(axis='both', which='major', labelsize=12)  # Change 12 to your desired size
    plt.grid(True)
    plt.legend()
    file_path = os.path.join(current_path, "Figures", f"pypsa_prices.pdf")
    plt.savefig(file_path)
    plt.show()

def plot_invests_analysis(ds1, ds2, save=False):
    # MEDEAS
    years = np.arange(2020, 2051)
    res1 = ds1.variables['invest_res_elec'][:]
    dfvar1 = pd.DataFrame(res1, columns=["hydro","geot_elec","solid_bioE_elec","oceanic","wind_onshore","wind_offshore","solar_PV","CSP"])
    res1 = dfvar1.sum(axis=1).values[25:]
    grid1 = ds1.variables['extra_monet_invest_to_cope_with_variable_elec_res'][:][25:]
    # sto1 = ds1.variables[''][:]

    res1 = np.cumsum(res1)
    grid1 = np.cumsum(grid1)


    # Create a stackplot
    plt.figure(figsize=(10, 6))
    plt.stackplot(years, res1, grid1, labels=['RES Deployment', 'Grid Reinforcement'], colors=['tab:green', 'teal'])

    plt.xlabel('Years [-]', fontsize=14)
    plt.ylabel('Cumulated Investments Assessment [T$]', fontsize=14)
    plt.tick_params(axis='both', which='major', labelsize=12)  # Change 12 to your desired size
    plt.grid(True)
    plt.legend()
    file_path = os.path.join(current_path, "Figures", 'analysis', "old_stack_invest.pdf")
    plt.savefig(file_path)
    plt.show()

    # New version

    res2 = ds2.variables['tot_investments_res'][:][25:]
    grid2 = ds2.variables['tot_investments_ntc'][:][25:]
    sto2 = ds2.variables['tot_investments_storage'][:][25:]

    res2 = np.cumsum(res2)
    grid2 = np.cumsum(grid2)
    sto2 = np.cumsum(sto2)

    # Create a stackplot
    plt.figure(figsize=(10, 6))
    plt.stackplot(years, res2, grid2, sto2, labels=['RES Deployment', 'Grid Reinforcement', 'Storage Deployment'], colors=['tab:green', 'teal', 'tab:purple'])

    plt.xlabel('Years [-]', fontsize=14)
    plt.ylabel('Cumulated Investments Assessment [T$]', fontsize=14)
    plt.tick_params(axis='both', which='major', labelsize=12)  # Change 12 to your desired size
    plt.grid(True)
    plt.legend()
    file_path = os.path.join(current_path, "Figures", 'analysis', "new_stack_invest.pdf")
    plt.savefig(file_path)
    plt.show()

def plot_shares(save=False):
    # Load the CSV file
    file_path = r'C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\pymedeas2_models\models\europe\modules_pymedeas_eu\surr_model\pypsa\capa and invest\interp_tech_shares_ls.csv'
    df = pd.read_csv(file_path)

    # Filter the DataFrame for decades
    df_decades = df[(df['Year'] % 5 == 0) & (df['Year'] >= 2020)]
    df_decades.rename(columns={'Hydro': 'Hydro (conv)'}, inplace=True)

    # Normalize proportions to sum to 100% per year
    df_decades.set_index('Year', inplace=True)
    df_decades_percent = df_decades.div(df_decades.sum(axis=1), axis=0) * 100

    # Use Seaborn's color palette
    sns_palette = sns.color_palette("tab10", n_colors=len(df_decades.columns))

    # Plot as stacked bar chart
    ax = df_decades_percent.plot(kind='bar', stacked=True, figsize=(12, 8), color=sns_palette)
    plt.ylabel('Percentage', fontsize=14)
    plt.xlabel('Year', fontsize=14)
    plt.tick_params(axis='both', which='major', labelsize=12)  
    plt.legend(title='Investments Shares', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    if save:
        file_path = os.path.join(current_path, "Figures", "share_tech.pdf")
        plt.savefig(file_path)
    plt.show()

def plot_demand_not_covered(save=False):

    ds_path = r'C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\pymedeas2_models\models\europe\FINAL\baseline_scenario.nc'
    dataset = nc.Dataset(ds_path)

    var = dataset.variables["total_fe_elec_consumption_twh"][:] # generation output minus transm&distrib loss
    var2 = dataset.variables["fe_demand_elec_consum_twh"][:] # demand elec from IOA without transm&distrib losses

    years = np.arange(1995, 2051)

    plt.figure(figsize=(10, 6))
    plt.plot(years, var)
    plt.plot(years, var2)
    plt.xlabel('Years [-]', fontsize=14)
    # plt.ylabel(y_axis_label, fontsize=14)
    plt.tick_params(axis='both', which='major', labelsize=12)  # Change 12 to your desired size
    plt.grid(True)
    plt.legend()
    if save:
        file_path = os.path.join(current_path, "Figures", f"{name_var}.svg")
        plt.savefig(file_path)
    plt.show()

if __name__ == '__main__':
    global flag, legend    # plot_shares(True)
    
    '''
    World - BAU
    '''
    # ds_path = r'C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\pymedeas2_models\models\world\results.nc' # results.nc = results_RES.nc
    # dataset_res = nc.Dataset(ds_path)

    # ds_path = r'C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\pymedeas2_models\models\world\results_FF.nc'
    # dataset_bau = nc.Dataset(ds_path)


    res_kinds = ["hydro","geot_elec","solid_bioE_elec","oceanic","wind_onshore","wind_offshore","solar_PV","CSP"]

    # plot_variable_bau(dataset_res, dataset_bau, 2021, "gdppc", "Gross Domestic Product per capita [$/pers.]", ("tab:blue", "tab:red"), save=True)
    # plot_ff_extraction(dataset_bau)
    # plot_baseline_outcome(save=True)

    '''
    World - Nuclear
    '''
    # ds_path = r'C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\pymedeas2_models\models\world\results_3_pronuc.nc'
    # dataset_nuc = nc.Dataset(ds_path)

    # ds_path = r'C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\pymedeas2_models\models\world\results_4_PhaseOutNuc.nc'
    # dataset_nonuc = nc.Dataset(ds_path)

    # ds_path = r'C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\pymedeas2_models\models\world\results_2_Decom.nc'
    # dataset_decom = nc.Dataset(ds_path)

    res_kinds = ["hydro","geot_elec","solid_bioE_elec","oceanic","wind_onshore","wind_offshore","solar_PV","CSP"]

    # plot_variable_nuc(dataset_nuc, dataset_nonuc, dataset_decom, 2015, "annual_gdppc_growth_rate", "Potential Max HDI [-]", ("tab:green", "tab:orange", "tab:cyan"), save=True)
    
    """ Capacity Factors - Curtailment """
    # res_kinds = ["hydro","geot_elec","solid_bioE_elec","oceanic","wind_onshore","wind_offshore","solar_PV","CSP"]
    # plot_group_subvar_cp_curt(dataset, "real_cp_res_elec", "RES capacity factors [-]", res_kinds, True)

    '''
    FF Extraction
    '''
    # ds_path = r'C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\pymedeas2_models\models\world\results_BAU.nc'
    # ds = nc.Dataset(ds_path)
    # plot_ff_extraction(ds)
    '''
    Europe
    '''
    # ds_path = r'C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\pymedeas2_models\models\europe\results_noPID.nc'
    # dataset = nc.Dataset(ds_path)

    # ds_path_2 = r'C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\pymedeas2_models\models\europe\results_Pcurt_Pls_E16.nc'
    # dataset2 = nc.Dataset(ds_path_2)

    # ds_path_3 = r'C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\pymedeas2_models\models\europe\results_Pcurt_Pls.nc'
    # dataset3 = nc.Dataset(ds_path_3)


    # plot_demand_not_covered()

    '''
    PyPSA-EUR
    '''
    # plot_costs_pypsa()

    '''
    5 - Integration baseline and High-RES
    '''
    """Baseline Scenario"""
    ds_path = r'C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\pymedeas2_models\models\europe\FINAL\new_implementation_overcap\baseline_scen_PID_0.1_curt.nc'
    baseline = nc.Dataset(ds_path)
    
    # plot_sm(baseline, features=True, targets=False, ylim=False, save=False, flag=False)
    # plot_sm(baseline, features=False, targets=True, ylim=False, save=False, flag=False)

    # plot_investments_1ds(baseline)

    """High RES"""
    ds_path = r'C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\pymedeas2_models\models\europe\FINAL\high-RES_scenario.nc'
    highRES = nc.Dataset(ds_path)
    
    # plot_sm(highRES, features=True, targets=False, ylim=False, save=False, flag=False)
    # plot_sm(highRES, features=False, targets=True, ylim=False, save=False, flag=False)

    """MLP vs RF"""
    # plot_MLP_RF(baseline)
    # plot_MLP_RF(highRES)

    '''
    6 - Feedback
    '''

    # plot_shares(save=True)

    ds_path = r'C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\pymedeas2_models\models\europe\FINAL\PID\perfecto_baseline_0.00001_0.01.nc'
    PID = nc.Dataset(ds_path)

    # plot_sm(PID, features=True, targets=False, ylim=False, save=True, flag=False)
    # plot_sm(PID, features=False, targets=True, ylim=False, save=True, flag=True)
    # plot_2_sm(baseline, PID)
    # plot_investments_2ds(baseline, PID)

    ds_path = r'C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\pymedeas2_models\models\europe\FINAL\PID\agg_baseline_scenario_PID_0.1_0.1_0.1_0.1.nc'
    agg_PID = nc.Dataset(ds_path)

    # plot_sm(agg_PID, features=True, targets=False, ylim=False, save=True, flag=False)
    # plot_sm(agg_PID, features=False, targets=True, ylim=False, save=True, flag=True)
    # plot_2_sm(baseline, agg_PID)
    # plot_investments_2ds(baseline, agg_PID)

    # ds_path = r'C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\pymedeas2_models\models\europe\results.nc'
    # results = nc.Dataset(ds_path)
    ds_path = r'C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\pymedeas2_models\models\europe\FINAL\OT.nc'
    OT = nc.Dataset(ds_path)
    ds_path = r'C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\pymedeas2_models\models\europe\FINAL\FFF.nc'
    FFF = nc.Dataset(ds_path)
    ds_path = r'C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\pymedeas2_models\models\europe\FINAL\PID\OT_PIDcurt_0.1.nc'
    OT_curt = nc.Dataset(ds_path)


    plot_sm(OT_curt, features=True, targets=False, ylim=False, save=True, flag=False)
    plot_sm(OT_curt, features=False, targets=True, ylim=False, save=True, flag=True)
    plot_2_sm(OT, OT_curt)
    plot_investments_2ds(OT, OT_curt)

    """
    7 - Comparative anaylsis
    """
    ds_path = r'C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\pymedeas2_models\models\europe\FINAL\comparative_analysis_base.nc'
    old_model = nc.Dataset(ds_path)

    ds_path = r'C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\pymedeas2_models\models\europe\FINAL\comparative_analysis_new.nc'
    new_model = nc.Dataset(ds_path)

    # analysis2(old_model, new_model, False, "load_shed_twh", "Loss of Load (Initial version) [TWh]", "Loss of Load (Proposed version) [TWh]", save=False)
    
    # analysis2(old_model, new_model, False, "res_elec_tot_overcapacity" , "Curtailment (Initial version) [-]", "Curtailment (Proposed version) [-]", save=True)
    
    # plot_resmix(old_model, False)
    # plot_resmix(new_model, True)

    # analysis(dataset2, dataset, True, "extra_monet_invest_to_cope_with_variable_elec_res" , "Cum. Transimission Investments (Initial version) [T$]", "Cum. Grid Investments (Proposed version) [T$]", save=True)
    # analysis(dataset2, dataset, True, "invest_res_elec" , "Cum. RES Investments (Initial version) [T$]", "Cum. RES Investments (Proposed version) [T$]", save=True)

    # analysis(dataset2, dataset, True, "tot_investments_storage" , "Storage Investments (Initial version) [T$]", "Storage Investments (Proposed version) [T$]", save=True)
    # analysis(dataset2, dataset, False, "load_shedding" , "Load Shedding (Initial version) [-]", "Load Shedding (Proposed version) [-]", save=True)
    # analysis(dataset2, dataset, True, "total_monet_invest_res_for_elec_tdolar" , "RES+Grid Investments (Initial version) [T$]", "RES+Grid Investments (Proposed version) [T$]", save=True)
    
    '''
    8 - Case Study
    '''
    ds_path = r'C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\pymedeas2_models\models\europe\FINAL\FFF.nc'
    FFF = nc.Dataset(ds_path)
    ds_path = r'C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\pymedeas2_models\models\europe\FINAL\BAU.nc'
    BAU = nc.Dataset(ds_path)
    ds_path = r'C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\pymedeas2_models\models\europe\FINAL\OT.nc'
    OT = nc.Dataset(ds_path)
    names=['FFF', 'BAU', 'OT']

    # plot_resmix(FFF, save=True)
    # plot_resmix(BAU, save=True)
    # plot_resmix(OT, save=True)

    # plot_regression(True)

    # plot_lim_wind(dataset)

    # cs_sm(FFF, BAU, OT, save=True)
    
    # plot_investments_combined([FFF, BAU, OT], names, save=True)
    
    # cs_variable(FFF, BAU, OT, 'peak_load', 'tab:blue', 'Total Electrical Demand [TWh]', save=False) # required_fed_by_fuel

    # cs_variable(FFF, BAU, OT, 'population', 'tab:blue', 'Population [pers.]', save=False)
    # cs_variable(FFF, BAU, OT, 'gdppc', 'steelblue', 'GDP per capita [T$/pers.]', save=True)
    # cs_variable(FFF, BAU, OT, 'real_demand_tdollars', 'red', 'GDP per capita [T$/pers.]', save=False)

    # cs_variable(FFF, BAU, OT, 'total_land_requirements_renew_mha', 'steelblue', 'Total Land Requirements for RES [MHa]', save=False)
    # cs_variable(FFF, BAU, OT, 'co2_emissions_per_fuel', 'olivedrab', 'CO2 Emissions induced by Electricity Gen. [GtCO2/y]', save=True)



