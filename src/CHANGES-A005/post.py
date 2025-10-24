import pandas as pd
from scipy.io import loadmat
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests
import numpy as np


NETWORKS = ['DorsAttn', 'SalVentAttn', 'Default']



def get_names(df):
    # Get atlas name before first period
    df['r1atlas'] = df['r1name'].str.extract(r'([^.]*)')
    df['r2atlas'] = df['r2name'].str.extract(r'([^.]*)')

    # hemisphere is after period, between two underscores
    df['r1hemi'] = df['r1name'].str.extract(r'\.[^_]+_([^_]+)_')
    df['r2hemi'] = df['r2name'].str.extract(r'\.[^_]+_([^_]+)_')
    
    # network is after period, between 2nd and 3rd underscores
    df['r1network'] = df['r1name'].str.extract(r'\.[^_]*_(?:[^_]*_){1}([^_]+)_')
    df['r2network'] = df['r2name'].str.extract(r'\.[^_]*_(?:[^_]*_){1}([^_]+)_')

    # region is after last underscore
    df['r1region'] = df['r1name'].str.extract(r'(?:[^_]*_){3}(.*)')
    df['r2region'] = df['r2name'].str.extract(r'(?:[^_]*_){3}(.*)')

    # handle schaefer400 with different format
    condition = df['r1atlas'] == 'Schaefer400'
    extracted_values = df.loc[condition, 'r1name'].str.extract(r'(?:[^_]*_){2}([^_]+)_')
    df.loc[condition, 'r1hemi'] = extracted_values[0]
    extracted_values = df.loc[condition, 'r1name'].str.extract(r'(?:[^_]*_){3}([^_]+)_')
    df.loc[condition, 'r1network'] = extracted_values[0]
    extracted_values = df.loc[condition, 'r1name'].str.extract(r'(?:[^_]*_){4}(.*)')
    df.loc[condition, 'r1region'] = extracted_values[0]

    condition = df['r2atlas'] == 'Schaefer400'
    extracted_values = df.loc[condition, 'r2name'].str.extract(r'(?:[^_]*_){2}([^_]+)_')
    df.loc[condition, 'r2hemi'] = extracted_values[0]
    extracted_values = df.loc[condition, 'r2name'].str.extract(r'(?:[^_]*_){3}([^_]+)_')
    df.loc[condition, 'r2network'] = extracted_values[0]
    extracted_values = df.loc[condition, 'r2name'].str.extract(r'(?:[^_]*_){4}(.*)')
    df.loc[condition, 'r2region'] = extracted_values[0]

    # handle CONN toolbox networks atlas format
    condition = df['r1atlas'] == 'networks'
    extracted_values = df.loc[condition, 'r1name'].str.extract(r'\.([^\.]*)\.')
    df.loc[condition, 'r1network'] = extracted_values[0]
    condition = df['r2atlas'] == 'networks'
    extracted_values = df.loc[condition, 'r2name'].str.extract(r'\.([^\.]*)\.')
    df.loc[condition, 'r2network'] = extracted_values[0]

    condition = df.r1region.isna()
    extracted_values = df.loc[condition, 'r1name'].str.extract(r'[^.]*\.([^.]*)$')
    df.loc[condition, 'r1region'] = extracted_values[0]

    condition = df.r2region.isna()
    extracted_values = df.loc[condition, 'r2name'].str.extract(r'[^.]*\.([^.]*)$')
    df.loc[condition, 'r2region'] = extracted_values[0]

    #condition = df['r2atlas'] == 'Yeo2011'
    #extracted_values = df.loc[condition, 'r2region']
    #df.loc[condition, 'r2network'] = extracted_values
    condition = (df['r2atlas'] == 'Yeo2011') & (df['r2region'] == 'Default')
    df.loc[condition, 'r2network'] = 'Default'
    condition = (df['r2atlas'] == 'Yeo2011') & (df['r2region'] == 'Dorsal Attention')
    df.loc[condition, 'r2network'] = 'DorsAttn'
    condition = (df['r2atlas'] == 'Yeo2011') & (df['r2region'] == 'Frontoparietal')
    df.loc[condition, 'r2network'] = 'Cont'
    condition = (df['r2atlas'] == 'Yeo2011') & (df['r2region'] == 'Salience')
    df.loc[condition, 'r2network'] = 'SalVentAttn'

    # Now make the concat'd names
    df['r1n'] = df[['r1atlas', 'r1hemi', 'r1network', 'r1region']].apply(lambda x : x.str.cat(sep='.'), 1)
    df['r2n'] = df[['r2atlas', 'r2hemi', 'r2network', 'r2region']].apply(lambda x : x.str.cat(sep='.'), 1)

    df.r1hemi = df.r1hemi.fillna('')
    df.r2hemi = df.r2hemi.fillna('')
    df.r1network = df.r1network.fillna('')
    df.r2network = df.r2network.fillna('')
    df.r1region = df.r1region.fillna('')
    df.r2region = df.r2region.fillna('')

    return df


def load_data(mat_file, subjects_file, conn_dir):
    data = []

    # Load from main conn mat file 
    m = loadmat(mat_file)
    sources = m['CONN_x']['Analyses'][0][0][0][0]['sources']
    sources = [x[0] for x in sources[0]]
    sources = ['sclimbic.Left-BF', 'sclimbic.Right-BF']

    # Load subjects
    with open(subjects_file, 'r') as f:
        subjects = f.read().splitlines()

    # Load each parcel size
    for nparcels in ['100', '200', '400']:
        m = loadmat(f'{conn_dir}/results/firstlevel/SBC_01/resultsROI_Condition001.mat')

        # Extract ROI names from m mat
        names1 = [x[0] for x in m['names'][0]]
        names2 = [x[0] for x in m['names2'][0]]
    
        # Extract the z values for pairs
        for s, subject in enumerate(subjects):
            for j, n1 in enumerate(names1):
                for k, n2 in enumerate(names2):
    
                    if n1 == n2:
                        continue
    
                    if n1.startswith('Schaefer') and n1[8:11] != nparcels:
                        continue
    
                    if n2.startswith('Schaefer') and n2[8:11] != nparcels:
                        continue
    
                    if n1 not in sources or (not n2.startswith('Yeo2011') and n2[8:11] != nparcels):
                        continue
    
                    data.append({
                        'id': subject,
                        'r1num': j,
                        'r2num': k,
                        'r1name': names1[j],
                        'r2name': names2[k],
                        #'r2name': names2[k].replace('\t','_'),
                        'zvalue': m['Z'][j][k][s]
                    })

    return data


def get_covariates(mat_file):
    covariates = {}

    m = loadmat(mat_file)

    nsubjects = int(m['CONN_x']['Setup'][0][0][0][0]['nsubjects'][0][0])

    # Get list of subject ids
    subjects = [m['CONN_x']['Setup'][0][0][0][0]['structural'][0][i][0][0][0][0][0] for i in range(0, 85)]
    subjects = [x.split('/')[6] for x in subjects]
    covariates['id'] = subjects

    # Get list of covariates
    covar_names = list(m['CONN_x']['Setup'][0][0][0][0]['l2covariates']['names'])[0][0][0]

    # Load each covariate values
    for i, c in enumerate(covar_names):
        n = str(c[0]).strip()
        if n == '' or n == 'AllSubjects' or n.startswith('QC_'):
            continue

        v = []
        for s in range(0, nsubjects):
            v.append(m['CONN_x']['Setup'][0][0][0][0]['l2covariates']['values'][0][0][0][s][0][i][0][0])

        # Append name/values to covariate list
        covariates[n] = v

    # Return dataframe with column per covariate
    return pd.DataFrame(covariates)


def __main__():
    ROOTDIR = '/OUTPUTS'
    subjects_file = f'{ROOTDIR}/subjects.txt'
    mat_file = f'{ROOTDIR}/conn.mat'
    csv_file = f'{ROOTDIR}/network_means.csv'
    conn_dir = f'{ROOTDIR}/conn'
    results = []

    # Load covariates
    covars = get_covariates(mat_file)

    # Load connectivity data
    data = load_data(mat_file)
    df = pd.DataFrame(data)
    df = get_names(df)
    print('loaded')

    # group by network, mean for each subject
    dfx = df[['id', 'r2atlas', 'r2network', 'zvalue']]
    dfx = dfx[dfx['r2network'].isin(NETWORKS)]
    dfg = dfx.groupby(['id', 'r2atlas', 'r2network']).mean()
    dfg.to_csv(csv_file)
    print(dfg)

    # Get just s400
    dfs = dfg.reset_index()
    dfs = dfs[dfs['r2atlas'] == 'Schaefer400']

    # Merge with covars and make combined sex column
    dff = pd.merge(covars, dfs)
    dff['SEX'] = np.where(dff['SEX_Male'] == 1, 'Male', 'Female')

    # Get results without controlling for anything
    results = []
    for n in NETWORKS:
        formula = f'CCI ~ {n}'
        print(formula)
        model = smf.ols(formula, data=dff).fit()

        beta = model.params[n]
        pval = model.pvalues[n]
        rsqd = model.rsquared

        results.append({'network': n, 'beta': beta, 'pval': pval, 'r2': rsqd})

    results = pd.DataFrame(results)
    results['p_fdr'] =  multipletests(results['pval'], method='fdr_bh')[1]
    results.to_csv('/OUTPUTS/results_no_covars.csv')
    print(results)

    # With controlling for AGE/SEX/Edu
    results = []
    for n in networks:
        formula = f'CCI ~ {n} + AGE + SEX + Edu'
        print(formula)
        model = smf.ols(formula, data=dff).fit()
        results.append({
            'network': n, 
            'beta': model.params[n],
            'pval':  model.pvalues[n],
            'r2':  model.rsquared})

    results = pd.DataFrame(results)
    results['p_fdr'] =  multipletests(results['pval'], method='fdr_bh')[1]
    results.to_csv('/OUTPUTS/results_with_covars.csv')
    print(results)
