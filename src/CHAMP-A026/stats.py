import os
import sys

import pandas as pd


def load_subject(subj_dir):
    dfg = pd.read_csv(f'{subj_dir}/gtmpvc.cblmgmwm.output/gtm.stats.dat', header=None, sep='\s+', usecols=[2,6], names=['ROI', 'SUVR-GTM'])
    dfv = pd.read_csv(f'{subj_dir}/stats/gtmseg.stats', comment='#', header=None, sep='\s+', usecols=[3,4], names=['VOL' ,'ROI'])

    # Get a new dataframe with ROI first
    df = dfg[['ROI', 'SUVR-GTM']]

    # Merge in the volumes
    df = df.merge(dfv, on='ROI')

    return df


def make_stats(subject_dir, csv_file):

    # Start an empty dataframe
    df = pd.DataFrame()

    # Find data
    subjects = sorted(os.listdir(subject_dir))
    print(f'{subjects=}')

    # Append each subject
    for s in subjects:
        print(f'Loading subject:{subject_dir}:{s}')
        subj = load_subject(f'{subject_dir}/{s}')
        subj['SUBJECT'] = s
        df = pd.concat([df, subj])

    # Sort and save
    df = df.sort_values(['SUBJECT', 'ROI'])
    df.to_csv(csv_file, index=False)


if __name__ == '__main__':
    subject_dir = sys.argv[1]
    stats_file = sys.argv[2]

    print(f'Making stats:{stats_file}:subjects={subject_dir}')
    make_stats(subject_dir, stats_file)
    print('DONE!')
