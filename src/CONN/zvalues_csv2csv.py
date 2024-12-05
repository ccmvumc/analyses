import pandas as pd


ZFILE = '/OUTPUTS/zvalues.csv'


def get_names(df):
    # Get atlas name before first period
    df['r1atlas'] = df['r1name'].str.extract(r'([^.]*)')
    df['r2atlas'] = df['r2name'].str.extract(r'([^.]*)')

    # hemisphere is after period, between two underscores
    df['r1hemi'] = df['r1name'].str.extract(r'\.[^_]+_([^_]+)_')
    df['r2hemi'] = df['r2name'].str.extract(r'\.[^_]+_([^_]+)_')
    
    # network is after period, between 2nd and 3rd underscores
    df['r1network'] = df['r1name'].str.extract(r'\.[^_]*_(?:[^_]*_){1}([^_]+)_')
    df['r2network'] = df['r2name'].str.extract(r'\.[^_]*_(?:[^_]*_){1}([^_]+)_')

    # region is after last underscore
    df['r1region'] = df['r1name'].str.extract(r'(?:[^_]*_){3}(.*)')
    df['r2region'] = df['r2name'].str.extract(r'(?:[^_]*_){3}(.*)')

    # handle schaefer400 with different format
    condition = df['r1atlas'] == 'Schaefer400'
    extracted_values = df.loc[condition, 'r1name'].str.extract(r'(?:[^_]*_){2}([^_]+)_')
    df.loc[condition, 'r1hemi'] = extracted_values[0]
    extracted_values = df.loc[condition, 'r1name'].str.extract(r'(?:[^_]*_){3}([^_]+)_')
    df.loc[condition, 'r1network'] = extracted_values[0]
    extracted_values = df.loc[condition, 'r1name'].str.extract(r'(?:[^_]*_){4}(.*)')
    df.loc[condition, 'r1region'] = extracted_values[0]

    condition = df['r2atlas'] == 'Schaefer400'
    extracted_values = df.loc[condition, 'r2name'].str.extract(r'(?:[^_]*_){2}([^_]+)_')
    df.loc[condition, 'r2hemi'] = extracted_values[0]
    extracted_values = df.loc[condition, 'r2name'].str.extract(r'(?:[^_]*_){3}([^_]+)_')
    df.loc[condition, 'r2network'] = extracted_values[0]
    extracted_values = df.loc[condition, 'r2name'].str.extract(r'(?:[^_]*_){4}(.*)')
    df.loc[condition, 'r2region'] = extracted_values[0]

    # handle CONN toolbox networks atlas format
    condition = df['r1atlas'] == 'networks'
    extracted_values = df.loc[condition, 'r1name'].str.extract(r'\.([^\.]*)\.')
    df.loc[condition, 'r1network'] = extracted_values[0]
    condition = df['r2atlas'] == 'networks'
    extracted_values = df.loc[condition, 'r2name'].str.extract(r'\.([^\.]*)\.')
    df.loc[condition, 'r2network'] = extracted_values[0]

    # handle those with hemisphere in name
    condition = df.r1atlas.str.endswith('_lh')
    df.loc[condition, 'r1hemi'] = 'LH'
    condition = df.r1atlas.str.endswith('_rh')
    df.loc[condition, 'r1hemi'] = 'RH'

    condition = df.r2atlas.str.endswith('_lh')
    df.loc[condition, 'r2hemi'] = 'LH'
    condition = df.r2atlas.str.endswith('_rh')
    df.loc[condition, 'r2hemi'] = 'RH'

    # Fill in the rest
    condition = df.r1hemi.isna()
    df.loc[condition, 'r1hemi'] = 'XH'

    condition = df.r2hemi.isna()
    df.loc[condition, 'r2hemi'] = 'XH'

    # Get the network name after first period
    condition = df.r1network.isna()
    extracted_values = df.loc[condition, 'r1name'].str.extract(r'\.([^\.]*)\.|^(.*)$')
    df.loc[condition, 'r1network'] = extracted_values[0]

    condition = df.r2network.isna()
    extracted_values = df.loc[condition, 'r2name'].str.extract(r'\.([^\.]*)\.|^(.*)$')
    df.loc[condition, 'r2network'] = extracted_values[0]

    condition = df.r1network.isna()
    extracted_values = df.loc[condition, 'r1name'].str.extract(r'([^.]*)')
    df.loc[condition, 'r1network'] = extracted_values[0]

    condition = df.r2network.isna()
    extracted_values = df.loc[condition, 'r2name'].str.extract(r'([^.]*)')
    df.loc[condition, 'r2network'] = extracted_values[0]

    condition = df.r2region.isna()
    extracted_values = df.loc[condition, 'r2name'].str.extract(r'[^.]*\.([^.]*)$')
    df.loc[condition, 'r2region'] = extracted_values[0]

    # Still blank so use the name as region
    condition = df.r1region.isna()
    extracted_values = df.loc[condition, 'r1name']
    df.loc[condition, 'r1region'] = extracted_values[0]

    condition = df.r2region.isna()
    extracted_values = df.loc[condition, 'r2name']
    df.loc[condition, 'r2region'] = extracted_values[0]

    # Now make the concat'd names
    df['r1n'] = df['r1atlas'] + '.' + df['r1hemi'] + '.' + df['r1network'] + '.' + df['r1region']
    df['r2n'] = df['r2atlas'] + '.' + df['r2hemi'] + '.' + df['r2network'] + '.' + df['r2region']

    return df


# Read, add columns, overwrite
df = pd.read_csv(ZFILE)
df = get_names(df)
df.to_csv(ZFILE, index=False)
print(df)
