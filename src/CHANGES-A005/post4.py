import pandas as pd
import seaborn as sns
from scipy.io import loadmat
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from statsmodels.stats.multitest import multipletests
from scipy import stats


CENTDIR = '/Users/boydb1/STUFF_for_ANALYSIS_repo/Schaefer2018/MNI/centroids'

ATLASES  = ['Kong2022Yeo17', 'Schaefer100', 'Schaefer200', 'Schaefer400']

NETWORK2COLOR = {
    'Aud': 'olive',
    'ContA': 'orange',
    'ContB': 'gold',
    'ContC': 'darkorange',
    'DefaultA': 'brown',
    'DefaultB': 'tan',
    'DefaultC': 'chocolate',
    'DorsAttnA': 'lime',
    'DorsAttnB': 'green',
    'Language': 'goldenrod',
    'SalVenAttnA': 'hotpink',
    'SalVenAttnB': 'magenta',
    'SomMotA': 'cyan',
    'SomMotB': 'deepskyblue',
    'SomMotC': 'aquamarine',
    'VisualA': 'darkviolet',
    'VisualB': 'violet',
    'VisualC': 'mediumpurple',
}


def load_one2three(dirname, pcount):
    centroids1 = pd.read_csv(f'{dirname}/Schaefer2018_{pcount}Parcels_7Networks_order_FSLMNI152_2mm.Centroid_RAS.csv')
    centroids3 = pd.read_csv(f'{dirname}/Schaefer2018_{pcount}Parcels_Kong2022_17Networks_order_FSLMNI152_2mm.Centroid_RAS.csv')
    one2three = {}
    for i, c1 in centroids1.iterrows():
        match = False
        for j, c3 in centroids3.iterrows():
            if c1['R'] == c3['R'] and c1['A'] == c3['A'] and c1['S'] == c3['S']:
                #print(c1['ROI Label'], c1['ROI Name'], c3['ROI Label'], c3['ROI Name'])
                n1 = c1['ROI Name']
                r1 = f'Schaefer{pcount}.{c1["ROI Name"]}'.replace('_','.', 3).replace('7Networks.','')
                r3 = f'Schaefer{pcount}.{c3["ROI Name"]}'.replace('_','.', 3).replace('17networks.','')
                one2three.update({r1: r3})
                match = True
    
        if not match:
            print('failed to match:', i)

    return one2three


def get_17names(df, dirname):
    one2three = {}

    for n in [100,200,400]:
        one2three.update(load_one2three(dirname, str(n)))

    df['r2n17'] = df['r2n'].map(one2three).fillna('')
    df[['r2atlas17', 'r2hemi17', 'r2network17', 'r2region17']] = df['r2n17'].str.split('.', expand=True).fillna('')

    return df


def get_covariates_csv(filename):
    # Load covariates from csv file to pandas dataframe
    df = pd.read_csv(filename)
    df['id'] = df['ID'].astype(str)
    df['Study'] = df['Study'].replace({1: 'CHANGES', 2: 'NewhouseCC', 3: 'ACOBA'})
    return df


def get_covariates_mat(mat_file):
    covariates = {}

    m = loadmat(mat_file)

    nsubjects = int(m['CONN_x']['Setup'][0][0][0][0]['nsubjects'][0][0])

    # Get list of subject ids
    subjects = [m['CONN_x']['Setup'][0][0][0][0]['structural'][0][i][0][0][0][0][0] for i in range(0, nsubjects)]
    subjects = [x.split('/')[-2] for x in subjects]
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

    condition = (df['r2atlas'] == 'Yeo2011') & (df['r2region'] == 'Default')
    df.loc[condition, 'r2network'] = 'Default'
    condition = (df['r2atlas'] == 'Yeo2011') & (df['r2region'] == 'Dorsal Attention')
    df.loc[condition, 'r2network'] = 'DorsAttn'
    condition = (df['r2atlas'] == 'Yeo2011') & (df['r2region'] == 'Frontoparietal')
    df.loc[condition, 'r2network'] = 'Cont'
    condition = (df['r2atlas'] == 'Yeo2011') & (df['r2region'] == 'Salience')
    df.loc[condition, 'r2network'] = 'SalVentAttn'
    condition = (df['r2atlas'] == 'Yeo2011') & (df['r2region'] == 'Visual')
    df.loc[condition, 'r2network'] = 'Vis'
    condition = (df['r2atlas'] == 'Yeo2011') & (df['r2region'] == 'Limbic')
    df.loc[condition, 'r2network'] = 'Limbic'
    condition = (df['r2atlas'] == 'Yeo2011') & (df['r2region'] == 'Somatosensory')
    df.loc[condition, 'r2network'] = 'SomMot'

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
    print(results)

    return results


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
                        'zvalue': m['Z'][j][k][s]
                    })

    # Return as dataframe
    df = pd.DataFrame(data)
    return df


def get_results(dfp, regions):
    results = []

    for r in regions:
        m = dfp[r].mean()
        t_stat, p_val = stats.ttest_1samp(dfp[r], 0)

        results.append({
            'region': r,
            'rmean': m,
            'beta': t_stat,
            'pval': p_val
        })

    results = pd.DataFrame(results)
    results['p_fdr'] = multipletests(results['pval'], method='fdr_bh')[1]
    return results



def get_network_color(network):
    return NETWORK2COLOR.get(network, 'black')


def make_report(df, pdf_file):
    with PdfPages(pdf_file) as pdf:
        _stemplots(df, pdf)


def _stemplots(df, pdf):
    sns.set_style('white')

    fig, ax = plt.subplots(nrows=4, ncols=1, figsize=(8.5, 11))
    fig.suptitle('SCLIMBIC Basal Forebrain RS Connectivity -- Kong 2022 Yeo 17 Networks\nAverage Connectivity(n=85)')

    for i, atlas in enumerate(ATLASES):
        dfa = df[df.atlas == atlas]
        if dfa.empty:
            continue

        _stemplot(ax[i], dfa)
        ax[i].set_xlabel(atlas)

    # Standardize ranges
    pos_lim = 0.20
    neg_lim = 0.20
    for i, atlas in enumerate(ATLASES):
        ax[i].set_ylim([-neg_lim, pos_lim])

    # Finalize
    plt.tight_layout()
    pdf.savefig(fig)


def _stemplot(ax, df):
    rowcount = len(df)

    df['linecolor'] = df['rmean'].apply(lambda x: 'red' if x > 0 else 'blue')

    # Draw the zero line
    ax.axhline(0, linewidth=1, color='grey')

    # Draw the stem lines
    linewidth = min(int(400/rowcount), 8)
    ax.vlines(df.region, 0, df.rmean, linewidth=linewidth, colors=df['linecolor'])

    # Draw the points per row
    markersize = int(10000/rowcount)
    for _, row in df.iterrows():

        _color = get_network_color(row['region'].split('.')[0])

        if row['pval'] > 0.05:
            _shape = '.'
            _face = 'white'
            _edge = _color
        elif row['p_fdr'] > 0.05:
            _shape = '.'
            _face = _color
            _edge = _color
        else:
            _shape = 'o'
            _face = _color
            _edge = _color

        ax.scatter(
            x=row['region'],
            y=row['rmean'],
            facecolors=_face,
            marker=_shape,
            edgecolors=_edge,
            alpha=1.0,
            s=markersize,
        )

        if row['rmean'] > 0.15:
            _text = f'  {row["region"].split('.')[2]}'
            ax_text = ax.text(
                row['region'],
                row['rmean'],
                _text,
                size='small',
                #weight='bold',
                rotation=45,
            )
            ax_text.set_in_layout(False)


    if len(df) > 17:
        ax.set_xticklabels([])
    else:
        ax.set_xticklabels([x.split('.')[0] for x in df.region])
        ax.tick_params(axis='x', labelrotation=45)

    ax.set_ylabel('Z')


def get_kong22(df):
    df['network'] = df['region'].str.split('.').str[0]

    dfx = df
    dfx = dfx[['network', 'rmean', 'beta', 'pval', 'p_fdr']]
    dfn = dfx.groupby(['network']).mean()
    dfn['pval'] = 0
    dfn['p_fdr'] = 0
    dfn = dfn.reset_index()
    dfn['region'] = dfn['network']
    dfn['atlas'] = 'Kong2022Yeo17'

    return dfn


def main(data_dir):
    pdf_file = f'{data_dir}/report4.pdf'
    subjects_file = f'{data_dir}/subjects.txt'
    mat_file = f'{data_dir}/conn.mat'
    conn_dir = f'{data_dir}/conn'

    print('loading data')
    df = load_data(mat_file, subjects_file, conn_dir)
    df = get_names(df)

    # Get r17 names
    df = get_17names(df, CENTDIR)

    # Mean per r2 parcel across all r1
    df['r2n17hr'] = df['r2network17'] + '.' + df['r2hemi'] + '.' + df['r2region']
    df = df.sort_values('r2n17hr')
    dfx = df[['id', 'r2atlas', 'r2n17hr', 'zvalue']]
    dfn = dfx.groupby(['id', 'r2atlas', 'r2n17hr']).mean()
    dfn = dfn.reset_index()

    all_results = pd.DataFrame()

    for atlas in ATLASES:
        if atlas == 'Kong2022Yeo17':
            continue

        dfp = dfn[dfn['r2atlas'] == atlas].pivot(
            index='id',
            columns=['r2n17hr'],
            values='zvalue'
        ).reset_index()

        regions = [x for x in list(dfp.columns) if x != 'id']
        results = get_results(dfp, regions)
        results['atlas'] = atlas
        all_results = pd.concat([all_results, results])


    results = get_kong22(all_results)
    all_results = pd.concat([all_results, results])

    dfs = pd.DataFrame(all_results)
    make_report(dfs, pdf_file)


if __name__ == "__main__":
    CSV_FILE = '/Users/boydb1/Desktop/covariates-CHANGES_A005.csv'
    DATA_DIR = '/Users/boydb1/Downloads/changes_rsfc_basalforebrain'
    main(DATA_DIR)
