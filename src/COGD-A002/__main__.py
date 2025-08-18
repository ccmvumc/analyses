'''COGD first level and second analysis of NBACK task, loads images processed by CONN toolbox'''

# INPUTS (per subject): 
#    in PREPROC subfolder SUBJECT/FMRI/Baseline/
#       and same
#    in PREPROC subfolder SUBJECt/FMRI/Week5/
#      "dswuFMRI.nii.gz" (these are the denosied/smoothed images)
#      "art_regression_outliers_and_movement_uFMRI.mat" (only for displaying motion, not used in first-level b/c already denoised)
#      "FMRI.nii.conditions.mat" (the spm format conditions we can load with scipy to make events table)
#    in subfolder FMRI/
#      "/FMRI.nii.behavior.txt" (only for displaying)
#
# OUTPUTS:
#    PDF
#       -page per subject displaying data, contrast, motion params
#       -group pages for single t of contrast, with age, BL vs WK5, with and without corrections
#


import os, sys

import pandas as pd

from . import firstlevel
from . import secondlevel


SESSIONS = ['Baseline', 'Week5']


def merge_behavior(input_dir, output_file):
    data = []
    subjects = [x for x in os.listdir(input_dir) if os.path.isdir(f'{input_dir}/{x}')]

    for subj in subjects:
        for sess in SESSIONS:
            b = {'SUBJECT': subj, 'SESSION': sess}
            f = os.path.join(input_dir, subj, 'FMRI', sess, 'FMRI.nii.behavior.txt')
            b.update(load_behavior(f))
            data.append(b)
            print(b)

    df = pd.DataFrame(data)

    df = df.drop(columns=[
        'zerobackdistractor_acc', 'zerobackdistractor_count', 'zerobackdistractor_rt',
        'zerobacktarget_acc', 'zerobacktarget_count' ,'zerobacktarget_rt'
    ])

    df = df.sort_values(['SUBJECT', 'SESSION'])

    print(df)

    df.to_csv(output_file, index=False)


def load_behavior(filename):
    b = {}
    with open(filename, "r") as f:
        for line in f:
            k, v = line.strip().split('=')
            b[k] = v

    return b


if __name__ == '__main__':
    firstlevel.main(sys.argv[1], sys.argv[2])
    secondlevel.main(sys.argv[2])
    merge_behavior(sys.argv[1], os.path.join(sys.argv[2], 'behavior.csv'))
