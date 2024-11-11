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


def make_contrast(subjects, subjectc, conditions, conditionc, sources, sourcec):
    return {
        'filename': '/OUTPUTS/conn.mat',
        'done': 1,
        'Analysis': {'type': 2},
        'Results': {
            'between_subjects': {
                'effect_names': np.array(subjects, dtype=object),
                'contrast': np.array(subjectc, dtype=np.double),
            },
            'between_conditions': {
                'effect_names': np.array(conditions, dtype=object),
                'contrast': np.array(conditionc, dtype=np.double),
            },
            'between_sources': {
                'effect_names': np.array(sources, dtype=object),
                'contrast': np.array(sourcec, dtype=np.double),
            }
        }
    }

# Build the batch in a format that will load correctly in matlab
batch_data = [
    # Main effect
    make_contrast(['AllSubjects'], [1], conditions[0:1], [1], sources[0:1], [1]),
    make_contrast(['AllSubjects'], [1], conditions[0:1], [1], sources[1:2], [1]),
    make_contrast(['AllSubjects'], [1], conditions[0:1], [1], sources[0:2], [0.5, 0.5]),
    make_contrast(['AllSubjects'], [1], conditions[0:1], [1], sources[0:2], [1, -1]),

    # Group comparison
    make_contrast(groups[0:2], [1, -1], conditions[0:1], [1], sources[0:1], [1]),
    make_contrast(groups[0:2], [1, -1], conditions[0:1], [1], sources[1:2], [1]),
    make_contrast(groups[0:2], [1, -1], conditions[0:1], [1], sources[0:2], [0.5, 0.5]),

    # Age effect
    make_contrast(['AllSubjects', 'AGE'], [0, 1], conditions[0:1], [1], sources[0:1], [1]),
    make_contrast(['AllSubjects', 'AGE'], [0, 1], conditions[0:1], [1], sources[1:2], [1]),
    make_contrast(['AllSubjects', 'AGE'], [0, 1], conditions[0:1], [1], sources[0:2], [0.5, 0.5]),

    # Sex comparison
    make_contrast(['SEX_M', 'SEX_F'], [1, -1], conditions[0:1], [1], sources[0:1], [1]),
    make_contrast(['SEX_M', 'SEX_F'], [1, -1], conditions[0:1], [1], sources[1:2], [1]),
    make_contrast(['SEX_M', 'SEX_F'], [1, -1], conditions[0:1], [1], sources[0:2], [0.5, 0.5]),
]

print(batch_data)

# Create file
mat['batch'] = np.array(batch_data)
savemat(OUTFILE, mat)
