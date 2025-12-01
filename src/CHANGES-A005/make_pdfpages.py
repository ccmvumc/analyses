import os
import logging

from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


logger = logging.getLogger('make_pdfpages')


def _add_pairplot_pages(pdf, df):
    sns.set_theme(style="white", rc={"figure.figsize": (8.5, 11)})

    # First pairplot all columns with no hue
    try:
        sns.pairplot(vars=df.columns, height=2.0)
        _fig = plt.gcf()
        pdf.savefig(_fig, dpi=300, papertype='letter', orientation='portrait')
        plt.close(_fig)
    except Exception as err:
        logger.error(f'pairplot failed:{err}')

    # seaborn pairplot without grouping, then group by sex, then group by group
    hues = [None, 'SEX', 'GROUP']

    if 'Study' in df.columns:
        hues.append('Study')

    for h in hues:
        logger.info(f'pairplot:{h}')
        sns.pairplot(df, hue=h, height=2.0)
        _fig = plt.gcf()
        _fig.tight_layout()
        pdf.savefig(_fig, dpi=300, papertype='letter', orientation='portrait')
        plt.close(_fig)

    # Now reg plots
    sns.pairplot(df, height=2.0, kind='reg', corner=True)
    _fig = plt.gcf()
    pdf.savefig(_fig, dpi=300, papertype='letter', orientation='portrait')
    plt.close(_fig)
    sns.pairplot(df, hue='SEX', height=2.0, kind='reg', corner=True)
    _fig = plt.gcf()
    pdf.savefig(_fig, dpi=300, papertype='letter', orientation='portrait')
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


def _add_more_pages(pdf, dfn):
    # Pivot to row per ID/atlas with column per network and keep other covars
    dfp = dfn.reset_index()
    dfp = dfp.pivot(
        index=['ID', 'r2atlas', 'CCI', 'AGE', 'Edu'],
        columns=['r2network'],
        values='zvalue'
    )
    dfp = dfp.reset_index()

    sns.set_style('whitegrid')
    sns.pairplot(
        dfp,
        hue='r2atlas',
        aspect=1.0,
        kind='reg',
        height=3.0,
        markers='.',
        x_vars=['CCI', 'AGE', 'Edu'],
        y_vars=['Default', 'DorsAttn', 'SalVentAttn']
    )
    _fig = plt.gcf()
    pdf.savefig(_fig, dpi=300, papertype='letter', orientation='portrait')
    plt.close(_fig)


def _load_network_means(filename):
    dfn = pd.read_csv(filename)
    dfn['ID'] = dfn['id'].astype(str)
    dfn = dfn.drop(columns=['id'])
    dfn = dfn.set_index('ID')
    return dfn


def _add_results_page(pdf, results_dir):
    fig, ax = plt.subplots(figsize=(8,4))
    ax.axis('off')




def make_report(pdf_file, csv_file, subjects_file, network_file):
    with PdfPages(pdf_file) as pdf:
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

            # Plot network means vs covars
            dfn = _load_network_means(network_file)
            dfn = pd.merge(dfn, df, left_index=True, right_index=True)
            _add_more_pages(pdf, dfn)


if __name__ == "__main__":
    CSV_FILE = '/INPUTS/covariates.csv'
    SUBJECTS_FILE = '/OUTPUTS/subjects.txt'
    PDF_NAME = '/OUTPUTS/report.pdf'
    NETWORK_FILE = '/OUTPUTS/network_means.csv'
    make_report(PDF_NAME, CSV_FILE, SUBJECTS_FILE, NETWORK_FILE)
