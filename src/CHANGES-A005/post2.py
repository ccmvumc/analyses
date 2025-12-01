import os

import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from neuroCombat import neuroCombat
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests


ATLASES  = ['Yeo2011', 'Schaefer100', 'Schaefer200', 'Schaefer400']

NETWORKS = ['Default', 'DorsAttn', 'SalVentAttn']

# Page 1: 
# conn values boxplots per network per study
# same box plots after combat

# Page 2:
# CCI ~ z: stemplot, color red/blue, marker by significance
# CCI ~ z + Age + Sex + Edu: stemplot
# CCI ~ z + Sex + Edu: surface/stemplot, """
# BF ~ z, """
# BF ~ z + Age + Sex + Edu, """
# BF + z + Sex + Edu, """

# Page 3: 
# same as page 1, but individual regions instead of averaging across networks


def get_results(df, network, formula):
    print(f'Fitting model:{formula}')
    model = smf.ols(formula, data=df).fit()

    print(model.summary())

    print(f'Extracting results:{network}')
    
    results = {
        'network': network,
        'beta': model.params[network],
        'pval': model.pvalues[network],
        'r2': model.rsquared
    }

    return results


def run_results(data_dir):
    # Calculate results for each network with and without covars

    for atlas in ATLASES:
        # Load combat means
        combat_file = f'{data_dir}/combat_network_means-{atlas}.csv'
        df = pd.read_csv(combat_file)

        # First without controlling
        results = []
        for n in NETWORKS:
            formula = f'CCI ~ {n}'
            results.append(get_results(df, n, formula))

        # Convert list to dataframe
        results = pd.DataFrame(results)

        # Get fdr-corrected pvals
        results['p_fdr'] = multipletests(results['pval'], method='fdr_bh')[1]

        # Save for this no covars for this atlas
        results.to_csv(f'{data_dir}/combat_cci_no_covars-{atlas}.csv', index=False)

        # Now with covars
        results = []
        for n in NETWORKS:
            # With controlling for AGE/SEX/Edu
            formula = f'CCI ~ {n} + AGE + SEX + Edu'
            results.append(get_results(df, n, formula))

        # Convert list to dataframe
        results = pd.DataFrame(results)

        # Get fdr-corrected pvals
        results['p_fdr'] = multipletests(results['pval'], method='fdr_bh')[1]

        # Save file with covars for this atlas
        results.to_csv(f'{data_dir}/combat_cci_with_covars-{atlas}.csv', index=False)


# Page A: appendix for parcellations
def _parcellations():
    return


def make_report(data_dir, pdf_file):
    with PdfPages(pdf_file) as pdf:
        _stemplots(data_dir, pdf)
        _stemplots_covars(data_dir, pdf)
        _boxplots(data_dir, pdf)
        _scatterplots(data_dir, pdf)


def marker(p):
    return '.' if p < 0.05 else 'x'


def _stemplot(ax, df):
    df['color'] = df['beta'].apply(lambda x: 'red' if x > 0 else 'blue')
    df['marker'] = df['pval'].apply(marker)

    # Draw the zero line
    ax.axhline(0, linewidth=1, color='black')

    # Draw the stem lines
    ax.vlines(df.network, 0, df.beta, linewidth=2, colors=df['color'])

    # Draw the points per row
    for _, row in df.iterrows():
        if row['pval'] > 0.05:
            _shape = 'o'
            _face = 'white'
            _edge = row['color']
        elif row['p_fdr'] > 0.05:
            _shape = 'o'
            _face = row['color']
            _edge = 'black'
        else:
            _shape = '*'
            _face = row['color']
            _edge = row['color']

        ax.scatter(
            x=row['network'],
            y=row['beta'],
            facecolors=_face,
            marker=_shape,
            edgecolors=_edge
        )

        if row['pval'] < 0.05:
            _text = f'  p={row["pval"]:.2f}'
            ax.text(
                row['network'],
                row['beta'],
                _text
            )

    ax.set_ylabel('Beta')


def _stemplots(data_dir, pdf):
    sns.set_style('darkgrid')

    fig, ax = plt.subplots(nrows=4, ncols=2, figsize=(8.5, 11))
    fig.suptitle('Basal Forebrain Connectivity\nCCI score ~ Z')

    ax[0][0].set_title('Before neuroCombat')
    ax[0][1].set_title('After neuroCombat')
    tot_lim = 0.5

    for i, atlas in enumerate(ATLASES):
        # Load data from file
        df = pd.read_csv(f'{data_dir}/results_no_covars-{atlas}.csv')
        df = df.sort_values('network')
    
        # Plot it
        _stemplot(ax[i][0], df)

        # Label it
        ax[i][0].set_xlabel(atlas)

        # Store limits
        cur_lim = max(abs(df.beta.min()), abs(df.beta.max()))*1.10
        tot_lim = max(tot_lim, cur_lim)

        # Load data from file
        df = pd.read_csv(f'{data_dir}/combat_cci_no_covars-{atlas}.csv')
    
        # Plot it
        _stemplot(ax[i][1], df)

        # Label it
        ax[i][1].set_xlabel(atlas)

        # Store limits
        cur_lim = max(abs(df.beta.min()), abs(df.beta.max()))*1.10
        tot_lim = max(tot_lim, cur_lim)

    # Standardize ranges
    for i, atlas in enumerate(ATLASES):
        ax[i][0].set_ylim([-tot_lim, tot_lim])
        ax[i][1].set_ylim([-tot_lim, tot_lim])

    # Finalize figure and save to pdf file
    plt.tight_layout()
    pdf.savefig(fig)
    plt.close(fig)


def _stemplots_covars(data_dir, pdf):
    sns.set_style('darkgrid')

    fig, ax = plt.subplots(nrows=4, ncols=2, figsize=(8.5, 11))
    fig.suptitle('Basal Forebrain Connectivity\nCCI score ~ Z + AGE + SEX + Edu')

    ax[0][0].set_title('Before neuroCombat')
    ax[0][1].set_title('After neuroCombat')
    tot_lim = 0.5

    for i, atlas in enumerate(ATLASES):
        # Load data from file
        df = pd.read_csv(f'{data_dir}/results_with_covars-{atlas}.csv')
        df = df.sort_values('network')
    
        # Plot it
        _stemplot(ax[i][0], df)

        # Label it
        ax[i][0].set_xlabel(atlas)

        # Store limits
        cur_lim = max(abs(df.beta.min()), abs(df.beta.max()))*1.10
        tot_lim = max(tot_lim, cur_lim)

        # Load data from file
        df = pd.read_csv(f'{data_dir}/combat_cci_with_covars-{atlas}.csv')
    
        # Plot it
        _stemplot(ax[i][1], df)

        # Label it
        ax[i][1].set_xlabel(atlas)

        # Store limits
        cur_lim = max(abs(df.beta.min()), abs(df.beta.max()))*1.10
        tot_lim = max(tot_lim, cur_lim)

    # Standardize ranges
    for i, atlas in enumerate(ATLASES):
        ax[i][0].set_ylim([-tot_lim, tot_lim])
        ax[i][1].set_ylim([-tot_lim, tot_lim])

    # Finalize figure and save to pdf file
    plt.tight_layout()
    pdf.savefig(fig)
    plt.close(fig)


def _scatterplots(data_dir, pdf):
    df = pd.DataFrame()
    df_pre = pd.DataFrame()

    for i, atlas in enumerate(ATLASES):
        dfb = pd.read_csv(f'{data_dir}/network_means-{atlas}.csv')
        dfb['atlas'] = atlas
        dfa = pd.read_csv(f'{data_dir}/combat_network_means-{atlas}.csv')
        dfa['atlas'] = atlas
        df = pd.concat([df, dfa])
        df_pre = pd.concat([df_pre, dfb])

    df_pre = pd.merge(df_pre, df[['ID', 'CCI', 'AGE', 'Edu']], left_on='id', right_on='ID')

    s = sns.pairplot(
        df_pre,
        hue='atlas', 
        aspect=1.0, 
        kind='reg',
        height=3.0,
        markers='.', 
        x_vars=['CCI', 'AGE', 'Edu'],
        y_vars=['Default', 'DorsAttn', 'SalVentAttn'],
    )
    s.fig.suptitle('Basal Forebrain Connectivity before neuroCombat')
    pdf.savefig(s.fig)

    sns.set_style('darkgrid')
    s = sns.pairplot(
        df,
        hue='atlas', 
        aspect=1.0, 
        kind='reg',
        height=3.0,
        markers='.', 
        x_vars=['CCI', 'AGE', 'Edu'],
        y_vars=['Default', 'DorsAttn', 'SalVentAttn'],
    )
    s.fig.suptitle('Basal Forebrain Connectivity after neuroCombat')
    pdf.savefig(s.fig)


def _boxplots(data_dir, pdf):
    sns.set_style('darkgrid')
    fig, ax = plt.subplots(nrows=4, ncols=2, figsize=(8.5, 11))
    fig.suptitle('Basal Forebrain Connectivity')

    for i, atlas in enumerate(ATLASES):
        dfb = pd.read_csv(f'{data_dir}/network_means-{atlas}.csv')
        dfa = pd.read_csv(f'{data_dir}/combat_network_means-{atlas}.csv')
        dfa['Study'] = dfa['Study'].replace({1: 'CHANGES', 2: 'NewhouseCC', 3: 'ACOBA'})
        dfb = pd.merge(dfb, dfa[['ID', 'Study']], left_on='id', right_on='ID')
        dfbm = pd.melt(dfb, id_vars=['ID', 'Study'], var_name=atlas, value_vars=NETWORKS, value_name='Z')
        dfam = pd.melt(dfa, id_vars=['ID', 'Study'], var_name=atlas, value_vars=NETWORKS, value_name='Z')

        # Plot network columns by Study, before Combat
        sns.boxplot(data=dfbm, ax=ax[i][0], hue='Study', y='Z', x=atlas)
        ax[i][0].set_ylim([-0.5, 0.5])
        if i == 0:
            ax[i][0].set_title('Before neuroCombat')
        else:
            ax[i][0].legend_.remove()

        # Plot network columns by Study, after Combat
        sns.boxplot(data=dfam, x=atlas, y='Z', ax=ax[i][1], hue='Study')
        ax[i][1].set_ylim([-0.5, 0.5])

        if i == 0:
            ax[i][1].set_title('After neuroCombat')
        else:
            ax[i][1].legend_.remove()

    # Finalize figure and save to pdf file
    plt.tight_layout()
    pdf.savefig()
    plt.close(fig)


def plot_main():
    plot = None

    return plot


def _load_covariates(filename):
    # Load covariates from csv file to pandas dataframe
    df = pd.read_csv(filename)
    df['ID'] = df['ID'].astype(str)
    df = df.set_index('ID')

    return df


def combat_means(df, combat_file):
    covars = df[['CCI', 'AGE', 'SEX', 'Edu', 'Study']]
    data = df[NETWORKS].T.values
    batch_col = 'Study'
    categorical_cols = ['SEX']

    # Run combat to get harmonized data
    combat_output = neuroCombat(
        dat=data,
        covars=covars,
        batch_col=batch_col,
        categorical_cols=categorical_cols,
    )

    # Save harmonized data
    df_combat = df.copy()
    df_combat[NETWORKS] = combat_output['data'].T
    df_combat.to_csv(combat_file)


def load_network_means(filename):
    df = pd.read_csv(filename)
    df['ID'] = df['id'].astype(str)
    df = df.drop(columns=['id'])
    df = df.set_index('ID')
    return df


def main(covariates_file, data_dir):
    pdf_file = f'{data_dir}/report.pdf'
    covars = _load_covariates(covariates_file)

    for a in ATLASES:
        input_file = f'{data_dir}/network_means-{a}.csv'
        combat_file = f'{data_dir}/combat_network_means-{a}.csv'

        # Load means, merge covars, combat
        df = load_network_means(input_file)
        df = pd.merge(df, covars, left_index=True, right_index=True)
        combat_means(df, combat_file)

    run_results(data_dir)
    make_report(data_dir, pdf_file)


if __name__ == "__main__":
    CSV_FILE = '/Users/boydb1/Desktop/covariates-CHANGES_A005.csv'
    DATA_DIR = '/Users/boydb1/Desktop/CHANGES-A005'
    main(CSV_FILE, DATA_DIR)
