'''
ML model definition for load shedding.
 
Derived from Romain Cloux's jupyter notebook, avialble at:
https://github.com/PtitVerredeRhum/Master_Thesis_Cloux
File: nn/Cloux_folder/ML_LoadShedding_CLX.ipynb
'''

# Packages import
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import KFold, GridSearchCV
from sklearn.utils import resample


import pandas as pd
import numpy as np
import time

import os
file_directory = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(file_directory, 'dataset.csv'))
df_filtered = df[df['GAMS_error'] != 2]

# ML-Dataset definition: Atributes X (features); labels y (target)
Dataset = df_filtered[['CapacityRatio', 'ShareFlex', 'ShareStorage', 'ShareWind', 'SharePV','rNTC','Curtailment_[TWh]', 'Shedding_[MWh]', 'Demand_[TWh]']]
y_shed = (100*Dataset['Shedding_[MWh]']/1e6/ Dataset['Demand_[TWh]'])
X = Dataset[['CapacityRatio', 'ShareFlex', 'ShareStorage', 'ShareWind', 'SharePV','rNTC']]

X_train, X_test, y_train, y_test = train_test_split(X, y_shed, test_size=0.3,random_state=42)

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
scoring='neg_root_mean_squared_error' #TODO What is that?

# # ------------------------------------------------------------------------------- Run the Multi Layer Perceptron
# print("Creation of the MLP model...")
# start_time = time.time()
# modelo = MLPRegressor(random_state=42)
# param_grid_mlp = {
#     'hidden_layer_sizes': [(128, 64, 32, 16), (100,50), (100,), (100, 50, 25)],            #[(50,), (100,), (50, 50), (100, 50)],
#     'activation': ['tanh', 'relu'],
#     'solver': ['adam', 'sgd'],
#     'alpha': [0.0001, 0.001, 0.01],
#     'learning_rate': ['constant', 'adaptive']
# }
# # Search for the best combination of hyperparameters
# grid_search_mlp = GridSearchCV(estimator=modelo, param_grid=param_grid_mlp, scoring=scoring, cv=my_cv, n_jobs=-1)
# grid_search_mlp.fit(X_train_sc, y_train_scaled)
# end_time = time.time()
# elapsed_time = end_time - start_time

# print(f"Model created in {elapsed_time:.2f} seconds.")

# best_mlp = grid_search_mlp.best_estimator_
# # Print best Result
# print("Best result: %f using the following hyperparameters %s" % (grid_search_mlp.best_score_, grid_search_mlp.best_params_))
# means = grid_search_mlp.cv_results_['mean_test_score']
# stds = grid_search_mlp.cv_results_['std_test_score']
# params = grid_search_mlp.cv_results_['params']

# # Save the model
# filename=r'\mlp_loadshedding.pkl'
# joblib.dump(best_mlp, file_directory+filename)
# print(f"Model saved at {file_directory+filename}.")


# # ------------------------------------------------------------------------------- Run the Multi Layer Perceptron WITH OVERSAMPLING
# print("Creation of the MLP model (with oversampling)...")

# X_train_zeros = X_train_sc[y_train_scaled == 0]
# y_train_zeros = y_train_scaled[y_train_scaled == 0]
# X_train_non_zeros = X_train_sc[y_train_scaled != 0]
# y_train_non_zeros = y_train_scaled[y_train_scaled != 0]


# X_train_non_zeros_upsampled, y_train_non_zeros_upsampled = resample(X_train_non_zeros, y_train_non_zeros, 
#                                                                    replace=True, 
#                                                                    n_samples=int(len(y_train_zeros)), 
#                                                                    random_state=42)


# X_train_balanced = np.vstack((X_train_non_zeros_upsampled, X_train_zeros))
# y_train_balanced = np.concatenate((y_train_non_zeros_upsampled, y_train_zeros))

# groups = np.where(y_train_balanced == 0, 0, 1)

# # MLP :
# start_time = time.time()
# modelo = MLPRegressor(max_iter=100, random_state=42)
# param_grid_mlp = {
#     'hidden_layer_sizes': [(200, 100, 100, 50)],
#     'activation': ['relu'],
#     'solver': ['adam'],
#     'alpha': [0.0001],
#     'learning_rate': ['constant']
# }

# # Search for the best combination of hyperparameters
# grid_search_mlp = GridSearchCV(estimator=modelo, param_grid=param_grid_mlp, scoring=scoring, cv=my_cv, n_jobs=-1)


# grid_search_mlp.fit(X_train_balanced, y_train_balanced)

# end_time = time.time()
# elapsed_time = end_time - start_time

# print(f"Model created in {elapsed_time:.2f} seconds.")

# best_mlp_oversamp = grid_search_mlp.best_estimator_

# # Print best Result
# print("Best result: %f using the following hyperparameters %s" % (grid_search_mlp.best_score_, grid_search_mlp.best_params_))
# means = grid_search_mlp.cv_results_['mean_test_score']
# stds = grid_search_mlp.cv_results_['std_test_score']
# params = grid_search_mlp.cv_results_['params']

# # Save the model
# filename=r'\mlp_loadshedding_oversamp.pkl'
# joblib.dump(best_mlp_oversamp, file_directory+filename)
# print(f"Model saved at {file_directory+filename}.")

# joblib.dump(scaler_X, file_directory+'_scaler_X_ls.pkl')
# joblib.dump(scaler_y, file_directory+'_scaler_y_ls.pkl')

# # ------------------------------------------------------------------------------------- Run the Random Forest

# print("Creation of the RF model...")
# start_time = time.time()
# modelo = RandomForestRegressor(random_state=42)
# scoring='neg_mean_absolute_error'
# params = {
#     # Number of trees in random forest
#     'n_estimators': [50],  # default=100
#      # Maximum number of levels in tree
#     'max_depth': [10],  #deafult = None
#      # The minimum number of samples required to split an internal node
#     'min_samples_split': [2],
#     # The minimum number of samples required to be at a leaf node
#     'min_samples_leaf' : [2],
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
# print(f"Model created in {elapsed_time:.2f} seconds.")

# best_rf = grid_search_rf.best_estimator_

# # Print best Result
# print("Best result: %f using the following hyperparameters %s" % (grid_search_rf.best_score_, grid_search_rf.best_params_))
# means = grid_search_rf.cv_results_['mean_test_score']
# stds = grid_search_rf.cv_results_['std_test_score']
# params = grid_search_rf.cv_results_['params']

# # Save the model
# filename=r'\rf_loadshedding.pkl'
# joblib.dump(best_rf, file_directory+filename)
# print(f"Model saved at {file_directory+filename}.")

# joblib.dump(scaler_X, file_directory+'_scaler_X_ls.pkl')
# joblib.dump(scaler_y, file_directory+'_scaler_y_ls.pkl')