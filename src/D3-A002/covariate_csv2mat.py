import scipy.io
import os
import pandas as pd
import numpy as np

# Load covariates from csv and save to mat for loading into conn_batch()

CSVFILE = 'covariates.csv'
MATFILE = 'covariates.mat'
mat = {}

df = pd.read_csv(CSVFILE)
names = df.columns
effects = df[names]

np_vectors = np.empty((len(names),), dtype=object)
for i in range(len(names)):
    np_vectors[i] = np.transpose(np.array([effects[names[i]]]))

mat['effect_names'] = np.array(names, dtype=object)
mat['effects'] =  np_vectors

# Create file
scipy.io.savemat(MATFILE, mat)
