import glob

import pandas as pd


ROOTDIR = '/OUTPUTS'


def load_subject(subj_dir):
    dfv = pd.read_csv(f'{subj_dir}/stats/gtmseg.stats', comment='#', header=None, sep='\s+', usecols=[3,4], names=['VOL' ,'ROI'])
    dfg = pd.read_csv(f'{subj_dir}/gtmpvc.esupravwm.output/gtm.stats.dat', header=None, sep='\s+', usecols=[2,6], names=['ROI', 'SUVR-GTM'])
    dfn = pd.read_csv(f'{subj_dir}/gtmpvc.esupravwm.output/nopvc.voxel.txt', header=None, sep='\s+', names=['SUVR-NOPVC'])

    # Load esupravwm volume
    dfe = pd.read_csv(f'{subj_dir}/esupravwm.volume.txt', header=None, names=['VOL'])
    dfe['ROI'] = 'esupravwm'
    dfe['SUVR-NOPVC'] = 1.0
    dfe['SUVR-GTM'] =  1.0

    # Get a new dataframe with ROI first
    df = dfg[['ROI', 'SUVR-GTM']]

    # Append the column for nopvc, we know it sorted the same
    df['SUVR-NOPVC'] = dfn['SUVR-NOPVC']

    # Merge in the volumes
    df = df.merge(dfv, on='ROI')

    # Append the row for esupravwm
    df = pd.concat([df, dfe])

    return df


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

print('DONE!')
