import numpy as np

from shared import load_edat, save_trials


def apply_columns(row):
    # Map the type from the type column 
    # TODO: can we do this with the map function?
    # This allows us to rename the trial type here
    
    row_type = row['TrialCondition']

    if row_type == 'RestRunBlockTrialCondition':
        row['_TYPE'] = 'Rest'
    elif row_type == '0BackRunBlockTrialCondition':
        row['_TYPE'] = '0Back'
    elif row_type == '1BackRunBlockTrialCondition':
        row['_TYPE'] = '1Back'
    elif row_type == '2BackRunBlockTrialCondition':
        row['_TYPE'] = '2Back'
    elif row_type == '3BackRunBlockTrialCondition':
        row['_TYPE'] = '3Back'
    else:
        raise ValueError('unknown trial type')

    row['_ONSET'] = row['StimText_OnsetTime']
    row['_RESP'] = row['StimText_RESP']

    if row._TYPE == 'Rest':
        row['_RT'] = np.nan
        row['_ACC'] = np.nan
    elif np.isnan(row['StimText_RESP']):
        row['_RT'] = np.nan
        row['_ACC'] = 0
    else:
        # Only get the RT and ACC if there's a response
        row['_RT'] = row['StimText_RT']
        row['_ACC'] = row['StimText_ACC']

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


def parse_nback(df):
    # Set trial numbering
    df['_TRIAL'] = df.index.copy()

    # Get the starting offset time
    df['_START_OFFSET_'] = df.iloc[0].RestProbe_OnsetTime

    # Apply new columns to each row
    df = df.apply(apply_columns, axis=1)

    # Get just the columns we need
    df = df[['INDEX', 'TYPE', 'RT', 'ACC', 'RESP', 'ONSET']]

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
