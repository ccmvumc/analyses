import glob
import pandas as pd

# Option Level 1234, Choose Left/Right


VERSIONMAP = {
    'effort_FMR_revisedDZ_run1': 'a', 
    'effort_FMR_revisedDZ_run1rab': 'b',
    'effort_FMR_revisedDZ_run1rc': 'b',
    'effort_FMR_revisedDZ_run2': 'a',  
    'effort_FMR_revisedDZ_run2rab': 'b',
    'effort_FMR_revisedDZ_run2rc': 'b',
    'effort_FMR_revisedDZ_run3': 'a',  
    'effort_FMR_revisedDZ_run3rab': 'b',
    'effort_FMR_revisedDZ_run3rc': 'b',
}

def load_eefrt(rootdir):
    e1 = glob.glob(f'{rootdir}/fMRI_EEFRT1/D3/*/*/*/*/*edat*.txt')
    data = []
    for e in sorted(e1):
        _, subj,sess,_,_,filename = e.rsplit('/', 5)
        data.append({
            'SUBJECT': subj,
            'SESSION': sess,
            'EFFORT1': filename,
            'PATH1': e,
        })

    df1 = pd.DataFrame(data)

    e2 = glob.glob(f'{rootdir}/fMRI_EEFRT2/D3/*/*/*/*/*edat*.txt')
    data = []
    for e in sorted(e2):
        _, subj,sess,_,_,filename = e.rsplit('/', 5)
        data.append({
            'SUBJECT': subj,
            'SESSION': sess,
            'EFFORT2': filename,
            'PATH2': e,
        })

    df2 = pd.DataFrame(data)

    e3 = glob.glob(f'{rootdir}/fMRI_EEFRT3/D3/*/*/*/*/*edat*.txt')
    data = []
    for e in sorted(e3):
        _, subj,sess,_,_,filename = e.rsplit('/', 5)
        data.append({
            'SUBJECT': subj,
            'SESSION': sess,
            'EFFORT3': filename,
            'PATH3': e,
        })

    df3 = pd.DataFrame(data)

    df = pd.merge(df1,df2)
    df = pd.merge(df,df3)

    return df


def read_edat(edat_path):
    import io
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
    return pd.read_csv(edat_path, sep='\t', encoding=encoding, skiprows=skiprows, header=0)


def parse_edat(filename):
    data = {}

    edat = read_edat(filename)

    if not (edat.iloc[0].ExperimentName).startswith('effort_FMR_revisedDZ_run'):
        raise Exception(f'Wrong Experiment:{edat.iloc[0].ExperimentName}:{filename}')

    # Get the experiment version
    data['VERSION'] = edat.iloc[0].ExperimentName

    # Get date run
    data['DATE'] = edat.iloc[0].SessionDate

    # Count how many times subject chose Left vs Right
    if 'ChoseL' in edat['SlideState'].values:
        data['COUNTLEFT'] = int(edat['SlideState'].value_counts().ChoseL)
    else:
        data['COUNTLEFT'] = 0

    if 'ChoseR' in edat['SlideState'].values:
        data['COUNTRIGHT'] = int(edat['SlideState'].value_counts().ChoseR)
    else:
        data['COUNTRIGHT'] = 0

    return data


def get_data(row):
    # Run 1 of Effort
    data = parse_edat(row.PATH1)
    row['LEFT1'] = data['COUNTLEFT'] / (data['COUNTLEFT'] + data['COUNTRIGHT'])
    row['DATE1'] = data['DATE']
    row['VERSION1'] = data['VERSION']

    # Run 2 of Effort
    data = parse_edat(row.PATH2)
    row['LEFT2'] = data['COUNTLEFT'] / (data['COUNTLEFT'] + data['COUNTRIGHT'])
    row['DATE2'] = data['DATE']
    row['VERSION2'] = data['VERSION']

    # Run 3 of Effort
    data = parse_edat(row.PATH3)
    row['LEFT3'] = data['COUNTLEFT'] / (data['COUNTLEFT'] + data['COUNTRIGHT'])
    row['DATE3'] = data['DATE']
    row['VERSION3'] = data['VERSION']

    # Get average
    row['LEFTPERCENT'] = int(((row['LEFT1'] + row['LEFT2'] + row['LEFT3']) / 3) * 100)

    return row


def extract_dir(rootdir, outfile):
    # Load filenames
    df = load_eefrt(ROOTDIR)

    # Get counts
    df = df.apply(get_data, axis=1)

    # Get session type
    df['SESSTYPE'] = df['SESSION'].str[-1].map({'a': 'Baseline', 'b': 'EndStep1'})

    df['VER1'] = df.VERSION1.map(VERSIONMAP)
    df['VER2'] = df.VERSION2.map(VERSIONMAP)
    df['VER3'] = df.VERSION3.map(VERSIONMAP)
    df['VERSION'] = df.VER1 + df.VER2 + df.VER3

    # Pivot to column per subject
    df['TYPEVER'] = df['SESSTYPE'] + df['VERSION']
    dfp = df.pivot(index=['SUBJECT'], columns=['TYPEVER'], values='LEFTPERCENT').fillna('')

    # Save it
    dfp.to_csv(outfile)


if __name__ == "__main__":
    import sys
    extract_dir(sys.argv[1], sys.argv[2])
