import pandas as pd


ZDIR = '/OUTPUTS'
INFILE = f'{ZDIR}/zvalues.csv'
OUTFILE_000 = f'{ZDIR}/zvalues-Schaefer000.csv'
OUTFILE_100 = f'{ZDIR}/zvalues-Schaefer100.csv'
OUTFILE_200 = f'{ZDIR}/Users/boydb1/Desktop/zvalues-Schaefer200.csv'
OUTFILE_400 = '/Users/boydb1/Desktop/zvalues-Schaefer400.csv'


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

    condition = df.r1region.isna()
    extracted_values = df.loc[condition, 'r1name'].str.extract(r'[^.]*\.([^.]*)$')
    df.loc[condition, 'r1region'] = extracted_values[0]

    condition = df.r2region.isna()
    extracted_values = df.loc[condition, 'r2name'].str.extract(r'[^.]*\.([^.]*)$')
    df.loc[condition, 'r2region'] = extracted_values[0]

    # Now make the concat'd names
    df['r1n'] = df[['r1atlas', 'r1hemi', 'r1network', 'r1region']].apply(lambda x : x.str.cat(sep='.'), 1)
    df['r2n'] = df[['r2atlas', 'r2hemi', 'r2network', 'r2region']].apply(lambda x : x.str.cat(sep='.'), 1)

    df.r1hemi = df.r1hemi.fillna('')
    df.r2hemi = df.r2hemi.fillna('')
    df.r1network = df.r1network.fillna('')
    df.r2network = df.r2network.fillna('')
    df.r1region = df.r1region.fillna('')
    df.r2region = df.r2region.fillna('')

    return df

# Read, add columns, overwrite

df = pd.read_csv(INFILE)

# No Schaefers
df[
    (~df.r1name.str.startswith('Schaefer')) &
    (~df.r2name.str.startswith('Schaefer'))
].to_csv(OUTFILE_000, index=False)

# Now with Schafer100
df[
    (~df.r1name.str.startswith('Schaefer200')) & 
    (~df.r2name.str.startswith('Schaefer200')) & 
    (~df.r1name.str.startswith('Schaefer400')) & 
    (~df.r2name.str.startswith('Schaefer400'))
].to_csv(OUTFILE_100, index=False)

# Now with Schafer200
df[
    (~df.r1name.str.startswith('Schaefer100')) & 
    (~df.r2name.str.startswith('Schaefer100')) & 
    (~df.r1name.str.startswith('Schaefer400')) & 
    (~df.r2name.str.startswith('Schaefer400'))
].to_csv(OUTFILE_200, index=False)

# Now with Schafer400
df[
    (~df.r1name.str.startswith('Schaefer100')) & 
    (~df.r2name.str.startswith('Schaefer100')) & 
    (~df.r1name.str.startswith('Schaefer200')) & 
    (~df.r2name.str.startswith('Schaefer200'))
].to_csv(OUTFILE_400, index=False)

# Add cleaned names
for f in [OUTFILE_000, OUTFILE_100, OUTFILE_200, OUTFILE_400]:
    print(f)
    df = pd.read_csv(f)
    df = get_names(df)
    df.to_csv(f)
    print(df)
