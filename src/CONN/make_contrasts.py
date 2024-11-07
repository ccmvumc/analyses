import glob
import os

import pandas as pd
import numpy as np
from scipy.io import loadmat, savemat


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

# Find groups
groups = df.GROUP.unique()
groups = [f'GROUP_{x}' for x in groups]
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
group_contrast = {
    'done': 1,
    'overwrite': 1,
    'analysis_number': 1,
    'between_subjects': {
        'effect_names': np.array(groups[0:2], dtype=object),
        'contrast': np.array([1, -1], dtype=np.double),
    },
    'between_conditions': {
        'effect_names': np.array(conditions[0:1], dtype=object),
        'contrast': np.array([1], dtype=np.double),
    },
    'between_sources': {
        'effect_names': np.array(sources, dtype=object),
        'contrast': np.array([1], dtype=np.double),
    }
}

# Compare sexes
sex_contrast = {
    'done': 1,
    'overwrite': 1,
    'analysis_number': 2,
    'between_subjects': {
        'effect_names': np.array(['SEX_M', 'SEX_F'], dtype=object),
        'contrast': np.array([1, -1], type=np.double),
    },
    'between_conditions': {
        'effect_names': np.array(conditions[0:1], dtype=object),
        'contrast':  np.array([1], dtype=np.double),
    },
    'between_sources': {
        'effect_names': np.array(sources, dtype=object),
        'contrast': np.array([1], dtype=np.double),
    }
}

# Age only
age_contrast = {
    'done': 1,
    'overwrite': 1,
    'analysis_number':  3,
    'between_subjects': {
        'effect_names': np.array(['AGE'], dtype=object),
        'contrast': np.array([1], dtype=np.double),
    },
    'between_conditions': {
        'effect_names': np.array(conditions[0:1], dtype=object),
        'contrast': np.array([1], dtype=np.double),
    },
    'between_sources': {
        'effect_names': np.array(sources, dtype=object),
        'contrast': np.array([1], dtype=np.double),
    }
}

# Build the batch in a format that will load correctly in matlab
dtype = [('Results', 'O')]
batch_data = np.array([
    (sex_contrast),
    (age_contrast), 
    (group_contrast)
], dtype=dtype)

# Create file
mat['contrasts'] = batch_data
savemat(OUTFILE, mat)
