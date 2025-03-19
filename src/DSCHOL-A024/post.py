import glob

import pandas as pd


ROOTDIR = '/OUTPUTS'


def load_subject(subj_dir):
    dfv = pd.read_csv(f'{subj_dir}/stats/gtmseg.stats', comment='#', header=None, sep='\s+', usecols=[3,4], names=['VOL' ,'ROI'])
    dfg = pd.read_csv(f'{subj_dir}/gtmpvc.cblmgmwm.output/gtm.stats.dat', header=None, sep='\s+', usecols=[2,6], names=['ROI', 'SUVR-GTM'])
    dfn = pd.read_csv(f'{subj_dir}/gtmpvc.cblmgmwm.output/nopvc.voxel.txt', header=None, sep='\s+', names=['SUVR-NOPVC'])

    # Get a new dataframe with ROI first
    df = dfg[['ROI', 'SUVR-GTM']]

    # Append the column for nopvc, we know it sorted the same
    df['SUVR-NOPVC'] = dfn['SUVR-NOPVC']

    # Merge in the volumes
    df = df.merge(dfv, on='ROI')

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
    dfp = dfp[['flobe', 'olobe', 'plobe', 'tlobe', 'cblm', 'insula', 'thalamus', 'cingulate', 'hippocampus']]
    dfp.to_csv(f'{ROOTDIR}/volumes.csv')


def save_suvr_gtm(df):
    dfp = df[['ROI', 'SUVR-GTM', 'SUBJECT']].pivot(
        columns='ROI', values='SUVR-GTM', index='SUBJECT')

    dfvol = df[['ROI', 'VOL', 'SUBJECT']].pivot(
        columns='ROI', values='VOL', index='SUBJECT')

    cblm_vol = \
        dfvol['Left-Cerebellum-Cortex'] + \
        dfvol['Left-Cerebellum-White-Matter'] + \
        dfvol['Right-Cerebellum-Cortex'] + \
        dfvol['Right-Cerebellum-White-Matter'] + \
        dfvol['Vermis']

    dfp['cblm'] = \
        dfp['Left-Cerebellum-Cortex']*(dfvol['Left-Cerebellum-Cortex']/(cblm_vol)) + \
        dfp['Left-Cerebellum-White-Matter']*(dfvol['Left-Cerebellum-White-Matter']/(cblm_vol))  + \
        dfp['Right-Cerebellum-Cortex']*(dfvol['Right-Cerebellum-Cortex']/(cblm_vol)) + \
        dfp['Right-Cerebellum-White-Matter']*(dfvol['Right-Cerebellum-White-Matter']/(cblm_vol)) + \
        dfp['Vermis'] *(dfvol['Vermis']/(cblm_vol))

    flobe_vol = \
        dfvol['ctx-lh-caudalmiddlefrontal'] + \
        dfvol['ctx-lh-frontalpole'] + \
        dfvol['ctx-lh-lateralorbitofrontal'] + \
        dfvol['ctx-lh-medialorbitofrontal'] + \
        dfvol['ctx-lh-paracentral'] + \
        dfvol['ctx-lh-parsopercularis'] + \
        dfvol['ctx-lh-parsorbitalis'] + \
        dfvol['ctx-lh-parstriangularis'] + \
        dfvol['ctx-lh-precentral'] + \
        dfvol['ctx-lh-rostralmiddlefrontal'] + \
        dfvol['ctx-lh-superiorfrontal'] + \
        dfvol['ctx-rh-caudalmiddlefrontal'] + \
        dfvol['ctx-rh-frontalpole'] + \
        dfvol['ctx-rh-lateralorbitofrontal'] + \
        dfvol['ctx-rh-medialorbitofrontal'] + \
        dfvol['ctx-rh-paracentral'] + \
        dfvol['ctx-rh-parsopercularis'] + \
        dfvol['ctx-rh-parsorbitalis'] + \
        dfvol['ctx-rh-parstriangularis'] + \
        dfvol['ctx-rh-precentral'] + \
        dfvol['ctx-rh-rostralmiddlefrontal'] + \
        dfvol['ctx-rh-superiorfrontal']

    dfp['flobe'] = (
            dfp['ctx-lh-caudalmiddlefrontal'] * (dfvol['ctx-lh-caudalmiddlefrontal'] / flobe_vol) + \
            dfp['ctx-lh-frontalpole'] * (dfvol['ctx-lh-frontalpole'] / flobe_vol) + \
            dfp['ctx-lh-lateralorbitofrontal'] * (dfvol['ctx-lh-lateralorbitofrontal'] / flobe_vol) + \
            dfp['ctx-lh-medialorbitofrontal'] * (dfvol['ctx-lh-medialorbitofrontal'] / flobe_vol) + \
            dfp['ctx-lh-paracentral'] * (dfvol['ctx-lh-paracentral'] / flobe_vol) + \
            dfp['ctx-lh-parsopercularis'] * (dfvol['ctx-lh-parsopercularis'] / flobe_vol) + \
            dfp['ctx-lh-parsorbitalis'] * (dfvol['ctx-lh-parsorbitalis'] / flobe_vol) + \
            dfp['ctx-lh-parstriangularis'] * (dfvol['ctx-lh-parstriangularis'] / flobe_vol) + \
            dfp['ctx-lh-precentral'] * (dfvol['ctx-lh-precentral'] / flobe_vol) + \
            dfp['ctx-lh-rostralmiddlefrontal'] * (dfvol['ctx-lh-rostralmiddlefrontal'] / flobe_vol) + \
            dfp['ctx-lh-superiorfrontal'] * (dfvol['ctx-lh-superiorfrontal'] / flobe_vol) + \
            dfp['ctx-rh-caudalmiddlefrontal'] * (dfvol['ctx-rh-caudalmiddlefrontal'] / flobe_vol) + \
            dfp['ctx-rh-frontalpole'] * (dfvol['ctx-rh-frontalpole'] / flobe_vol) + \
            dfp['ctx-rh-lateralorbitofrontal'] * (dfvol['ctx-rh-lateralorbitofrontal'] / flobe_vol) + \
            dfp['ctx-rh-medialorbitofrontal'] * (dfvol['ctx-rh-medialorbitofrontal'] / flobe_vol) + \
            dfp['ctx-rh-paracentral'] * (dfvol['ctx-rh-paracentral'] / flobe_vol) + \
            dfp['ctx-rh-parsopercularis'] * (dfvol['ctx-rh-parsopercularis'] / flobe_vol) + \
            dfp['ctx-rh-parsorbitalis'] * (dfvol['ctx-rh-parsorbitalis'] / flobe_vol) + \
            dfp['ctx-rh-parstriangularis'] * (dfvol['ctx-rh-parstriangularis'] / flobe_vol) + \
            dfp['ctx-rh-precentral'] * (dfvol['ctx-rh-precentral'] / flobe_vol) + \
            dfp['ctx-rh-rostralmiddlefrontal'] * (dfvol['ctx-rh-rostralmiddlefrontal'] / flobe_vol) + \
            dfp['ctx-rh-superiorfrontal'] * (dfvol['ctx-rh-superiorfrontal'] / flobe_vol)
    )

    caudalmiddlefrontal_vol = dfvol['ctx-lh-caudalmiddlefrontal'] + dfvol['ctx-rh-caudalmiddlefrontal']

    dfp['caudalmiddlefrontal'] = \
        dfp['ctx-lh-caudalmiddlefrontal'] * (dfvol['ctx-lh-caudalmiddlefrontal'] / caudalmiddlefrontal_vol) + \
        dfp['ctx-rh-caudalmiddlefrontal'] * (dfvol['ctx-rh-caudalmiddlefrontal'] / caudalmiddlefrontal_vol)

    frontalpole_vol = dfvol['ctx-lh-caudalmiddlefrontal'] + dfvol['ctx-rh-caudalmiddlefrontal']

    dfp['frontalpole'] = \
         dfp['ctx-lh-frontalpole'] * (dfvol['ctx-lh-caudalmiddlefrontal'] / frontalpole_vol) + \
         dfp['ctx-rh-frontalpole'] * (dfvol['ctx-rh-caudalmiddlefrontal'] / frontalpole_vol)

    lateralorbitalfrontal_vol = dfvol['ctx-lh-lateralorbitofrontal'] + dfvol['ctx-rh-lateralorbitofrontal']
    dfp['lateralorbitofrontal'] = \
         dfp['ctx-lh-lateralorbitofrontal'] * (dfvol['ctx-lh-lateralorbitofrontal'] / lateralorbitalfrontal_vol) + \
         dfp['ctx-rh-lateralorbitofrontal'] * (dfvol['ctx-rh-lateralorbitofrontal'] / lateralorbitalfrontal_vol)

    medialorbitofrontal_vol = dfvol['ctx-lh-medialorbitofrontal'] + dfvol['ctx-rh-medialorbitofrontal']
    dfp['medialorbitofrontal'] = \
        dfp['ctx-lh-medialorbitofrontal'] * (dfvol['ctx-lh-medialorbitofrontal'] / medialorbitofrontal_vol) + \
        dfp['ctx-rh-medialorbitofrontal'] * (dfvol['ctx-rh-medialorbitofrontal'] / medialorbitofrontal_vol)

    paracentral_vol = dfvol['ctx-lh-paracentral'] + dfvol['ctx-rh-paracentral']
    dfp['paracentral'] = \
        dfp['ctx-lh-paracentral'] * (dfvol['ctx-lh-paracentral'] / paracentral_vol) + \
        dfp['ctx-rh-paracentral'] * (dfvol['ctx-rh-paracentral'] / paracentral_vol)

    parsopercularis_vol = dfvol['ctx-lh-parsopercularis'] + dfvol['ctx-rh-parsopercularis']
    dfp['parsopercularis'] = \
        dfp['ctx-lh-parsopercularis'] * (dfvol['ctx-lh-parsopercularis'] / parsopercularis_vol) + \
        dfp['ctx-rh-parsopercularis'] * (dfvol['ctx-rh-parsopercularis'] / parsopercularis_vol)

    parsorbitalis_vol = dfvol['ctx-lh-parsorbitalis'] + dfvol['ctx-rh-parsorbitalis']
    dfp['parsorbitalis'] = \
        dfp['ctx-lh-parsorbitalis'] * (dfvol['ctx-lh-parsorbitalis'] / parsorbitalis_vol) + \
        dfp['ctx-rh-parsorbitalis'] * (dfvol['ctx-rh-parsorbitalis'] / parsorbitalis_vol)

    parstriangularis_vol = dfvol['ctx-lh-parstriangularis'] + dfvol['ctx-rh-parstriangularis']
    dfp['parstriangularis'] = \
        dfp['ctx-lh-parstriangularis'] * (dfvol['ctx-lh-parstriangularis'] / parstriangularis_vol) + \
        dfp['ctx-rh-parstriangularis'] * (dfvol['ctx-rh-parstriangularis'] / parstriangularis_vol)

    precentral_vol = dfvol['ctx-lh-precentral'] + dfvol['ctx-rh-precentral']
    dfp['precentral'] = \
        dfp['ctx-lh-precentral'] * (dfvol['ctx-lh-precentral'] / precentral_vol) + \
        dfp['ctx-rh-precentral'] * (dfvol['ctx-rh-precentral'] / precentral_vol)

    rostralmiddlefrontal_vol = dfvol['ctx-lh-rostralmiddlefrontal'] + dfvol['ctx-rh-rostralmiddlefrontal']
    dfp['rostralmiddlefrontal'] = \
        dfp['ctx-lh-rostralmiddlefrontal'] * (dfvol['ctx-lh-rostralmiddlefrontal'] / rostralmiddlefrontal_vol) + \
        dfp['ctx-rh-rostralmiddlefrontal'] * (dfvol['ctx-rh-rostralmiddlefrontal'] / rostralmiddlefrontal_vol)

    superiorfrontal_vol = dfvol['ctx-lh-superiorfrontal'] + dfvol['ctx-rh-superiorfrontal']
    dfp['superiorfrontal'] = \
        dfp['ctx-lh-superiorfrontal'] * (dfvol['ctx-lh-superiorfrontal'] / superiorfrontal_vol) + \
        dfp['ctx-rh-superiorfrontal'] * (dfvol['ctx-rh-superiorfrontal'] / superiorfrontal_vol)

    plobe_vol = \
        dfvol['ctx-lh-inferiorparietal'] + \
        dfvol['ctx-lh-postcentral'] + \
        dfvol['ctx-lh-precuneus'] + \
        dfvol['ctx-lh-superiorparietal'] + \
        dfvol['ctx-lh-supramarginal'] + \
        dfvol['ctx-rh-inferiorparietal'] + \
        dfvol['ctx-rh-postcentral'] + \
        dfvol['ctx-rh-precuneus'] + \
        dfvol['ctx-rh-superiorparietal'] + \
        dfvol['ctx-rh-supramarginal']

    dfp['plobe'] = \
        dfp['ctx-lh-inferiorparietal'] * (dfvol['ctx-lh-inferiorparietal'] / plobe_vol) + \
        dfp['ctx-lh-postcentral'] * (dfvol['ctx-lh-postcentral'] / plobe_vol) + \
        dfp['ctx-lh-precuneus'] * (dfvol['ctx-lh-precuneus'] / plobe_vol) + \
        dfp['ctx-lh-superiorparietal'] * (dfvol['ctx-lh-superiorparietal'] / plobe_vol) + \
        dfp['ctx-lh-supramarginal'] * (dfvol['ctx-lh-supramarginal'] / plobe_vol) + \
        dfp['ctx-rh-inferiorparietal'] * (dfvol['ctx-rh-inferiorparietal'] / plobe_vol) + \
        dfp['ctx-rh-postcentral'] * (dfvol['ctx-rh-postcentral'] / plobe_vol) + \
        dfp['ctx-rh-precuneus'] * (dfvol['ctx-rh-precuneus'] / plobe_vol) + \
        dfp['ctx-rh-superiorparietal'] * (dfvol['ctx-rh-superiorparietal'] / plobe_vol) + \
        dfp['ctx-rh-supramarginal'] * (dfvol['ctx-rh-supramarginal'] / plobe_vol)

    inferiorparietal_vol = dfvol['ctx-lh-inferiorparietal'] + dfvol['ctx-rh-inferiorparietal']
    dfp['inferiorparietal'] =\
        dfp['ctx-lh-inferiorparietal'] * (dfvol['ctx-lh-inferiorparietal'] / inferiorparietal_vol) + \
        dfp['ctx-rh-inferiorparietal'] * (dfvol['ctx-rh-inferiorparietal'] / inferiorparietal_vol)

    postcentral_vol = dfvol['ctx-lh-postcentral'] + dfvol['ctx-rh-postcentral']
    dfp['postcentral'] =\
        dfp['ctx-lh-postcentral'] * (dfvol['ctx-lh-postcentral'] / postcentral_vol) + \
        dfp['ctx-rh-postcentral'] * (dfvol['ctx-rh-postcentral'] / postcentral_vol)

    precuneus_vol = dfvol['ctx-lh-precuneus'] + dfvol['ctx-rh-precuneus']
    dfp['precuneus'] =\
        dfp['ctx-lh-precuneus'] * (dfvol['ctx-lh-precuneus'] / precuneus_vol) + \
        dfp['ctx-rh-precuneus'] * (dfvol['ctx-rh-precuneus'] / precuneus_vol)

    superiorparietal_vol = dfvol['ctx-lh-superiorparietal'] + dfvol['ctx-rh-superiorparietal']
    dfp['superiorparietal'] =\
        dfp['ctx-lh-superiorparietal'] * (dfvol['ctx-lh-superiorparietal'] / superiorparietal_vol) + \
        dfp['ctx-rh-superiorparietal'] * (dfvol['ctx-rh-superiorparietal'] / superiorparietal_vol)

    supramarginal_vol = dfvol['ctx-lh-supramarginal'] + dfvol['ctx-rh-supramarginal']
    dfp['supramarginal'] =\
        dfp['ctx-lh-supramarginal'] * (dfvol['ctx-lh-supramarginal'] / supramarginal_vol) + \
        dfp['ctx-rh-supramarginal'] * (dfvol['ctx-rh-supramarginal'] / supramarginal_vol)

    tlobe_vol = \
        dfvol['ctx-lh-bankssts'] + \
        dfvol['ctx-lh-entorhinal'] + \
        dfvol['ctx-lh-fusiform'] + \
        dfvol['ctx-lh-inferiortemporal'] + \
        dfvol['ctx-lh-middletemporal'] + \
        dfvol['ctx-lh-parahippocampal'] + \
        dfvol['ctx-lh-superiortemporal'] + \
        dfvol['ctx-lh-temporalpole'] + \
        dfvol['ctx-lh-transversetemporal'] + \
        dfvol['ctx-rh-bankssts'] + \
        dfvol['ctx-rh-entorhinal'] + \
        dfvol['ctx-rh-fusiform'] + \
        dfvol['ctx-rh-inferiortemporal'] + \
        dfvol['ctx-rh-middletemporal'] + \
        dfvol['ctx-rh-parahippocampal'] + \
        dfvol['ctx-rh-superiortemporal'] + \
        dfvol['ctx-rh-temporalpole'] + \
        dfvol['ctx-rh-transversetemporal']

    dfp['tlobe'] = \
        dfp['ctx-lh-bankssts'] * (dfvol['ctx-lh-bankssts'] / tlobe_vol) + \
        dfp['ctx-lh-entorhinal'] * (dfvol['ctx-lh-entorhinal'] / tlobe_vol) + \
        dfp['ctx-lh-fusiform'] * (dfvol['ctx-lh-fusiform'] / tlobe_vol) + \
        dfp['ctx-lh-inferiortemporal'] * (dfvol['ctx-lh-inferiortemporal'] / tlobe_vol) + \
        dfp['ctx-lh-middletemporal'] * (dfvol['ctx-lh-middletemporal'] / tlobe_vol) + \
        dfp['ctx-lh-parahippocampal'] * (dfvol['ctx-lh-parahippocampal'] / tlobe_vol) + \
        dfp['ctx-lh-superiortemporal'] * (dfvol['ctx-lh-superiortemporal'] / tlobe_vol) + \
        dfp['ctx-lh-temporalpole'] * (dfvol['ctx-lh-temporalpole'] / tlobe_vol) + \
        dfp['ctx-lh-transversetemporal'] * (dfvol['ctx-lh-transversetemporal'] / tlobe_vol) + \
        dfp['ctx-rh-bankssts'] * (dfvol['ctx-rh-bankssts'] / tlobe_vol) + \
        dfp['ctx-rh-entorhinal'] * (dfvol['ctx-rh-entorhinal'] / tlobe_vol) + \
        dfp['ctx-rh-fusiform'] * (dfvol['ctx-rh-fusiform'] / tlobe_vol) + \
        dfp['ctx-rh-inferiortemporal'] * (dfvol['ctx-rh-inferiortemporal'] / tlobe_vol) + \
        dfp['ctx-rh-middletemporal'] * (dfvol['ctx-rh-middletemporal'] / tlobe_vol) + \
        dfp['ctx-rh-parahippocampal'] * (dfvol['ctx-rh-parahippocampal'] / tlobe_vol) + \
        dfp['ctx-rh-superiortemporal'] * (dfvol['ctx-rh-superiortemporal'] / tlobe_vol) + \
        dfp['ctx-rh-temporalpole'] * (dfvol['ctx-rh-temporalpole'] / tlobe_vol) + \
        dfp['ctx-rh-transversetemporal'] * (dfvol['ctx-rh-transversetemporal'] / tlobe_vol)

    bankssts_vol = dfvol['ctx-lh-bankssts'] + dfvol['ctx-rh-bankssts']
    dfp['bankssts'] =\
        dfp['ctx-lh-bankssts'] * (dfvol['ctx-lh-bankssts'] / bankssts_vol) + \
        dfp['ctx-rh-bankssts'] * (dfvol['ctx-rh-bankssts'] / bankssts_vol)

    entorhinal_vol = dfvol['ctx-lh-entorhinal'] + dfvol['ctx-rh-entorhinal']
    dfp['entorhinal'] =\
        dfp['ctx-lh-entorhinal'] * (dfvol['ctx-lh-entorhinal'] / entorhinal_vol) + \
        dfp['ctx-rh-entorhinal'] * (dfvol['ctx-rh-entorhinal'] / entorhinal_vol)

    fusiform_vol = dfvol['ctx-lh-fusiform'] + dfvol['ctx-rh-fusiform']
    dfp['fusiform'] =\
        dfp['ctx-lh-fusiform'] * (dfvol['ctx-lh-fusiform'] / fusiform_vol) + \
        dfp['ctx-rh-fusiform'] * (dfvol['ctx-rh-fusiform'] / fusiform_vol)

    inferiortemporal_vol = dfvol['ctx-lh-inferiortemporal'] + dfvol['ctx-rh-inferiortemporal']
    dfp['inferiortemporal'] = \
        dfp['ctx-lh-inferiortemporal'] * (dfvol['ctx-lh-inferiortemporal'] / inferiortemporal_vol) + \
        dfp['ctx-rh-inferiortemporal'] * (dfvol['ctx-rh-inferiortemporal'] / inferiortemporal_vol)

    middletemporal_vol = dfvol['ctx-lh-middletemporal'] + dfvol['ctx-rh-middletemporal']
    dfp['middletemporal'] = \
        dfp['ctx-lh-middletemporal'] * (dfvol['ctx-lh-middletemporal'] / middletemporal_vol) + \
        dfp['ctx-rh-middletemporal'] * (dfvol['ctx-rh-middletemporal'] / middletemporal_vol)

    parahippocampal_vol = dfvol['ctx-lh-parahippocampal'] + dfvol['ctx-rh-parahippocampal']
    dfp['parahippocampal'] = \
        dfp['ctx-lh-parahippocampal'] * (dfvol['ctx-lh-parahippocampal'] / parahippocampal_vol) + \
        dfp['ctx-rh-parahippocampal'] * (dfvol['ctx-rh-parahippocampal'] / parahippocampal_vol)

    superiortemporal_vol = dfvol['ctx-lh-superiortemporal'] + dfvol['ctx-rh-superiortemporal']
    dfp['superiortemporal'] =\
        dfp['ctx-lh-superiortemporal'] * (dfvol['ctx-lh-superiortemporal'] / superiortemporal_vol) + \
        dfp['ctx-rh-superiortemporal'] * (dfvol['ctx-rh-superiortemporal'] / superiortemporal_vol)

    temporalpole_vol = dfvol['ctx-lh-temporalpole'] + dfvol['ctx-rh-temporalpole']
    dfp['temporalpole'] =\
        dfp['ctx-lh-temporalpole'] * (dfvol['ctx-lh-temporalpole'] / temporalpole_vol) + \
        dfp['ctx-rh-temporalpole'] * (dfvol['ctx-rh-temporalpole'] / temporalpole_vol)

    transversetemporal_vol = dfvol['ctx-lh-transversetemporal'] + dfvol['ctx-rh-transversetemporal']
    dfp['transversetemporal'] =\
        dfp['ctx-lh-transversetemporal'] * (dfvol['ctx-lh-transversetemporal'] / transversetemporal_vol) + \
        dfp['ctx-rh-transversetemporal'] * (dfvol['ctx-rh-transversetemporal'] / transversetemporal_vol)

    olobe_vol = \
        dfvol['ctx-lh-cuneus'] + \
        dfvol['ctx-lh-lateraloccipital'] + \
        dfvol['ctx-lh-lingual'] + \
        dfvol['ctx-lh-pericalcarine'] + \
        dfvol['ctx-rh-cuneus'] + \
        dfvol['ctx-rh-lateraloccipital'] + \
        dfvol['ctx-rh-lingual'] + \
        dfvol['ctx-rh-pericalcarine']

    dfp['olobe'] = \
        dfp['ctx-lh-cuneus'] * (dfvol['ctx-lh-cuneus'] / olobe_vol) + \
        dfp['ctx-lh-lateraloccipital'] * (dfvol['ctx-lh-lateraloccipital'] / olobe_vol) + \
        dfp['ctx-lh-lingual'] * (dfvol['ctx-lh-lingual'] / olobe_vol) + \
        dfp['ctx-lh-pericalcarine'] * (dfvol['ctx-lh-pericalcarine'] / olobe_vol) + \
        dfp['ctx-rh-cuneus'] * (dfvol['ctx-rh-cuneus'] / olobe_vol) + \
        dfp['ctx-rh-lateraloccipital'] * (dfvol['ctx-rh-lateraloccipital'] / olobe_vol) + \
        dfp['ctx-rh-lingual'] * (dfvol['ctx-rh-lingual'] / olobe_vol) + \
        dfp['ctx-rh-pericalcarine'] * (dfvol['ctx-rh-pericalcarine'] / olobe_vol)

    cuneus_vol = dfvol['ctx-lh-cuneus'] + dfvol['ctx-rh-cuneus']
    dfp['cuneus'] = \
        dfp['ctx-lh-cuneus'] * (dfvol['ctx-lh-cuneus'] / cuneus_vol) + \
        dfp['ctx-rh-cuneus'] * (dfvol['ctx-rh-cuneus'] / cuneus_vol)

    lateraloccipital_vol = dfvol['ctx-lh-lateraloccipital'] + dfvol['ctx-rh-lateraloccipital']
    dfp['lateraloccipital'] = \
        dfp['ctx-lh-lateraloccipital'] * (dfvol['ctx-lh-lateraloccipital'] / lateraloccipital_vol) + \
        dfp['ctx-rh-lateraloccipital'] * (dfvol['ctx-rh-lateraloccipital'] / lateraloccipital_vol)

    lingual_vol = dfvol['ctx-lh-lingual'] + dfvol['ctx-rh-lingual']
    dfp['lingual'] = \
        dfp['ctx-lh-lingual'] * (dfvol['ctx-lh-lingual'] / lingual_vol) + \
        dfp['ctx-rh-lingual'] * (dfvol['ctx-rh-lingual'] / lingual_vol)

    pericalcarine_vol = dfvol['ctx-lh-pericalcarine'] + dfvol['ctx-rh-pericalcarine']
    dfp['pericalcarine'] = \
        dfp['ctx-lh-pericalcarine'] * (dfvol['ctx-lh-pericalcarine'] / pericalcarine_vol) + \
        dfp['ctx-rh-pericalcarine'] * (dfvol['ctx-rh-pericalcarine'] / pericalcarine_vol)

    cingulate_vol = \
        dfvol['ctx-lh-caudalanteriorcingulate'] + \
        dfvol['ctx-lh-isthmuscingulate'] + \
        dfvol['ctx-lh-posteriorcingulate'] + \
        dfvol['ctx-lh-rostralanteriorcingulate'] + \
        dfvol['ctx-rh-caudalanteriorcingulate'] + \
        dfvol['ctx-rh-isthmuscingulate'] + \
        dfvol['ctx-rh-posteriorcingulate'] + \
        dfvol['ctx-rh-rostralanteriorcingulate']

    dfp['cingulate'] = \
        dfp['ctx-lh-caudalanteriorcingulate'] * dfvol['ctx-lh-caudalanteriorcingulate'] / cingulate_vol + \
        dfp['ctx-lh-isthmuscingulate'] * dfvol['ctx-lh-isthmuscingulate'] / cingulate_vol + \
        dfp['ctx-lh-posteriorcingulate'] * dfvol['ctx-lh-posteriorcingulate'] / cingulate_vol + \
        dfp['ctx-lh-rostralanteriorcingulate'] * dfvol['ctx-lh-rostralanteriorcingulate'] / cingulate_vol + \
        dfp['ctx-rh-caudalanteriorcingulate'] * dfvol['ctx-rh-caudalanteriorcingulate'] / cingulate_vol + \
        dfp['ctx-rh-isthmuscingulate'] * dfvol['ctx-rh-isthmuscingulate'] / cingulate_vol + \
        dfp['ctx-rh-posteriorcingulate'] * dfvol['ctx-rh-posteriorcingulate'] / cingulate_vol + \
        dfp['ctx-rh-rostralanteriorcingulate'] * dfvol['ctx-rh-rostralanteriorcingulate'] / cingulate_vol

    caudalanteriorcingulate_vol = dfvol['ctx-lh-caudalanteriorcingulate'] + dfvol['ctx-rh-caudalanteriorcingulate']
    dfp['caudalanteriorcingulate'] = \
        dfp['ctx-lh-caudalanteriorcingulate'] * (dfvol['ctx-lh-caudalanteriorcingulate'] / caudalanteriorcingulate_vol) + \
        dfp['ctx-rh-caudalanteriorcingulate'] * (dfvol['ctx-rh-caudalanteriorcingulate'] / caudalanteriorcingulate_vol)

    isthmuscingulate_vol = dfvol['ctx-lh-isthmuscingulate'] + dfvol['ctx-rh-isthmuscingulate']
    dfp['isthmuscingulate'] = \
        dfp['ctx-lh-isthmuscingulate'] * (dfvol['ctx-lh-isthmuscingulate'] / isthmuscingulate_vol) + \
        dfp['ctx-rh-isthmuscingulate'] * (dfvol['ctx-rh-isthmuscingulate'] / isthmuscingulate_vol)

    posteriorcingulate_vol = dfvol['ctx-lh-posteriorcingulate'] + dfvol['ctx-rh-posteriorcingulate']
    dfp['posteriorcingulate'] = \
        dfp['ctx-lh-posteriorcingulate'] * (dfvol['ctx-lh-posteriorcingulate'] / posteriorcingulate_vol) + \
        dfp['ctx-rh-posteriorcingulate'] * (dfvol['ctx-rh-posteriorcingulate'] / posteriorcingulate_vol)

    rostralanteriorcingulate_vol = dfvol['ctx-lh-rostralanteriorcingulate'] + dfvol['ctx-rh-rostralanteriorcingulate']
    dfp['rostralanteriorcingulate'] = \
        dfp['ctx-lh-rostralanteriorcingulate'] * (dfvol['ctx-lh-rostralanteriorcingulate'] / rostralanteriorcingulate_vol) + \
        dfp['ctx-rh-rostralanteriorcingulate'] * (dfvol['ctx-rh-rostralanteriorcingulate'] / rostralanteriorcingulate_vol)

    thalamus_vol = dfvol['Left-Thalamus'] + dfvol['Right-Thalamus']
    dfp['thalamus'] = \
         dfp['Left-Thalamus'] * (dfvol['Left-Thalamus'] / thalamus_vol) + \
         dfp['Right-Thalamus'] * (dfvol['Right-Thalamus'] / thalamus_vol)

    hippo_vol = dfvol['Left-Hippocampus'] + dfvol['Right-Hippocampus']
    dfp['hippocampus'] = \
        dfp['Left-Hippocampus'] * (dfvol['Left-Hippocampus'] / hippo_vol) + \
        dfp['Right-Hippocampus'] * (dfvol['Right-Hippocampus'] / hippo_vol)

    insula_vol = dfvol['ctx-lh-insula'] + dfvol['ctx-rh-insula']
    dfp['insula'] = \
        dfp['ctx-lh-insula'] * (dfvol['ctx-lh-insula'] / insula_vol) + \
        dfp['ctx-rh-insula'] * (dfvol['ctx-rh-insula'] / insula_vol)

    putamen_vol = dfvol['Left-Putamen'] + dfvol['Right-Putamen']
    dfp['putamen'] = \
        dfp['Left-Putamen'] * (dfvol['Left-Putamen'] / putamen_vol) + \
        dfp['Right-Putamen'] * (dfvol['Right-Putamen'] / putamen_vol)

    pallidum_vol = dfvol['Left-Pallidum'] + dfvol['Right-Pallidum']
    dfp['pallidum'] = \
        dfp['Left-Pallidum'] * (dfvol['Left-Pallidum'] / pallidum_vol) + \
        dfp['Right-Pallidum'] * (dfvol['Right-Pallidum'] / pallidum_vol)

    amygdala_vol = dfvol['Left-Amygdala'] + dfvol['Right-Amygdala']
    dfp['amygdala'] = \
        dfp['Left-Amygdala'] * (dfvol['Left-Amygdala'] / amygdala_vol) + \
        dfp['Right-Amygdala'] * (dfvol['Right-Amygdala'] / amygdala_vol)


    dfp_all = dfp[['caudalmiddlefrontal', 'frontalpole', 'lateralorbitofrontal', 'medialorbitofrontal','paracentral', \
                   'parsopercularis', 'parstriangularis', 'precentral', 'rostralmiddlefrontal', 'superiorfrontal', \
                   'inferiorparietal', 'precuneus', 'superiorparietal', 'supramarginal', 'bankssts', 'entorhinal', \
                   'fusiform', 'inferiortemporal', 'middletemporal', 'parahippocampal', 'superiortemporal', 'temporalpole', \
                   'transversetemporal', 'cuneus', 'lateraloccipital', 'lingual', 'pericalcarine', 'caudalanteriorcingulate', \
                   'isthmuscingulate', 'posteriorcingulate', 'rostralanteriorcingulate', 'thalamus', 'hippocampus', 'insula',
                   'putamen', 'amygdala']]
    dfp = dfp[['flobe', 'olobe', 'plobe', 'tlobe', 'cblm', 'insula', 'thalamus', 'cingulate', 'hippocampus']]
    dfp.to_csv(f'{ROOTDIR}/suvr_gtm.csv')
    dfp_all.to_csv(f'{ROOTDIR}/suvr_gtm_extended.csv')


def save_suvr_no_pvc(df):
    dfp = df[['ROI', 'SUVR-NOPVC', 'SUBJECT']].pivot(
        columns='ROI', values='SUVR-NOPVC', index='SUBJECT')

    dfvol = df[['ROI', 'VOL', 'SUBJECT']].pivot(
        columns='ROI', values='VOL', index='SUBJECT')

    cblm_vol = \
        dfvol['Left-Cerebellum-Cortex'] + \
        dfvol['Left-Cerebellum-White-Matter'] + \
        dfvol['Right-Cerebellum-Cortex'] + \
        dfvol['Right-Cerebellum-White-Matter'] + \
        dfvol['Vermis']

    dfp['cblm'] = \
        dfp['Left-Cerebellum-Cortex']*(dfvol['Left-Cerebellum-Cortex']/(cblm_vol)) + \
        dfp['Left-Cerebellum-White-Matter']*(dfvol['Left-Cerebellum-White-Matter']/(cblm_vol))  + \
        dfp['Right-Cerebellum-Cortex']*(dfvol['Right-Cerebellum-Cortex']/(cblm_vol)) + \
        dfp['Right-Cerebellum-White-Matter']*(dfvol['Right-Cerebellum-White-Matter']/(cblm_vol)) + \
        dfp['Vermis'] *(dfvol['Vermis']/(cblm_vol))

    flobe_vol = \
        dfvol['ctx-lh-caudalmiddlefrontal'] + \
        dfvol['ctx-lh-frontalpole'] + \
        dfvol['ctx-lh-lateralorbitofrontal'] + \
        dfvol['ctx-lh-medialorbitofrontal'] + \
        dfvol['ctx-lh-paracentral'] + \
        dfvol['ctx-lh-parsopercularis'] + \
        dfvol['ctx-lh-parsorbitalis'] + \
        dfvol['ctx-lh-parstriangularis'] + \
        dfvol['ctx-lh-precentral'] + \
        dfvol['ctx-lh-rostralmiddlefrontal'] + \
        dfvol['ctx-lh-superiorfrontal'] + \
        dfvol['ctx-rh-caudalmiddlefrontal'] + \
        dfvol['ctx-rh-frontalpole'] + \
        dfvol['ctx-rh-lateralorbitofrontal'] + \
        dfvol['ctx-rh-medialorbitofrontal'] + \
        dfvol['ctx-rh-paracentral'] + \
        dfvol['ctx-rh-parsopercularis'] + \
        dfvol['ctx-rh-parsorbitalis'] + \
        dfvol['ctx-rh-parstriangularis'] + \
        dfvol['ctx-rh-precentral'] + \
        dfvol['ctx-rh-rostralmiddlefrontal'] + \
        dfvol['ctx-rh-superiorfrontal']

    dfp['flobe'] = (
            dfp['ctx-lh-caudalmiddlefrontal'] * (dfvol['ctx-lh-caudalmiddlefrontal'] / flobe_vol) + \
            dfp['ctx-lh-frontalpole'] * (dfvol['ctx-lh-frontalpole'] / flobe_vol) + \
            dfp['ctx-lh-lateralorbitofrontal'] * (dfvol['ctx-lh-lateralorbitofrontal'] / flobe_vol) + \
            dfp['ctx-lh-medialorbitofrontal'] * (dfvol['ctx-lh-medialorbitofrontal'] / flobe_vol) + \
            dfp['ctx-lh-paracentral'] * (dfvol['ctx-lh-paracentral'] / flobe_vol) + \
            dfp['ctx-lh-parsopercularis'] * (dfvol['ctx-lh-parsopercularis'] / flobe_vol) + \
            dfp['ctx-lh-parsorbitalis'] * (dfvol['ctx-lh-parsorbitalis'] / flobe_vol) + \
            dfp['ctx-lh-parstriangularis'] * (dfvol['ctx-lh-parstriangularis'] / flobe_vol) + \
            dfp['ctx-lh-precentral'] * (dfvol['ctx-lh-precentral'] / flobe_vol) + \
            dfp['ctx-lh-rostralmiddlefrontal'] * (dfvol['ctx-lh-rostralmiddlefrontal'] / flobe_vol) + \
            dfp['ctx-lh-superiorfrontal'] * (dfvol['ctx-lh-superiorfrontal'] / flobe_vol) + \
            dfp['ctx-rh-caudalmiddlefrontal'] * (dfvol['ctx-rh-caudalmiddlefrontal'] / flobe_vol) + \
            dfp['ctx-rh-frontalpole'] * (dfvol['ctx-rh-frontalpole'] / flobe_vol) + \
            dfp['ctx-rh-lateralorbitofrontal'] * (dfvol['ctx-rh-lateralorbitofrontal'] / flobe_vol) + \
            dfp['ctx-rh-medialorbitofrontal'] * (dfvol['ctx-rh-medialorbitofrontal'] / flobe_vol) + \
            dfp['ctx-rh-paracentral'] * (dfvol['ctx-rh-paracentral'] / flobe_vol) + \
            dfp['ctx-rh-parsopercularis'] * (dfvol['ctx-rh-parsopercularis'] / flobe_vol) + \
            dfp['ctx-rh-parsorbitalis'] * (dfvol['ctx-rh-parsorbitalis'] / flobe_vol) + \
            dfp['ctx-rh-parstriangularis'] * (dfvol['ctx-rh-parstriangularis'] / flobe_vol) + \
            dfp['ctx-rh-precentral'] * (dfvol['ctx-rh-precentral'] / flobe_vol) + \
            dfp['ctx-rh-rostralmiddlefrontal'] * (dfvol['ctx-rh-rostralmiddlefrontal'] / flobe_vol) + \
            dfp['ctx-rh-superiorfrontal'] * (dfvol['ctx-rh-superiorfrontal'] / flobe_vol)
    )

    caudalmiddlefrontal_vol = dfvol['ctx-lh-caudalmiddlefrontal'] + dfvol['ctx-rh-caudalmiddlefrontal']

    dfp['caudalmiddlefrontal'] = \
        dfp['ctx-lh-caudalmiddlefrontal'] * (dfvol['ctx-lh-caudalmiddlefrontal'] / caudalmiddlefrontal_vol) + \
        dfp['ctx-rh-caudalmiddlefrontal'] * (dfvol['ctx-rh-caudalmiddlefrontal'] / caudalmiddlefrontal_vol)

    frontalpole_vol = dfvol['ctx-lh-caudalmiddlefrontal'] + dfvol['ctx-rh-caudalmiddlefrontal']

    dfp['frontalpole'] = \
         dfp['ctx-lh-frontalpole'] * (dfvol['ctx-lh-caudalmiddlefrontal'] / frontalpole_vol) + \
         dfp['ctx-rh-frontalpole'] * (dfvol['ctx-rh-caudalmiddlefrontal'] / frontalpole_vol)

    lateralorbitalfrontal_vol = dfvol['ctx-lh-lateralorbitofrontal'] + dfvol['ctx-rh-lateralorbitofrontal']
    dfp['lateralorbitofrontal'] = \
         dfp['ctx-lh-lateralorbitofrontal'] * (dfvol['ctx-lh-lateralorbitofrontal'] / lateralorbitalfrontal_vol) + \
         dfp['ctx-rh-lateralorbitofrontal'] * (dfvol['ctx-rh-lateralorbitofrontal'] / lateralorbitalfrontal_vol)

    medialorbitofrontal_vol = dfvol['ctx-lh-medialorbitofrontal'] + dfvol['ctx-rh-medialorbitofrontal']
    dfp['medialorbitofrontal'] = \
        dfp['ctx-lh-medialorbitofrontal'] * (dfvol['ctx-lh-medialorbitofrontal'] / medialorbitofrontal_vol) + \
        dfp['ctx-rh-medialorbitofrontal'] * (dfvol['ctx-rh-medialorbitofrontal'] / medialorbitofrontal_vol)

    paracentral_vol = dfvol['ctx-lh-paracentral'] + dfvol['ctx-rh-paracentral']
    dfp['paracentral'] = \
        dfp['ctx-lh-paracentral'] * (dfvol['ctx-lh-paracentral'] / paracentral_vol) + \
        dfp['ctx-rh-paracentral'] * (dfvol['ctx-rh-paracentral'] / paracentral_vol)

    parsopercularis_vol = dfvol['ctx-lh-parsopercularis'] + dfvol['ctx-rh-parsopercularis']
    dfp['parsopercularis'] = \
        dfp['ctx-lh-parsopercularis'] * (dfvol['ctx-lh-parsopercularis'] / parsopercularis_vol) + \
        dfp['ctx-rh-parsopercularis'] * (dfvol['ctx-rh-parsopercularis'] / parsopercularis_vol)

    parsorbitalis_vol = dfvol['ctx-lh-parsorbitalis'] + dfvol['ctx-rh-parsorbitalis']
    dfp['parsorbitalis'] = \
        dfp['ctx-lh-parsorbitalis'] * (dfvol['ctx-lh-parsorbitalis'] / parsorbitalis_vol) + \
        dfp['ctx-rh-parsorbitalis'] * (dfvol['ctx-rh-parsorbitalis'] / parsorbitalis_vol)

    parstriangularis_vol = dfvol['ctx-lh-parstriangularis'] + dfvol['ctx-rh-parstriangularis']
    dfp['parstriangularis'] = \
        dfp['ctx-lh-parstriangularis'] * (dfvol['ctx-lh-parstriangularis'] / parstriangularis_vol) + \
        dfp['ctx-rh-parstriangularis'] * (dfvol['ctx-rh-parstriangularis'] / parstriangularis_vol)

    precentral_vol = dfvol['ctx-lh-precentral'] + dfvol['ctx-rh-precentral']
    dfp['precentral'] = \
        dfp['ctx-lh-precentral'] * (dfvol['ctx-lh-precentral'] / precentral_vol) + \
        dfp['ctx-rh-precentral'] * (dfvol['ctx-rh-precentral'] / precentral_vol)

    rostralmiddlefrontal_vol = dfvol['ctx-lh-rostralmiddlefrontal'] + dfvol['ctx-rh-rostralmiddlefrontal']
    dfp['rostralmiddlefrontal'] = \
        dfp['ctx-lh-rostralmiddlefrontal'] * (dfvol['ctx-lh-rostralmiddlefrontal'] / rostralmiddlefrontal_vol) + \
        dfp['ctx-rh-rostralmiddlefrontal'] * (dfvol['ctx-rh-rostralmiddlefrontal'] / rostralmiddlefrontal_vol)

    superiorfrontal_vol = dfvol['ctx-lh-superiorfrontal'] + dfvol['ctx-rh-superiorfrontal']
    dfp['superiorfrontal'] = \
        dfp['ctx-lh-superiorfrontal'] * (dfvol['ctx-lh-superiorfrontal'] / superiorfrontal_vol) + \
        dfp['ctx-rh-superiorfrontal'] * (dfvol['ctx-rh-superiorfrontal'] / superiorfrontal_vol)

    plobe_vol = \
        dfvol['ctx-lh-inferiorparietal'] + \
        dfvol['ctx-lh-postcentral'] + \
        dfvol['ctx-lh-precuneus'] + \
        dfvol['ctx-lh-superiorparietal'] + \
        dfvol['ctx-lh-supramarginal'] + \
        dfvol['ctx-rh-inferiorparietal'] + \
        dfvol['ctx-rh-postcentral'] + \
        dfvol['ctx-rh-precuneus'] + \
        dfvol['ctx-rh-superiorparietal'] + \
        dfvol['ctx-rh-supramarginal']

    dfp['plobe'] = \
        dfp['ctx-lh-inferiorparietal'] * (dfvol['ctx-lh-inferiorparietal'] / plobe_vol) + \
        dfp['ctx-lh-postcentral'] * (dfvol['ctx-lh-postcentral'] / plobe_vol) + \
        dfp['ctx-lh-precuneus'] * (dfvol['ctx-lh-precuneus'] / plobe_vol) + \
        dfp['ctx-lh-superiorparietal'] * (dfvol['ctx-lh-superiorparietal'] / plobe_vol) + \
        dfp['ctx-lh-supramarginal'] * (dfvol['ctx-lh-supramarginal'] / plobe_vol) + \
        dfp['ctx-rh-inferiorparietal'] * (dfvol['ctx-rh-inferiorparietal'] / plobe_vol) + \
        dfp['ctx-rh-postcentral'] * (dfvol['ctx-rh-postcentral'] / plobe_vol) + \
        dfp['ctx-rh-precuneus'] * (dfvol['ctx-rh-precuneus'] / plobe_vol) + \
        dfp['ctx-rh-superiorparietal'] * (dfvol['ctx-rh-superiorparietal'] / plobe_vol) + \
        dfp['ctx-rh-supramarginal'] * (dfvol['ctx-rh-supramarginal'] / plobe_vol)

    inferiorparietal_vol = dfvol['ctx-lh-inferiorparietal'] + dfvol['ctx-rh-inferiorparietal']
    dfp['inferiorparietal'] =\
        dfp['ctx-lh-inferiorparietal'] * (dfvol['ctx-lh-inferiorparietal'] / inferiorparietal_vol) + \
        dfp['ctx-rh-inferiorparietal'] * (dfvol['ctx-rh-inferiorparietal'] / inferiorparietal_vol)

    postcentral_vol = dfvol['ctx-lh-postcentral'] + dfvol['ctx-rh-postcentral']
    dfp['postcentral'] =\
        dfp['ctx-lh-postcentral'] * (dfvol['ctx-lh-postcentral'] / postcentral_vol) + \
        dfp['ctx-rh-postcentral'] * (dfvol['ctx-rh-postcentral'] / postcentral_vol)

    precuneus_vol = dfvol['ctx-lh-precuneus'] + dfvol['ctx-rh-precuneus']
    dfp['precuneus'] =\
        dfp['ctx-lh-precuneus'] * (dfvol['ctx-lh-precuneus'] / precuneus_vol) + \
        dfp['ctx-rh-precuneus'] * (dfvol['ctx-rh-precuneus'] / precuneus_vol)

    superiorparietal_vol = dfvol['ctx-lh-superiorparietal'] + dfvol['ctx-rh-superiorparietal']
    dfp['superiorparietal'] =\
        dfp['ctx-lh-superiorparietal'] * (dfvol['ctx-lh-superiorparietal'] / superiorparietal_vol) + \
        dfp['ctx-rh-superiorparietal'] * (dfvol['ctx-rh-superiorparietal'] / superiorparietal_vol)

    supramarginal_vol = dfvol['ctx-lh-supramarginal'] + dfvol['ctx-rh-supramarginal']
    dfp['supramarginal'] =\
        dfp['ctx-lh-supramarginal'] * (dfvol['ctx-lh-supramarginal'] / supramarginal_vol) + \
        dfp['ctx-rh-supramarginal'] * (dfvol['ctx-rh-supramarginal'] / supramarginal_vol)

    tlobe_vol = \
        dfvol['ctx-lh-bankssts'] + \
        dfvol['ctx-lh-entorhinal'] + \
        dfvol['ctx-lh-fusiform'] + \
        dfvol['ctx-lh-inferiortemporal'] + \
        dfvol['ctx-lh-middletemporal'] + \
        dfvol['ctx-lh-parahippocampal'] + \
        dfvol['ctx-lh-superiortemporal'] + \
        dfvol['ctx-lh-temporalpole'] + \
        dfvol['ctx-lh-transversetemporal'] + \
        dfvol['ctx-rh-bankssts'] + \
        dfvol['ctx-rh-entorhinal'] + \
        dfvol['ctx-rh-fusiform'] + \
        dfvol['ctx-rh-inferiortemporal'] + \
        dfvol['ctx-rh-middletemporal'] + \
        dfvol['ctx-rh-parahippocampal'] + \
        dfvol['ctx-rh-superiortemporal'] + \
        dfvol['ctx-rh-temporalpole'] + \
        dfvol['ctx-rh-transversetemporal']

    dfp['tlobe'] = \
        dfp['ctx-lh-bankssts'] * (dfvol['ctx-lh-bankssts'] / tlobe_vol) + \
        dfp['ctx-lh-entorhinal'] * (dfvol['ctx-lh-entorhinal'] / tlobe_vol) + \
        dfp['ctx-lh-fusiform'] * (dfvol['ctx-lh-fusiform'] / tlobe_vol) + \
        dfp['ctx-lh-inferiortemporal'] * (dfvol['ctx-lh-inferiortemporal'] / tlobe_vol) + \
        dfp['ctx-lh-middletemporal'] * (dfvol['ctx-lh-middletemporal'] / tlobe_vol) + \
        dfp['ctx-lh-parahippocampal'] * (dfvol['ctx-lh-parahippocampal'] / tlobe_vol) + \
        dfp['ctx-lh-superiortemporal'] * (dfvol['ctx-lh-superiortemporal'] / tlobe_vol) + \
        dfp['ctx-lh-temporalpole'] * (dfvol['ctx-lh-temporalpole'] / tlobe_vol) + \
        dfp['ctx-lh-transversetemporal'] * (dfvol['ctx-lh-transversetemporal'] / tlobe_vol) + \
        dfp['ctx-rh-bankssts'] * (dfvol['ctx-rh-bankssts'] / tlobe_vol) + \
        dfp['ctx-rh-entorhinal'] * (dfvol['ctx-rh-entorhinal'] / tlobe_vol) + \
        dfp['ctx-rh-fusiform'] * (dfvol['ctx-rh-fusiform'] / tlobe_vol) + \
        dfp['ctx-rh-inferiortemporal'] * (dfvol['ctx-rh-inferiortemporal'] / tlobe_vol) + \
        dfp['ctx-rh-middletemporal'] * (dfvol['ctx-rh-middletemporal'] / tlobe_vol) + \
        dfp['ctx-rh-parahippocampal'] * (dfvol['ctx-rh-parahippocampal'] / tlobe_vol) + \
        dfp['ctx-rh-superiortemporal'] * (dfvol['ctx-rh-superiortemporal'] / tlobe_vol) + \
        dfp['ctx-rh-temporalpole'] * (dfvol['ctx-rh-temporalpole'] / tlobe_vol) + \
        dfp['ctx-rh-transversetemporal'] * (dfvol['ctx-rh-transversetemporal'] / tlobe_vol)

    bankssts_vol = dfvol['ctx-lh-bankssts'] + dfvol['ctx-rh-bankssts']
    dfp['bankssts'] =\
        dfp['ctx-lh-bankssts'] * (dfvol['ctx-lh-bankssts'] / bankssts_vol) + \
        dfp['ctx-rh-bankssts'] * (dfvol['ctx-rh-bankssts'] / bankssts_vol)

    entorhinal_vol = dfvol['ctx-lh-entorhinal'] + dfvol['ctx-rh-entorhinal']
    dfp['entorhinal'] =\
        dfp['ctx-lh-entorhinal'] * (dfvol['ctx-lh-entorhinal'] / entorhinal_vol) + \
        dfp['ctx-rh-entorhinal'] * (dfvol['ctx-rh-entorhinal'] / entorhinal_vol)

    fusiform_vol = dfvol['ctx-lh-fusiform'] + dfvol['ctx-rh-fusiform']
    dfp['fusiform'] =\
        dfp['ctx-lh-fusiform'] * (dfvol['ctx-lh-fusiform'] / fusiform_vol) + \
        dfp['ctx-rh-fusiform'] * (dfvol['ctx-rh-fusiform'] / fusiform_vol)

    inferiortemporal_vol = dfvol['ctx-lh-inferiortemporal'] + dfvol['ctx-rh-inferiortemporal']
    dfp['inferiortemporal'] = \
        dfp['ctx-lh-inferiortemporal'] * (dfvol['ctx-lh-inferiortemporal'] / inferiortemporal_vol) + \
        dfp['ctx-rh-inferiortemporal'] * (dfvol['ctx-rh-inferiortemporal'] / inferiortemporal_vol)

    middletemporal_vol = dfvol['ctx-lh-middletemporal'] + dfvol['ctx-rh-middletemporal']
    dfp['middletemporal'] = \
        dfp['ctx-lh-middletemporal'] * (dfvol['ctx-lh-middletemporal'] / middletemporal_vol) + \
        dfp['ctx-rh-middletemporal'] * (dfvol['ctx-rh-middletemporal'] / middletemporal_vol)

    parahippocampal_vol = dfvol['ctx-lh-parahippocampal'] + dfvol['ctx-rh-parahippocampal']
    dfp['parahippocampal'] = \
        dfp['ctx-lh-parahippocampal'] * (dfvol['ctx-lh-parahippocampal'] / parahippocampal_vol) + \
        dfp['ctx-rh-parahippocampal'] * (dfvol['ctx-rh-parahippocampal'] / parahippocampal_vol)

    superiortemporal_vol = dfvol['ctx-lh-superiortemporal'] + dfvol['ctx-rh-superiortemporal']
    dfp['superiortemporal'] =\
        dfp['ctx-lh-superiortemporal'] * (dfvol['ctx-lh-superiortemporal'] / superiortemporal_vol) + \
        dfp['ctx-rh-superiortemporal'] * (dfvol['ctx-rh-superiortemporal'] / superiortemporal_vol)

    temporalpole_vol = dfvol['ctx-lh-temporalpole'] + dfvol['ctx-rh-temporalpole']
    dfp['temporalpole'] =\
        dfp['ctx-lh-temporalpole'] * (dfvol['ctx-lh-temporalpole'] / temporalpole_vol) + \
        dfp['ctx-rh-temporalpole'] * (dfvol['ctx-rh-temporalpole'] / temporalpole_vol)

    transversetemporal_vol = dfvol['ctx-lh-transversetemporal'] + dfvol['ctx-rh-transversetemporal']
    dfp['transversetemporal'] =\
        dfp['ctx-lh-transversetemporal'] * (dfvol['ctx-lh-transversetemporal'] / transversetemporal_vol) + \
        dfp['ctx-rh-transversetemporal'] * (dfvol['ctx-rh-transversetemporal'] / transversetemporal_vol)

    olobe_vol = \
        dfvol['ctx-lh-cuneus'] + \
        dfvol['ctx-lh-lateraloccipital'] + \
        dfvol['ctx-lh-lingual'] + \
        dfvol['ctx-lh-pericalcarine'] + \
        dfvol['ctx-rh-cuneus'] + \
        dfvol['ctx-rh-lateraloccipital'] + \
        dfvol['ctx-rh-lingual'] + \
        dfvol['ctx-rh-pericalcarine']

    dfp['olobe'] = \
        dfp['ctx-lh-cuneus'] * (dfvol['ctx-lh-cuneus'] / olobe_vol) + \
        dfp['ctx-lh-lateraloccipital'] * (dfvol['ctx-lh-lateraloccipital'] / olobe_vol) + \
        dfp['ctx-lh-lingual'] * (dfvol['ctx-lh-lingual'] / olobe_vol) + \
        dfp['ctx-lh-pericalcarine'] * (dfvol['ctx-lh-pericalcarine'] / olobe_vol) + \
        dfp['ctx-rh-cuneus'] * (dfvol['ctx-rh-cuneus'] / olobe_vol) + \
        dfp['ctx-rh-lateraloccipital'] * (dfvol['ctx-rh-lateraloccipital'] / olobe_vol) + \
        dfp['ctx-rh-lingual'] * (dfvol['ctx-rh-lingual'] / olobe_vol) + \
        dfp['ctx-rh-pericalcarine'] * (dfvol['ctx-rh-pericalcarine'] / olobe_vol)

    cuneus_vol = dfvol['ctx-lh-cuneus'] + dfvol['ctx-rh-cuneus']
    dfp['cuneus'] = \
        dfp['ctx-lh-cuneus'] * (dfvol['ctx-lh-cuneus'] / cuneus_vol) + \
        dfp['ctx-rh-cuneus'] * (dfvol['ctx-rh-cuneus'] / cuneus_vol)

    lateraloccipital_vol = dfvol['ctx-lh-lateraloccipital'] + dfvol['ctx-rh-lateraloccipital']
    dfp['lateraloccipital'] = \
        dfp['ctx-lh-lateraloccipital'] * (dfvol['ctx-lh-lateraloccipital'] / lateraloccipital_vol) + \
        dfp['ctx-rh-lateraloccipital'] * (dfvol['ctx-rh-lateraloccipital'] / lateraloccipital_vol)

    lingual_vol = dfvol['ctx-lh-lingual'] + dfvol['ctx-rh-lingual']
    dfp['lingual'] = \
        dfp['ctx-lh-lingual'] * (dfvol['ctx-lh-lingual'] / lingual_vol) + \
        dfp['ctx-rh-lingual'] * (dfvol['ctx-rh-lingual'] / lingual_vol)

    pericalcarine_vol = dfvol['ctx-lh-pericalcarine'] + dfvol['ctx-rh-pericalcarine']
    dfp['pericalcarine'] = \
        dfp['ctx-lh-pericalcarine'] * (dfvol['ctx-lh-pericalcarine'] / pericalcarine_vol) + \
        dfp['ctx-rh-pericalcarine'] * (dfvol['ctx-rh-pericalcarine'] / pericalcarine_vol)

    cingulate_vol = \
        dfvol['ctx-lh-caudalanteriorcingulate'] + \
        dfvol['ctx-lh-isthmuscingulate'] + \
        dfvol['ctx-lh-posteriorcingulate'] + \
        dfvol['ctx-lh-rostralanteriorcingulate'] + \
        dfvol['ctx-rh-caudalanteriorcingulate'] + \
        dfvol['ctx-rh-isthmuscingulate'] + \
        dfvol['ctx-rh-posteriorcingulate'] + \
        dfvol['ctx-rh-rostralanteriorcingulate']

    dfp['cingulate'] = \
        dfp['ctx-lh-caudalanteriorcingulate'] * dfvol['ctx-lh-caudalanteriorcingulate'] / cingulate_vol + \
        dfp['ctx-lh-isthmuscingulate'] * dfvol['ctx-lh-isthmuscingulate'] / cingulate_vol + \
        dfp['ctx-lh-posteriorcingulate'] * dfvol['ctx-lh-posteriorcingulate'] / cingulate_vol + \
        dfp['ctx-lh-rostralanteriorcingulate'] * dfvol['ctx-lh-rostralanteriorcingulate'] / cingulate_vol + \
        dfp['ctx-rh-caudalanteriorcingulate'] * dfvol['ctx-rh-caudalanteriorcingulate'] / cingulate_vol + \
        dfp['ctx-rh-isthmuscingulate'] * dfvol['ctx-rh-isthmuscingulate'] / cingulate_vol + \
        dfp['ctx-rh-posteriorcingulate'] * dfvol['ctx-rh-posteriorcingulate'] / cingulate_vol + \
        dfp['ctx-rh-rostralanteriorcingulate'] * dfvol['ctx-rh-rostralanteriorcingulate'] / cingulate_vol

    caudalanteriorcingulate_vol = dfvol['ctx-lh-caudalanteriorcingulate'] + dfvol['ctx-rh-caudalanteriorcingulate']
    dfp['caudalanteriorcingulate'] = \
        dfp['ctx-lh-caudalanteriorcingulate'] * (dfvol['ctx-lh-caudalanteriorcingulate'] / caudalanteriorcingulate_vol) + \
        dfp['ctx-rh-caudalanteriorcingulate'] * (dfvol['ctx-rh-caudalanteriorcingulate'] / caudalanteriorcingulate_vol)

    isthmuscingulate_vol = dfvol['ctx-lh-isthmuscingulate'] + dfvol['ctx-rh-isthmuscingulate']
    dfp['isthmuscingulate'] = \
        dfp['ctx-lh-isthmuscingulate'] * (dfvol['ctx-lh-isthmuscingulate'] / isthmuscingulate_vol) + \
        dfp['ctx-rh-isthmuscingulate'] * (dfvol['ctx-rh-isthmuscingulate'] / isthmuscingulate_vol)

    posteriorcingulate_vol = dfvol['ctx-lh-posteriorcingulate'] + dfvol['ctx-rh-posteriorcingulate']
    dfp['posteriorcingulate'] = \
        dfp['ctx-lh-posteriorcingulate'] * (dfvol['ctx-lh-posteriorcingulate'] / posteriorcingulate_vol) + \
        dfp['ctx-rh-posteriorcingulate'] * (dfvol['ctx-rh-posteriorcingulate'] / posteriorcingulate_vol)

    rostralanteriorcingulate_vol = dfvol['ctx-lh-rostralanteriorcingulate'] + dfvol['ctx-rh-rostralanteriorcingulate']
    dfp['rostralanteriorcingulate'] = \
        dfp['ctx-lh-rostralanteriorcingulate'] * (dfvol['ctx-lh-rostralanteriorcingulate'] / rostralanteriorcingulate_vol) + \
        dfp['ctx-rh-rostralanteriorcingulate'] * (dfvol['ctx-rh-rostralanteriorcingulate'] / rostralanteriorcingulate_vol)

    thalamus_vol = dfvol['Left-Thalamus'] + dfvol['Right-Thalamus']
    dfp['thalamus'] = \
         dfp['Left-Thalamus'] * (dfvol['Left-Thalamus'] / thalamus_vol) + \
         dfp['Right-Thalamus'] * (dfvol['Right-Thalamus'] / thalamus_vol)

    hippo_vol = dfvol['Left-Hippocampus'] + dfvol['Right-Hippocampus']
    dfp['hippocampus'] = \
        dfp['Left-Hippocampus'] * (dfvol['Left-Hippocampus'] / hippo_vol) + \
        dfp['Right-Hippocampus'] * (dfvol['Right-Hippocampus'] / hippo_vol)

    insula_vol = dfvol['ctx-lh-insula'] + dfvol['ctx-rh-insula']
    dfp['insula'] = \
        dfp['ctx-lh-insula'] * (dfvol['ctx-lh-insula'] / insula_vol) + \
        dfp['ctx-rh-insula'] * (dfvol['ctx-rh-insula'] / insula_vol)

    putamen_vol = dfvol['Left-Putamen'] + dfvol['Right-Putamen']
    dfp['putamen'] = \
        dfp['Left-Putamen'] * (dfvol['Left-Putamen'] / putamen_vol) + \
        dfp['Right-Putamen'] * (dfvol['Right-Putamen'] / putamen_vol)

    pallidum_vol = dfvol['Left-Pallidum'] + dfvol['Right-Pallidum']
    dfp['pallidum'] = \
        dfp['Left-Pallidum'] * (dfvol['Left-Pallidum'] / pallidum_vol) + \
        dfp['Right-Pallidum'] * (dfvol['Right-Pallidum'] / pallidum_vol)

    amygdala_vol = dfvol['Left-Amygdala'] + dfvol['Right-Amygdala']
    dfp['amygdala'] = \
        dfp['Left-Amygdala'] * (dfvol['Left-Amygdala'] / amygdala_vol) + \
        dfp['Right-Amygdala'] * (dfvol['Right-Amygdala'] / amygdala_vol)


    dfp_all = dfp[['caudalmiddlefrontal', 'frontalpole', 'lateralorbitofrontal', 'medialorbitofrontal','paracentral', \
                   'parsopercularis', 'parstriangularis', 'precentral', 'rostralmiddlefrontal', 'superiorfrontal', \
                   'inferiorparietal', 'precuneus', 'superiorparietal', 'supramarginal', 'bankssts', 'entorhinal', \
                   'fusiform', 'inferiortemporal', 'middletemporal', 'parahippocampal', 'superiortemporal', 'temporalpole', \
                   'transversetemporal', 'cuneus', 'lateraloccipital', 'lingual', 'pericalcarine', 'caudalanteriorcingulate', \
                   'isthmuscingulate', 'posteriorcingulate', 'rostralanteriorcingulate', 'thalamus', 'hippocampus', 'insula',
                   'putamen', 'amygdala']]
    dfp = dfp[['flobe', 'olobe', 'plobe', 'tlobe', 'cblm', 'insula', 'thalamus', 'cingulate', 'hippocampus']]
    dfp.to_csv(f'{ROOTDIR}/suvr_no_pvc.csv')
    dfp_all.to_csv(f'{ROOTDIR}/suvr_no_pvc_extended.csv')


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
save_suvr_gtm(df)
save_suvr_no_pvc(df)

print('DONE!')
