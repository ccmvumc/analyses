'''CHAMP first level and second analysis of NBACK task, loads images processed by CONN toolbox'''

# INPUTS (per subject): 
#    in PREPROC subfolder FMRI/Baseline/
#      "dswuFMRI1.nii.gz" (these are the denosied/smoothed images)
#      "art_regression_outliers_and_movement_uFMRI1.mat" (for display only, not used in first-level, already denoised)
#      "FMRI1.nii.conditions.mat" (the spm format conditions we can load with scipy to make events table)
#    in subfolder FMRI/
#      "behavior.txt" (only for displaying)
#
# OUTPUTS:
#    PDF
#       -page per subject displaying data, contrast, motion params
#       -group pages for single t of contrast, with age, PLC vs MEC, with and without corrections
#

import os, sys
from glob import glob

import pandas as pd

from . import firstlevel
from . import secondlevel


SESSIONS = ['MEC', 'PLC']


def merge_behavior(input_dir, output_file):
    data = []
    subjects = sorted([x for x in os.listdir(input_dir) if os.path.isdir(f'{input_dir}/{x}')])

    for subj in subjects:
        for sess in SESSIONS:
            b = {'SUBJECT': subj, 'SESSION': sess}
            try:
                f = glob(f'{input_dir}/{subj}/**/FMRI/{sess}/FMRI.nii.behavior.txt', recursive=True)[0]
            except Exception as err:
                print(f'failed to load behavior:{subj}:{sess}:{err}')
                continue

            print(f'loading behavior file:{f}')
            b.update(load_behavior(f))
            data.append(b)

    df = pd.DataFrame(data)

    df = df.sort_values(['SUBJECT', 'SESSION'])

    df.to_csv(output_file, index=False)


def merge_stats(input_dir, output_file):
    data = []
    subjects = sorted([x for x in os.listdir(input_dir) if os.path.isdir(f'{input_dir}/{x}')])

    for subj in subjects:
        for sess in SESSIONS:
            b = {'SUBJECT': subj, 'SESSION': sess}
            f = os.path.join(input_dir, subj, sess, 'stats.txt')
            b.update(load_stats(f))
            data.append(b)

    df = pd.DataFrame(data)

    drop_columns = [x for x in df.columns if x.endswith('constant')]

    df = df.drop(columns=drop_columns)

    df = df.sort_values(['SUBJECT', 'SESSION'])

    df.to_csv(output_file, index=False)


def load_behavior(filename):
    b = {}
    with open(filename, "r") as f:
        for line in f:
            k, v = line.strip().split('=')
            b[k] = v

    return b


def load_stats(filename):
    stats = {}
    with open(filename, "r") as f:
        for line in f:
            k, v = line.strip().split('=')
            stats[k] = v

    return stats


if __name__ == '__main__':
    #merge_behavior(sys.argv[1], os.path.join(sys.argv[2], 'behavior.csv'))
    print('1st')
    firstlevel.main(sys.argv[1], sys.argv[2])
    print('2nd')
    secondlevel.main(sys.argv[2])
    merge_stats(
        os.path.join(sys.argv[2], 'SUBJECTS'),
        os.path.join(sys.argv[2], 'stats.csv')
    )
    print('DONE!')
