
from shared import save_behavior, load_trials


def parse_behavior():
    # Initialize the summary data
    data = {}

    # Load the trials data
    df = load_trials()

    # Accuracy
    data['overall_acc'] = df.ACC.mean()
    data['zeroback_acc'] = df[df.TYPE == '0Back'].ACC.mean()
    data['twoback_acc'] = df[df.TYPE == '2Back'].ACC.mean()
    data['zerobacktarget_acc'] = df[(df.TYPE == '0Back') & (df.SUBTYPE == 'Target')].ACC.mean()
    data['zerobackdistractor_acc'] = df[(df.TYPE == '0Back') & (df.SUBTYPE == 'Distractor')].ACC.mean()
    data['twobackbegin_acc'] = df[(df.TYPE == '2Back') & (df.SUBTYPE == 'Begin')].ACC.mean()
    data['twobacktarget_acc'] = df[(df.TYPE == '2Back') & (df.SUBTYPE == 'Target')].ACC.mean()
    data['twobackdistractor_acc'] = df[(df.TYPE == '2Back') & (df.SUBTYPE == 'Distractor')].ACC.mean()
 
    # Counts
    data['overall_count'] = len(df)
    data['zeroback_count'] = len(df[df.TYPE == '0Back'])
    data['twoback_count'] = len(df[df.TYPE == '2Back'])
    data['zerobacktarget_count'] = len(df[(df.TYPE == '0Back') & (df.SUBTYPE == 'Target')])
    data['zerobackdistractor_count'] = len(df[(df.TYPE == '0Back') & (df.SUBTYPE == 'Distractor')])
    data['twobackbegin_count'] = len(df[(df.TYPE == '2Back') & (df.SUBTYPE == 'Begin')])
    data['twobacktarget_count'] = len(df[(df.TYPE == '2Back') & (df.SUBTYPE == 'Target')])
    data['twobackdistractor_count'] = len(df[(df.TYPE == '2Back') & (df.SUBTYPE == 'Distractor')])

    # Reaction Time
    data['overall_rt'] = df.RT.mean()
    data['zeroback_rt'] = df[df.TYPE == '0Back'].RT.mean()
    data['twoback_rt'] = df[df.TYPE == '2Back'].RT.mean()
    data['zerobacktarget_rt'] = df[(df.TYPE == '0Back') & (df.SUBTYPE == 'Target')].RT.mean()
    data['zerobackdistractor_rt'] = df[(df.TYPE == '0Back') & (df.SUBTYPE == 'Distractor')].RT.mean()
    data['twobackbegin_rt'] = df[(df.TYPE == '2Back') & (df.SUBTYPE == 'Begin')].RT.mean()
    data['twobacktarget_rt'] = df[(df.TYPE == '2Back') & (df.SUBTYPE == 'Target')].RT.mean()
    data['twobackdistractor_rt'] = df[(df.TYPE == '2Back') & (df.SUBTYPE == 'Distractor')].RT.mean()

    # Round floats to 2 places
    for k, v in data.items():
        if isinstance(v, float):
            data[k] = round(v, 2)

    # Convert all values to string
    data = {k: str(v) for k, v in data.items()}

    return data


def extract_behavior():
    data = parse_behavior()

    # write text file
    save_behavior(data)


if __name__ == '__main__':
    extract_behavior()
