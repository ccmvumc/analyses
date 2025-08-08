TR=0.8

CONDITION_MAP = {
    '0BackRunBlockTrialCondition': '0Back',
    '1BackRunBlockTrialCondition': '1Back',
    '2BackRunBlockTrialCondition': '2Back',
    '3BackRunBlockTrialCondition': '3Back',
}

CONTRASTS = [
    [[-1, 0, 1, 0, 0]],
    [[ 1, 0, -1, 0, 0]],
    [[-3, -2, -1, 6, 0]],
    [[6, -1, -2, -3, 0]],
]

CUT_COORDS = [-20, 0, 15, 30, 45]

DURATION = 3.0
