import scipy.io
import os
import pandas as pd
import numpy as np

# Load covariates from csv and save to mat for loading into conn_batch()

CSVFILE = '/INPUTS/covariates.csv'
MATFILE = '/OUTPUTS/covariates.mat'
mat = {}

df = pd.read_csv(CSVFILE)

# Filter out non-numeric data and force float
effects = df.select_dtypes(include=[np.number])
effects = effects.astype(float)
names = effects.columns

np_vectors = np.empty((len(names),), dtype=object)
for i in range(len(names)):
    np_vectors[i] = np.transpose(np.array([effects[names[i]]]))

mat['effect_names'] = np.array(names, dtype=object)
mat['effects'] =  np_vectors

# Create file
scipy.io.savemat(MATFILE, mat)
