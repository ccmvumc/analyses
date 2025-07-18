
from ..shared import save_behavior, load_trials


def parse_behavior():
    # Initialize the summary data
    data = {}

    # Load the trials data
    df = load_trials()

    # Accuracy
    data['overall_acc'] = df.ACC.mean().round(2)
    data['zeroback_acc'] = df[df.TYPE == '0Back'].ACC.mean().round(2)
    data['twoback_acc'] = df[df.TYPE == '2Back'].ACC.mean().round(2)
    data['zerobacktarget_acc'] = df[(df.TYPE == '0Back') & (df.SUBTYPE == 'Target')].ACC.mean().round(2)
    data['zerobackdistractor_acc'] = df[(df.TYPE == '0Back') & (df.SUBTYPE == 'Distractor')].ACC.mean().round(2)
    data['twobackbegin_acc'] = df[(df.TYPE == '2Back') & (df.SUBTYPE == 'Begin')].ACC.mean().round(2)
    data['twobacktarget_acc'] = df[(df.TYPE == '2Back') & (df.SUBTYPE == 'Target')].ACC.mean().round(2)
    data['twobackdistractor_acc'] = df[(df.TYPE == '2Back') & (df.SUBTYPE == 'Distractor')].ACC.mean().round(2)
 
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
    data['overall_rt'] = df.RT.mean().round(2)
    data['zeroback_rt'] = df[df.TYPE == '0Back'].RT.mean().round(2)
    data['twoback_rt'] = df[df.TYPE == '2Back'].RT.mean().round(2)
    data['zerobacktarget_rt'] = df[(df.TYPE == '0Back') & (df.SUBTYPE == 'Target')].RT.mean().round(2)
    data['zerobackdistractor_rt'] = df[(df.TYPE == '0Back') & (df.SUBTYPE == 'Distractor')].RT.mean().round(2)
    data['twobackbegin_rt'] = df[(df.TYPE == '2Back') & (df.SUBTYPE == 'Begin')].RT.mean().round(2)
    data['twobacktarget_rt'] = df[(df.TYPE == '2Back') & (df.SUBTYPE == 'Target')].RT.mean().round(2)
    data['twobackdistractor_rt'] = df[(df.TYPE == '2Back') & (df.SUBTYPE == 'Distractor')].RT.mean().round(2)

    data = {k: str(v) for k, v in data.items()}

    return data


def extract_behavior():
    data = parse_behavior()

    # write text file
    save_behavior(data)


if __name__ == '__main__':
    extract_behavior()
