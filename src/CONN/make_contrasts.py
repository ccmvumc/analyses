import glob
import os

import scipy.io
import pandas as pd
import numpy as np


COVFILE = '/INPUTS/covariates.csv'
OUTFILE = '/OUTPUTS/contrasts.mat'
mat = {}
contrasts = []
groups = []
sources = []
conditions = []


# TODO: handle 3 group comparison by adding B vs C, A vs C, and f test
# TODO: site effects
# TODO: control for site, sex, age
# TODO: multiple sources
# TODO: age only
# TODO: multiple conditions


# Load subject data
df = pd.read_csv(COVFILE)
columns = df.columns
print(columns)

# Find groups
groups = [x for x in columns if x.startswith('GROUP_')]
print(f'{groups=}')

# load conditions
_file = glob.glob('/OUTPUTS/*/conn_project/results/preprocessing/_list_conditions.mat')[0]
m = loadmat(_file)
conditions = [x[0] for x in m['allnames'][0]]
print(f'{conditions=}')

# load regions
_file = glob.glob('/OUTPUTS/*/conn_project/results/firstlevel/SBC_01/_list_sources.mat')[0]
m = loadmat(_file)
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


# Age only
contrasts.append({
    'Results': {
        'done': 1,
        'overwrite': 1,
        'analysis_number': [3],
        'between_subjects': {
            'effect_names': ['AGE'],
            'contrast': [1],
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