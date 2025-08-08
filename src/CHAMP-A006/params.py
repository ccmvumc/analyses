# Scan Repetition Time
TR=0.8

# Shorthand for trial condition names in EDAT
CONDITION_MAP = {
    '0BackRunBlockTrialCondition': '0Back',
    '1BackRunBlockTrialCondition': '1Back',
    '2BackRunBlockTrialCondition': '2Back',
    '3BackRunBlockTrialCondition': '3Back',
}

# First Level Contrasts of Task Conditions 0,1,2,3 (last column is nilearn constant)
CONTRASTS = [
    [[-1, 0, 1, 0, 0]],
    [[-3, -1, 1, 3, 0]],
]

# Axial Slices for display
CUT_COORDS = [-20, 0, 15, 30, 45]

# Duration in seconds of each trial of events
DURATION = 3.0

# For displaying zmaps, 2.807 is equivalent of p<0.005
THRESHOLD = 2.807

# Maximum for colorbar
VMAX = 6

# Colormap used to display zmaps
COLORMAP = 'cold_hot'
