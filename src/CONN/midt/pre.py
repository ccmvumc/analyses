
from glob import glob

import numpy as np
import scipy.io

from shared import save_behavior, load_trials, load_edat, write_spm_conditions, save_trials


CONDITIONS = ['Reward', 'NoReward']
DURATION = 2.0  # duration of each trial


def parse_behavior(df):
    # Initialize the summary data
    data = {}

    # Accuracy of all trials
    data['overall_ACC'] = df.ACC.mean()

    # Accuracy of each trial type
    for c in CONDITIONS:
        data[c + '_ACC'] = df[(df.TYPE == c)].ACC.mean()

    # Initialize trial count
    data['overall_trial_count'] = len(df)

    data['overall_rt_mean'] = df.RT.mean()

    # Round floats to 2 places
    for k, v in data.items():
        if isinstance(v, float):
            data[k] = round(v, 2)

    # rename to all lowercase 
    data = {k.lower(): v for k, v in data.items()}

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
    start_offset = df.iloc[0].starting_OnsetTime

    # Subtract start time and convert to seconds
    df['_Onset'] = (df['Cue1_OnsetTime'] - start_offset) / 1000.0

    return df


def make_conditions(edat_file, conditions, duration, conditions_file):
    names = []
    onsets = []
    durations = []

    # Load data from edat txt file to a pandas dataframe
    df = load_midt(edat_file)

    # Load onsets and durations for each condition
    for cond_name in conditions:
        if cond_name == 'Reward':
            val = '$4'
        else:
            val = '$0'

        # Get the onsets that match the val
        cond_onsets = list(df[df['Current_SubTrial_'] == val]['_Onset'])

        # Append to onset list
        onsets.append(cond_onsets)

        # Set the name of the condition
        names.append(cond_name)

        # Set the durations
        durations.append([duration])

    # Save to mat file for spm
    write_spm_conditions(names, onsets, durations, conditions_file)


def apply_columns(row):
    # Map the type
    row_type = row['Current_SubTrial_']
    if row_type == '$4':
        row['_TYPE'] = 'Reward'
    elif row_type == '$0':
        row['_TYPE'] = 'NoReward'
    else:
        raise ValueError('unknown trial type')

    row['_ONSET'] = row['Cue1_OnsetTime']
    row['_RESP'] = row['Cue1_RESP']
    #row['_RT'] = row['_RT']
    #row['_ACC'] = row['_ACC']

    # Apply offset to onset time
    row['_ONSET'] = (row['_ONSET'] - row['_START_OFFSET_']) / 1000.0

    # Give the columns better names
    row['INDEX'] = row['_TRIAL']
    row['TYPE'] = row['_TYPE']
    row['RT'] = row['_RT'] 
    row['ACC'] = row['_ACC'] 
    row['RESP'] = row['_RESP'] 
    row['ONSET'] = row['_ONSET']

    return row


def parse_midt(df):
    # Set trial numbering
    df['_TRIAL'] = df.index.copy()

    # Get the starting offset time
    df['_START_OFFSET_'] = df.iloc[0].starting_OnsetTime

    # Apply new columns to each row
    df = df.apply(apply_columns, axis=1)

    # Get just the columns we need
    df = df[['INDEX', 'TYPE', 'RT', 'ACC', 'RESP', 'ONSET']]

    # Return a dataframe of the results
    return df


def extract_trials(edat_file, trials_file):
    # Load the edat file into a pandas dataframe
    df = load_edat(edat_file)

    # Parse the df to get a dataframe of just the generic columns
    df = parse_midt(df)

    # write csv file
    save_trials(df, trials_file)


def extract(edat_file):
    edat_base = edat_file.rsplit('.edat.txt')[0]
    conditions_file = edat_base + '.conditions.mat'
    trials_file = edat_base + '.trials.csv'
    behavior_file = edat_base + '.behavior.txt'

    make_conditions(edat_file, CONDITIONS, DURATION, conditions_file)

    extract_trials(edat_file, trials_file)

    extract_behavior(trials_file, behavior_file)


def main():
    edat_files = glob('/OUTPUTS/PREPROC/*/FMRI/*/*.edat.txt')

    for e in edat_files:
        print(f'Extracting from EDAT:{e}')
        extract(e)


if __name__ == '__main__':
    main()   
