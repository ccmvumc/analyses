import numpy as np

from shared import load_edat, save_trials


# no single column has onset/acc/rt. have to combine
def apply_columns(row):

    # Map the shorthand type from the type column
    row_type = row['Procedure[SubTrial]']
    if row_type == 'ZeroBackProc':
         row['_TYPE'] = '0Back'
    elif row_type == 'TwoBackProc':
         row['_TYPE'] = '2Back'
    else:
        raise ValueError('unknown trial type')

    if row_type == 'ZeroBackProc':
        row['_ONSET'] = row['ZeroBackStimuli.OnsetTime']
        row['_RESP'] = row['ZeroBackStimuli.RESP']
        row['_RT'] = row['ZeroBackStimuli.RT']
        row['_ACC'] = row['ZeroBackStimuli.ACC']
    
        if str(row['ZeroBackTarget']) == '1':
            row['_SUBTYPE'] = 'Target'
        else:
            row['_SUBTYPE'] = 'Distractor'
    elif row_type == 'TwoBackProc':
        if row['Procedure[LogLevel6]'] == 'TrailTwoBackBegin':
            row['_ONSET'] = row['TwoBackBegin.OnsetTime']
            row['_RESP'] = row['TwoBackBegin.RESP']
            row['_RT'] = row['TwoBackBegin.RT']
            row['_ACC'] = row['TwoBackBegin.ACC']
            row['_SUBTYPE'] = 'Begin'
        elif row['Procedure[LogLevel6]'] == 'TrailTwoBackTarget':
            row['_ONSET'] = row['TwoBackTarget.OnsetTime']
            row['_RESP'] = row['TwoBackTarget.RESP']
            row['_RT'] = row['TwoBackTarget.RT']
            row['_ACC'] = row['TwoBackTarget.ACC']
            row['_SUBTYPE'] = 'Target'
        elif row['Procedure[LogLevel6]'] == 'TrailTwoBackDistractor':
            row['_ONSET'] = row['TwoBackDistractor.OnsetTime']
            row['_RESP'] = row['TwoBackDistractor.RESP']
            row['_RT'] = row['TwoBackDistractor.RT']
            row['_ACC'] = row['TwoBackDistractor.ACC']
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

    # Get the starting offset time
    df['_START_OFFSET_'] = df['Synchronize.OffsetTime'].iloc[0]

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
