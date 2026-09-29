import os
from glob import glob

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from nilearn.glm.second_level import SecondLevelModel
from nilearn.plotting import plot_stat_map

from params import CUT_COORDS, THRESHOLDS, COLORMAP, TITLE, TITLE_SIZE


CONTRAST_COUNT = 2

COVARS_FILE = '/Users/boydb1/Downloads/D3-A014_covariates_2026-09-25.csv'

CYTOKINES_FILE = '/Users/boydb1/Downloads/D3 Inflammation Cleaning Summaries/D3 Cytokines CRP raw Z Scores.xlsx'


def _load_covariates(filename):
    # Check for covariates file
    if not os.path.exists(filename):
        raise Exception('no csv file, cannot run covars')

    # Load covariates from csv file to pandas dataframe
    print(f'loading csv:{filename}')
    df = pd.read_csv(filename)

    return df


def _load_cytokines(filename):
    # Check for covariates file
    if not os.path.exists(filename):
        raise Exception('cytokines excel file not found')

    print(f'loading excel:{filename}')
    df = pd.read_excel(filename)

    df = df[['ID', 'Site', 'CRP_2', 'InflamScoreLN', 'InflamLNHighLowMed']]

    return df


def _run(subjects_dir, group_dir, roi_dir):
    print(subjects_dir)
    print(group_dir)
    print(roi_dir)

    #print('Second Level paired-t tests')
    #paired_dir = f'{group_dir}/paired-t'
    #os.makedirs(paired_dir, exist_ok=True)
    #_paired(subjects_dir, paired_dir, roi_dir)

    print('Second Level single-t tests')
    single_dir = f'{group_dir}/single-t'
    os.makedirs(single_dir, exist_ok=True)
    _single(subjects_dir, single_dir, roi_dir)


def _single(subjects_dir, group_dir, roi_dir):

    # Single t for each contrast
    for i in range(_contrast_count()):
        cid = str(i+1)
        print(f'Getting single t for contrast:{cid}')

        cmaps = sorted(glob(f'{subjects_dir}/*/*/conn_project/results/firstlevel/SBC_01/contrast{cid}.nii.gz'))
        print(subjects_dir)

        if len(cmaps) == 0:
            print(f'no cmaps found for contrast:{cid}')
            continue

        design_matrix = pd.DataFrame([1] * len(cmaps), columns=["intercept"])

        model = SecondLevelModel(smoothing_fwhm=8.0)

        model = model.fit(cmaps, design_matrix=design_matrix)

        zmap = model.compute_contrast(
            second_level_contrast="intercept",
            output_type="z_score"
        )

        zmap.to_filename(f'{group_dir}/contrast{cid}_zmap.nii.gz')

        # Make a letter paper size figure with rows of plots in 1 column
        fig, ax = plt.subplots(3, 1, figsize=(8.5,11))

        # Plot each t value
        for a, t in enumerate(THRESHOLDS):
            display = plot_stat_map(
                zmap,
                threshold=t,
                cut_coords=CUT_COORDS,
                display_mode='z',
                cmap=COLORMAP,
                vmax=t*2,
                axes=ax[a],
            )

            display.title(
                f'{TITLE} (n={len(cmaps)}) 2nd-Level single-t contrast_{cid}:{t=}',
                size=TITLE_SIZE
            )

            # Trace ROIs on stats map
            for r in glob(f'{roi_dir}/*.nii.gz'):
                display.add_contours(r, levels=[0.5], colors="g")

        # Save plot
        plt.savefig(f'{group_dir}/singlet_contrast{cid}_report.pdf')

        plt.close()

        # Get the default report
        print('Second Level generate_report()')
        report = model.generate_report(contrasts=np.array([1]), two_sided=True)
        print(f'Saving report to: {group_dir}/contrast{cid}_glm_report.html')
        report.save_as_html(f'{group_dir}/contrast{cid}_glm_report.html')




# Group comparison, D vs C, control for Age and Sex





def _glm_report(df, images, filename):
    sex_all, sex_all_key = pd.factorize(df['SEX'])
    group_all, group_all_key = pd.factorize(df['GROUP'])
    hilo_all, hilo_all_key = pd.factorize(df['InflamLNHighLowMed'])
    crp2_all, crp2_all_key = pd.factorize(df['CRP_2'])
    score_all, score_all_key = pd.factorize(df['InflamScoreLN'])

    subject_count = len(df)
    df['AGE'] = df['AGE'].astype(float)
    design_matrix = pd.DataFrame({
        "AGE": (df['AGE'] - df['AGE'].mean()) / df['AGE'].std(),
        "SEX": sex_all,
        "GROUP": group_all,
        "InflamLNHighLowMed": hilo_all,
        "CRP_2": crp2_all,
        "InflamScoreLN": score_all,
        "intercept": [1] * subject_count,
    })

    print('Fitting full model')
    second_level_model = SecondLevelModel().fit(
        images,
        design_matrix=design_matrix
    )

    print('generate_report() with contrasts')

    report = second_level_model.generate_report(
        contrasts=["AGE", "GROUP", "SEX", "InflamLNHighLowMed", "CRP_2", "InflamScoreLN"],
        two_sided=True,
    )

    print(f'save report:{filename}')
    report.save_as_html(filename)


def _contrast_count():
    return CONTRAST_COUNT


def glm_reports(subjects_dir, group_dir):
    df = _load_covariates(COVARS_FILE)
    df = pd.merge(df, _load_cytokines(CYTOKINES_FILE))

    # Make reports
    print('Making nilearn.glm reports')
    for i in range(_contrast_count()):
        cid = str(i+1)
        report_file = f'{group_dir}/covars_contrast{cid}_report.html'

        # Get Baseline only *a
        cmaps = sorted(glob(f'{subjects_dir}/*/*a/conn_project/results/firstlevel/SBC_01/contrast{cid}.nii.gz'))
        if len(cmaps) == 0:
            print(f'no cmaps found for contrast:{cid}')
            return

        # Filter covars to only subjects with images
        image_subjects = [x.split('/')[-7] for x in cmaps]
        df = df[df["ID"].isin(image_subjects)]

        # Filter images to only subjects with all covars
        covar_subjects = df.ID.unique()
        cmaps = [x for x in cmaps if x.split('/')[-7] in covar_subjects]

        # Make report of filtered images with corresponding dataframe
        _glm_report(df, cmaps, report_file)


def main(root_dir):
    subjects_dir = os.path.join(root_dir, 'SUBJECTS')
    group_dir = os.path.join(root_dir, 'GROUP')
    roi_dir = os.path.join(root_dir, 'ROIS')

    _run(subjects_dir, group_dir, roi_dir)

    glm_reports(subjects_dir, group_dir)


if __name__ == '__main__':
    import sys

    main(sys.argv[1])
