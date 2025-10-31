import os
from glob import glob

import numpy as np
import scipy.io

from shared import save_behavior, load_trials, load_edat, write_spm_conditions, save_trials


DURATION = 2.0  # duration of each trial


def parse_behavior(df):
    # Initialize the summary data
    data = {}

    # Initialize trial count
    data['overall_trial_count'] = len(df)

    return data


def extract_behavior(trials_file, behavior_file):
    # Load the trials data
    df = load_trials(trials_file)

    data = parse_behavior(df)

    # write text file
    save_behavior(data, behavior_file)


def load_midt(edat_file):
    # Load the edat as a dataframe
    df = load_edat(edat_file)

    # Get the offset to the first trial
    start1_offset = df.iloc[0].starting_OnsetTime
    start2_offset = df.iloc[27].starting1_OnsetTime

    # Subtract start time and convert to seconds
    df['Cue_Onset1'] = (df['Cue1_OnsetTime'] - start1_offset) / 1000.0
    df['Cue_Onset2'] = (df['Cue1_OnsetTime'] - start2_offset) / 1000.0
    df['Fbk_Onset1'] = (df['fbk_OnsetTime'] - start1_offset) / 1000.0
    df['Fbk_Onset2'] = (df['fbk_OnsetTime'] - start2_offset) / 1000.0

    df['Rwd'] = df['Rwd'].astype(str)

    return df


def make_conditions(edat_file, conditions1_file, conditions2_file):
    names = []
    onsets1 = []
    onsets2 = []
    durations = []

    # Load data from edat txt file to a pandas dataframe
    df = load_midt(edat_file)

    # Load onsets and durations for each reward condition
    for cond_name in ['Reward', 'NoReward']:
        if cond_name == 'Reward':
            val = '4'
        else:
            val = '0'

        # Get the onsets that match the val
        cond1_onsets = list(df[(df['Rwd'] == val) & (df['Procedure_Trial_'] == 'RunBlk1')]['Cue_Onset1'])
        cond2_onsets = list(df[(df['Rwd'] == val) & (df['Procedure_Trial_'] == 'RunBlk2')]['Cue_Onset2'])

        # Append to onset list
        onsets1.append(cond1_onsets)
        onsets2.append(cond2_onsets)

        # Set the name of the condition
        names.append(cond_name)

        # Set the durations
        durations.append(DURATION)

    # Load onsets and durations for hits and misses only only reward trials
    for cond_name in ['HitReward', 'MissReward']:
        if cond_name == 'HitReward':
            val = 'Hit!'
        else:
            val = 'Miss!'

        # Get the onsets that match the val
        cond1_onsets = list(df[(df['Chng'] == val) & (df['Rwd'] == '4') & (df['Procedure_Trial_'] == 'RunBlk1')]['Fbk_Onset1'])
        cond2_onsets = list(df[(df['Chng'] == val) & (df['Rwd'] == '4') & (df['Procedure_Trial_'] == 'RunBlk2')]['Fbk_Onset2'])

        # Append to onset list
        onsets1.append(cond1_onsets)
        onsets2.append(cond2_onsets)

        # Set the name of the condition
        names.append(cond_name)

        # Set the durations
        durations.append(DURATION)


    # Save to mat file for spm
    write_spm_conditions(names, onsets1, durations, conditions1_file)
    write_spm_conditions(names, onsets2, durations, conditions2_file)


def apply_columns(row):
    # Map the type
    row_type = row['Current_SubTrial_']

    row['INDEX'] = row['_TRIAL']
    row['RT'] = ''
    row['ACC'] = ''
    row['RESP'] = ''

    row['BLOCK'] = row['Procedure_Trial_']

    if row_type == '+$4':
        row['TYPE'] = 'Reward'
    elif row_type == '$0.00':
        row['TYPE'] = 'NoReward'
    else:
        row['TYPE'] = 'Other'

    try:
        row['ONSET'] = row['Cue1_OnsetTime']
  
        # Apply offset to onset time
        row['ONSET'] = (row['ONSET'] - row['_START_OFFSET_']) / 1000.0
    except Exception as err:
        row['ONSET'] = ''

    return row


def parse_midt(df):
    # Set trial numbering
    df['_TRIAL'] = df.index.copy()

    # Get the starting offset time
    df['_START_OFFSET_'] = df.iloc[0].starting_OnsetTime

    # Apply new columns to each row
    df = df.apply(apply_columns, axis=1)

    # Get just the columns we need
    df = df[['INDEX', 'BLOCK', 'TYPE', 'ONSET']]

    df = df[df.TYPE.isin(['Reward', 'NoReward'])]

    # Return a dataframe of the results
    return df


def extract_trials(edat_file, trials_file):
    # Load the edat file into a pandas dataframe
    df = load_edat(edat_file)

    # Parse the df to get a dataframe of just the generic columns
    df = parse_midt(df)

    # write csv files
    save_trials(df, trials_file)


def extract(edat_file):
    edat_dir = os.path.dirname(edat_file)
    conditions1_file = f'{edat_dir}/FMRI1.nii.conditions.mat'
    conditions2_file = f'{edat_dir}/FMRI2.nii.conditions.mat'
    trials_file = f'{edat_dir}/trials.csv'
    behavior_file = f'{edat_dir}/behavior.txt'

    make_conditions(edat_file, conditions1_file, conditions2_file)

    extract_trials(edat_file, trials_file)

    extract_behavior(trials_file, behavior_file)


def main(output_dir):
    edat_files = glob(f'{output_dir}/PREPROC/*/FMRI/*/FMRI1.nii.edat.txt')

    for e in edat_files:
        print(f'Extracting from EDAT:{e}')
        extract(e)


if __name__ == '__main__':
    import sys
    output_dir = sys.argv[1]
    main(output_dir)
    print('DONE!')
