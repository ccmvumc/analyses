import glob
import os

import pandas as pd
import numpy as np
from scipy.io import loadmat, savemat


COVFILE = '/INPUTS/covariates.csv'
OUTFILE = '/OUTPUTS/contrasts.mat'
mat = {}
contrasts = []
sources = []
conditions = []
batch_data = []


print('make_contrast')

# Load subject data
df = pd.read_csv(COVFILE)

print(df)

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

# Overall time effect of contrast
batch_data.append(
    make_contrast(
        ['AllSubjects', 'AGE'],
        [1, 0], 
        ['MEC', 'PLC'],
        [1, -1],
        ['Effect of 2BACK', 'Effect of OBACK'], 
        [1, -1]
    )
)

# Build the batch in a format that will load correctly in matlab
for c in conditions:
    for s in sources:
        # Main effect
        batch_data.append(
            make_contrast(['AllSubjects'], [1], c, [1], s, [1])
        )

        # Age effect
        batch_data.append(
            make_contrast(['AllSubjects', 'AGE'], [0, 1], c, [1], s, [1])
        )

print(batch_data)

# Create file
mat['batch'] = np.array(batch_data)
savemat(OUTFILE, mat)
