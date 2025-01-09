#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Commented part (lines 13-276): capacities and investments data extraction from pypsa models.
Uncommented part (lines 278-424): data filtering for further use, saved in  ratios_EUR_MW.xlsx and tech_shares.xlsx. 

Wrote by Umair Muhammad Tureen and Noe Diffels
November 2024
"""
import pypsa
import pandas as pd
import matplotlib.pyplot as plt
import os 
current_script_dir = os.path.dirname(os.path.realpath(__file__))

def assign_locations(n):
    for c in n.iterate_components(n.one_port_components | n.branch_components):
        ifind = pd.Series(c.df.index.str.find(" ", start=4), c.df.index)
        for i in ifind.unique():
            names = ifind.index[ifind == i]
            c.df.loc[names, "location"] = "" if i == -1 else names.str[:i]
            
opt_name = {"Store": "e", "Line": "s", "Transformer": "s"}
planning_horizons = [2020,2030,2040,2050]

def load_file(filename):
    """
    Loads the network file using pypsa.
    """
    return pypsa.Network(filename)

def load_files(planning_horizons):
    """
    Loads network files for each planning horizon
    """
    files = {}
    for planning_horizon in planning_horizons:
        # Directly specify the filename for each planning_horizon
        filename = (r"C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\Umair\rNTC\Code_data 1\Code_data\elec_s_32_lvopt_EQ0.70c_1H-T-H-B-I-A-dist1_"+str(planning_horizon)+".nc")
        
        # Load the network file and store it in the dictionary
        files[planning_horizon] = load_file(filename)
    
    return files
loaded_files = load_files(planning_horizons)

def calculate_costs(planning_horizons):
    """ This function computes costs on EU level """
    costs_dict = {}  # Initialize dictionary for storing costs per horizon

    for planning_horizon in planning_horizons:
        
        n = loaded_files[planning_horizon]

        costs_dict[planning_horizon] = pd.DataFrame()

        # Calculate costs component by component
        for c in n.iterate_components(n.branch_components | n.controllable_one_port_components ^ {"Load"}):
            # Capital costs
            capital_costs = c.df.capital_cost * c.df[opt_name.get(c.name, "p") + "_nom_opt"]
            capital_costs_grouped = capital_costs.groupby(c.df.carrier).sum()
            capital_costs_grouped = pd.concat([capital_costs_grouped], keys=["capital"])
            capital_costs_grouped = pd.concat([capital_costs_grouped], keys=[c.list_name])

            costs_dict[planning_horizon] = costs_dict[planning_horizon].reindex(
                capital_costs_grouped.index.union(costs_dict[planning_horizon].index)
            )
            costs_dict[planning_horizon].loc[capital_costs_grouped.index, "costs"] = capital_costs_grouped

            # Marginal costs
            if c.name == "Link":
                p = c.pnl.p0.multiply(n.snapshot_weightings.generators, axis=0).sum()
            elif c.name == "Line":
                continue
            elif c.name == "StorageUnit":
                p_all = c.pnl.p.multiply(n.snapshot_weightings.generators, axis=0)
                p_all[p_all < 0.0] = 0.0
                p = p_all.sum()
            else:
                p = c.pnl.p.multiply(n.snapshot_weightings.generators, axis=0).sum()

            # Adjust sequestration cost
            if c.name == "Store":
                items = c.df.index[
                    (c.df.carrier == "co2 stored") & (c.df.marginal_cost <= -100.0)
                ]
                c.df.loc[items, "marginal_cost"] = -20.0

            # Marginal costs grouping
            marginal_costs = p * c.df.marginal_cost
            marginal_costs_grouped = marginal_costs.groupby(c.df.carrier).sum()
            marginal_costs_grouped = pd.concat([marginal_costs_grouped], keys=["marginal"])
            marginal_costs_grouped = pd.concat([marginal_costs_grouped], keys=[c.list_name])

            # Reindex and add to the DataFrame
            costs_dict[planning_horizon] = costs_dict[planning_horizon].reindex(
                marginal_costs_grouped.index.union(costs_dict[planning_horizon].index)
            )
            costs_dict[planning_horizon].loc[marginal_costs_grouped.index, "costs"] = marginal_costs_grouped
            
    return costs_dict


def calculate_capacities(planning_horizons):
    """ This function computes capacities on EU level """
    capacities_dict = {}
    for planning_horizon in planning_horizons:
        capacities_dict[planning_horizon] = pd.DataFrame()  # Initialize DataFrame for each horizon
        n = loaded_files[planning_horizon]
        for c in n.iterate_components(n.branch_components | n.controllable_one_port_components ^ {"Load"}):
            # Calculate the capacities for each component
            capacities_grouped = (
                c.df[opt_name.get(c.name, "p") + "_nom_opt"].groupby(c.df.carrier).sum()
            )
            capacities_grouped = pd.concat([capacities_grouped], keys=[c.list_name])

            # Reindex to avoid any mismatch
            capacities_dict[planning_horizon] = capacities_dict[planning_horizon].reindex(
                capacities_grouped.index.union(capacities_dict[planning_horizon].index)
            )

            # Store capacities in the dictionary
            label = "capacities"
            capacities_dict[planning_horizon].loc[capacities_grouped.index, label] = capacities_grouped

    return capacities_dict


def calculate_country_capacities(planning_horizons):
    """ This function computes capacities on country level """
    nodal_capacities_dict = {}
    for planning_horizon in planning_horizons:
        nodal_capacities_dict[planning_horizon] = pd.DataFrame()  # Initialize DataFrame for each horizon
        n = loaded_files[planning_horizon]
        assign_locations(n)
        for c in n.iterate_components(n.branch_components | n.controllable_one_port_components ^ {"Load"}):
            # Compute nodal capacities for each component
            nodal_capacities_c = c.df.groupby(["location", "carrier"])[
                opt_name.get(c.name, "p") + "_nom_opt"
            ].sum()

            # Create a MultiIndex for the components
            index = pd.MultiIndex.from_tuples(
                [(c.list_name,) + t for t in nodal_capacities_c.index.to_list()]
            )

            # Reindex the DataFrame
            nodal_capacities_dict[planning_horizon] = nodal_capacities_dict[planning_horizon].reindex(
                index.union(nodal_capacities_dict[planning_horizon].index)
            )
            label = "nodal_capacities"
            # Store nodal capacities in the dictionary for each planning horizon
            nodal_capacities_dict[planning_horizon].loc[index, label] = nodal_capacities_c.values

    return nodal_capacities_dict


def calculate_country_costs(planning_horizons):
    """ This function computes costs on country level """
    nodal_costs_dict = {}
    for planning_horizon in planning_horizons:
        # Initialize DataFrame for each planning horizon if not already initialized
        if planning_horizon not in nodal_costs_dict:
            nodal_costs_dict[planning_horizon] = pd.DataFrame()
        n = loaded_files[planning_horizon]
        assign_locations(n)
        for c in n.iterate_components(n.branch_components | n.controllable_one_port_components ^ {"Load"}):
            # Calculate capital costs for each component
            c.df["capital_costs"] = (
                c.df.capital_cost * c.df[opt_name.get(c.name, "p") + "_nom_opt"]
            )
            capital_costs = c.df.groupby(["location", "carrier"])["capital_costs"].sum()

            # Create a MultiIndex for the components
            index = pd.MultiIndex.from_tuples(
                [(c.list_name, "capital") + t for t in capital_costs.index.to_list()]
            )

            # Reindex the DataFrame for the current planning horizon
            nodal_costs_dict[planning_horizon] = nodal_costs_dict[planning_horizon].reindex(
                index.union(nodal_costs_dict[planning_horizon].index)
            )

            # Assign the capital costs values to the DataFrame
            nodal_costs_dict[planning_horizon].loc[index, 'nodal_costs'] = capital_costs.values

            # Process marginal costs
            if c.name == "Link":
                p = c.pnl.p0.multiply(n.snapshot_weightings.generators, axis=0).sum()
            elif c.name == "Line":
                continue
            elif c.name == "StorageUnit":
                p_all = c.pnl.p.multiply(n.snapshot_weightings.generators, axis=0)
                p_all[p_all < 0.0] = 0.0
                p = p_all.sum()
            else:
                p = c.pnl.p.multiply(n.snapshot_weightings.generators, axis=0).sum()

            # Sequestration cost correction
            if c.name == "Store":
                items = c.df.index[
                    (c.df.carrier == "co2 stored") & (c.df.marginal_cost <= -100.0)
                ]
                c.df.loc[items, "marginal_cost"] = -20.0

            # Calculate the marginal costs for each component
            c.df["marginal_costs"] = p * c.df.marginal_cost
            marginal_costs = c.df.groupby(["location", "carrier"])["marginal_costs"].sum()

            # Create a MultiIndex for the marginal costs
            index = pd.MultiIndex.from_tuples(
                [(c.list_name, "marginal") + t for t in marginal_costs.index.to_list()]
            )

            # Reindex the DataFrame for the current planning horizon
            nodal_costs_dict[planning_horizon] = nodal_costs_dict[planning_horizon].reindex(
                index.union(nodal_costs_dict[planning_horizon].index)
            )

            # Assign the marginal costs values to the DataFrame
            nodal_costs_dict[planning_horizon].loc[index, 'nodal_costs'] = marginal_costs.values

    return nodal_costs_dict



def load_required_data():
    """ This function loads the required data. Its important to note that costs unit is Euros
    and generators in MW and storeage in MWh. The gridscale battery is named "battery" in stores category"""
    costs_dict = calculate_costs(planning_horizons)
    combined_costs = pd.concat(
        {planning_horizon: df["costs"] for planning_horizon, df in costs_dict.items()}, 
        axis=1
    )
    combined_costs.columns.name = "planning_horizon"
    combined_costs = combined_costs.fillna(0)
    print(combined_costs)
    capital_costs = combined_costs.xs('capital', level=1)
    print(capital_costs)

    capacities_dict = calculate_capacities(planning_horizons)
    capacities = pd.concat(
        {planning_horizon: df["capacities"] for planning_horizon, df in capacities_dict.items()}, 
        axis=1
    )
    capacities.columns.name = "planning_horizon"
    capacities = capacities.fillna(0)
    
    nodal_capacities_dict = calculate_country_capacities(planning_horizons)
    country_capacities = pd.concat(
        {planning_horizon: df["nodal_capacities"] for planning_horizon, df in nodal_capacities_dict.items()}, 
        axis=1
    )
    country_capacities.columns.name = "planning_horizon"
    country_capacities = country_capacities.fillna(0)
    
    nodal_costs_dict = calculate_country_costs(planning_horizons)
    combined_nodal_costs = pd.concat(
        {planning_horizon: df['nodal_costs'] for planning_horizon, df in nodal_costs_dict.items()},
        axis=1
    )
    combined_nodal_costs.columns.name = "planning_horizon"
    combined_nodal_costs = combined_nodal_costs.fillna(0)
    country_capital_costs = combined_nodal_costs.xs('capital', level=1)
    
    return capital_costs, capacities, country_capacities, country_capital_costs


capital_costs, capacities, country_capacities, country_capital_costs = load_required_data()

capital_costs = pd.DataFrame(capital_costs)
capacities = pd.DataFrame(capacities)

# Calculate the ratio (EUR/MW)
ratios = capital_costs / capacities
# Replace infinities and NaN values with 0 for cases where capacities are 0
ratios = ratios.replace([float('inf'), -float('inf')], 0).fillna(0)

capital_costs.to_csv('investments.csv')
capacities.to_csv('capacities.csv')
ratios.to_csv('ratios_EURperMW.csv')

def get_data_investments():
    """
    shares = the share among capacities groups: RES, Storage, rNTC
    tech_shares = the share among all techno
    """
    investments = pd.read_csv(current_script_dir+'\\inputs\\investments_usefull.csv', index_col=1)
    tech_shares = pd.DataFrame(index=[2020, 2030, 2040, 2050])
    tech_shares.index.name = "Year"  # Add an index name

    ''' rNTC Investments'''
    grid_distribution_investments = investments.loc[investments.index.str.contains('electricity')]
    AC_lines_investments = investments.loc[investments.index.str.contains('AC')]
    DC_lines_investments = investments.loc[investments.index.str.contains('DC')]
    # Initialize an empty DataFrame with years as the index
    rNTC_inv = pd.DataFrame(index=[2020, 2030, 2040, 2050])
    rNTC_inv.index.name = "Year"  # Add an index name
    # Compute values for each year
    for year in rNTC_inv.index:
        year_str = str(year)  # Ensure year is a string to match column names
        grid_value = grid_distribution_investments.loc['electricity distribution grid', year_str]
        ac_value = AC_lines_investments.loc['AC', year_str]
        dc_value = DC_lines_investments.loc['DC', year_str]
        rNTC_inv.loc[year, 'Grid Investment'] = ac_value + dc_value

        tech_shares.loc[year, 'Distrib Grid'] = grid_value
        tech_shares.loc[year, 'AC Lines'] = ac_value
        tech_shares.loc[year, 'DC Lines'] = dc_value
    #print(rNTC_inv.T)
    

    ''' RES Investments '''
    pv_investments = investments.loc[investments.index.str.contains('solar')]
    ror_investments = investments.loc[investments.index.str.contains('ror')]
    wind_investments = investments.loc[investments.index.str.contains('wind')]

    # Initialize an empty DataFrame with years as the index
    res_inv = pd.DataFrame(index=[2020, 2030, 2040, 2050])
    res_inv.index.name = "Year"  # Add an index name
    # Compute values for each year
    for year in res_inv.index:
        year_str = str(year)  # Ensure year is a string to match column names
        pv_value = pv_investments.loc['solar', year_str]+pv_investments.loc['solar rooftop', year_str]
        ror_value = ror_investments.loc['ror', year_str]
        windon_value = wind_investments.loc['onwind', year_str]
        windoffac_value = wind_investments.loc['offwind-ac', year_str]
        windoffdc_value = wind_investments.loc['offwind-dc', year_str]
        

        res_inv.loc[year, 'RES Investment [EUR]'] = pv_value + ror_value + windon_value + windoffac_value + windoffdc_value

        tech_shares.loc[year, 'Solar'] = pv_value
        tech_shares.loc[year, 'ROR'] = ror_value
        tech_shares.loc[year, 'Wind (Onshore)'] = windon_value
        tech_shares.loc[year, 'Wind (Offshore)'] = windoffac_value + windoffdc_value
        
    #print(res_inv.T)

    ''' Storage Investments '''
    PHS_investments = investments.loc[investments.index.str.contains('PHS')]
    hydro_investments = investments.loc[investments.index.str.contains('hydro')]
    battery_investments = investments.loc[investments.index.str.contains('battery')] # Contains also 'home battery' row but only 'battery' selected afterwards. 
    # Initialize an empty DataFrame with years as the index
    storage_inv = pd.DataFrame(index=[2020, 2030, 2040, 2050])
    storage_inv.index.name = "Year"  # Add an index name
    # Compute values for each year
    for year in storage_inv.index:
        year_str = str(year)  # Ensure year is a string to match column names
        phs_value = PHS_investments.loc['PHS', year_str]
        hydro_value = hydro_investments.loc['hydro', year_str]
        battery_value = battery_investments.loc['battery', year_str]
        storage_inv.loc[year, 'Storage Investment'] = hydro_value + phs_value

        tech_shares.loc[year, 'PHS'] = phs_value
        tech_shares.loc[year, 'Hydro'] = hydro_value
        tech_shares.loc[year, 'Battery'] = battery_value

    #print(storage_inv.T)

    """ Shares among all investments """
    # Ensure the ratios DataFrame is initialized correctly
    group_shares = pd.DataFrame(index=[2020, 2030, 2040, 2050])
    storage_inv.index.name = "Year"  # Add an index name

    shares_curt = tech_shares.copy()
    shares_curt = shares_curt[["Distrib Grid", "AC Lines", "DC Lines", "PHS", "Hydro", "Battery"]]
    for year in group_shares.index:
        # Compute the sum of investments for the given year
        rNTC_value = rNTC_inv.loc[year].iloc[0]
        res_value = res_inv.loc[year].iloc[0]
        storage_value = storage_inv.loc[year].iloc[0]
        sum = rNTC_value + res_value + storage_value
        sum_curt = rNTC_value + storage_value
        # Assign the shares and total
        group_shares.loc[year, 'Share rNTC [-]'] = rNTC_value / sum
        group_shares.loc[year, 'Share RES [-]'] = res_value / sum
        group_shares.loc[year, 'Share Storage [-]'] = storage_value / sum
        group_shares.loc[year, 'Total [EUR]'] = sum

        
        shares_curt.loc[year, :] = shares_curt.loc[year, :]/shares_curt.loc[year, :].sum()
        tech_shares.loc[year, :] = tech_shares.loc[year, :]/tech_shares.loc[year, :].sum() 

    # Display the resulting DataFrame
    print(group_shares.T)
    group_shares.T.to_csv(current_script_dir+'\\outputs\\group_shares.csv')

    print(tech_shares.T)
    tech_shares.T.to_csv(current_script_dir+'\\outputs\\tech_shares_ls.csv')

    print(tech_shares.T)
    shares_curt.T.to_csv(current_script_dir+'\\outputs\\tech_shares_curt.csv')

    print(shares_curt.iloc[0].sum())





#get_data_investments()


def get_data_ratios():
    ratios = pd.read_csv(current_script_dir+'\\inputs\\ratios_EURperMW.csv', index_col=1)

    ratio_invest = pd.DataFrame(index=[2020, 2030, 2040, 2050])
    ratio_invest.index.name = "Year"  # Add an index name

    ratio_solar = ratios.loc[ratios.index.str.contains('solar')]
    ratio_ror = ratios.loc[ratios.index.str.contains('ror')]
    ratio_wind = ratios.loc[ratios.index.str.contains('wind')]
    
    ratio_AC = ratios.loc[ratios.index.str.contains('AC')]
    ratio_DC = ratios.loc[ratios.index.str.contains('DC')]
    ratio_distrib_grid = ratios.loc[ratios.index.str.contains('electricity distribution grid')]

    ratio_phs = ratios.loc[ratios.index.str.contains('PHS')]
    ratio_hydro = ratios.loc[ratios.index.str.contains('hydro')]
    ratio_battery = ratios.loc[ratios.index.str.contains('battery')]

    for year in ratio_invest.index:
        ratio_invest.loc[year, 'Solar'] = ratio_solar.loc['solar', str(year)]
        ratio_invest.loc[year, 'ROR'] = ratio_ror.loc['ror', str(year)]
        ratio_invest.loc[year, 'Wind (Onshore)'] = ratio_wind.loc['onwind', str(year)]
        ratio_invest.loc[year, 'Wind (Offshore)'] = ratio_wind.loc['offwind-ac', str(year)]+ratio_wind.loc['offwind-dc', str(year)]

        ratio_invest.loc[year, 'AC Lines'] = ratio_AC.loc['AC', str(year)]
        ratio_invest.loc[year, 'DC Lines'] = ratio_DC.loc['DC', str(year)]
        ratio_invest.loc[year, 'Distrib Grid'] = ratio_distrib_grid.loc['electricity distribution grid', str(year)]

        ratio_invest.loc[year, 'PHS'] = ratio_phs.loc['PHS', str(year)]
        ratio_invest.loc[year, 'Hydro'] = ratio_hydro.loc['hydro', str(year)]
        ratio_invest.loc[year, 'Battery'] = ratio_battery.loc['battery', str(year)] 

    # print(ratio_invest.T)
    ratio_invest.T.to_csv(current_script_dir+'\\outputs\\ratios_EUR_MW.csv')


get_data_investments()
get_data_ratios()

