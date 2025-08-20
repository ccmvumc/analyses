# Scan Repetition Time
TR=3.0

# First-Level Contrasts of Task Conditions 0BACK,2BACK,REST (last column is nilearn constant)
CONTRASTS = [
    [[-1, 1, 0, 0]],
    [[1, 0, -1, 0]],
    [[0, 1, -1, 0]],
    [[0.5, 0.5, -1, 0]],
]

# Axial Slices for display
CUT_COORDS = [-20, 0, 15, 30, 45]

# For displaying zmaps, 2.807 is equivalent of p<0.005
THRESHOLD = 2.807

# Maximum for colorbar
VMAX = 6

# Colormap used to display zmaps
COLORMAP = 'cold_hot'

# Regions of interest for beta value extraction
ROIS = [
    {
        'name': 'acc',
        'atlas': 'Schaefer200',
        'labels': [73, 179]
    },
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
