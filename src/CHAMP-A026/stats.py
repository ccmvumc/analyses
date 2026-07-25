import glob

import pandas as pd


ROOTDIR = '/OUTPUTS'


def load_subject(subj_dir):
    dfv = pd.read_csv(f'{subj_dir}/stats/gtmseg.stats', comment='#', header=None, sep='\s+', usecols=[3,4], names=['VOL' ,'ROI'])
    dfg = pd.read_csv(f'{subj_dir}/gtmpvc.esupravwm.output/gtm.stats.dat', header=None, sep='\s+', usecols=[2,6], names=['ROI', 'SUVR-GTM'])

    # Get a new dataframe with ROI first
    df = dfg[['ROI', 'SUVR-GTM']]

    # Merge in the volumes
    df = df.merge(dfv, on='ROI')

    return df


def save_volumes(df):
    dfp = df[['ROI', 'VOL', 'SUBJECT']].pivot(
        columns='ROI',
        values='VOL',
        index='SUBJECT')

    dfp.to_csv(f'{ROOTDIR}/volumes.csv')


def save_suvr(df):
    dfp = df[['ROI', 'SUVR-NOPVC', 'SUBJECT']].pivot(
        columns='ROI',
        values='SUVR-NOPVC', 
        index='SUBJECT')
    
    dfp.to_csv(f'{ROOTDIR}/suvr.csv')


# Start an empty dataframe
df = pd.DataFrame()

# Append each subject
for s in glob.glob(f'{ROOTDIR}/DATA/SUBJECTS/*'):
    subj = load_subject(s)
    subj['SUBJECT'] = s.rsplit('/', 1)[1]
    df = pd.concat([df, subj])

# Sort and save
df = df.sort_values(['SUBJECT', 'ROI'])
df.to_csv(f'{ROOTDIR}/all.csv', index=False)
save_volumes(df)
save_suvr(df)

print('DONE!')
