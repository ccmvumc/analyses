import os
from glob import glob

import numpy as np
import scipy.io

from shared import save_behavior, load_trials, load_edat, write_spm_conditions, save_trials


# We want to assess response to cue and feedback.
# Responses can be hits or misses for trial types of reward or noreward. 
# Noreward means none was possible for that trial.


def parse_behavior(df):
    # Initialize the summary data
    data = {}

    # Initialize trial count
    data['hit_reward_count'] = ((df.FBK == 'hit') & (df.TYPE == 'Reward')).sum()
    data['miss_reward_count'] = ((df.FBK == 'miss') & (df.TYPE == 'Reward')).sum()
    data['hit_noreward_count'] = ((df.FBK == 'hit') & (df.TYPE == 'NoReward')).sum()
    data['miss_noreward_count'] = ((df.FBK == 'miss') & (df.TYPE == 'NoReward')).sum()
    data['overall_hit_count'] = (df.FBK == 'hit').sum()
    data['overall_miss_count'] = (df.FBK == 'miss').sum()
    data['overall_trial_count'] = len(df)
    data['overall_reward_count'] = (df.TYPE == 'Reward').sum()
    data['overall_noreward_count'] = (df.TYPE == 'NoReward').sum()

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

    return df


def make_conditions(edat_file, conditions1_file, conditions2_file):
    ''' Take single MIDT edat file to create 2 conditions files for the 2 runs in the EDAT'''
    names = []   # Condition names, will be the same for both runs
    onsets1 = [] # Run 1 onsets
    onsets2 = [] # Run 2 onsets
    durations = [] # Condition durations also same for both runs

    # Load data from edat txt file to a pandas dataframe
    df = load_midt(edat_file)

    # Load onsets and durations for each reward condition
    for cond_name in ['Reward', 'NoReward']:
        if cond_name == 'Reward':
            val = 4
        else:
            val = 0

        # Get the onsets that match the val
        cond1_onsets = list(df[(df['Rwd'] == val) & (df['Procedure_Trial_'] == 'RunBlk1')]['Cue_Onset1'])
        cond2_onsets = list(df[(df['Rwd'] == val) & (df['Procedure_Trial_'] == 'RunBlk2')]['Cue_Onset2'])

        print(f'run1:{cond_name}:{cond1_onsets}')
        print(f'run2:{cond_name}:{cond2_onsets}')

        # Append to onset list
        onsets1.append(cond1_onsets)
        onsets2.append(cond2_onsets)

        # Set the name of the condition
        names.append(cond_name)

        # Set the durations
        durations.append(2.0)

    # Load onsets and durations for hits and misses only only reward trials
    for cond_name in ['HitReward', 'MissReward']:
        if cond_name == 'HitReward':
            val = 'Hit!'
        else:
            val = 'Miss!'

        # Get the onsets that match the val
        cond1_onsets = list(df[(df['Chng'] == val) & (df['Rwd'] == 4) & (df['Procedure_Trial_'] == 'RunBlk1')]['Fbk_Onset1'])
        cond2_onsets = list(df[(df['Chng'] == val) & (df['Rwd'] == 4) & (df['Procedure_Trial_'] == 'RunBlk2')]['Fbk_Onset2'])

        print(f'run1:{cond_name}:{cond1_onsets}')
        print(f'run2:{cond_name}:{cond2_onsets}')

        # Append to onset list, per run
        onsets1.append(cond1_onsets)
        onsets2.append(cond2_onsets)

        # Set the name of the condition
        names.append(cond_name)

        # Set the durations
        durations.append(1.0)

    # Additional condition for Fbk when No reward whether Miss or not a reward trial, to contrast with HitReward
    names.append('MissOrNoReward')
    cond1_onsets = list(df[((df['Chng'] == 'Miss!') | (df['Rwd'] == 0)) & (df['Procedure_Trial_'] == 'RunBlk1')]['Fbk_Onset1'])
    cond2_onsets = list(df[((df['Chng'] == 'Miss!') | (df['Rwd'] == 0)) & (df['Procedure_Trial_'] == 'RunBlk2')]['Fbk_Onset2'])
    onsets1.append(cond1_onsets)
    onsets2.append(cond2_onsets)

    # Save to mat file for spm, per run
    write_spm_conditions(names, onsets1, durations, conditions1_file)
    write_spm_conditions(names, onsets2, durations, conditions2_file)


def apply_columns(row):
    # Map the type
    row_type = row['Rwd']

    row['INDEX'] = row['_TRIAL']
    row['RT'] = ''
    row['ACC'] = ''
    row['RESP'] = ''
    row['FBK'] = ''

    row['BLOCK'] = row['Procedure_Trial_']

    if row_type == 4:
        row['TYPE'] = 'Reward'
    elif row_type == 0:
        row['TYPE'] = 'NoReward'
    else:
        row['TYPE'] = 'Other'

    try:
        row['ONSET'] = row['Cue1_OnsetTime']
  
        # Apply offset to onset time
        row['ONSET'] = (row['ONSET'] - row['_START_OFFSET_']) / 1000.0
    except Exception as err:
        row['ONSET'] = ''

    # Get trial result
    if row['Chng'] == 'Hit!':
        row['FBK'] = 'hit'
    elif row['Chng'] == 'Miss!':
        row['FBK'] = 'miss'

    return row


def parse_midt(df):
    # Set trial numbering
    df['_TRIAL'] = df.index.copy()

    # Get the starting offset time
    df['_START_OFFSET_'] = df.iloc[0].starting_OnsetTime

    # Apply new columns to each row
    df = df.apply(apply_columns, axis=1)

    # Get just the columns we need
    df = df[['INDEX', 'BLOCK', 'TYPE', 'ONSET', 'FBK']]

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
