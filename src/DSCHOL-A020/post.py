import glob

import pandas as pd


ROOTDIR = '/OUTPUTS'


def load_subject(subj_dir):
    dfv = pd.read_csv(f'{subj_dir}/stats/gtmseg.stats', comment='#', header=None, sep='\s+', usecols=[3,4], names=['VOL' ,'ROI'])
    dfg = pd.read_csv(f'{subj_dir}/gtmpvc.esupravwm.output/gtm.stats.dat', header=None, sep='\s+', usecols=[2,6], names=['ROI', 'SUVR-GTM'])
    dfn = pd.read_csv(f'{subj_dir}/gtmpvc.esupravwm.output/nopvc.voxel.txt', header=None, sep='\s+', names=['SUVR-NOPVC'])

    # Sum volumes


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


def save_volumes(df):
    dfp = df[['ROI', 'VOL', 'SUBJECT']].pivot(columns='ROI', values='VOL', index='SUBJECT')

    dfp['cblm'] = \
        dfp['Left-Cerebellum-Cortex'] + \
        dfp['Left-Cerebellum-White-Matter'] + \
        dfp['Right-Cerebellum-Cortex'] + \
        dfp['Right-Cerebellum-White-Matter'] + \
        dfp['Vermis']

    dfp['flobe'] = \
        dfp['ctx-lh-caudalmiddlefrontal'] + \
        dfp['ctx-lh-frontalpole'] + \
        dfp['ctx-lh-lateralorbitofrontal'] + \
        dfp['ctx-lh-medialorbitofrontal'] + \
        dfp['ctx-lh-paracentral'] + \
        dfp['ctx-lh-parsopercularis'] + \
        dfp['ctx-lh-parsorbitalis'] + \
        dfp['ctx-lh-parstriangularis'] + \
        dfp['ctx-lh-precentral'] + \
        dfp['ctx-lh-rostralmiddlefrontal'] + \
        dfp['ctx-lh-superiorfrontal'] + \
        dfp['ctx-rh-caudalmiddlefrontal'] + \
        dfp['ctx-rh-frontalpole'] + \
        dfp['ctx-rh-lateralorbitofrontal'] + \
        dfp['ctx-rh-medialorbitofrontal'] + \
        dfp['ctx-rh-paracentral'] + \
        dfp['ctx-rh-parsopercularis'] + \
        dfp['ctx-rh-parsorbitalis'] + \
        dfp['ctx-rh-parstriangularis'] + \
        dfp['ctx-rh-precentral'] + \
        dfp['ctx-rh-rostralmiddlefrontal'] + \
        dfp['ctx-rh-superiorfrontal']

    dfp['plobe'] = \
        dfp['ctx-lh-inferiorparietal'] + \
        dfp['ctx-lh-postcentral'] + \
        dfp['ctx-lh-precuneus'] + \
        dfp['ctx-lh-superiorparietal'] + \
        dfp['ctx-lh-supramarginal'] + \
        dfp['ctx-rh-inferiorparietal'] + \
        dfp['ctx-rh-postcentral'] + \
        dfp['ctx-rh-precuneus'] + \
        dfp['ctx-rh-superiorparietal'] + \
        dfp['ctx-rh-supramarginal']

    dfp['tlobe'] = \
        dfp['ctx-lh-bankssts'] + \
        dfp['ctx-lh-entorhinal'] + \
        dfp['ctx-lh-fusiform'] + \
        dfp['ctx-lh-inferiortemporal'] + \
        dfp['ctx-lh-middletemporal'] + \
        dfp['ctx-lh-parahippocampal'] + \
        dfp['ctx-lh-superiortemporal'] + \
        dfp['ctx-lh-temporalpole'] + \
        dfp['ctx-lh-transversetemporal'] + \
        dfp['ctx-rh-bankssts'] + \
        dfp['ctx-rh-entorhinal'] + \
        dfp['ctx-rh-fusiform'] + \
        dfp['ctx-rh-inferiortemporal'] + \
        dfp['ctx-rh-middletemporal'] + \
        dfp['ctx-rh-parahippocampal'] + \
        dfp['ctx-rh-superiortemporal'] + \
        dfp['ctx-rh-temporalpole'] + \
        dfp['ctx-rh-transversetemporal']

    dfp['olobe'] = \
        dfp['ctx-lh-cuneus'] + \
        dfp['ctx-lh-lateraloccipital'] + \
        dfp['ctx-lh-lingual'] + \
        dfp['ctx-lh-pericalcarine'] + \
        dfp['ctx-rh-cuneus'] + \
        dfp['ctx-rh-lateraloccipital'] + \
        dfp['ctx-rh-lingual'] + \
        dfp['ctx-rh-pericalcarine']

    dfp['cingulate'] = \
        dfp['ctx-lh-caudalanteriorcingulate'] + \
        dfp['ctx-lh-isthmuscingulate'] + \
        dfp['ctx-lh-posteriorcingulate'] + \
        dfp['ctx-lh-rostralanteriorcingulate'] + \
        dfp['ctx-rh-caudalanteriorcingulate'] + \
        dfp['ctx-rh-isthmuscingulate'] + \
        dfp['ctx-rh-posteriorcingulate'] + \
        dfp['ctx-rh-rostralanteriorcingulate']

    dfp['thalamus'] = dfp['Left-Thalamus'] + dfp['Right-Thalamus']
    dfp['hippocampus'] = dfp['Left-Hippocampus'] + dfp['Right-Hippocampus']
    dfp['insula'] = dfp['ctx-lh-insula'] + dfp['ctx-rh-insula']
    dfp = dfp[['flobe', 'olobe', 'plobe', 'tlobe', 'cblm', 'insula', 'thalamus', 'cingulate', 'hippocampus']]
    dfp.to_csv(f'{ROOTDIR}/volumes.csv')


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

print('DONE!')
