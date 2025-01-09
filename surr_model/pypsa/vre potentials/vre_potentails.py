#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  3 10:33:56 2024

@author: umair
"""

import pypsa
import numpy as np

"""
Atlite Calculates for each network node the,
(1) installable capacity (based on land-use)
(2) the available generation time series (based on weather data)
(3) Atlite computes how much of the technology can be installed at each
cutout grid cell and each node using the `atlite
<https://github.com/pypsa/atlite>`_ library. This uses the CORINE land use data,
LUISA land use data, Natura2000 nature reserves, GEBCO bathymetry data, and
shipping lanes.
(4) To compute the layout of generators in each node's Voronoi cell, the installable
potential in each grid cell is multiplied with the capacity factor at each grid
cell.
(5) The maximal installable potential for the node (`p_nom_max`) is computed by
adding up the installable potentials of the individual grid cells. If the model
comes close to this limit, then the time series may slightly overestimate
production since it is assumed the geographical distribution is proportional to
capacity factor.
"""

n=pypsa.Network(r"C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\TFE\master-thesis_DIFFELS\Umair\rNTC\Code_data 1\Code_data\elec_s_32_lvopt_EQ0.70c_1H-T-H-B-I-A-dist1_2030.nc")

def max_vre_potentials(n):
    
    df_pv = n.generators.p_nom_max.filter(like="solar")
    df_pv = df_pv[~df_pv.isin([np.inf, -np.inf])]
    solar_pv = df_pv.sum()/1e3

    df_offshore = n.generators.p_nom_max.filter(like="offwind")
    df_offshore = df_offshore[~df_offshore.isin([np.inf, -np.inf])]
    offshore = df_offshore.sum()/1e3

    df_onwind = n.generators.p_nom_max.filter(like="onwind")
    df_onwind= df_onwind[~df_onwind.isin([np.inf, -np.inf])]
    onwind = df_onwind.sum()/1e3
    
    
    return solar_pv, offshore, onwind

solar_pv, offshore, onwind = max_vre_potentials(n)
    
# Digits expressed in GW
print(solar_pv)
print(offshore)
print(onwind)