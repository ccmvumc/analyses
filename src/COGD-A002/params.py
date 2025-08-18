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
