
from shared import save_behavior, load_trials


CONDITIONS = ['0Back', '1Back', '2Back', '3Back']


def parse_behavior():
    # Initialize the summary data
    data = {}

    # Load the trials data
    df = load_trials()

    # Accuracy of all trials
    data['overall_ACC'] = df.ACC.mean()

    # Accuracy of each trial type
    for c in CONDITIONS:
        data[c + '_ACC'] = df[(df.TYPE == c)].ACC.mean()

    # Initialize trial count
    data['overall_trial_count'] = len(df)

    data['overall_rt_mean'] = df.RT.mean()

    # Round floats to 2 places
    for k, v in data.items():
        if isinstance(v, float):
            data[k] = round(v, 2)

    # rename to all lowercase 
    data = {k.lower(): v for k, v in data.items()}

    return data


def extract_behavior():
    data = parse_behavior()

    # write text file
    save_behavior(data)


if __name__ == '__main__':
    extract_behavior()
