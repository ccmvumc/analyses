import logging
import os, shutil

from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import matplotlib.image as img 
import seaborn as sns
import pandas as pd


logger = logging.getLogger('make_pdfpages')


def _add_results_page(pdf, subjects, conditions, sources, thresholds, prefix):
    slice_print = f'{result_dir}/{prefix}_slice_print.jpg'
    volume_print = f'{result_dir}/{prefix}_volume_print.jpg'

    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(8.5, 11))

    fig.suptitle(f'Between Subject Effects: {subjects}\nBetween Session Effects: {conditions}\nBetween Condition Effects: {sources}\nThresholds: {thresholds}')

    _image = img.imread(volume_print)
    axes[0].imshow(_image)
    axes[0].axis('off')

    _image = img.imread(slice_print)
    axes[1].imshow(_image)
    axes[1].axis('off')

    plt.subplots_adjust(left=0.01, top=0.85, right=0.98, bottom=0.01, wspace=0.01, hspace=0.01)

    pdf.savefig(fig)

    plt.close(fig)


def _add_results(pdf, result_dir, subjects, conditions, sources):
    # Copy png to jpg to allow read
    [shutil.copyfile(f'{result_dir}/{p}', f'{result_dir}/{p[:-4]}.jpg') for p in os.listdir(result_dir) if p.endswith('.png')]

    _add_results_page(pdf, subjects, conditions, sources, 'Preset1', 'preset1')
    _add_results_page(pdf, subjects, conditions, sources, 'Preset1', 'preset1_p0.005')
    _add_results_page(pdf, subjects, conditions, sources, 'Preset1', 'preset1_p0.05')
    _add_results_page(pdf, subjects, conditions, sources, 'Preset2', 'preset2')
    _add_results_page(pdf, subjects, conditions, sources, 'Preset2, p<0.005', 'preset2_p0.005')
    _add_results_page(pdf, subjects, conditions, sources, 'Preset2, p<0.05', 'preset2_p0.05')


def _add_pairplot_pages(pdf, df):
    # seaborn pairplot without grouping, then group by sex, then group by group
    for h in [None, 'SEX', 'GROUP']:
        sns.pairplot(df, hue=h)
        _fig = plt.gcf()
        pdf.savefig(_fig, dpi=300)
        plt.close(_fig)


def _load_covariates(filename, subjects):
    # Load covariates from csv file to pandas dataframe
    logger.info(f'loading csv:{filename}')
    df = pd.read_csv(filename)

    # Set index and select subjects
    df['ID'] = df['ID'].astype(str)
    df = df.set_index('ID')
    df = df.loc[subjects]

    return df


def make_report(results_dir, pdf_file, csv_file, subjects_file):
    with PdfPages(pdf_file) as pdf:
        # Page for each second-level result
        for subj in sorted(os.listdir(results_dir)):
            if subj.startswith('.'):
                continue

            for cond in sorted(os.listdir(os.path.join(results_dir, subj))):
                if cond.startswith('.'):
                    continue

                for sources in sorted(os.listdir(os.path.join(results_dir, subj, cond))):
                    if sources.startswith('.'):
                        continue

                    logger.info(f'add_results:{subj}:{cond}:{sources}')
                    _dir = os.path.join(results_dir, subj, cond, sources)
                    _add_results(pdf, _dir, subj, cond, sources)

        # Covariate plots
        if not os.path.exists(csv_file):
            logger.info('no csv file, cannot plot covariates.')
        elif not os.path.exists(subjects_file):
            logger.info('no subjects file, cannot plot covariates.')
        else:
            # Load subjects
            with open(subjects_file, 'r') as f:
                subjects = f.read().splitlines()

            # Load subject covars
            df = _load_covariates(csv_file, subjects)

            # Plot covars on PDF
            _add_pairplot_pages(pdf, df)


if __name__ == "__main__":
    CSV_FILE = '/INPUTS/covariates.csv'
    SUBJECTS_FILE = '/OUTPUTS/subjects.txt'
    RESULTS_DIR = '/OUTPUTS/conn/results/secondlevel/SBC_01'
    PDF_NAME = '/OUTPUTS/report.pdf'
    make_report(RESULTS_DIR, PDF_NAME, CSV_FILE, SUBJECTS_FILE)
