import numpy as np
import scipy.io

from shared import CONTRAST_FILE, write_contrasts


# Conditions in .mat files
# 0BackRunBlockTrialCondition
# 1BackRunBlockTrialCondition
# 2BackRunBlockTrialCondition
# 3BackRunBlockTrialCondition 

# Contrasts of interest are:
# 0Back > 2Back
# 2Back > 0Back
# 3Back > 2Back > 1Back > 0Back
# 0Back > 1Back > 2Back > 3Back


def get_contrasts():
    # TODO: only for runs with 3back, add the parametrically increasing/decreasing
    names = [
        '0Back_gt_2Back', 
        '2Back_gt_0Back', 
        'ParamInc',
        'ParamDec'
    ]

    vectors = list([
        np.array([1.0,  0.0, -1.0, 0.0], dtype=np.double),
        np.array([-1.0, 0.0, 1.0,  0.0], dtype=np.double),
        np.array([-3.0, -2.0, -1.0, 6.0], dtype=np.double),
        np.array([6.0, -1.0, -2.0, -3.0], dtype=np.double)
    ])
    return (names, vectors)


if __name__ == '__main__':
    names, vectors = get_contrasts()
    print(names)
    print(vectors)
    write_contrasts(names, vectors, CONTRAST_FILE)
