import logging
import os, shutil

from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import matplotlib.image as img 
import seaborn as sns
import pandas as pd


logger = logging.getLogger('make_pdfpages')


def _add_results_page(pdf, result_dir, subjects, conditions, sources):
    shutil.copyfile(f'{result_dir}/slice_print.png', f'{result_dir}/slice_print.jpg')
    shutil.copyfile(f'{result_dir}/volume_print.png', f'{result_dir}/volume_print.jpg')

    slice_print = os.path.join(result_dir, 'slice_print.jpg')
    volume_print = os.path.join(result_dir, 'volume_print.jpg')

    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(8.5, 11))

    fig.suptitle(f'{subjects}\n{conditions}\n{sources}')

    _image = img.imread(volume_print)
    axes[0].imshow(_image)
    axes[0].axis('off')

    _image = img.imread(slice_print)
    axes[1].imshow(_image)
    axes[1].axis('off')

    plt.subplots_adjust(left=0.01, top=0.85, right=0.98, bottom=0.01, wspace=0.01, hspace=0.01)

    pdf.savefig(fig)

    plt.close(fig)


def _add_pairplot_pages(pdf, df):
    # seaborn pairplot without grouping
    sns.pairplot(df)
    pdf.savefig(plt.gcf(), dpi=300)
    plt.close(fig)

    # then group by sex
    sns.pairplot(df, hue='SEX')
    pdf.savefig(plt.gcf(), dpi=300)
    plt.close(fig)

    # then subject group
    sns.pairplot(df, hue='GROUP')
    pdf.savefig(plt.gcf(), dpi=300)
    plt.close(fig)


def _load_covariates(filename, subjects):
    # Load covariates from csv file to pandas dataframe
    logger.info(f'loading csv:{filename}')
    df = pd.read_csv(filename, dtype=str)

    # Set index and select subjects
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
                    _add_results_page(pdf, _dir, subj, cond, sources)

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
