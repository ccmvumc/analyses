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


def save_volumes(df):
    dfp = df[['ROI', 'VOL', 'SUBJECT']].pivot(
        columns='ROI', values='VOL', index='SUBJECT')

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
    dfp = dfp[['flobe', 'olobe', 'plobe', 'tlobe', 'cblm', 'insula', 'thalamus', 'cingulate', 'hippocampus', 'esupravwm']]
    dfp.to_csv(f'{ROOTDIR}/volumes.csv')


def save_suvr(df):
    dfp = df[['ROI', 'SUVR-NOPVC', 'SUBJECT']].pivot(
        columns='ROI', values='SUVR-NOPVC', index='SUBJECT')

    dfp['cblm'] = \
        (dfp['Left-Cerebellum-Cortex'] + \
        dfp['Left-Cerebellum-White-Matter'] + \
        dfp['Right-Cerebellum-Cortex'] + \
        dfp['Right-Cerebellum-White-Matter'] + \
        dfp['Vermis']) / 5.0

    dfp['flobe'] = \
        (dfp['ctx-lh-caudalmiddlefrontal'] + \
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
        dfp['ctx-rh-superiorfrontal']) / 22.0

    dfp['caudalmiddlefrontal'] = \
        (dfp['ctx-lh-caudalmiddlefrontal'] + dfp['ctx-rh-caudalmiddlefrontal']) / 2.0

    dfp['frontalpole'] = \
        (dfp['ctx-lh-frontalpole'] + dfp['ctx-rh-frontalpole']) / 2.0

    dfp['lateralorbitofrontal'] = \
        (dfp['ctx-lh-lateralorbitofrontal'] + dfp['ctx-rh-lateralorbitofrontal']) / 2.0

    dfp['medialorbitofrontal'] = \
        (dfp['ctx-lh-medialorbitofrontal'] + dfp['ctx-rh-medialorbitofrontal']) / 2.0

    dfp['paracentral'] = \
        (dfp['ctx-lh-paracentral'] + dfp['ctx-rh-paracentral']) / 2.0

    dfp['parsopercularis'] = \
        (dfp['ctx-lh-parsopercularis'] + dfp['ctx-rh-parsopercularis']) / 2.0

    dfp['parsorbitalis'] = \
        (dfp['ctx-lh-parsorbitalis'] + dfp['ctx-rh-parsorbitalis']) / 2.0

    dfp['parstriangularis'] = \
        (dfp['ctx-lh-parstriangularis'] + dfp['ctx-rh-parstriangularis']) / 2.0

    dfp['precentral'] = \
        (dfp['ctx-lh-precentral'] + dfp['ctx-rh-precentral']) / 2.0

    dfp['rostralmiddlefrontal'] = \
        (dfp['ctx-lh-rostralmiddlefrontal'] + dfp['ctx-rh-rostralmiddlefrontal']) / 2.0

    dfp['superiorfrontal'] = \
        (dfp['ctx-lh-superiorfrontal'] + dfp['ctx-rh-superiorfrontal']) / 2.0

    dfp['plobe'] = \
        (dfp['ctx-lh-inferiorparietal'] + \
        dfp['ctx-lh-postcentral'] + \
        dfp['ctx-lh-precuneus'] + \
        dfp['ctx-lh-superiorparietal'] + \
        dfp['ctx-lh-supramarginal'] + \
        dfp['ctx-rh-inferiorparietal'] + \
        dfp['ctx-rh-postcentral'] + \
        dfp['ctx-rh-precuneus'] + \
        dfp['ctx-rh-superiorparietal'] + \
        dfp['ctx-rh-supramarginal']) / 10.0

    dfp['inferiorparietal'] =\
        (dfp['ctc-lh-inferiorparietal'] + dfp['ctc-rh-inferiorparietal']) / 2.0

    dfp['postcentral'] =\
        (dfp['ctx-lh-postcentral'] + dfp['ctx-rh-postcentral']) / 2.0

    dfp['precuneus'] =\
        (dfp['ctx-lh-precuneus'] + dfp['ctx-rh-precuneus']) / 2.0

    dfp['superiorparietal'] =\
        (dfp['ctx-lh-superiorparietal'] + dfp['ctx-rh-superiorparietal']) / 2.0

    dfp['supramarginal'] =\
        (dfp['ctx_lh_supramarginal'] + dfp['ctx_rh_supramarginal']) / 2.0

    dfp['tlobe'] = \
        (dfp['ctx-lh-bankssts'] + \
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
        dfp['ctx-rh-transversetemporal']) / 18.0

    dfp['bankssts'] =\
        (dfp['ctx-lh-bankssts'] + dfp['ctx-rh-bankssts']) / 2.0

    dfp['entorhinal'] =\
        (dfp['ctx-lh-entorhinal'] + dfp['ctx-rh-entorhinal']) / 2.0

    dfp['fusiform'] =\
        (dfp['ctx-lh-fusiform'] + dfp['ctx-rh-fusiform']) / 2.0

    dfp['inferiortemporal'] = \
        (dfp['ctx-lh-inferiortemporal'] + dfp['ctx-rh-inferiortemporal']) / 2.0

    dfp['middletemporal'] = \
        (dfp['ctx-lh-middletemporal'] + dfp['ctx-rh-middletemporal']) / 2.0

    dfp['parahippocampal'] = \
        (dfp['ctx-lh-parahippocampal'] + dfp['ctx-rh-parahippocampal']) / 2.0

    dfp['superiortemporal'] =\
        (dfp['ctx-lh-superiortemporal'] + dfp['ctx-rh-superiortemporal']) / 2.0

    dfp['temporalpole'] =\
        (dfp['ctx-lh-temporalpole'] + dfp['ctx-rh-temporalpole']) / 2.0

    dfp['transversetemporal'] =\
        (dfp['ctx-lh-transversetemporal'] + dfp['ctx-rh-transversetemporal']) / 2.0

    dfp['olobe'] = \
        (dfp['ctx-lh-cuneus'] + \
        dfp['ctx-lh-lateraloccipital'] + \
        dfp['ctx-lh-lingual'] + \
        dfp['ctx-lh-pericalcarine'] + \
        dfp['ctx-rh-cuneus'] + \
        dfp['ctx-rh-lateraloccipital'] + \
        dfp['ctx-rh-lingual'] + \
        dfp['ctx-rh-pericalcarine']) / 8.0

    dfp['cuneus'] = \
        (dfp['ctx-lh-cuneus'] + dfp['ctx-rh-cuneus']) / 2.0

    dfp['lateraloccipital'] = \
        (dfp['ctx-lh-lateraloccipital'] + dfp['ctx-rh-lateraloccipital']) / 2.0

    dfp['lingual'] = \
        (dfp['ctx-lh-lingual'] + dfp['ctx-rh-lingual']) / 2.0

    dfp['pericalcarine'] = \
        (dfp['ctx-lh-pericalcarine'] + dfp['ctx-rh-pericalcarine']) / 2.0

    dfp['cingulate'] = \
        (dfp['ctx-lh-caudalanteriorcingulate'] + \
        dfp['ctx-lh-isthmuscingulate'] + \
        dfp['ctx-lh-posteriorcingulate'] + \
        dfp['ctx-lh-rostralanteriorcingulate'] + \
        dfp['ctx-rh-caudalanteriorcingulate'] + \
        dfp['ctx-rh-isthmuscingulate'] + \
        dfp['ctx-rh-posteriorcingulate'] + \
        dfp['ctx-rh-rostralanteriorcingulate']) / 8.0

    dfp['caudalanteriorcingulate'] = \
        (dfp['ctx-lh-caudalanteriorcingulate'] + dfp['ctx-rh-caudalanteriorcingulate']) / 2.0

    dfp['isthmuscingulate'] = \
        (dfp['ctx-lh-isthmuscingulate'] + dfp['ctx-rh-isthmuscingulate']) / 2.0

    dfp['posteriorcingulate'] = \
        (dfp['ctx-lh-posteriorcingulate'] + dfp['ctx-rh-posteriorcingulate']) / 2.0

    dfp['rostralanteriorcingulate'] = \
        (dfp['ctx-lh-rostralanteriorcingulate'] + dfp['ctx-rh-rostralanteriorcingulate']) / 2.0

    dfp['thalamus'] = (dfp['Left-Thalamus'] + dfp['Right-Thalamus']) / 2.0
    dfp['hippocampus'] = (dfp['Left-Hippocampus'] + dfp['Right-Hippocampus']) / 2.0
    dfp['insula'] = (dfp['ctx-lh-insula'] + dfp['ctx-rh-insula']) / 2.0
    dfp['putamen'] = (dfp['Left-Putamen'] + dfp['Right-Putamen']) / 2.0
    dfp['pallidum'] = (dfp['Left-Pallidum'] + dfp['Right-Pallidum']) / 2.0
    dfp['amygdala'] = (dfp['Left-Amygdala'] + dfp['Right-Amygdala']) / 2.0


    dfp_all = dfp[['caudalmiddlefrontal', 'frontalpole', 'lateralorbitofrontal', 'medialorbitofrontal','paracentral', \
                   'parsopercularis', 'parstriangularis', 'precentral', 'rostralmiddlefrontal', 'superiorfrontal', \
                   'inferiorparietal', 'precuneus', 'superiorparietal', 'supramarginal', 'bankssts', 'entorhinal', \
                   'fusiform', 'inferiortemporal', 'middletemporal', 'parahippocampal', 'superiortemporal', 'temporalpole', \
                   'transversetemporal', 'cuneus', 'lateraloccipital', 'lingual', 'pericalcarine', 'caudalanteriorcingulate', \
                   'isthmuscingulate', 'posteriorcingulate', 'rostralanteriorcingulate', 'thalamus', 'hippocampus', 'insula',
                   'putamen', 'amygdala']]
    dfp = dfp[['flobe', 'olobe', 'plobe', 'tlobe', 'cblm', 'insula', 'thalamus', 'cingulate', 'hippocampus', 'esupravwm']]
    dfp.to_csv(f'{ROOTDIR}/suvr.csv')
    dfp_all.to_csv(f'{ROOTDIR}/suvr_extended.csv')


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
