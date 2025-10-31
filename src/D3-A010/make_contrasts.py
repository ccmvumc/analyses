import numpy as np
from scipy.io import savemat


def make_contrast(filename, subjects, subjectc, conditions, conditionc, sources, sourcec):
    return {
        'filename': filename,
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

# Build the batch in a format that will load correctly in matlab/CONN
filename = '/OUTPUTS/conn.mat',
mat = {}
batch_data = []

# Reward minus NoReward, Main effect
batch_data.append(make_contrast(filename, ['AllSubjects'], [1], ['Baseline'], [1], ['Effect of Reward', 'Effect of NoReward'], [1, -1]))

# Main effect, controls only
batch_data.append(make_contrast(filename, ['GROUP_Control'], [1], ['Baseline'], [1], ['Effect of Reward', 'Effect of NoReward'], [1, -1]))

# Main effect, depressed only
batch_data.append(make_contrast(filename, ['GROUP_Depress'], [1], ['Baseline'], [1], ['Effect of Reward', 'Effect of NoReward'], [1, -1]))

# Hit minus Miss for Rewards, Main effect
batch_data.append(make_contrast(filename, ['AllSubjects'], [1], ['Baseline'], [1], ['Effect of HitReward', 'Effect of MissReward'], [1, -1]))

# then controls only
batch_data.append(make_contrast(filename, ['GROUP_Control'], [1], ['Baseline'], [1], ['Effect of HitReward', 'Effect of MissReward'], [1, -1]))

# then depressed only
batch_data.append(make_contrast(filename, ['GROUP_Depress'], [1], ['Baseline'], [1], ['Effect of HitReward', 'Effect of MissReward'], [1, -1]))

print(batch_data)

# Create file
mat['batch'] = np.array(batch_data)
OUTFILE = '/OUTPUTS/contrasts.mat'
savemat(OUTFILE, mat)
