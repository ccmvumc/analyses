
from glob import glob

import numpy as np
import scipy.io

from shared import save_behavior, load_trials, load_edat, write_spm_conditions, save_trials


CONDITIONS = ['Reward', 'NoReward']
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
            val = '+$4'
        else:
            val = '$0.00'

        # Get the onsets that match the val
        cond_onsets = list(df[df['Current_SubTrial_'] == val]['_Onset'])

        # Append to onset list
        onsets.append(cond_onsets)

        # Set the name of the condition
        names.append(cond_name)

        # Set the durations
        durations.append(duration)

    # Save to mat file for spm
    write_spm_conditions(names, onsets, durations, conditions_file)


def apply_columns(row):
    # Map the type
    row_type = row['Current_SubTrial_']

    row['INDEX'] = row['_TRIAL']
    row['RT'] = ''
    row['ACC'] = ''
    row['RESP'] = ''

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
    df = df[['INDEX', 'TYPE', 'RT', 'ACC', 'RESP', 'ONSET']]

    df = df[df.TYPE.isin(CONDITIONS)]

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


def main(output_dir):
    edat_files = glob(f'{output_dir}/PREPROC/*/FMRI/*/*.edat.txt')

    for e in edat_files:
        print(f'Extracting from EDAT:{e}')
        extract(e)


if __name__ == '__main__':
    import sys
    output_dir = sys.argv[1]
    main(output_dir)
    print('DONE!')
