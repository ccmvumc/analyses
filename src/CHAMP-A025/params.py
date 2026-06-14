TITLE='CHAMP N-Back Task'

TITLE_SIZE = 9

# First Level Contrasts of Task Conditions 0,1,2,3 (last column is nilearn constant)
CONTRASTS = [
    [[-1, 0, 1, 0, 0]],
#    [[-6, 1, 2, 3, 0]],
#    [[-3, 1, 2, 0, 0]],
]

# Axial Slices for display
CUT_COORDS = [-15, 0, 15, 30, 45]

# For displaying 2tailed zmaps, 2.807 is equivalent of p<0.005, 1.96 for p<0.05
THRESHOLDS = [1.96, 2.807, 3.291]

# Colormap used to display zmaps
COLORMAP = 'RdBu_r'

# Regions of interest for beta value extraction
ROIS = [
    {
        'name': 'dlpfc',
        'atlas': 'Schaefer200',
        'labels': [66, 67, 68, 69, 70, 170, 171, 172, 173, 174, 175, 176]
    },
    {
        'name': 'ppc',
        'atlas': 'Schaefer200',
        'labels': [61, 62, 63, 165, 166, 167]
    },
]
