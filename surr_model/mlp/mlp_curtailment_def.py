'''
ML model definition for curtailment.
 
Derived from Romain Cloux's jupyter notebook, avialble at:
https://github.com/PtitVerredeRhum/Master_Thesis_Cloux
File: nn/Cloux_folder/ML_Curtailment_CLX.ipynb
'''

# Packages import
import joblib
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import KFold, GridSearchCV
import numpy as np

import pandas as pd
import time

import os
file_directory = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(file_directory, 'dataset.csv'))
df_filtered = df[df['GAMS_error'] != 2]

# ML-Dataset definition: Atributes X (features); labels y (target)
Dataset = df_filtered[['CapacityRatio', 'ShareFlex', 'ShareStorage', 'ShareWind', 'SharePV','rNTC','Curtailment_[TWh]', 'Shedding_[MWh]', 'CurtailmentToRESGeneration_[%]']]
y_curtail = Dataset['CurtailmentToRESGeneration_[%]']
X = Dataset[['CapacityRatio', 'ShareFlex', 'ShareStorage', 'ShareWind', 'SharePV','rNTC']]

X_train, X_test, y_train, y_test = train_test_split(X, y_curtail, test_size=0.3,random_state=42)

scaler_X = MinMaxScaler()
X_train_sc = scaler_X.fit_transform(X_train)
X_test_sc = scaler_X.transform(X_test)

scaler_y = MinMaxScaler()
y_train_scaled = scaler_y.fit_transform(y_train.values.reshape(-1, 1)).ravel()
y_test_scaled = scaler_y.transform(y_test.values.reshape(-1, 1)).ravel()

num_folds = 10
error_metrics = {'neg_mean_absolute_error','neg_root_mean_squared_error'}
models = {('MLP', MLPRegressor()),('RFR', RandomForestRegressor())}
my_cv = KFold(n_splits=10, shuffle=True, random_state=42)

# ------------------------------------------------------------------------------------- Run the Multi Layer Perceptron
print("Creation of the MLP model...")
start_time = time.time()
modelo = MLPRegressor(max_iter=50, random_state=42)
scoring='neg_mean_absolute_error' #TODO What is that?
param_grid_mlp = {
    'hidden_layer_sizes': [(100,50)],           
    'activation': ['relu'],
    'solver': ['adam'],
    'alpha': [0.0001],
    'learning_rate': ['constant']
}
# Search for the best combination of hyperparameters
grid_search_mlp = GridSearchCV(estimator=modelo, param_grid=param_grid_mlp, scoring=scoring, cv=my_cv, n_jobs=-1)
grid_search_mlp.fit(X_train_sc, y_train_scaled)
end_time = time.time()
elapsed_time = end_time - start_time

print(f"Model created in {elapsed_time:.2f} seconds.")

best_mlp = grid_search_mlp.best_estimator_
# Print best Result
print("Best result: %f using the following hyperparameters %s" % (grid_search_mlp.best_score_, grid_search_mlp.best_params_))
# means = grid_search_mlp.cv_results_['mean_test_score']
# stds = grid_search_mlp.cv_results_['std_test_score']
# params = grid_search_mlp.cv_results_['params']

# Save the model
filename=r'\mlp_curtailment.pkl'
joblib.dump(best_mlp, file_directory+filename)
print(f"Model saved at {file_directory+filename}.")

joblib.dump(scaler_X, file_directory+'_scaler_X_curt.pkl')
joblib.dump(scaler_y, file_directory+'_scaler_y_curt.pkl')



# # ------------------------------------------------------------------------------------- Run the Random Forest
# print("Creation of the RF model...")
# modelo = RandomForestRegressor(random_state=42)
# scoring='neg_mean_absolute_error'
# params = {
#     # Number of trees in random forest
#     'n_estimators': [500],  # default=100
#      # Maximum number of levels in tree
#     'max_depth': [None],  #deafult = None
#      # The minimum number of samples required to split an internal node
#     'min_samples_split': [2],
#     # The minimum number of samples required to be at a leaf node
#     'min_samples_leaf' : [1],
#     # The number of features to consider when looking for the best split
#     'max_features' : [None],
#     # Whether bootstrap samples are used when building trees
#     'bootstrap' : [True]
# }


# # Search for the best combination of hyperparameters
# grid_search_rf = GridSearchCV(estimator=modelo, param_grid=params, scoring=scoring, cv=my_cv, n_jobs=-1)

# start_time = time.time()

# grid_search_rf.fit(X_train_sc, y_train_scaled)

# end_time = time.time()
# elapsed_time = end_time - start_time

# print(f"Temps d'exécution : {elapsed_time:.4f} secondes")

# best_rf = grid_search_rf.best_estimator_

# # Print best Result
# print("Best result: %f using the following hyperparameters %s" % (grid_search_rf.best_score_, grid_search_rf.best_params_))
# # means = grid_search_rf.cv_results_['mean_test_score']
# # stds = grid_search_rf.cv_results_['std_test_score']
# # params = grid_search_rf.cv_results_['params']

# # Save the model
# filename=r'\rf_curtailment.pkl'
# joblib.dump(best_rf, file_directory+filename)
# print(f"Model saved at {file_directory+filename}.")



# years = np.arange(1995, 2050)

# var = "sto"
# features = []
# bounds = [(0.4, 1.3), (0.25, 0.9), (0, 3), (0, 0.55*1.8), (0, 0.35*1.8), (0, 0.75)]  # Modify here to select values for constant features

# # Populate features with mean of bounds
# for element in bounds:
#     features.append(np.mean(element))

# features[2] = 0  # For ShareStorage, set it to 0 initially
# features = [features]

# # Create a DataFrame to store the features with appropriate names
# features_df = pd.DataFrame(
#     features,
#     columns=['CapacityRatio', 'ShareFlex', 'ShareStorage', 'ShareWind', 'SharePV', 'rNTC']
# )

# print("Initial feature values:")
# print(features_df)

# # Initialize target lists
# target_MLP = []
# share_sto = []

# # Loop through years and predict values
# for i in range(len(years)):
#     share_sto.append(features_df.loc[0, 'ShareStorage'])  # Append current ShareStorage value
    
#     # Scale features
#     features_scaled = scaler_X.transform(features_df)
    
#     # Make prediction using MLP model
#     MLP_output_scaled = best_mlp.predict(features_scaled)[0]  # Assuming 1 output for each prediction
#     MLP_output = scaler_y.inverse_transform(MLP_output_scaled.reshape(-1, 1)).flatten()  # Inverse transform to get original scale
    
#     target_MLP.append(MLP_output)
    
#     # Update ShareStorage feature for next iteration
#     features_df.loc[0, 'ShareStorage'] = features_df.loc[0, 'ShareStorage'] + 0.05  # Increment ShareStorage

# # Plot the feature evolution over years
# cap_ratio = [features_df.loc[0, 'CapacityRatio']] * len(years)
# share_flex = [features_df.loc[0, 'ShareFlex']] * len(years)
# share_wind = [features_df.loc[0, 'ShareWind']] * len(years)
# share_pv = [features_df.loc[0, 'SharePV']] * len(years)
# rNTC = [features_df.loc[0, 'rNTC']] * len(years)

# # First plot: Feature values over years
# plt.figure(figsize=(10, 6))
# plt.plot(years, cap_ratio, label='Capacity Ratio', color='tab:red')
# plt.plot(years, share_flex, label='Share Flex', color='tab:blue')
# plt.plot(years, share_sto, label='Share Storage', color='tab:purple')
# plt.plot(years, share_wind, label='Share Wind', color='tab:orange')
# plt.plot(years, share_pv, label='Share PV', color='tab:green')
# plt.plot(years, rNTC, label='rNTC', color='teal')
# plt.legend()
# plt.xlabel('Years [-]', fontsize=14)
# plt.ylabel('Dimensionless [-]', fontsize=14)
# plt.tick_params(axis='both', which='major', labelsize=12)
# plt.grid(True)
# plt.show()

# plt.close()  # Close plot for the next one
# plt.figure(figsize=(10, 6))

# # Plot the MLP target over the years
# plt.plot(years, target_MLP, label='Curtailment - MLP', color='gold')
# plt.legend()
# plt.xlabel('Years [-]', fontsize=14)
# plt.ylabel('Curtailment [%]', fontsize=14)
# plt.tick_params(axis='both', which='major', labelsize=12)
# plt.grid(True)
# plt.show()


# Surface plot

# x1_values = np.linspace(0, 1, 15) 
# x2_values = np.linspace(0, 1, 15)  
# x1_mesh, x2_mesh = np.meshgrid(x1_values, x2_values)


# x1 = np.linspace(0.3, 1.3, 15) 
# x2 = np.linspace(0.25, 1.0, 15)  
# x3 = np.linspace(0, 3.00, 15)  
# x4 = np.linspace(0, 0.55, 15)  
# x5 = np.linspace(0, 0.35, 15)  
# x6 = np.linspace(0, 0.75, 15)  


# valeurs_scaled = scaler_X.transform(np.array([1.16, 0.42, 0.001, 0.2, 0.05, 0.28]).reshape(1, -1))
# print("Valeurs scaled:", valeurs_scaled)

# static_values = np.full(225, 0.5)  
# CR_static = np.full(225, valeurs_scaled[0, 0])
# flex_static = np.full(225, valeurs_scaled[0, 1])
# sto_static = np.full(225, valeurs_scaled[0, 2])
# wind_static = np.full(225, valeurs_scaled[0, 3])
# PV_static = np.full(225, valeurs_scaled[0, 4])
# NTC_static = np.full(225, valeurs_scaled[0, 5])

# # sto wind
# input_data_df = pd.DataFrame(
#     np.column_stack((CR_static, flex_static, x1_mesh.flatten(), x2_mesh.flatten(), PV_static, NTC_static)),
#     columns=['CapacityRatio', 'ShareFlex', 'ShareStorage', 'ShareWind', 'SharePV', 'rNTC']
# )

# predictions = best_mlp.predict(input_data_df)
# predictions_mesh = predictions.reshape(x1_mesh.shape)

# predictions_original = predictions.reshape(x1_mesh.shape)
# predictions_original = scaler_y.inverse_transform(predictions.reshape(-1, 1)).reshape(x1_mesh.shape)

# fig = plt.figure(figsize=(10, 8))
# A, B = np.meshgrid(x3, x4)
# ax1 = fig.add_subplot(111, projection='3d')
# surf = ax1.plot_surface(A, B, predictions_original, cmap='viridis', edgecolor='none')
# ax1.set_xlabel('Share storage [.]', fontsize=14)
# ax1.set_ylabel('Share wind [.]',fontsize=14)
# ax1.set_zlabel('Curtailment [%]',fontsize=14)
# fig.colorbar(surf, ax=ax1, shrink=0.5, aspect=5)
# plt.show()