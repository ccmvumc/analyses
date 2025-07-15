
from shared import load_edat, write_spm_conditions, get_conditions


TYPE_FIELD = 'TrialCondition'  # edat column that stores trial condition
TYPE_FIELD_SUFFIX = 'RunBlockTrialCondition'
DURATION = 0.0


def _get_conditions():
    '''Values in type field are condition with suffix'''
    return [f'{x}{TYPE_FIELD_SUFFIX}' for x in get_conditions()]


def load_nback():
    # Load the edat as a dataframe
    df = load_edat()

    # Get the offset to the first trial
    start_offset = df.iloc[0].RestProbe_OnsetTime

    # Get subset of rows
    _conditions = _get_conditions()
    df = df[df[TYPE_FIELD].isin(_conditions)]

    # Subtract start time and convert to seconds
    df['_Onset'] = (df['StimText_OnsetTime'] - start_offset) / 1000.0

    return df


def make_conditions(conditions, type_field, duration):
    names = []
    onsets = []
    durations = []

    # Load nback data from edat txt file to a pandas dataframe
    df = load_nback()

    # Load onsets and durations for each condition
    for cond in conditions:
        # Get the list of onsets for this condition
        cond_onsets = list(df[df[type_field] == cond]['_Onset'])
        onsets.append(cond_onsets)

        # Set the name of the condition
        names.append(cond)

        # Set the durations
        durations.append([duration])

    # Save to mat file for spm
    write_spm_conditions(names, onsets, durations)


if __name__ == '__main__':
    make_conditions(get_conditions(), TYPE_FIELD, DURATION)
