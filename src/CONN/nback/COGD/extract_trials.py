import numpy as np

from ..shared import load_edat, save_trials


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
    
        if str(row['ZeroBackTarget']) == '1':
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


def extract_trials():
    # Load the edat file into a pandas dataframe
    df = load_edat()

    # Parse the df to get a dataframe of just the generic columns
    df = parse_nback(df)

    # write csv file
    save_trials(df)


if __name__ == '__main__':
    extract_trials()
