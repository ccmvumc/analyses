
from shared import load_edat, write_spm_conditions


def load_nback():
    names = ['REST', '0BACK', '2BACK']
    durations = [20.0, 60.0, 60.0]

    # Load the edat as a dataframe
    df = load_edat()

    offset_time = int(df['Synchronize_OffsetTime'].iloc[0])
    rest_times = list(df['Rest_OnsetTime'].unique())
    rest_onsets = [(int(x) - offset_time) / 1000 for x in rest_times]
    zero_times = df[df['Procedure_SubTrial_'] == 'ZeroBackProc']['Rest_OnsetTime'].unique()
    zero_onsets = [int(int(x) - offset_time + 24000)  / 1000  for x in zero_times]
    two_times = df[df['Procedure_SubTrial_'] == 'TwoBackProc']['Rest_OnsetTime'].unique()
    two_onsets = [int(int(x) - offset_time + 24000)  / 1000  for x in two_times]

    onsets = [rest_onsets, zero_onsets, two_onsets]

    return names, onsets, durations


def extract_conditions():
    names, onsets, durations = load_nback()

    # Save to mat file for spm
    write_spm_conditions(names, onsets, durations)


if __name__ == '__main__':
    extract_conditions()
