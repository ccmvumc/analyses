# ---ROI-only
# Schaefer200 Frontal and Cingulate
# DnSeg NBM

# Yeo Networks
# Orange: Frontoparietal
# Red: Default Mode
# Green: Salience
# Yellow: Limbic
# Pink: Dorsal Attention
# Purple: Visual
# Blue: Somatosensory motor

import os

import pandas as pd
import numpy as np
import seaborn as sns
import nilearn.plotting
from scipy.stats import ttest_rel, false_discovery_control, ttest_1samp
from nilearn.datasets import load_fsaverage, load_fsaverage_data, fetch_atlas_yeo_2011
from nilearn import plotting
from matplotlib.colors import ListedColormap
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import nibabel.freesurfer as fs


def get_colormap(lut_file):
    # Load file into np array
    lut = np.loadtxt(lut_file, dtype=str)

    # Extract rgb columns
    rgb_values = lut[:, 1:4].astype(float)

    # Return as colormap    
    return ListedColormap(rgb_values)


def get_colormap_left(lut_file):
    # Load file into np arry
    lut = np.loadtxt(lut_file, dtype=str)

    # Extract rgb columns from first half
    half_index = int(len(lut) / 2)
    rgb_values = lut[:half_index, 1:4].astype(float)

    # Return as colormap    
    return ListedColormap(rgb_values)


def get_colormap_right(lut_file):
    # Load file into np arry
    lut = np.loadtxt(lut_file, dtype=str)

    # Extract rgb columns from last half
    half_index = int(len(lut) / 2)
    rgb_values = lut[half_index:, 1:4].astype(float)

    # Return as colormap    
    return ListedColormap(rgb_values)


def get_atlas(df):
    df['r1atlas'] = df['r1name'].str.split('.').str[0]
    df['r2atlas'] = df['r2name'].str.split('.').str[0]
    return df


def get_hemi(df):
    df.loc[df.r1atlas == 'Schaefer200', 'r1hemi'] = df.r1name.str.split('.').str[1].str.split('_').str[1]
    df.loc[df.r2atlas == 'Schaefer200', 'r2hemi'] = df.r2name.str.split('.').str[1].str.split('_').str[1]
    df.loc[df.r1atlas.isin(['networks', 'Hypothal', 'Yeo2011', 'DnSeg']), 'r1region'] = 'both'
    df.loc[df.r2atlas.isin(['networks', 'Hypothal', 'Yeo2011', 'DnSeg']), 'r2region'] = 'both'
    return df


def get_network(df):
    df.loc[df.r1atlas == 'Schaefer200', 'r1network'] = df.r1name.str.split('.').str[1].str.split('_').str[2]
    df.loc[df.r2atlas == 'Schaefer200', 'r2network'] = df.r2name.str.split('.').str[1].str.split('_').str[2]
    df.loc[df.r1atlas.isin(['networks']), 'r1network'] = df.r1name.str.split('.').str[1]
    df.loc[df.r2atlas.isin(['networks']), 'r2network'] = df.r2name.str.split('.').str[1]
    df.loc[df.r1atlas.isin(['DnSeg']), 'r1network'] = df.r1name
    df.loc[df.r2atlas.isin(['DnSeg']), 'r2network'] = df.r2name
    return df


def get_region(df):
    df.loc[df.r1atlas == 'Schaefer200', 'r1region'] = df.r1name.str.split('.').str[1].str.split('_', n=3).str[3]
    df.loc[df.r2atlas == 'Schaefer200', 'r2region'] = df.r2name.str.split('.').str[1].str.split('_', n=3).str[3]
    df.loc[df.r1atlas.isin(['networks']), 'r1region'] = df.r1name.str.split('.').str[2]
    df.loc[df.r2atlas.isin(['networks']), 'r2region'] = df.r2name.str.split('.').str[2]
    df.loc[df.r1atlas.isin(['DnSeg']), 'r1region'] = df.r1name
    df.loc[df.r2atlas.isin(['DnSeg']), 'r2region'] = df.r2name
    return df


def get_short(df):
    df.loc[df.r1atlas.isin(['Schaefer200']), 'r1'] = df['r1atlas'] + '.' + df['r1hemi'] + '.' + df['r1network'] + '.' + df['r1region']
    df.loc[df.r2atlas.isin(['Schaefer200']), 'r2'] = df['r2atlas'] + '.' + df['r2hemi'] + '.' + df['r2network'] + '.' + df['r2region']
    df.loc[df.r1atlas.isin(['DnSeg']), 'r1'] = df.r1name
    df.loc[df.r2atlas.isin(['DnSeg']), 'r2'] = df.r2name
    return df


def _parse_data(filename):
    df = pd.read_csv(filename)

    df = get_atlas(df)

    # Drop conn networks
    df = df[(df.r1atlas != 'networks') & (df.r2atlas != 'networks')]

    df = get_hemi(df)
    df = get_network(df)
    df = get_region(df)
    df = get_short(df)

    # Drop undefined
    df = df[(~df.r1.str.contains('undefined')) & (~df.r2.str.contains('undefined'))]

    # Remove duplicates keeping first
    df = df.drop_duplicates()

    return df


def _add_matrix_pages_others(data, pdf):
    print(f'adding matrix page others')

    # Load data and filter out atlases
    df = data[f'Schaefer100']
    df = df[df.r1atlas != 'Schaefer100']
    df = df[df.r2atlas != 'Schaefer100']
    df = df[df.r1atlas != 'Yeo2011']
    df = df[df.r2atlas != 'Yeo2011']
    df = df[~df.r1atlas.isin(['HBT_lh', 'HBT_rh', 'Hypothal', 'sclimbic'])]
    df = df[~df.r2atlas.isin(['HBT_lh', 'HBT_rh', 'Hypothal', 'sclimbic'])]

    # Per event
    df0 = df[df.condition == 'rest-Baseline']
    df6 = df[df.condition == 'rest-Week06']
    df12 = df[df.condition == 'rest-Week12']

    # Baseline
    connmat = df0.pivot_table(
        index='r1',
        columns='r2',
        values='zvalue',
        fill_value=0,
        aggfunc='mean'
    )

    fig, ax = plt.subplots(1, 1, figsize=(8.5, 11))

    _plot = sns.heatmap(connmat, cmap='viridis', ax=ax)
    ax.set_title('NBM/Thalamus\nBaseline Group Mean Functional Connectivity')

    plt.subplots_adjust(left=0.4, top=0.9, right=0.98, bottom=0.3)

    pdf.savefig(fig)

    # Week6
    connmat = df6.pivot_table(
        index='r1',
        columns='r2',
        values='zvalue',
        fill_value=0,
        aggfunc='mean'
    )

    fig, ax = plt.subplots(1, 1, figsize=(8.5, 11))

    _plot = sns.heatmap(connmat, cmap='viridis', ax=ax)
    ax.set_title('NBM/Thalamus\nWeek 6 Group Mean Functional Connectivity')

    plt.subplots_adjust(left=0.4, top=0.9, right=0.98, bottom=0.3)

    pdf.savefig(fig)

    # Week12
    connmat = df12.pivot_table(
        index='r1',
        columns='r2',
        values='zvalue',
        fill_value=0,
        aggfunc='mean'
    )

    fig, ax = plt.subplots(1, 1, figsize=(8.5, 11))

    _plot = sns.heatmap(connmat, cmap='viridis', ax=ax)
    ax.set_title('NBM/Thalamus\nWeek 12 Group Mean Functional Connectivity')

    plt.subplots_adjust(left=0.4, top=0.9, right=0.98, bottom=0.3)

    pdf.savefig(fig)

    # Format data for stats and run t-test of BL vs week6
    dfp = df.pivot(index='id', columns=['r1', 'r2', 'condition'], values='zvalue')
    dfp_baseline = dfp.xs('rest-Baseline', level='condition', axis=1).values
    dfp_week6 = dfp.xs('rest-Week06', level='condition', axis=1).values
    t_values, p_values = ttest_rel(dfp_week6, dfp_baseline, axis=0)

    # Handle results
    pairs = dfp.xs('rest-Baseline', level='condition', axis=1).columns
    results = pd.DataFrame({
        'r1': [pair[0] for pair in pairs],
        'r2': [pair[1] for pair in pairs],
        'tvalue': t_values,
        'pvalue': p_values
    })

    # Get fdr corrected pvalues
    results['fdr_p_values'] = false_discovery_control(p_values)

    # Plot results tvalues, p < 0.05, fdr
    rois = pd.unique(results[['r1', 'r2']].values.ravel())
    matrix = pd.DataFrame(data=np.nan, index=rois, columns=rois)

    for _, row in results.iterrows():
        matrix.loc[row['r1'], row['r2']] = row['tvalue']
        matrix.loc[row['r2'], row['r1']] = row['tvalue']

    fig, ax = plt.subplots(1, 1, figsize=(8.5, 11))
    sns.heatmap(matrix, cmap="coolwarm", cbar=True, mask=np.isnan(matrix), ax=ax)
    ax.set_title('NBM/Thalamus\nttest_rel(Week6 - Baseline) [None]')

    plt.subplots_adjust(left=0.4, top=0.9, right=0.98, bottom=0.3)
    pdf.savefig(fig)

    # Plot p < 0.05
    significant = results[results['pvalue'] < 0.05]
    matrix = pd.DataFrame(data=np.nan, index=rois, columns=rois)
    for _, row in significant.iterrows():
        matrix.loc[row['r1'], row['r2']] = row['tvalue']
        matrix.loc[row['r2'], row['r1']] = row['tvalue']

    fig, ax = plt.subplots(1, 1, figsize=(8.5, 11))
    sns.heatmap(matrix, cmap="coolwarm", cbar=True, mask=np.isnan(matrix), ax=ax)
    ax.set_title('NBM/Thalamus\nttest_rel(Week6 - Baseline) [p<0.05]')
    plt.subplots_adjust(left=0.4, top=0.9, right=0.98, bottom=0.3)
    pdf.savefig(fig)

    # Format fdr data
    significant = results[results['fdr_p_values'] < 0.05]
    matrix = pd.DataFrame(data=np.nan, index=rois, columns=rois)
    for _, row in significant.iterrows():
        matrix.loc[row['r1'], row['r2']] = row['tvalue']
        matrix.loc[row['r2'], row['r1']] = row['tvalue']

    # Plot fdr
    fig, ax = plt.subplots(1, 1, figsize=(8.5, 11))
    sns.heatmap(matrix, cmap="coolwarm", cbar=True, mask=np.isnan(matrix), ax=ax)
    ax.set_title('NBM/Thalamus\nttest_rel(Week6 - Baseline) [FDR p<0.05]')
    plt.subplots_adjust(left=0.4, top=0.9, right=0.98, bottom=0.3)
    pdf.savefig(fig)


def _add_matrix_pages(data, pdf):

    for s in [100, 200, 400]:
        print(f'adding matrix page:{s}')
        df = data[f'Schaefer{s}']

        # Per event
        df0 = df[df.condition == 'rest-Baseline']
        df6 = df[df.condition == 'rest-Week06']
        df12 = df[df.condition == 'rest-Week12']

        # Baseline
        connmat = df0.pivot_table(
            index='r1',
            columns='r2',
            values='zvalue',
            fill_value=0,
            aggfunc='mean'
        )

        fig, ax = plt.subplots(1, 1, figsize=(8.5, 11))

        _plot = sns.heatmap(connmat, cmap='viridis', ax=ax)
        ax.set_title(f'Schaefer{s}\nBaseline Group Mean Functional Connectivity')

        plt.subplots_adjust(left=0.4, top=0.9, right=0.98, bottom=0.3)

        pdf.savefig(fig)

        # Week6
        connmat = df6.pivot_table(
            index='r1',
            columns='r2',
            values='zvalue',
            fill_value=0,
            aggfunc='mean'
        )

        fig, ax = plt.subplots(1, 1, figsize=(8.5, 11))

        _plot = sns.heatmap(connmat, cmap='viridis', ax=ax)
        ax.set_title(f'Schaefer{s}\nWeek 6 Group Mean Functional Connectivity')

        plt.subplots_adjust(left=0.4, top=0.9, right=0.98, bottom=0.3)

        pdf.savefig(fig)

        # Week12
        connmat = df12.pivot_table(
            index='r1',
            columns='r2',
            values='zvalue',
            fill_value=0,
            aggfunc='mean'
        )

        fig, ax = plt.subplots(1, 1, figsize=(8.5, 11))

        _plot = sns.heatmap(connmat, cmap='viridis', ax=ax)
        ax.set_title(f'Schaefer{s}\nWeek 12 Group Mean Functional Connectivity')

        plt.subplots_adjust(left=0.4, top=0.9, right=0.98, bottom=0.3)

        pdf.savefig(fig)

        # Baseline vs Week6

        # Format data for stats and run t-test of BL vs week6
        dfp = df.pivot(index='id', columns=['r1', 'r2', 'condition'], values='zvalue')
        dfp_baseline = dfp.xs('rest-Baseline', level='condition', axis=1).values
        dfp_week6 = dfp.xs('rest-Week06', level='condition', axis=1).values
        t_values, p_values = ttest_rel(dfp_week6, dfp_baseline, axis=0)

        # Handle results
        pairs = dfp.xs('rest-Baseline', level='condition', axis=1).columns
        results = pd.DataFrame({
            'r1': [pair[0] for pair in pairs],
            'r2': [pair[1] for pair in pairs],
            'tvalue': t_values,
            'pvalue': p_values
        })

        # Get fdr corrected pvalues
        results['fdr_p_values'] = false_discovery_control(p_values)

        # Plot results tvalues, p < 0.05, fdr
        rois = pd.unique(results[['r1', 'r2']].values.ravel())
        matrix = pd.DataFrame(data=np.nan, index=rois, columns=rois)

        for _, row in results.iterrows():
            matrix.loc[row['r1'], row['r2']] = row['tvalue']
            matrix.loc[row['r2'], row['r1']] = row['tvalue']

        fig, ax = plt.subplots(1, 1, figsize=(8.5, 11))
        sns.heatmap(matrix, cmap="coolwarm", cbar=True, mask=np.isnan(matrix), ax=ax)
        ax.set_title(f'Schaefer{s}\nttest_rel(Week6 - Baseline) [None]')

        plt.subplots_adjust(left=0.4, top=0.9, right=0.98, bottom=0.3)
        pdf.savefig(fig)

        # Plot p < 0.05
        significant = results[results['pvalue'] < 0.05]
        matrix = pd.DataFrame(data=np.nan, index=rois, columns=rois)
        for _, row in significant.iterrows():
            matrix.loc[row['r1'], row['r2']] = row['tvalue']
            matrix.loc[row['r2'], row['r1']] = row['tvalue']

        fig, ax = plt.subplots(1, 1, figsize=(8.5, 11))
        sns.heatmap(matrix, cmap="coolwarm", cbar=True, mask=np.isnan(matrix), ax=ax)
        ax.set_title(f'Schaefer{s}\nttest_rel(Week6 - Baseline) [p<0.05]')
        plt.subplots_adjust(left=0.4, top=0.9, right=0.98, bottom=0.3)
        pdf.savefig(fig)

        # Format fdr data
        significant = results[results['fdr_p_values'] < 0.05]
        matrix = pd.DataFrame(data=np.nan, index=rois, columns=rois)
        for _, row in significant.iterrows():
            matrix.loc[row['r1'], row['r2']] = row['tvalue']
            matrix.loc[row['r2'], row['r1']] = row['tvalue']

        # Plot fdr
        fig, ax = plt.subplots(1, 1, figsize=(8.5, 11))
        sns.heatmap(matrix, cmap="coolwarm", cbar=True, mask=np.isnan(matrix), ax=ax)
        ax.set_title(f'Schaefer{s}\nttest_rel(Week6 - Baseline) [FDR p<0.05]')
        plt.subplots_adjust(left=0.4, top=0.9, right=0.98, bottom=0.3)
        pdf.savefig(fig)


    return pdf


def _add_atlas_pages(pdf):
    _plot_atlas_surfs(pdf)

    return pdf


def _add_stats_pages(data, pdf):
    rois = ['DnSeg_lh', 'DnSeg_rh']

    for test_type in ['ttest_1samp', 'ttest_rel']:
        for roi in rois:
            _plot_stats_surf(data, roi, pdf, test_type=test_type)
            _plot_stats_surf(data, roi, pdf, test_type=test_type, correction='p<0.05')
            _plot_stats_surf(data, roi, pdf, test_type=test_type, correction='fdrp<0.05')

    return pdf


def _map_stats_surf(stats, labels):
    surf = np.full(labels.shape, np.nan)

    # Take the list of stats in same order as parcels
    # Load the annot
    # Use stats and annot to create surface of stats, the stats cover mutliple vertices in the surface
    # we use the annotation to map the stat to multiple vertices. The annot index matches the parcel
    # index.

    for i in range(len(stats)):
        # Set all surface of this ROI to stats value
        surf[labels == i + 1] = stats[i]

    return surf


def _plot_stats_surf_row(stat_lh, stat_rh, roi_lh, roi_rh, axes_row):
    ''' Plots left/right surface maps medial and lateral views with bluewhitered colormap'''
    cmap = 'coolwarm' #'BuRd_r' # #'coolwarm' #'bwr'
    fsaverage_meshes = load_fsaverage("fsaverage5")
    fsaverage_sulcal = load_fsaverage_data(data_type="sulcal")
    darkness = 0.1

    if 'Yeo2011' in roi_lh:
        row_title = 'Yeo 7Networks'
        vmax = 14
    elif '100' in roi_lh:
        row_title = 'Schaefer100'
        vmax = 100
    elif '200' in roi_lh:
        row_title = 'Schaefer200'
        vmax = 200
    elif '400' in roi_lh:
        row_title = 'Schaefer400'
        vmax = 400

    levels=[x for x in range(1, int(vmax / 2) + 1)]
    colors=['silver' for x in range(1, int(vmax / 2 ) + 1)]

    fig = plotting.plot_surf_stat_map(
        surf_mesh=fsaverage_meshes["inflated"],
        stat_map=stat_lh,
        hemi='left',
        view='lateral',
        title=row_title,
        axes=axes_row[0],
        colorbar=True,
        cmap=cmap,
        threshold=0.1,
        bg_map=fsaverage_sulcal,
        bg_on_data=False,
        darkness=darkness,
    )

    plotting.plot_surf_contours(
        surf_mesh=fsaverage_meshes["inflated"],
        roi_map=roi_lh,
        hemi='left',
        axes=axes_row[0],
        levels=levels,
        colors=colors,
    )

    plotting.plot_surf_stat_map(
        surf_mesh=fsaverage_meshes["inflated"],
        stat_map=stat_lh,
        hemi='left',
        view='medial',
        title='Left',
        axes=axes_row[1],
        colorbar=False,
        cmap=cmap,
        threshold=0.1,
        bg_map=fsaverage_sulcal,
        bg_on_data=False,
        darkness=darkness,
    )

    plotting.plot_surf_contours(
        surf_mesh=fsaverage_meshes["inflated"],
        roi_map=roi_lh,
        hemi='left',
        axes=axes_row[1],
        levels=levels,
        colors=colors,
    )

    plotting.plot_surf_stat_map(
        surf_mesh=fsaverage_meshes["inflated"],
        stat_map=stat_rh,
        hemi='right',
        view='medial',
        title='Right',
        axes=axes_row[2],
        colorbar=False,
        cmap=cmap,
        threshold=0.1,
        bg_map=fsaverage_sulcal,
        bg_on_data=False,
        darkness=darkness,
    )

    plotting.plot_surf_contours(
        surf_mesh=fsaverage_meshes["inflated"],
        roi_map=roi_rh,
        hemi='right',
        axes=axes_row[2],
        levels=levels,
        colors=colors,
    )

    # Right Lateral
    plotting.plot_surf_stat_map(
        surf_mesh=fsaverage_meshes["inflated"],
        stat_map=stat_rh,
        hemi='right',
        view='lateral',
        title=row_title,
        axes=axes_row[3],
        colorbar=True,
        cmap=cmap,
        threshold=0.1,
        bg_map=fsaverage_sulcal,
        bg_on_data=False,
        darkness=darkness,
    )

    plotting.plot_surf_contours(
        surf_mesh=fsaverage_meshes["inflated"],
        roi_map=roi_rh,
        hemi='right',
        axes=axes_row[3],
        levels=levels,
        colors=colors,
    )


def _plot_stats_surf(data, roi, pdf, test_type='ttest_1samp', correction=None):
    cur_row = 0
    if test_type == 'ttest_rel':
        fig_title = f'Source ROI:{roi}\n{test_type}(Week6 - Baseline) [{correction}]'
    else:
        fig_title = f'Source ROI:{roi}\n{test_type}() [{correction}]'

    # First plot Yeo 7 which is combined hemispheres
    df = data['Schaefer100']
    dfx = df[(df.r1.isin([roi])) & (df.r2.str.startswith('Yeo2011'))]

    dfp = dfx.pivot(index='id', columns=['r1', 'r2', 'condition'], values='zvalue')
    dfp_baseline = dfp.xs('rest-Baseline', level='condition', axis=1).values
    dfp_week6 = dfp.xs('rest-Week06', level='condition', axis=1).values
    dfp_week12 = dfp.xs('rest-Week12', level='condition', axis=1).values

    if test_type == 'ttest_1samp':
        dfp_mean = np.mean(np.array([dfp_baseline, dfp_week6, dfp_week12]), axis=0)
        t_values, p_values = ttest_1samp(dfp_mean, popmean=0, axis=0)
    elif test_type == 'ttest_rel':
        t_values, p_values = ttest_rel(dfp_week6, dfp_baseline, axis=0)
    else:
        raise Exception(f'invalid test type:{test_type}')

    # Get fdr corrected pvalues
    fdr_p_values = false_discovery_control(p_values)

    if correction == 'p<0.05':
        stats = [-0.01] * len(t_values)
        for i, t in enumerate(t_values):
            if float(p_values[i]) < 0.05:
                stats[i] = t
    elif correction == 'fdrp<0.05':
        stats = [-0.01] * len(t_values)
        for i, t in enumerate(t_values):
            if float(fdr_p_values[i]) < 0.05:
                stats[i] = t
    else:
        stats = t_values

    lh_file = f'/Users/boydb1/git/analyses/atlases/lh.Yeo2011_7Networks_N1000.annot'
    rh_file = f'/Users/boydb1/git/analyses/atlases/rh.Yeo2011_7Networks_N1000.annot'

    # Load the main surface
    fsaverage_meshes = load_fsaverage("fsaverage5")

    # Load schaefer labels
    labels_lh, _, names_lh = fs.read_annot(lh_file)
    labels_rh, _, names_rh = fs.read_annot(rh_file)

    # Yeo2011 is combined hemis
    stats_lh = stats
    stats_rh = stats

    surf_lh = _map_stats_surf(stats_lh, labels_lh)
    surf_rh = _map_stats_surf(stats_rh, labels_rh)

    # create a figure with multiple axes to plot each
    # NOTE: remember the projection=3d or you'll get an error when nilearn 
    # tries to call view_init in surface plotting
    fig, axes = plt.subplots(nrows=4, ncols=4, figsize=(8.5, 11), subplot_kw={'projection': '3d'})

    # Plot Yeo 2011 on first row
    _plot_stats_surf_row(surf_lh, surf_rh, lh_file, rh_file, axes[cur_row])

    # Plot the next 3 rows
    cur_row += 1
    for s in [100, 200, 400]:

        # Get just NBM to Schaefer
        df = data[f'Schaefer{s}']
        dfx = df[(df.r1.isin([roi])) & (df.r2.str.startswith(f'Schaefer{s}'))]

        # Pivot to zvalues per pair per condition
        dfp = dfx.pivot(index='id', columns=['r1', 'r2', 'condition'], values='zvalue')
        dfp_baseline = dfp.xs('rest-Baseline', level='condition', axis=1).values
        dfp_week6 = dfp.xs('rest-Week06', level='condition', axis=1).values
        dfp_week12 = dfp.xs('rest-Week12', level='condition', axis=1).values

        if test_type == 'ttest_1samp':
            dfp_mean = np.mean(np.array([dfp_baseline, dfp_week6, dfp_week12]), axis=0)
            t_values, p_values = ttest_1samp(dfp_mean, popmean=0, axis=0)
        elif test_type == 'ttest_rel':
            t_values, p_values = ttest_rel(dfp_week6, dfp_baseline, axis=0)
        else:
            raise Exception(f'invalid test type:{test_type}')

        # Get fdr corrected pvalues
        fdr_p_values = false_discovery_control(p_values)

        if correction == 'p<0.05':
            stats = [-0.01] * len(t_values)
            for i, t in enumerate(t_values):
                if float(p_values[i]) < 0.05:
                    stats[i] = t
        elif correction == 'fdrp<0.05':
            stats = [-0.01] * len(t_values)
            for i, t in enumerate(t_values):
                if float(fdr_p_values[i]) < 0.05:
                    stats[i] = t
        else:
            stats = t_values

        # Split left/right
        _mid = len(stats) // 2
        stats_lh = stats[:_mid]
        stats_rh = stats[_mid:]

        # Load schaefer labels
        lh_file = f'/Users/boydb1/git/analyses/atlases/Schaefer2018/FreeSurfer5.3/fsaverage5/label/lh.Schaefer2018_{s}Parcels_7Networks_order.annot'
        rh_file = f'/Users/boydb1/git/analyses/atlases/Schaefer2018/FreeSurfer5.3/fsaverage5/label/rh.Schaefer2018_{s}Parcels_7Networks_order.annot'
        labels_lh, _, names_lh = fs.read_annot(lh_file)
        labels_rh, _, names_rh = fs.read_annot(rh_file)

        # Map stats to surface labels
        surf_lh = _map_stats_surf(stats_lh, labels_lh)
        surf_rh = _map_stats_surf(stats_rh, labels_rh)

        # Plot left/right to a row
        _plot_stats_surf_row(surf_lh, surf_rh, lh_file, rh_file, axes[cur_row])

        # Go to next row
        cur_row += 1

    fig.suptitle(fig_title)

    pdf.savefig(fig)

    return pdf


def _plot_atlas_surfs(pdf):
    cur_row = 0

    # Ceate a figure with multiple axes to plot each.
    # Remember the projection=3d or you'll get an error when nilearn 
    # tries to call view_init in surface plotting.
    fig, axes = plt.subplots(nrows=4, ncols=4, figsize=(8.5, 11), subplot_kw={'projection': '3d'})

    # Plot Yeo 2011 on first row
    lut_file = f'/Users/boydb1/git/analyses/atlases/Yeo2011_7Networks_ColorLUT.fsleyes.lut.txt'
    lh_file = f'/Users/boydb1/git/analyses/atlases/lh.Yeo2011_7Networks_N1000.annot'
    rh_file = f'/Users/boydb1/git/analyses/atlases/rh.Yeo2011_7Networks_N1000.annot'
    _plot_atlas_surf_row(lh_file, rh_file, lut_file, axes[cur_row])

    # Plot the next 3 rows
    cur_row += 1
    for count in [100, 200, 400]:
        lut_file = f'/Users/boydb1/git/analyses/atlases/Schaefer2018/MNI/fsleyes_lut/Schaefer2018_{count}Parcels_7Networks_order.lut'
        lh_file = f'/Users/boydb1/git/analyses/atlases/Schaefer2018/FreeSurfer5.3/fsaverage5/label/lh.Schaefer2018_{count}Parcels_7Networks_order.annot'
        rh_file = f'/Users/boydb1/git/analyses/atlases/Schaefer2018/FreeSurfer5.3/fsaverage5/label/rh.Schaefer2018_{count}Parcels_7Networks_order.annot'

        # Plot left/right to a row
        _plot_atlas_surf_row(lh_file, rh_file, lut_file, axes[cur_row])

        # Go to next row
        cur_row += 1

    fig.suptitle(f'Parcellations')

    pdf.savefig(fig)

    return pdf


def _plot_atlas_surf_row(lh_file, rh_file, lut_file, axes_row):
    fsaverage_meshes = load_fsaverage("fsaverage5")
    fsaverage_sulcal = load_fsaverage_data(data_type="sulcal")

    if 'Yeo2011' in lh_file:
        row_title = 'Yeo 7Networks'
        vmax = 7
    elif '100' in lh_file:
        row_title = 'Schaefer100'
        vmax = 50
    elif '200' in lh_file:
        row_title = 'Schaefer200'
        vmax = 100
    elif '400' in lh_file:
        row_title = 'Schaefer400'
        vmax = 200
    else:
        row_title = 'TBD'
        vmax = 100

    levels = [x for x in range(0, vmax)]
    colors = ['silver' for x in range(0, vmax)]

    # Convet fsleyes-formatted lookup table file to nilearn colormap
    if 'Yeo2011' in lh_file:
        # Yeo is 1-7 for both hemis
        cmap_left = get_colormap(lut_file)
        cmap_right = cmap_left
    else:
        # schaefer parcels are not symmetrical so we need to latter half of the colormap,
        # but the annotaion labels are indexed from 1 for right hemis
        cmap_left = get_colormap_left(lut_file)
        cmap_right = get_colormap_right(lut_file)

    plotting.plot_surf_roi(
        surf_mesh=fsaverage_meshes["inflated"],
        roi_map=lh_file,
        hemi='left',
        view='lateral',
        title=row_title,
        cmap=cmap_left,
        vmin=1,
        vmax=vmax,
        axes=axes_row[0],
        alpha=1.0,
    )

    plotting.plot_surf_contours(
        surf_mesh=fsaverage_meshes["inflated"],
        roi_map=lh_file,
        hemi='left',
        axes=axes_row[0],
        levels=levels,
        colors=colors,
    )

    plotting.plot_surf_roi(
        surf_mesh=fsaverage_meshes["inflated"],
        roi_map=lh_file,
        hemi='left',
        view='medial',
        title=f'Left',
        cmap=cmap_left,
        vmin=1,
        vmax=vmax,
        axes=axes_row[1],
        alpha=1.0,
    )

    plotting.plot_surf_contours(
        surf_mesh=fsaverage_meshes["inflated"],
        roi_map=lh_file,
        hemi='left',
        axes=axes_row[1],
        levels=levels,
        colors=colors,
    )

    plotting.plot_surf_roi(
        surf_mesh=fsaverage_meshes["inflated"],
        roi_map=rh_file,
        hemi='right',
        view='medial',
        title=f'Right',
        cmap=cmap_right,
        vmin=1,
        vmax=vmax,
        axes=axes_row[2],
        alpha=1.0,
    )

    plotting.plot_surf_contours(
        surf_mesh=fsaverage_meshes["inflated"],
        roi_map=rh_file,
        hemi='right',
        axes=axes_row[2],
        levels=levels,
        colors=colors,
    )

    plotting.plot_surf_roi(
        surf_mesh=fsaverage_meshes["inflated"],
        roi_map=rh_file,
        hemi='right',
        view='lateral',
        title=row_title,
        cmap=cmap_right,
        vmin=1,
        vmax=vmax,
        axes=axes_row[3],
        alpha=1.0,
    )

    plotting.plot_surf_contours(
        surf_mesh=fsaverage_meshes["inflated"],
        roi_map=rh_file,
        hemi='right',
        axes=axes_row[3],
        levels=levels,
        colors=colors,
    )


def _load_data(datadir):
    data = {}

    for s in [100, 200, 400]:
    #for s in [100]:
        parsed_csv = f'{datadir}/test-Schaefer{s}.csv'

        print(f'loading:{parsed_csv}')
        df = pd.read_csv(parsed_csv, index_col=False)
        df = df.drop_duplicates()

        if s == 200:
            df = df[~df.r1.str.startswith('Schaefer100')]
            df = df[~df.r2.str.startswith('Schaefer100')]
        elif s == 400:
            df = df[~df.r1.str.startswith('Schaefer100')]
            df = df[~df.r2.str.startswith('Schaefer100')]
            df = df[~df.r1.str.startswith('Schaefer200')] 
            df = df[~df.r2.str.startswith('Schaefer200')]

        data[f'Schaefer{s}'] = df

    return data


def make_pdf(datadir, filename):
    data = _load_data(datadir)

    print('making pdf')
    with PdfPages(filename) as pdf:
        print('making matrix pages')
        _add_matrix_pages(data, pdf)
        _add_matrix_pages_others(data, pdf)

        print('making atlas pages')
        _add_atlas_pages(pdf)

        print('making stats pages')
        _add_stats_pages(data, pdf)


def parse_all(datadir):
    for s in [100, 200, 400]:
        inputs_csv = f'{datadir}/zvalues-Schaefer{s}.csv'
        parsed_csv = f'{datadir}/test-Schaefer{s}.csv'
   
        if not os.path.exists(parsed_csv):
            print(f'parsing data:{inputs_csv}')
            df = _parse_data(inputs_csv)
            df.to_csv(parsed_csv, index=False)
        else:
            print(f'exists:{parsed_csv}')


DATADIR = '/Users/boydb1/Downloads'
pdf_file = 'test-report.pdf'
parse_all(DATADIR)
make_pdf(DATADIR, pdf_file)
