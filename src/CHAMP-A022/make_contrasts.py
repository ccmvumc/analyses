import glob
import os

import pandas as pd
import numpy as np
from scipy.io import loadmat, savemat


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


def make_contrasts(covariates_file, contrasts_file):
    mat = {}
    contrasts = []
    sources = []
    conditions = []
    batch_data = []

    print('make_contrasts')

    # Load subject data
    df = pd.read_csv(covariates_file)

    # load conditions
    _file = glob.glob('/OUTPUTS/*/conn_project/results/preprocessing/_list_conditions.mat')[0]
    m = loadmat(_file)
    conditions = [x[0] for x in m['allnames'][0]]
    print(f'{conditions=}')

    # load regions
    _file = glob.glob('/OUTPUTS/*/conn_project/results/firstlevel/SBC_01/_list_sources.mat')[0]
    m = loadmat(_file)
    sources = [x[0] for x in m['sourcenames'][0]]
    print(f'{sources=}')

    # Overall effect of ROIs
    batch_data.append(
        make_contrast(
            ['AllSubjects', 'AGE'],
            [1, 0],
            ['rest-MEC', 'rest-PLC'],
            [1/2, 1/2],
            ['sclimbic.Left-BF'], 
            [1]
        )
    )
    batch_data.append(
        make_contrast(
            ['AllSubjects', 'AGE'],
            [1, 0],
            ['rest-MEC', 'rest-PLC'],
            [1/2, 1/2],
            ['sclimbic.Right-BF'], 
            [1]
        )
    )

    # Time effect of ROIs
    batch_data.append(
        make_contrast(
            ['AllSubjects', 'AGE'],
            [1, 0],
            ['rest-MEC', 'rest-PLC'],
            [1, -1],
            ['sclimbic.Left-BF'], 
            [1]
        )
    )
    batch_data.append(
        make_contrast(
            ['AllSubjects', 'AGE'],
            [1, 0],
            ['rest-MEC', 'rest-PLC'],
            [1, -1],
            ['sclimbic.Right-BF'], 
            [1]
        )
    )

    print(batch_data)

    # Create file
    mat['batch'] = np.array(batch_data)
    savemat(contrasts_file, mat)


if __name__ == '__main__':
    covariates_file = sys.argv[1]
    contrasts_file = sys.argv[2]

    print(f'Making contrasts:{covariates_file=}:{contrasts_file=}')
    make_contrasts(covariates_file, contrasts_file)
    print('DONE!')
