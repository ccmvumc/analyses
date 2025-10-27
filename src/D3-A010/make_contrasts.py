import numpy as np
from scipy.io import savemat


def make_contrast(subjects, subjectc, conditions, conditionc, sources, sourcec):
    return {
        'filename': '/OUTPUTS/conn.mat',
        'done': 1,
        'Analysis': {'type': 2},
        'Results': {
            'between_subjects': {
                'effect_names': np.array(subjects, dtype=object),
                'contrast': np.array(subjectc, dtype=np.double),
            },
            'between_conditions': {
                'effect_names': np.array(conditions, dtype=object),
                'contrast': np.array(conditionc, dtype=np.double),
            },
            'between_sources': {
                'effect_names': np.array(sources, dtype=object),
                'contrast': np.array(sourcec, dtype=np.double),
            }
        }
    }


OUTFILE = '/OUTPUTS/contrasts.mat'
mat = {}
batch_data = []


# Build the batch in a format that will load correctly in matlab/CONN


# Reward minus NoReward, Main effect
batch_data.append(make_contrast(['AllSubjects'],   [1], ['Baseline'], [1], ['Effect of Reward', 'Effect of NoReward'], [1, -1]))

# Main effect, controls only
batch_data.append(make_contrast(['GROUP_Control'], [1], ['Baseline'], [1], ['Effect of Reward', 'Effect of NoReward'], [1, -1]))

# Main effect, depressed only
batch_data.append(make_contrast(['GROUP_Depress'], [1], ['Baseline'], [1], ['Effect of Reward', 'Effect of NoReward'], [1, -1]))


print(batch_data)

# Create file
mat['batch'] = np.array(batch_data)
savemat(OUTFILE, mat)
