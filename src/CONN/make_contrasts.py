import scipy.io
import os
import pandas as pd
import numpy as np


ROOTDIR = '/OUTPUTS/conn'
OUTFILE = '/OUTPUTS/contrasts.mat'
COVFILE = '/OUTPUTS/covariates.mat'
mat = {}
contrasts = []
groups = []
sources = []
conditions = []


# Load subject data
df = pd.read_csv(COVFILE)
columns = df.columns
print(columns)

# Find groups
groups = [x for x in columns if x.startswith('GROUP_')]
print(f'{groups=}')

# load conditions
m = loadmat(f'{ROOTDIR}/results/preprocessing/_list_conditions.mat')
conditions = [x[0] for x in m['allnames'][0]]
print(f'{conditions=}')

# load regions
m = loadmat(f'{ROOTDIR}/results/firstlevel/SBC_01/_list_sources.mat')
sources =  [x[0] for x in m['sourcenames'][0]]
print(f'{sources=}')

# Compare groups
contrasts.append({
    'Results': {
        'done': 1,
        'overwrite': 1,
        'analysis_number': [1],
        'between_subjects': {
            'effect_names': groups[0:2],
            'contrast': [1, -1],
        },
        'between_conditions': {
            'effect_names': conditions[0:1],
            'contrast': [1],
        },
        'between_sources': {
            'effect_names': sources,
            'contrast': [1],
        }
    }
})

# Compare sexes
contrasts.append({
    'Results': {
        'done': 1,
        'overwrite': 1,
        'analysis_number': [2],
        'between_subjects': {
            'effect_names': ['SEX_M', 'SEX_F'],
            'contrast': [1, -1],
        },
        'between_conditions': {
            'effect_names': conditions[0:1],
            'contrast': [1],
        },
        'between_sources': {
            'effect_names': sources,
            'contrast': [1],
        }
    }
})

mat['contrasts'] = contrasts

# Create file
scipy.io.savemat(OUTFILE, mat)
