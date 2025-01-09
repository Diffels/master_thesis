"""
Targets implementation within MEDEAS.

Wrote by Noe Diffels
October 2024

This file defines the targets computed by the surrogate model and associated features, such as delayed_features, used in the PID control.
"""

import joblib
import os
import pandas as pd

file_directory = os.path.dirname(os.path.abspath(__file__)) # contains ..\models\europe, don't know why it stops at europe.
# Import the MLP models:
curt_model = joblib.load(file_directory+r'\modules_pymedeas_eu\surr_model\mlp\mlp_curtailment.pkl')
loadshed_model = joblib.load(file_directory+r'\modules_pymedeas_eu\surr_model\mlp\mlp_loadshedding_oversamp.pkl')

# Import the RF models:
RF_curt_model = joblib.load(file_directory+r'\modules_pymedeas_eu\surr_model\mlp\RF_curtailment.pkl')
RF_loadshed_model = joblib.load(file_directory+r'\modules_pymedeas_eu\surr_model\mlp\RF_loadshedding.pkl')

# Importation of scaling factors: 
scaler_X_curt = joblib.load(r'C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\pymedeas2_models\models\europe\modules_pymedeas_eu\surr_model\mlp\mlp_scaler_X_curt.pkl')
scaler_y_curt = joblib.load(r'C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\pymedeas2_models\models\europe\modules_pymedeas_eu\surr_model\mlp\mlp_scaler_y_curt.pkl')

scaler_X_ls = joblib.load(r'C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\pymedeas2_models\models\europe\modules_pymedeas_eu\surr_model\mlp\mlp_scaler_X_ls.pkl')
scaler_y_ls = joblib.load(r'C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\pymedeas2_models\models\europe\modules_pymedeas_eu\surr_model\mlp\mlp_scaler_y_ls.pkl')

@component.add(
    name="Curtailment",
    units="Dmnl",
    comp_type="Constant",
    depends_on={
        "cap_ratio": 1,
        "share_flex": 1,
        "share_sto":1,
        "share_wind": 1,
        "share_pv": 1,
        "rNTC": 1,
        },
)
def curtailment():
    """
    The curtailment target represents, for a given time step, the ratio between total energy curtailed from VRES and the maximum VRES generation from all units.
    """

    features = [[cap_ratio(), share_flex(), share_sto(), share_wind(), share_pv(), rNTC()]]

    # features_df = pd.DataFrame(
    # features,
    # columns=['CapacityRatio', 'ShareFlex', 'ShareStorage', 'ShareWind', 'SharePV', 'rNTC'])

    features_scaled = scaler_X_curt.transform(features)
    output_scaled = curt_model.predict(features_scaled)[0]
    output = scaler_y_curt.inverse_transform(output_scaled.reshape(-1, 1)).flatten()/100 # %->Dmnl [-]
    # print(output)

    if output < 0:
        #print(f"\nNegative curtailment({output}), set at 0.")
        return 0
    else:
        return float(output)

@component.add(
    name="Curtailment delayed",
    units="Dmnl",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_curtailment": 1},
    other_deps={
        "_delayfixed_curtailment": {
            "initial": {},
            "step": {},
        }
    },
)
def curtailment_delayed():
    """
    The curtailment target but delayed of one time step. The initial value is set to 0. 
    """

    return _delayfixed_curtailment()

_delayfixed_curtailment = DelayFixed(
    lambda: curtailment(),
    lambda: time_step(),
    lambda: 0, # Initial value fixed at 0.
    time_step,
    "_delayfixed_curtailment",
)

@component.add(
    name="Energy Curtailed",
    units="TWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"curtailment": 1,
                "installed_capacity_res_elec": 5,
                "cp_res_elec": 5},
)

def energy_curtailed_twh():
    """
    The energy curtailed is the curtailment expressed in TWh instead of being dimensionless.
    """
    
    cap_installed_pv = float(installed_capacity_res_elec().loc['solar_PV']*cp_res_elec().loc['solar_PV']) # TW
    cap_installed_wind = float(installed_capacity_res_elec().loc['wind_onshore']*cp_res_elec().loc['wind_onshore']) + float(installed_capacity_res_elec().loc['wind_offshore']*cp_res_elec().loc['wind_offshore']) # TW

    # cap_installed_geoth = installed_capacity_res_elec().loc['geot_elec'] * cp_res_elec().loc['geot_elec']# TW
    # cap_installed_biomass = installed_capacity_res_elec().loc['solid_bioE_elec'] * cp_res_elec().loc['solid_bioE_elec']# TW
    # cap_installed_hydro = installed_capacity_res_elec().loc['hydro'] * cp_res_elec().loc['hydro'] # TW
    # cap_installed_oceanic = installed_capacity_res_elec().loc['oceanic'] * cp_res_elec().loc['oceanic']# TW
    # cap_installed_csp = installed_capacity_res_elec().loc['CSP'] * cp_res_elec().loc['CSP'] # TW

    cap_installed_vres = cap_installed_pv + cap_installed_wind
    # cap_installed_vres = cap_installed_vres + cap_installed_hydro + cap_installed_oceanic + cap_installed_csp + cap_installed_geoth + cap_installed_biomass # TW
    
    return curtailment() * 8760 * cap_installed_vres

    
@component.add(
    name="Load Shedding",
    units="Dmnl",
    comp_type="Normal",  
    depends_on={
        "cap_ratio": 1,
        "share_flex": 1,
        "share_sto":1,
        "share_wind": 1,
        "share_pv": 1,
        "rNTC": 1,
        },
)
def load_shedding():
    """
    The load shedding target represents, for a given time step, the ratio between the load that can not be fulfilled (Typically when production is smaller than demand.) and the total demand.
    """

    features = [[cap_ratio(), share_flex(), share_sto(), share_wind(), share_pv(), rNTC()]]
    features_scaled = scaler_X_ls.transform(features)
    output_scaled = loadshed_model.predict(features_scaled)[0]
    output = scaler_y_ls.inverse_transform(output_scaled.reshape(-1, 1)).flatten()/100 # %->Dmnl [-]

    if output < 0:
        #print("\nNegative load shedding, set at 0.")
        return 0
    else:
        return float(output)


@component.add(
    name="Load Shedding delayed",
    units="Dmnl",
    comp_type="Stateful",
    comp_subtype="DelayFixed",
    depends_on={"_delayfixed_load_shedding": 1},
    other_deps={
        "_delayfixed_load_shedding": {
            "initial": {},
            "step": {},
        }
    },
)
def load_shedding_delayed():
    """
    The load shedding target but delayed of one time step. The initial value is set to 0. 
    """

    return _delayfixed_load_shedding()

_delayfixed_load_shedding = DelayFixed(
    lambda: load_shedding(),
    lambda: time_step(),
    lambda: 0, # Initial value fixed at 0.
    time_step,
    "_delayfixed_load_shedding",
)
   
@component.add(
    name="Load Shed (not fulfilled)",
    units="TWh",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"load_shedding": 1,
                "total_fe_elec_demand_twh": 1},
)

def load_shed_twh():
    """
    The load shed is the load shedding expressed in TWh instead of being dimensionless.
    """

    return load_shedding() * total_fe_elec_demand_twh()



@component.add(
    name="RF - Curtailment",
    units="Dmnl",
    comp_type="Constant",
    depends_on={
        "cap_ratio": 1,
        "share_flex": 1,
        "share_sto":1,
        "share_wind": 1,
        "share_pv": 1,
        "rNTC": 1,
        },
)
def RF_curtailment():

    features = [[cap_ratio(), share_flex(), share_sto(), share_wind(), share_pv(), rNTC()]]
    features_scaled = scaler_X_curt.transform(features)
    output_scaled = RF_curt_model.predict(features_scaled)[0]
    output = scaler_y_curt.inverse_transform(output_scaled.reshape(-1, 1)).flatten()/100 # %->Dmnl [-]

    if output < 0:
        #print(f"\nNegative curtailment({output}), set at 0.")
        return 0
    else:
        return float(output)
    
@component.add(
    name="RF - Load Shedding",
    units="Dmnl",
    comp_type="Normal",  
    depends_on={
        "cap_ratio": 1,
        "share_flex": 1,
        "share_sto":1,
        "share_wind": 1,
        "share_pv": 1,
        "rNTC": 1,
        },
)
def RF_load_shedding():
    features = [[cap_ratio(), share_flex(), share_sto(), share_wind(), share_pv(), rNTC()]]
    features_scaled = scaler_X_ls.transform(features)
    output_scaled = RF_loadshed_model.predict(features_scaled)[0]
    output = scaler_y_ls.inverse_transform(output_scaled.reshape(-1, 1)).flatten()/100 # %->Dmnl [-]

    if output < 0:
        #print("\nNegative load shedding, set at 0.")
        return 0
    else:
        return float(output)