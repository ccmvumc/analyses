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


LUT = {
    0: 'unknown',
    1: 'bankssts',
    2: 'caudalanteriorcingulate',
    3: 'caudalmiddlefrontal',
    4: 'corpuscallosum',
    5: 'cuneus',
    6: 'entorhinal',
    7: 'fusiform',
    8: 'inferiorparietal',
    9: 'inferiortemporal',
    10: 'isthmuscingulate',
    11: 'lateraloccipital',
    12: 'lateralorbitofrontal',
    13: 'lingual',
    14: 'medialorbitofrontal',
    15: 'middletemporal',
    16: 'parahippocampal',
    17: 'paracentral',
    18: 'parsopercularis',
    19: 'parsorbitalis',
    20: 'parstriangularis',
    21: 'pericalcarine',
    22: 'postcentral',
    23: 'posteriorcingulate',
    24: 'precentral',
    25: 'precuneus',
    26: 'rostralanteriorcingulate',
    27: 'rostralmiddlefrontal',
    28: 'superiorfrontal',
    29: 'superiorparietal',
    30: 'superiortemporal',
    31: 'supramarginal',
    32: 'frontalpole',
    33: 'temporalpole',
    34: 'transversetemporal',
    35: 'insula',
}


results_surfarea_lh = {
    'bankssts': 0.751250,
    'caudalanteriorcingulate': 0.571250,
    'caudalmiddlefrontal': 0.933750,
    'cuneus': 0.731250,
    'entorhinal': 0.118125,
    'frontalpole': 0.190000,
    'inferiorparietal': 0.978125,
    'fusiform': 0.961250,
    'inferiortemporal': 0.950625,
    'insula': 0.775625,
    'isthmuscingulate': 0.140000,
    'lateraloccipital': 0.921875,
    'lateralorbitofrontal': 0.998750,
    'lingual': 0.740625,
    'medialorbitofrontal': 0.999375,
    'middletemporal': 0.957500,
    'paracentral': 0.971875,
    'parahippocampal': 0.795000,
    'parsopercularis': 0.356250,
    'parsorbitalis': 0.876250,
    'parstriangularis': 0.376875,
    'pericalcarine': 0.758125,
    'postcentral': 0.978750,
    'posteriorcingulate': 0.997500,
    'precentral': 0.978750,
    'precuneus': 0.925625,
    'rostralanteriorcingulate': 0.688125,
    'rostralmiddlefrontal': 0.743750,
    'superiorfrontal': 0.926250,
    'superiorparietal': 0.787500,
    'superiortemporal': 0.518750, 
    'supramarginal': 0.723750,
    'temporalpole': 0.072500,
    'transversetemporal': 0.553750,
}

results_surfarea_rh = {
    'bankssts': 0.998125,
    'caudalanteriorcingulate': 0.923125,
    'caudalmiddlefrontal': 0.855625,
    'cuneus': 0.780625,
    'entorhinal': 0.218125,
    'frontalpole': 0.126250,
    'fusiform': 0.950000,
    'inferiorparietal': 0.878750,
    'inferiortemporal': 0.831250,
    'insula':  0.551250,
    'isthmuscingulate': 0.565625,
    'lateraloccipital': 0.775625,
    'lateralorbitofrontal': 0.986875,
    'lingual': 0.711250,
    'medialorbitofrontal': 0.972500,
    'middletemporal': 0.971250,
    'paracentral': 0.874375,
    'parahippocampal': 0.806875,
    'parsopercularis': 0.788125,
    'parsorbitalis': 0.960625,
    'parstriangularis': 0.693750,
    'pericalcarine': 0.819375,
    'postcentral': 0.725000,
    'posteriorcingulate': 0.981250,
    'precentral': 0.907500,
    'precuneus': 0.837500,
    'rostralanteriorcingulate': 0.809375,
    'rostralmiddlefrontal': 0.656250,
    'superiorfrontal': 0.761875,
    'superiorparietal': 0.335000,
    'superiortemporal': 0.864375,
    'supramarginal': 0.723125,
    'temporalpole': 0.058125,
    'transversetemporal': 0.676250,
}

results_thickavg_lh = {
    'bankssts': 0.99375,
    'caudalanteriorcingulate': 0.056875,
    'caudalmiddlefrontal': 0.51125,
    'cuneus': 0.045625,
    'entorhinal': 0.999375,
    'frontalpole': 0.093125,
    'fusiform': 0.886875,
    'inferiorparietal': 0.09,
    'inferiortemporal': 0.4975,
    'insula': 0.696875,
    'isthmuscingulate': 0.14625,
    'lateraloccipital': 0.03125,
    'lateralorbitofrontal': 0.590625,
    'lingual': 0.175625,
    'medialorbitofrontal': 0.305625,
    'middletemporal': 0.999375,
    'paracentral': 0.723125,
    'parahippocampal': 0.1975,
    'parsopercularis': 0.6975,
    'parsorbitalis': 0.721875,
    'parstriangularis': 0.648125,
    'pericalcarine': 0.01,
    'postcentral':   0.98,
    'posteriorcingulate': 0.89375,
    'precentral': 0.8825,
    'precuneus': 0.31375,
    'rostralanteriorcingulate': 0.661875,
    'rostralmiddlefrontal': 0.58375,
    'superiorfrontal': 0.92375,
    'superiorparietal': 0.051875,
    'superiortemporal': 0.99875,
    'supramarginal': 0.445,
    'temporalpole': 1,
    'transversetemporal': 0.975,
}


results_thickavg_rh = {
    'bankssts': 1,
    'caudalanteriorcingulate': 0.088125,
    'caudalmiddlefrontal': 0.64375,
    'cuneus': 0.038125,
    'entorhinal': 0.999375,
    'frontalpole': 0.248125,
    'fusiform': 0.9975,
    'inferiorparietal': 0.85,
    'inferiortemporal': 0.8425,
    'insula': 0.99,
    'isthmuscingulate': 0.045,
    'lateraloccipital': 0.263125,
    'lateralorbitofrontal': 0.76125,
    'lingual': 0.79625,
    'medialorbitofrontal': 0.350625,
    'middletemporal': 1,
    'paracentral': 0.959375,
    'parahippocampal': 0.69375,
    'parsopercularis': 0.9575,
    'parsorbitalis': 0.81375,
    'parstriangularis': 0.814375,
    'pericalcarine': 0.009375,
    'postcentral': 0.970625,
    'posteriorcingulate': 0.5075,
    'precentral': 0.98625,
    'precuneus': 0.46875,
    'rostralanteriorcingulate': 0.66125,
    'rostralmiddlefrontal': 0.54125,
    'superiorfrontal': 0.98,
    'superiorparietal': 0.271875,
    'superiortemporal': 1,
    'supramarginal': 0.998125,
    'temporalpole': 1,
    'transversetemporal': 0.739375,
}

results_volume_lh = {
    'accumbensarea': 0.375,
    'amygdala': 0.996875,
    'bankssts': 0.8775,
    'caudalanteriorcingulate': 0.533125,
    'caudalmiddlefrontal': 0.9475,
    'caudate': 0.093125,
    'cuneus': 0.305,
    'entorhinal': 0.8125,
    'frontalpole': 0.036875,
    'fusiform': 0.98375,
    'hippocampus': 0.945,
    'inferiorparietal': 0.938125,
    'inferiortemporal': 0.799375,
    'insula': 0.86,
    'isthmuscingulate': 0.03125,
    'lateraloccipital': 0.594375,
    'lateralorbitofrontal': 0.980625,
    'lingual': 0.36625,
    'medialorbitofrontal': 0.97,
    'middletemporal': 1,
    'pallidum': 0.908125,
    'paracentral': 0.980625,
    'parahippocampal': 0.14375,
    'parsopercularis': 0.448125,
    'parsorbitalis': 0.893125,
    'parstriangularis': 0.201875,
    'pericalcarine': 0.379375,
    'postcentral': 0.999375,
    'posteriorcingulate': 1,
    'precentral': 0.9975,
    'precuneus': 0.84625,
    'putamen': 0.068125,
    'rostralanteriorcingulate': 0.69875,
    'rostralmiddlefrontal': 0.486875,
    'superiorfrontal': 0.98,
    'superiorparietal': 0.32125,
    'superiortemporal': 0.978125,
    'supramarginal': 0.666875,
    'temporalpole': 0.896875,
    'thalamus': 0.961875,
    'transversetemporal': 0.8225,
    'ventraldc': 0.83875,
}

results_volume_rh = {
    'accumbensarea': 0.98125,
    'amygdala': 0.9625,
    'bankssts': 1,
    'caudalanteriorcingulate': 0.834375,
    'caudalmiddlefrontal': 0.904375,
    'caudate': 0.176875,
    'cuneus': 0.215625,
    'entorhinal': 0.600625,
    'frontalpole': 0.00375,
    'fusiform': 0.9975,
    'hippocampus': 0.999375,
    'inferiorparietal': 0.943125,
    'inferiortemporal': 0.6825,
    'insula': 0.7875,
    'isthmuscingulate': 0.24875,
    'lateraloccipital': 0.7325,
    'lateralorbitofrontal': 0.98125,
    'lingual': 0.803125,
    'medialorbitofrontal': 0.890625,
    'middletemporal': 1,
    'pallidum': 0.915625,
    'paracentral': 0.9825,
    'parahippocampal': 0.796875,
    'parsopercularis': 0.965,
    'parsorbitalis': 0.924375,
    'parstriangularis': 0.671875,
    'pericalcarine': 0.286875,
    'postcentral': 0.974375,
    'posteriorcingulate': 0.995625,
    'precentral': 0.998125,
    'precuneus': 0.82875,
    'putamen': 0.06375,
    'rostralanteriorcingulate': 0.77875,
    'rostralmiddlefrontal': 0.390625,
    'superiorfrontal': 0.97625,
    'superiorparietal': 0.153125,
    'superiortemporal': 1,
    'supramarginal': 0.970625,
    'temporalpole': 0.90875,
    'thalamus': 0.98625,
    'transversetemporal': 0.975,
    'ventraldc': 0.984375,
}


def get_colormap(lut_file):
    # Load file into np array
    lut = np.loadtxt(lut_file, dtype=str)

    # Extract rgb columns
    rgb_values = lut[:, 1:4].astype(float)

    # Return as colormap    
    return ListedColormap(rgb_values)


def _parse_data():
    df = pd.DataFrame()
    return df


def _add_pages(pdf):
    _plot_surfs(pdf)
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
        #print(i, stats[i])
        if stats[i] > 0.95 or stats[i] < 0.05:
            surf[labels == i + 1] = stats[i]

    return surf


def _plot_surfs(pdf):
    # Ceate a figure with multiple axes to plot each.
    # Remember the projection=3d or you'll get an error when nilearn 
    # tries to call view_init in surface plotting.
    fig, axes = plt.subplots(nrows=5, ncols=4, figsize=(8.5, 11), subplot_kw={'projection': '3d'})

    roi_lh =  '/Users/boydb1/git/analyses/atlases/Schaefer2018/FreeSurfer5.3/fsaverage5/label/lh.aparc.annot'
    roi_rh =  '/Users/boydb1/git/analyses/atlases/Schaefer2018/FreeSurfer5.3/fsaverage5/label/rh.aparc.annot'
    lut_lh = '/Users/boydb1/git/analyses/atlases/freesurfercolorlut_lh.txt'
    lut_rh = '/Users/boydb1/git/analyses/atlases/freesurfercolorlut_rh.txt'

    labels_lh, _, names_lh = fs.read_annot(roi_lh)
    labels_rh, _, names_rh = fs.read_annot(roi_rh)

    names = list([str(x) for x in names_lh])
    count_lh = len(names_lh) - 1
    count_rh = len(names_rh) - 1

    _plot_atlas_surf_row(roi_lh, roi_rh, lut_lh, lut_rh, axes[0])

    # Surface Area
    stats_lh = [0] * count_lh
    stats_rh = [0] * count_rh
    for i in range(0, count_lh):
        try:
            stats_lh[i] = results_surfarea_lh[LUT[i+1]]
        except KeyError as err:
            stats_lh[i] = np.nan
        
        try:
            stats_rh[i] = results_surfarea_rh[LUT[i+1]]
        except KeyError as err:
            stats_rh[i] = np.nan

    surf_lh = _map_stats_surf(stats_lh, labels_lh)
    surf_rh = _map_stats_surf(stats_rh, labels_rh)
    _plot_stats_surf_row(surf_lh, surf_rh, roi_lh, roi_rh, axes[1], 'Surface Area')

    # Thickness
    stats_lh = [0] * count_lh
    stats_rh = [0] * count_rh
    for i in range(0, count_lh):
        try:
            stats_lh[i] = results_thickavg_lh[LUT[i+1]]
        except KeyError as err:
            stats_lh[i] = np.nan
        
        try:
            stats_rh[i] = results_thickavg_rh[LUT[i+1]]
        except KeyError as err:
            stats_rh[i] = np.nan

    surf_lh = _map_stats_surf(stats_lh, labels_lh)
    surf_rh = _map_stats_surf(stats_rh, labels_rh)
    _plot_stats_surf_row(surf_lh, surf_rh, roi_lh, roi_rh, axes[2], 'Thickness')

    # Volume
    stats_lh = [0] * count_lh
    stats_rh = [0] * count_rh
    for i in range(0, count_lh):
        try:
            stats_lh[i] = results_volume_lh[LUT[i+1]]
        except KeyError as err:
            stats_lh[i] = np.nan
        
        try:
            stats_rh[i] = results_volume_rh[LUT[i+1]]
        except KeyError as err:
            stats_rh[i] = np.nan

    surf_lh = _map_stats_surf(stats_lh, labels_lh)
    surf_rh = _map_stats_surf(stats_rh, labels_rh)
    _plot_stats_surf_row(surf_lh, surf_rh, roi_lh, roi_rh, axes[3], 'Volume')

    for i in range(0,4):
        axes[4][i].axis('off')

    # Plot left sub volumes
    _ax = fig.add_subplot(5, 4, 18)
    _ax.axis('off')
    _ax.text(0.3, 1.3, 'Accumbens', color='red')
    _ax.text(0.3, 1.2, 'Amygdala', color='red')
    _ax.text(0.3, 1.1, 'Caudate', color='grey')
    _ax.text(0.3, 1.0, 'Hippocampus', color='grey')
    _ax.text(0.3, 0.9, 'Pallidum', color='grey')
    _ax.text(0.3, 0.8, 'Putamen', color='grey')
    _ax.text(0.3, 0.7, 'Thalamus', color='red')
    _ax.text(0.3, 0.6, 'VentralDC', color='grey')

    # Plot right sub volumes
    _ax = fig.add_subplot(5, 4, 19)
    _ax.axis('off')
    _ax.text(0.3, 1.3, 'Accumbens', color='grey')
    _ax.text(0.3, 1.2, 'Amygdala', color='red')
    _ax.text(0.3, 1.1, 'Caudate', color='grey')
    _ax.text(0.3, 1.0, 'Hippocampus', color='red')
    _ax.text(0.3, 0.9, 'Pallidum', color='grey')
    _ax.text(0.3, 0.8, 'Putamen', color='grey')
    _ax.text(0.3, 0.7, 'Thalamus', color='red')
    _ax.text(0.3, 0.6, 'VentralDC', color='red')

    fig.suptitle(f'Bayesian Analysis of FreeSurfer - Results (<0.05, >0.95)')

    pdf.savefig(fig)

    return pdf


def _plot_atlas_surf_row(lh_file, rh_file, lh_lut, rh_lut, axes_row):
    fsaverage_meshes = load_fsaverage("fsaverage5")
    fsaverage_sulcal = load_fsaverage_data(data_type="sulcal")
    row_title = 'DK Atlas'
    vmax = 36
    levels = [x for x in range(0, vmax)]
    colors = ['silver' for x in range(0, vmax)]

    # Convet fsleyes-formatted lookup table file to nilearn colormap
    lh_cmap = get_colormap(lh_lut)
    rh_cmap = get_colormap(rh_lut)

    plotting.plot_surf_roi(
        surf_mesh=fsaverage_meshes["inflated"],
        roi_map=lh_file,
        hemi='left',
        view='lateral',
        title=row_title,
        cmap=lh_cmap,
        axes=axes_row[0],
        alpha=1.0,
    )

    plotting.plot_surf_roi(
        surf_mesh=fsaverage_meshes["inflated"],
        roi_map=lh_file,
        hemi='left',
        view='medial',
        title=f'Left',
        cmap=lh_cmap,
        axes=axes_row[1],
        alpha=1.0,
    )

    plotting.plot_surf_roi(
        surf_mesh=fsaverage_meshes["inflated"],
        roi_map=rh_file,
        hemi='right',
        view='medial',
        title=f'Right',
        cmap=rh_cmap,
        axes=axes_row[2],
        alpha=1.0,
    )

    plotting.plot_surf_roi(
        surf_mesh=fsaverage_meshes["inflated"],
        roi_map=rh_file,
        hemi='right',
        view='lateral',
        title=row_title,
        cmap=rh_cmap,
        axes=axes_row[3],
    )


def _plot_stats_surf_row(stat_lh, stat_rh, roi_lh, roi_rh, axes_row, row_title):
    ''' Plots left/right surface maps medial and lateral views with bluewhitered colormap'''
    cmap = 'coolwarm'
    fsaverage_meshes = load_fsaverage("fsaverage5")
    fsaverage_sulcal = load_fsaverage_data(data_type="sulcal")
    darkness = 0.9
    vmax = 36
    levels=[x for x in range(0, vmax)]
    colors=['silver' for x in range(0, vmax)]

    fig = plotting.plot_surf_stat_map(
        surf_mesh=fsaverage_meshes["inflated"],
        stat_map=stat_lh,
        hemi='left',
        view='lateral',
        title=row_title,
        axes=axes_row[0],
        colorbar=False,
        cmap=cmap,
        alpha=1.0,
        vmin=0.0,
        vmax=1.0,
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
        darkness=darkness,
        alpha=1.0,
        vmin=0.0,
        vmax=1.0,
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
        darkness=darkness,
        alpha=1.0,
        vmin=0.0,
        vmax=1.0,
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
        colorbar=False,
        cmap=cmap,
        darkness=darkness,
        alpha=1.0,
        vmin=0.0,
        vmax=1.0,
    )

    plotting.plot_surf_contours(
        surf_mesh=fsaverage_meshes["inflated"],
        roi_map=roi_rh,
        hemi='right',
        axes=axes_row[3],
        levels=levels,
        colors=colors,
    )


def _load_data(datadir):
    data = {}
    return data


def make_pdf(datadir, filename):
    data = _load_data(datadir)

    print('making pdf')
    with PdfPages(filename) as pdf:
        print('making atlas pages')
        _add_pages(pdf)


DATADIR = '/Users/boydb1/Downloads'
pdf_file = 'test-aparc-report.pdf'
#parse_all(DATADIR)
make_pdf(DATADIR, pdf_file)
