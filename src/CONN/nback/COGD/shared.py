import pandas as pd
import io
import numpy as np
import scipy.io


def read_edat(edat_path):
    skiprows = 0
    first_field = 'ExperimentName'
    encoding = 'utf-16'

    # Determine how many rows to skip prior to header
    try:
        with io.open(edat_path, encoding=encoding) as _f:
            for line in _f:
                if line.startswith(first_field):
                    break
                else:
                    skiprows += 1
    except UnicodeError:
        encoding = 'utf-8'
        with io.open(edat_path, encoding=encoding) as _f:
            for line in _f:
                if line.startswith(first_field):
                    break
                else:
                    skiprows += 1

    # Load Data
    df = pd.read_csv(
        edat_path, sep='\t', encoding=encoding, skiprows=skiprows, header=0)
    return df


def load_edat(filename):
    df = read_edat(filename)

    # Fix column names
    df.columns = df.columns.map(
        lambda x: x.replace('.', '_').replace(']', '_').replace('[', '_'))

    return df


def write_spm_conditions(names, onsets, durations, filename):
    np_names = np.array(names, dtype=object)
    np_onsets = np.empty((len(names),), dtype=object)
    np_durations = np.empty((len(names),), dtype=object)
    for i in range(len(names)):
        np_onsets[i] = onsets[i]
        np_durations[i] = durations[i]

    # Create SPM mat object
    mat = {}
    mat['names'] = np_names
    mat['onsets'] = np_onsets
    mat['durations'] = np_durations

    # Create file
    scipy.io.savemat(filename, mat)


def load_behavior(filename):
    b = {}
    with open(filename, "r") as f:
        for line in f:
            k, v = line.split('=')
            b[k] = v

    return b


def load_trials(filename):
    return pd.read_csv(filename)


def save_behavior(data, filename):
    '''Write text file with behavior values'''
    with open(filename, "w") as f:
        for k in sorted(data):
            f.write("%s=%s\n" % (k, data[k]))


def save_trials(df, filename):
    df.to_csv(filename, index=False)


def write_contrasts(names, vectors, filename):
    np_vectors = np.empty((len(names),), dtype=object)
    for i in range(len(names)):
        np_vectors[i] = vectors[i]

    mat = {}
    mat['tcon_name'] = np.array(names, dtype=object)
    mat['tcon_vec'] = np.array(np_vectors, dtype=object)

    try:
        scipy.io.savemat(filename, mat)
    except OSError:
        print('error saving file:' + filename)
        return False

    return True
