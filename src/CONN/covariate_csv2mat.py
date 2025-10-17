import scipy.io
import os
import pandas as pd
import numpy as np

# Load covariates from csv and save to mat for loading into conn_batch()

CSVFILE = '/INPUTS/covariates.csv'
MATFILE = '/OUTPUTS/covariates.mat'
mat = {}

# Load subject data
df = pd.read_csv(CSVFILE)
df['ID'] = df['ID'].astype(str)

print(f'loaded {len(df)} subjects from {CSVFILE}')
print(df)

subjects = [x for x in os.listdir('/INPUTS') if os.path.isdir(f'/INPUTS/{x}')]

print(f'{len(subjects)} subjects downloaded')

# Filter by subject list    
df = df[df.ID.isin(subjects)]

print(f'Saving covariates for {len(df)} subjects')
print(df)

# TODO: compare sort order of subjects to df, error if different?

# Mean center age
df['AGE'] = df['AGE'].astype(float)
df['AGE'] = (df['AGE'] - df['AGE'].mean()) / df['AGE'].std()

# Convert categorical columns to dummy columns
dummies = [x for x in ['SITE', 'GROUP', 'SEX'] if x in df.columns]
if dummies:
    df = pd.get_dummies(df, columns=dummies, dtype='int')

# Filter out non-numeric data and force float
effects = df.select_dtypes(include=[np.number])
effects = effects.astype(float)
names = [x for x in effects.columns if x != 'ID']

# Build vector of values for each covariate
np_vectors = np.empty((len(names),), dtype=object)
for i in range(len(names)):
    np_vectors[i] = np.transpose(np.array([effects[names[i]]]))

# Store in mat format as expected by SPM/CONN
mat['effect_names'] = np.array(names, dtype=object)
mat['effects'] = np_vectors

# Create file
scipy.io.savemat(MATFILE, mat)
