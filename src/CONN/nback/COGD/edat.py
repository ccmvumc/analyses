
from glob import glob

import numpy as np
import scipy.io

from shared import save_behavior, load_trials, load_edat, write_spm_conditions, save_trials


CONDITIONS = ['REST', '0BACK', '2BACK']
DURATIONS = [20.0, 60.0, 60.0]


def parse_behavior(df):
    # Initialize the summary data
    data = {}

    # Drop the Begin trials that are not used for accuracy/RT
    df = df[df.SUBTYPE != 'Begin']

    # Accuracy
    data['overall_acc'] = df.ACC.mean()
    data['zeroback_acc'] = df[df.TYPE == '0Back'].ACC.mean()
    data['twoback_acc'] = df[df.TYPE == '2Back'].ACC.mean()
    data['zerobacktarget_acc'] = df[(df.TYPE == '0Back') & (df.SUBTYPE == 'Target')].ACC.mean()
    data['zerobackdistractor_acc'] = df[(df.TYPE == '0Back') & (df.SUBTYPE == 'Distractor')].ACC.mean()
    data['twobacktarget_acc'] = df[(df.TYPE == '2Back') & (df.SUBTYPE == 'Target')].ACC.mean()
    data['twobackdistractor_acc'] = df[(df.TYPE == '2Back') & (df.SUBTYPE == 'Distractor')].ACC.mean()
 
    # Counts
    data['overall_count'] = len(df)
    data['zeroback_count'] = len(df[df.TYPE == '0Back'])
    data['twoback_count'] = len(df[df.TYPE == '2Back'])
    data['zerobacktarget_count'] = len(df[(df.TYPE == '0Back') & (df.SUBTYPE == 'Target')])
    data['zerobackdistractor_count'] = len(df[(df.TYPE == '0Back') & (df.SUBTYPE == 'Distractor')])
    data['twobacktarget_count'] = len(df[(df.TYPE == '2Back') & (df.SUBTYPE == 'Target')])
    data['twobackdistractor_count'] = len(df[(df.TYPE == '2Back') & (df.SUBTYPE == 'Distractor')])

    # Reaction Time
    data['overall_rt'] = df.RT.mean()
    data['zeroback_rt'] = df[df.TYPE == '0Back'].RT.mean()
    data['twoback_rt'] = df[df.TYPE == '2Back'].RT.mean()
    data['zerobacktarget_rt'] = df[(df.TYPE == '0Back') & (df.SUBTYPE == 'Target')].RT.mean()
    data['zerobackdistractor_rt'] = df[(df.TYPE == '0Back') & (df.SUBTYPE == 'Distractor')].RT.mean()
    data['twobacktarget_rt'] = df[(df.TYPE == '2Back') & (df.SUBTYPE == 'Target')].RT.mean()
    data['twobackdistractor_rt'] = df[(df.TYPE == '2Back') & (df.SUBTYPE == 'Distractor')].RT.mean()

    # Round floats to 2 places
    for k, v in data.items():
        if isinstance(v, float):
            data[k] = round(v, 2)

    # Convert all values to string
    data = {k: str(v) for k, v in data.items()}

    return data


def extract_behavior(trials_file, behavior_file):
    # Load the trials data
    df = load_trials(trials_file)

    data = parse_behavior(df)

    # write text file
    save_behavior(data, behavior_file)


def load_nback(edat_file):
    # Load the edat as a dataframe
    df = load_edat(edat_file)

    return df


def extract_conditions(edat_file, conditions_file):
    names = CONDITIONS
    durations = DURATIONS
    onsets = []

    # Load nback data from edat txt file to a pandas dataframe
    df = load_nback(edat_file)

    offset_time = int(df['Synchronize_OffsetTime'].iloc[0])
    rest_times = list(df['Rest_OnsetTime'].unique())
    rest_onsets = [(int(x) - offset_time) / 1000 for x in rest_times]
    zero_times = df[df['Procedure_SubTrial_'] == 'ZeroBackProc']['Rest_OnsetTime'].unique()
    zero_onsets = [int(int(x) - offset_time + 24000)  / 1000  for x in zero_times]
    two_times = df[df['Procedure_SubTrial_'] == 'TwoBackProc']['Rest_OnsetTime'].unique()
    two_onsets = [int(int(x) - offset_time + 24000)  / 1000  for x in two_times]

    onsets = [rest_onsets, zero_onsets, two_onsets]

    # Save to mat file for spm
    write_spm_conditions(names, onsets, durations, conditions_file)


# no single column has onset/acc/rt. have to combine
def apply_columns(row):

    # Map the shorthand type from the type column
    row_type = row['Procedure_SubTrial_']
    if row_type == 'ZeroBackProc':
         row['_TYPE'] = '0Back'
    elif row_type == 'TwoBackProc':
         row['_TYPE'] = '2Back'
    else:
        raise ValueError('unknown trial type')

    if row_type == 'ZeroBackProc':
        row['_ONSET'] = row['ZeroBackStimuli_OnsetTime']
        row['_RESP'] = row['ZeroBackStimuli_RESP']
        row['_RT'] = row['ZeroBackStimuli_RT']
        row['_ACC'] = row['ZeroBackStimuli_ACC']

        if row['ZeroBackTarget'] == '1':
            row['_SUBTYPE'] = 'Target'
        else:
            row['_SUBTYPE'] = 'Distractor'
    elif row_type == 'TwoBackProc':
        if row['Procedure_LogLevel6_'] == 'TrailTwoBackBegin':
            row['_ONSET'] = row['TwoBackBegin_OnsetTime']
            row['_RESP'] = row['TwoBackBegin_RESP']
            row['_RT'] = row['TwoBackBegin_RT']
            row['_ACC'] = row['TwoBackBegin_ACC']
            row['_SUBTYPE'] = 'Begin'
        elif row['Procedure_LogLevel6_'] == 'TrailTwoBackTarget':
            row['_ONSET'] = row['TwoBackTarget_OnsetTime']
            row['_RESP'] = row['TwoBackTarget_RESP']
            row['_RT'] = row['TwoBackTarget_RT']
            row['_ACC'] = row['TwoBackTarget_ACC']
            row['_SUBTYPE'] = 'Target'
        elif row['Procedure_LogLevel6_'] == 'TrailTwoBackDistractor':
            row['_ONSET'] = row['TwoBackDistractor_OnsetTime']
            row['_RESP'] = row['TwoBackDistractor_RESP']
            row['_RT'] = row['TwoBackDistractor_RT']
            row['_ACC'] = row['TwoBackDistractor_ACC']
            row['_SUBTYPE'] = 'Distractor'
        else:
            raise ValueError('unknown 2Back sub-trial type')

    # # Apply offset to onset time
    row['_ONSET'] = (float(row['_ONSET']) - float(row['_START_OFFSET_'])) / 1000.0

    # # Give the columns better names
    row['INDEX'] = int(row['_TRIAL'])
    row['TYPE'] = row['_TYPE']
    row['RT'] = int(row['_RT'])
    row['ACC'] = int(row['_ACC'])
    row['RESP'] = row['_RESP']
    row['ONSET'] = float(row['_ONSET'])
    row['SUBTYPE'] = row['_SUBTYPE']

    return row


def parse_nback(df):
    # Set trial numbering
    df['_TRIAL'] = df.index.copy()

    # Get the starting offset time from first row
    df['_START_OFFSET_'] = df['Synchronize_OffsetTime'].iloc[0]

    # Apply new columns to each row
    df = df.apply(apply_columns, axis=1)

    # # Get just the columns we need
    df = df[['INDEX', 'TYPE', 'SUBTYPE', 'RT', 'ACC', 'RESP', 'ONSET']]

    # Return a dataframe of the results
    return df


def extract_trials(edat_file, trials_file):
    # Load the edat file into a pandas dataframe
    df = load_edat(edat_file)

    # Parse the df to get a dataframe of just the generic columns
    df = parse_nback(df)

    # write csv file
    save_trials(df, trials_file)


def extract_all(edat_file):
    edat_base = edat_file.rsplit('.edat.txt')[0]
    conditions_file = edat_base + '.conditions.mat'
    trials_file = edat_base + '.trials.csv'
    behavior_file = edat_base + '.behavior.txt'

    extract_conditions(edat_file, conditions_file)

    extract_trials(edat_file, trials_file)

    extract_behavior(trials_file, behavior_file)


def main():
    edat_files = glob('/OUTPUTS/PREPROC/*/FMRI/*/*.edat.txt')

    for e in edat_files:
        print(f'Extracting from EDAT:{e}')
        extract_all(e)


if __name__ == '__main__':
    main()   
