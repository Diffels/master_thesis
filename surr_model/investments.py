"""
Grid Investments related variables implementation within MEDEAS.

Wrote by Noe Diffels
November 2024

This file defines all variables linked to the new grid invstments definition and the PID control of both surrogate model targets (curtailment & load shedding).  
"""

import pandas as pd 
import os
from models.europe.modules_pymedeas_eu.surr_model.PID import PID
file_directory = os.path.dirname(os.path.abspath(__file__))

# Import the dataframes
df_tech_shares_ls = pd.read_csv(file_directory+r"\modules_pymedeas_eu\surr_model\pypsa\capa and invest\interp_tech_shares_ls.csv", index_col='Year') 
df_tech_shares_curt = pd.read_csv(file_directory+r"\modules_pymedeas_eu\surr_model\pypsa\capa and invest\interp_tech_shares_curt.csv", index_col='Year') 

df_prices_1995USD_W = pd.read_csv(r"C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\pymedeas2_models\interp_prices_1995USD_W.csv", index_col="Year") 
df_ratios_rNTC_TW = pd.read_csv(file_directory+r"\modules_pymedeas_eu\surr_model\pypsa\rNTC\ratio_rNTC_TW.csv", index_col='Year') 
df_rNTC = pd.read_csv(file_directory+r"\modules_pymedeas_eu\surr_model\pypsa\rNTC\interp_rNTC.csv", index_col="Year")
# df_exchange_rates =  pd.read_csv(file_directory+r"\modules_pymedeas_eu\surr_model\pypsa\capa and invest\usd_conversion\output\exchange_rates.csv", index_col="Year")

@component.add(
    name="Grid Investments - Load Shedding control",
    units="T$",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time": 1, 
                "load_shedding_delayed": 1},
)
def new_investments_grid_ls():
    """
    New investments required by control feedback, for load shedding.
    """

    if time() == 1995:
        time_prev = 0
    else:
        time_prev = time()-0.03125
    return PID(0, 0, 0, time(), time_prev, 0, load_shedding_delayed()) # previously (P=1e-16)


@component.add(
    name="Cumulated Grid Investments - Load shedding control",
    units="T$",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_cumulated_new_investments_grid_ls": 1},
    other_deps={
        "_integ_cumulated_new_investments_grid_ls": {
            "initial": {},
            "step": {"new_investments_grid_ls": 1},
        }
    },
)
def cumulated_new_investments_grid_ls():
    """
    Cumulated grid investment computed with PID control, for load shedding.
    """
    return _integ_cumulated_new_investments_grid_ls()
_integ_cumulated_new_investments_grid_ls = Integ(
    lambda: new_investments_grid_ls(),
    lambda: 0,
    "_integ_cumulated_new_investments_grid_ls",
)


@component.add(
    name="Grid Investments - Curtailment control",
    units="T$",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time": 1, 
                "curtailment_delayed": 1},
)
def new_investments_grid_curt():
    """
    New investments required by control feedback, for curtailment.
    """
        
    if time() == 1995:
        time_prev = 0
    else:
        time_prev = time()-0.03125

    return PID(0, 0, 0, time(), time_prev, 0, curtailment_delayed()) # Previously 1 (former res) or 0.01 (new res, no outbounds)
    # BAU il faut mettre 0.35 je pense, à verif

@component.add(
    name="Cumulated Grid Investments - Curtailment control",
    units="T$",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_cumulated_new_investments_grid_curt": 1},
    other_deps={
        "_integ_cumulated_new_investments_grid_curt": {
            "initial": {},
            "step": {"new_investments_grid_curt": 1},
        }
    },
)
def cumulated_new_investments_grid_curt():
    """
    Cumulated grid investment computed with PID control, for curtailment.
    """
    return _integ_cumulated_new_investments_grid_curt()
_integ_cumulated_new_investments_grid_curt = Integ(
    lambda: new_investments_grid_curt(),
    lambda: 0,
    "_integ_cumulated_new_investments_grid_curt",
)


@component.add(
    name="Investment share of new capacities",
    units="Dmnl",
    subscripts=["Capacities"],
    comp_type="Data",
    comp_subtype="Normal",
    depends_on={"time": 1},
)
def investments_shares_ls():
    """
    The investments shares for new capacities installed (RES, Storage, NTC) from all grid investments regarding load shedding.
    If 1000$ are invested, how would they be splitted into these capacities?
    Data derived from PyPSA-EUR model and time-dependent.
    """
    value = xr.DataArray(
           np.nan, {"Capacities": _subscript_dict["Capacities"]}, ["Capacities"]
        )
    values = df_tech_shares_ls.loc[round(time())]
    value.loc[["Solar"]] = values["Solar"]
    value.loc[["ROR"]] = values["ROR"]
    value.loc[["Wind (Onshore)"]] = values["Wind (Onshore)"]
    value.loc[["Wind (Offshore)"]] = values["Wind (Offshore)"]
    value.loc[["AC Lines"]] = values["AC Lines"]
    value.loc[["DC Lines"]] = values["DC Lines"]
    value.loc[["Distrib Grid"]] = values["Distrib Grid"]
    value.loc[["PHS"]] = values["PHS"]
    value.loc[["Hydro"]] = values["Hydro"]
    value.loc[["Battery"]] = values["Battery"]
    return value

@component.add(
    name="Investment share of new capacities",
    units="Dmnl",
    subscripts=["Capacities"],
    comp_type="Data",
    comp_subtype="Normal",
    depends_on={"time": 1},
)
def investments_shares_curt():
    """
    The investments shares for new capacities installed (RES, Storage, NTC) from all grid investments regarding curtailment.
    If 1000$ are invested, how would they be splitted into these capacities?
    Data derived from PyPSA-EUR model and time-dependent.
    """
    value = xr.DataArray(
           np.nan, {"Capacities": _subscript_dict["Capacities"]}, ["Capacities"]
        )
    values = df_tech_shares_curt.loc[round(time())]
    value.loc[["Solar"]] = 0
    value.loc[["ROR"]] = 0
    value.loc[["Wind (Onshore)"]] = 0
    value.loc[["Wind (Offshore)"]] = 0
    value.loc[["AC Lines"]] = values["AC Lines"]
    value.loc[["DC Lines"]] = values["DC Lines"]
    value.loc[["Distrib Grid"]] = values["Distrib Grid"]
    value.loc[["PHS"]] = values["PHS"]
    value.loc[["Hydro"]] = values["Hydro"]
    value.loc[["Battery"]] = values["Battery"]
    return value


@component.add(
                
    name="Additionnal RES installation from Surrogate model feedback control",
    units="TW",
    subscripts=["RES_elec"],
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"cumulated_new_investments_grid_ls": 1, 
                "investments_shares_ls": 1,
                },        
)
def sm_new_capacity_res_elec():
    """
 
    """
    value = xr.DataArray(np.nan, {"RES_elec": _subscript_dict["RES_elec"]}, ["RES_elec"])

    if float(time()) < activation_year_feedback():
        value.loc[["hydro"]] = 0  
        value.loc[["geot_elec"]] = 0
        value.loc[["solid_bioE_elec"]] = 0
        value.loc[["oceanic"]] = 0
        value.loc[["wind_onshore"]] = 0
        value.loc[["wind_offshore"]] = 0
        value.loc[["solar_PV"]] = 0
        value.loc[["CSP"]] = 0

    else:
        ratio_USD_W = df_prices_1995USD_W.loc[round(time())]
        ratio_USD_W = ratio_USD_W.loc[["Solar","ROR","Wind (Onshore)","Wind (Offshore)"]]

        value.loc[["hydro"]] = float(new_investments_grid_ls()) * float(investments_shares_ls().loc["ROR"]) / ratio_USD_W["ROR"]  
        value.loc[["geot_elec"]] = 0
        value.loc[["solid_bioE_elec"]] = 0
        value.loc[["oceanic"]] = 0
        value.loc[["wind_onshore"]] = float(new_investments_grid_ls()) * float(investments_shares_ls().loc["Wind (Onshore)"]) / ratio_USD_W["Wind (Onshore)"]
        value.loc[["wind_offshore"]] = float(new_investments_grid_ls()) * float(investments_shares_ls().loc["Wind (Offshore)"]) / ratio_USD_W["Wind (Offshore)"]
        value.loc[["solar_PV"]] = float(new_investments_grid_ls()) * float(investments_shares_ls().loc["Solar"]) / ratio_USD_W["Solar"]
        value.loc[["CSP"]] = 0
        
    return value

@component.add(
    name="cumulated_solar_PV_feedback",
    units="TW",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_cumulated_solar_PV_feedback": 1},
    other_deps={
        "_integ_cumulated_solar_PV_feedback": {
            "initial": {},
            "step": {"sm_new_capacity_res_elec": 1},
        }
    },
)
def cumulated_solar_PV_feedback():
    """
    Cumulated total RES capacity by the feedback mechanism.
    """
    return _integ_cumulated_solar_PV_feedback()
_integ_cumulated_solar_PV_feedback = Integ(
    lambda: float(sm_new_capacity_res_elec().loc['solar_PV']),
    lambda: 0,
    "_integ_cumulated_solar_PV_feedback",
)

@component.add(
    name="cumulated_wind_offshore_feedback",
    units="TW",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_cumulated_wind_offshore_feedback": 1},
    other_deps={
        "_integ_cumulated_wind_offshore_feedback": {
            "initial": {},
            "step": {"sm_new_capacity_res_elec": 1},
        }
    },
)
def cumulated_wind_offshore_feedback():
    """
    Cumulated total RES capacity by the feedback mechanism.
    """
    return _integ_cumulated_wind_offshore_feedback()
_integ_cumulated_wind_offshore_feedback = Integ(
    lambda: float(sm_new_capacity_res_elec().loc['wind_offshore']),
    lambda: 0,
    "_integ_cumulated_wind_offshore_feedback",
)

@component.add(
    name="cumulated_wind_onshore_feedback",
    units="TW",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_cumulated_wind_onshore_feedback": 1},
    other_deps={
        "_integ_cumulated_wind_onshore_feedback": {
            "initial": {},
            "step": {"sm_new_capacity_res_elec": 1},
        }
    },
)
def cumulated_wind_onshore_feedback():
    """
    Cumulated total RES capacity by the feedback mechanism.
    """
    return _integ_cumulated_wind_onshore_feedback()
_integ_cumulated_wind_onshore_feedback = Integ(
    lambda: float(sm_new_capacity_res_elec().loc['wind_onshore']),
    lambda: 0,
    "_integ_cumulated_wind_onshore_feedback",
)

@component.add(
    name="cumulated_hydro_feedback",
    units="TW",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_cumulated_hydro_feedback": 1},
    other_deps={
        "_integ_cumulated_hydro_feedback": {
            "initial": {},
            "step": {"sm_new_capacity_res_elec": 1},
        }
    },
)
def cumulated_hydro_feedback():
    """
    Cumulated total RES capacity by the feedback mechanism.
    """
    return _integ_cumulated_hydro_feedback()
_integ_cumulated_hydro_feedback = Integ(
    lambda: float(sm_new_capacity_res_elec().loc['hydro']),
    lambda: 0,
    "_integ_cumulated_hydro_feedback",
)

@component.add(                
    name="Cumulated RES capacity feedback",
    units="TW",
    subscripts=["RES_elec"],
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"cumulated_hydro_feedback": 1,
                "cumulated_wind_onshore_feedback": 1,
                "cumulated_wind_offshore_feedback": 1,
                "cumulated_solar_PV_feedback": 1,               
                },        
)
def cumulated_capacity_res_elec():

    value = xr.DataArray(np.nan, {"RES_elec": _subscript_dict["RES_elec"]}, ["RES_elec"])
    value.loc[["hydro"]] = float(cumulated_hydro_feedback()) 
    value.loc[["geot_elec"]] = 0
    value.loc[["solid_bioE_elec"]] = 0
    value.loc[["oceanic"]] = 0
    value.loc[["wind_onshore"]] = float(cumulated_wind_onshore_feedback())
    value.loc[["wind_offshore"]] = float(cumulated_wind_onshore_feedback())
    value.loc[["solar_PV"]] = float(cumulated_solar_PV_feedback()) 
    value.loc[["CSP"]] = 0
    return value


@component.add(
    name="Additional Storage capacity installation from Surrogate model feedback control",
    units="TW",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"cumulated_new_investments_grid_ls": 1, 
                "investments_shares_ls": 1, 
               },        
)
def sm_new_capacity_storage():
    """
    Additional Storage capacity that came from new grid investments and PID feedback control, considering ratios [$/TW] and investment shares.
    We do not take into account the curtailment PID feedback due to an implementation error found in previous works of the surrogate model. 
    Please read master's thesis Section 2.3.5 for further information. 
    """
    if float(time()) < activation_year_feedback():
        return 0
    
    else:
        ratio_USD_W = df_prices_1995USD_W.loc[round(time())]
        ratio_USD_W = ratio_USD_W.loc[["PHS","Hydro","Battery"]]
        
        return float(new_investments_grid_ls())*(float(investments_shares_ls().loc["PHS"])/ratio_USD_W["PHS"]+float(investments_shares_ls().loc["Hydro"])/ratio_USD_W["Hydro"]+float(investments_shares_ls().loc["Battery"])/ratio_USD_W["Battery"]) + float(new_investments_grid_curt())*(float(investments_shares_curt().loc["PHS"])/ratio_USD_W["PHS"]+float(investments_shares_curt().loc["Hydro"])/ratio_USD_W["Hydro"]+float(investments_shares_curt().loc["Battery"])/ratio_USD_W["Battery"])

@component.add(
    name="cumulated_storage_feedback",
    units="TW",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_cumulated_storage_feedback": 1},
    other_deps={
        "_integ_cumulated_storage_feedback": {
            "initial": {},
            "step": {"sm_new_capacity_storage": 1},
        }
    },
)
def cumulated_storage_feedback():
    """
    Cumulated total storage capacity added by the feedback mechanism.
    """
    return _integ_cumulated_storage_feedback()
_integ_cumulated_storage_feedback = Integ(
    lambda: float(sm_new_capacity_storage()),
    lambda: 0,
    "_integ_cumulated_storage_feedback",
)


@component.add(
    name="Additional NTC Capacity from Surrogate model feedback control",
    units="TW",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"cumulated_new_investments_grid_ls": 1,
                "cumulated_new_investments_grid_curt": 1, 
                "investments_shares_ls": 3, 
                },
)
def sm_new_capacity_ntc():
    """
    Additional NTC capacity that came from new grid investments and PID feedback control, considering ratios [$/TW] and investment shares.
    Both curtailment and load shedding feedback loops are taken into account. 
    """
    if float(time()) < activation_year_feedback():
        # return 0
        ratio_USD_W = df_prices_1995USD_W.loc[round(time())]
        ratio_USD_W = ratio_USD_W.loc[["AC Lines","DC Lines","Distrib Grid"]]
    else:
        ratio_USD_W = df_prices_1995USD_W.loc[round(time())]
        ratio_USD_W = ratio_USD_W.loc[["AC Lines","DC Lines","Distrib Grid"]]

    return float(new_investments_grid_ls())*(float(investments_shares_ls().loc["AC Lines"])/ratio_USD_W["AC Lines"]+float(investments_shares_ls().loc["DC Lines"])/ratio_USD_W["DC Lines"]+float(investments_shares_ls().loc["Distrib Grid"])/ratio_USD_W["Distrib Grid"])  + float(new_investments_grid_curt())*(float(investments_shares_curt().loc["AC Lines"])/ratio_USD_W["AC Lines"]+float(investments_shares_curt().loc["DC Lines"])/ratio_USD_W["DC Lines"]+float(investments_shares_curt().loc["Distrib Grid"])/ratio_USD_W["Distrib Grid"])

@component.add(
    name="cumulated_ntc_feedback",
    units="TW",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_cumulated_ntc_feedback": 1},
    other_deps={
        "_integ_cumulated_ntc_feedback": {
            "initial": {},
            "step": {"sm_new_capacity_ntc": 1},
        }
    },
)
def cumulated_ntc_feedback():
    """
    Cumulated total lines capacity added by the feedback mechanism.
    """
    return _integ_cumulated_ntc_feedback()
_integ_cumulated_ntc_feedback = Integ(
    lambda: float(sm_new_capacity_ntc()),
    lambda: 0,
    "_integ_cumulated_ntc_feedback",
)


# feedback-related investments
@component.add(
    name="Total of the investements grid controlled by PID",
    units="T$",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"new_investments_grid_curt": 1,
                "new_investments_grid_ls": 1},        
)
def tot_investments_grid_feedback():
    return cumulated_new_investments_grid_curt() + cumulated_new_investments_grid_ls()

# RES-related investments
@component.add(
    name="Total of the investments in new RES capacity, by type.",
    units="T$",
    comp_type="Auxiliary",
    subscripts=["RES_elec"],
    comp_subtype="Normal",
    depends_on={"res_elec_capacity_under_construction_tw": 8,
                "invest_cost_res_elec": 4},        
)
def annualized_investments_res_by_type():
    # return installed_capacity_res_elec() * invest_cost_res_elec()
    value = xr.DataArray(np.nan, {"RES_elec": _subscript_dict["RES_elec"]}, ["RES_elec"])

            
    value.loc[["geot_elec"]] = float(res_elec_capacity_under_construction_tw().loc["geot_elec"]) * float(invest_cost_res_elec().loc["geot_elec"])/30
    value.loc[["solid_bioE_elec"]] = float(res_elec_capacity_under_construction_tw().loc["solid_bioE_elec"]) * float(invest_cost_res_elec().loc["solid_bioE_elec"])/30
    value.loc[["oceanic"]] = float(res_elec_capacity_under_construction_tw().loc["oceanic"]) * float(invest_cost_res_elec().loc["oceanic"])/30
    value.loc[["CSP"]] = float(res_elec_capacity_under_construction_tw().loc["CSP"]) * float(invest_cost_res_elec().loc["CSP"])/25

    # MEDEAS Annualized prices
    if float(time()) < activation_year_feedback():
        value.loc[["hydro"]] = float(res_elec_capacity_under_construction_tw().loc["hydro"]) * float(invest_cost_res_elec().loc["hydro"])/80
        value.loc[["wind_onshore"]] = float(res_elec_capacity_under_construction_tw().loc["wind_onshore"]) * float(invest_cost_res_elec().loc["wind_onshore"])/20
        value.loc[["wind_offshore"]] = float(res_elec_capacity_under_construction_tw().loc["wind_offshore"]) * float(invest_cost_res_elec().loc["wind_offshore"])/20
        value.loc[["solar_PV"]] = float(res_elec_capacity_under_construction_tw().loc["solar_PV"]) * float(invest_cost_res_elec().loc["solar_PV"])/25

    # PyPSA-EUR Annualized prices
    else: 
        ratio_USD_W = df_prices_1995USD_W.loc[round(time())]
        ratio_USD_W = ratio_USD_W.loc[["Solar","ROR","Wind (Onshore)","Wind (Offshore)"]]

        value.loc[["hydro"]] = float(res_elec_capacity_under_construction_tw().loc["hydro"]) * ratio_USD_W["ROR"]
        value.loc[["wind_onshore"]] = float(res_elec_capacity_under_construction_tw().loc["wind_onshore"]) * ratio_USD_W["Wind (Onshore)"]
        value.loc[["wind_offshore"]] = float(res_elec_capacity_under_construction_tw().loc["wind_offshore"]) * ratio_USD_W["Wind (Offshore)"]
        value.loc[["solar_PV"]] = float(res_elec_capacity_under_construction_tw().loc["solar_PV"]) * ratio_USD_W["Solar"]

    # To avoid negative investments while RES decreasing (FFF scenarios), set at 0:
    value = value.clip(min=0)

    return value

# @component.add(
#     name="MEDEAS Annualized Investments (for comparison purposes)",
#     units="T$",
#     comp_type="Auxiliary",
#     subscripts=["RES_elec"],
#     comp_subtype="Normal",
#     depends_on={"res_elec_capacity_under_construction_tw": 8,
#                 "invest_cost_res_elec": 4},        
# )
# def MEDEAS_annualized_investments_res_by_type():
#     # return installed_capacity_res_elec() * invest_cost_res_elec()
#     value = xr.DataArray(np.nan, {"RES_elec": _subscript_dict["RES_elec"]}, ["RES_elec"])

            
#     value.loc[["geot_elec"]] = float(res_elec_capacity_under_construction_tw().loc["geot_elec"]) * float(invest_cost_res_elec().loc["geot_elec"])/30
#     value.loc[["solid_bioE_elec"]] = float(res_elec_capacity_under_construction_tw().loc["solid_bioE_elec"]) * float(invest_cost_res_elec().loc["solid_bioE_elec"])/30
#     value.loc[["oceanic"]] = float(res_elec_capacity_under_construction_tw().loc["oceanic"]) * float(invest_cost_res_elec().loc["oceanic"])/30
#     value.loc[["CSP"]] = float(res_elec_capacity_under_construction_tw().loc["CSP"]) * float(invest_cost_res_elec().loc["CSP"])/25
#     value.loc[["hydro"]] = float(res_elec_capacity_under_construction_tw().loc["hydro"]) * float(invest_cost_res_elec().loc["hydro"])/80
#     value.loc[["wind_onshore"]] = float(res_elec_capacity_under_construction_tw().loc["wind_onshore"]) * float(invest_cost_res_elec().loc["wind_onshore"])/20
#     value.loc[["wind_offshore"]] = float(res_elec_capacity_under_construction_tw().loc["wind_offshore"]) * float(invest_cost_res_elec().loc["wind_offshore"])/20
#     value.loc[["solar_PV"]] = float(res_elec_capacity_under_construction_tw().loc["solar_PV"]) * float(invest_cost_res_elec().loc["solar_PV"])/25

#     return value


# RES-related investments
@component.add(
    name="Total of the investments in new RES capacity, by type.",
    units="T$",
    comp_type="Auxiliary",
    subscripts=["RES_elec"],
    comp_subtype="Normal",
    depends_on={"res_elec_capacity_under_construction_tw": 8,
                "invest_cost_res_elec": 4},        
)
def investments_res_by_type():
    # return installed_capacity_res_elec() * invest_cost_res_elec()
    value = xr.DataArray(np.nan, {"RES_elec": _subscript_dict["RES_elec"]}, ["RES_elec"])

            
    value.loc[["geot_elec"]] = float(res_elec_capacity_under_construction_tw().loc["geot_elec"]) * float(invest_cost_res_elec().loc["geot_elec"])
    value.loc[["solid_bioE_elec"]] = float(res_elec_capacity_under_construction_tw().loc["solid_bioE_elec"]) * float(invest_cost_res_elec().loc["solid_bioE_elec"])
    value.loc[["oceanic"]] = float(res_elec_capacity_under_construction_tw().loc["oceanic"]) * float(invest_cost_res_elec().loc["oceanic"])
    value.loc[["CSP"]] = float(res_elec_capacity_under_construction_tw().loc["CSP"]) * float(invest_cost_res_elec().loc["CSP"])

    # MEDEAS prices
    if float(time()) < activation_year_feedback():
        value.loc[["hydro"]] = float(res_elec_capacity_under_construction_tw().loc["hydro"]) * float(invest_cost_res_elec().loc["hydro"])
        value.loc[["wind_onshore"]] = float(res_elec_capacity_under_construction_tw().loc["wind_onshore"]) * float(invest_cost_res_elec().loc["wind_onshore"])
        value.loc[["wind_offshore"]] = float(res_elec_capacity_under_construction_tw().loc["wind_offshore"]) * float(invest_cost_res_elec().loc["wind_offshore"])
        value.loc[["solar_PV"]] = float(res_elec_capacity_under_construction_tw().loc["solar_PV"]) * float(invest_cost_res_elec().loc["solar_PV"])

    # PyPSA-EUR prices
    else: 
        ratio_USD_W = df_prices_1995USD_W.loc[round(time())]
        ratio_USD_W = ratio_USD_W.loc[["Solar","ROR","Wind (Onshore)","Wind (Offshore)"]]

        value.loc[["hydro"]] = float(res_elec_capacity_under_construction_tw().loc["hydro"]) * ratio_USD_W["ROR"] * 80
        value.loc[["wind_onshore"]] = float(res_elec_capacity_under_construction_tw().loc["wind_onshore"]) * ratio_USD_W["Wind (Onshore)"] * 27
        value.loc[["wind_offshore"]] = float(res_elec_capacity_under_construction_tw().loc["wind_offshore"]) * ratio_USD_W["Wind (Offshore)"] * 27
        value.loc[["solar_PV"]] = float(res_elec_capacity_under_construction_tw().loc["solar_PV"]) * ratio_USD_W["Solar"] * 35

    # To avoid negative investments while RES decreasing (FFF scenarios), set at 0:
    value = value.clip(min=0)

    return value

@component.add(
    name="Total of the investements in new RES capacity",
    units="T$",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"investments_res_by_type": 1},        
)
def tot_investments_res():
    return sum(investments_res_by_type().rename({"RES_elec": "RES_elec!"}), dim=["RES_elec!"])


@component.add(
    name="Total of the annualized investements in new RES capacity",
    units="T$",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"annualized_investments_res_by_type": 1},        
)
def annualized_investments_res():
    return sum(annualized_investments_res_by_type().rename({"RES_elec": "RES_elec!"}), dim=["RES_elec!"])


# Storage-related investments
@component.add(
    name="Total of the investements in new Storage capacity",
    units="T$",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"total_capacity_elec_storage_tw": 1,
                "sm_new_capacity_storage": 1},        
)
def tot_investments_storage():
    if float(time()) < activation_year_feedback():
        return 0
    else:
        ratio_USD_W = df_prices_1995USD_W.loc[round(time())] # Year,Solar,ROR,Wind (Onshore),Wind (Offshore),AC Lines,DC Lines,Distrib Grid,PHS,Hydro,Battery
        ratio_USD_W = ratio_USD_W.loc[["PHS","Hydro","Battery"]]
        ratio_USD_W["PHS"] = ratio_USD_W["PHS"]*80
        ratio_USD_W["Hydro"] = ratio_USD_W["Hydro"]*80
        ratio_USD_W["Battery"] = ratio_USD_W["Battery"]*15
        tot_invest = (float(new_storage_installed_capacity())) * ratio_USD_W.mean()
        if tot_invest < 0:
            return 0
        else:
            return tot_invest

@component.add(
    name="new_storage_installed_capacity",
    units="TW/year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time": 1,
        "total_capacity_elec_storage_tw": 1,
        "total_capacity_elec_storage_tw_delayed": 1,
        "time_step": 1,
        "table_hist_capacity_phs":1,
    },
)
def new_storage_installed_capacity():
    return (
        if_then_else(
            time() > 1995,
            lambda: total_capacity_elec_storage_tw() - total_capacity_elec_storage_tw_delayed(),
            lambda: table_hist_capacity_phs(1995),
        )
        / time_step()
    )

@component.add(
    name="Installed_capacity_storage_elec_delayed",
    units="TW",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_installed_capacity_storage_elec_delayed": 1},
    other_deps={
        "_delayfixed_installed_capacity_storage_elec_delayed": {
            "initial": {"table_hist_capacity_phs": 1, "time_step": 1},
            "step": {"total_capacity_elec_storage_tw": 1},
        }
    },
)
def total_capacity_elec_storage_tw_delayed():
    return _delayfixed_installed_capacity_storage_elec_delayed()
_delayfixed_installed_capacity_storage_elec_delayed = DelayFixed(
    lambda: total_capacity_elec_storage_tw(),
    lambda: time_step(),
    lambda: table_hist_capacity_phs(1995),
    time_step,
    "_delayfixed_installed_capacity_storage_elec_delayed",
)


# Grid-related investments
@component.add(
    name="Total of the investements in new Grid (NTC) capacity",
    units="T$",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"rNTC": 1,
                "sm_new_capacity_ntc": 1,
                "exchange_rates_USD_EUR": 1},        
)
def tot_investments_ntc():
    df = df_rNTC["Investments [1995-USD]"]/1e12
    base_load_TUSD = df.loc[round(time())]

    if float(time()) < activation_year_feedback():
        ratio_USD_W = df_prices_1995USD_W.loc[round(time())]
        ratio_USD_W = ratio_USD_W.loc[["AC Lines","DC Lines","Distrib Grid"]] * 40
        add_feedback_TUSD = float(sm_new_capacity_ntc()) * ratio_USD_W.mean()
    else:
        ratio_USD_W = df_prices_1995USD_W.loc[round(time())]
        ratio_USD_W = ratio_USD_W.loc[["AC Lines","DC Lines","Distrib Grid"]] * 40
        add_feedback_TUSD = float(sm_new_capacity_ntc()) * ratio_USD_W.mean()

    tot_investments = base_load_TUSD + add_feedback_TUSD
    return tot_investments


# Total investments RES - Storage - Grid
@component.add(
    name="Total of the investements (RES, Storage, NTC)",
    units="$",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"tot_investments_res": 1,
                "tot_investments_storage": 1,
                "tot_investments_ntc": 1},        
)
def TOT_investments():
    return float(tot_investments_res())  + float(tot_investments_storage()) + float(tot_investments_ntc())


# Total investments RES - Storage - Grid
@component.add(
    name="Activation year for the society reaction mechanism",
    units="Year",
    comp_type="Constant",
    comp_subtype="Normal",
    depends_on={},        
)
def activation_year_feedback():
    return 2020