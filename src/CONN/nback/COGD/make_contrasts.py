import numpy as np
import scipy.io

from ..shared import CONTRAST_FILE, write_contrasts


# Conditions in .mat files
# Rest
# 0Back
# 2BackRunBlockTrialCondition

# Contrasts of interest are:
# (a) 0back > rest
# (b) 2back > rest
# (c) (2back > rest) > (0back > rest)


def get_contrasts():
    names = [
        '0Back_gt_Rest', 
        '2Back_gt_Rest', 
        '2Back_gt_0Back',
    ]

    vectors = list([
        np.array([-1.0, 1.0, 0.0], dtype=np.double),
        np.array([-1.0, 0.0, 1.0], dtype=np.double),
        np.array([0.0, -1.0, 1.0], dtype=np.double)
    ])
    return (names, vectors)


if __name__ == '__main__':
    names, vectors = get_contrasts()
    print(names)
    print(vectors)
    write_contrasts(names, vectors, CONTRAST_FILE)
