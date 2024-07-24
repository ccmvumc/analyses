import scipy.io
import os
import pandas as pd

ROOTDIR = '/OUTPUTS/DATA'

# Map names as saved in CONN file to our shorter codes
NAME2CODE = {
    'networks.DefaultMode.MPFC (1,55,-3)': 'MPFC',
    'networks.DefaultMode.LP (L) (-39,-77,33)': 'L_PL',
    'networks.DefaultMode.LP (R) (47,-67,29)': 'R_PL',
    'networks.DefaultMode.PCC (1,-61,38)': 'PCC',
    'networks.Salience.ACC (0,22,35)': 'ACC',
    'networks.Salience.AInsula (L) (-44,13,1)': 'L_INS',
    'networks.Salience.AInsula (R) (47,14,0)': 'R_INS',
    'networks.FrontoParietal.LPFC (L)  (-43,33,28)': 'L_LPFC',
    'networks.FrontoParietal.PPC (L)  (-46,-58,49)': 'L_PPC',
    'networks.FrontoParietal.LPFC (R)  (41,38,30)': 'R_LPFC',
    'networks.FrontoParietal.PPC (R)  (52,-52,45)': 'R_PPC',
}

# Get just the codes/names names
NAMES = list(NAME2CODE.keys())
CODES = list(NAME2CODE.values())

# Get the unique pairs
PAIRS = [f'{x}-{y}' for i, x in enumerate(CODES) for y in CODES[i+1:]]

# Initialize list of records
data = []

# Load CONN file for each subject/session
for subject in sorted(os.listdir(ROOTDIR)):
    for session in sorted(os.listdir(os.path.join(ROOTDIR, subject))):
        # Initialze new record for subject/session
        record = {'SUBJECT': subject, 'SESSION': session}

        # Load the CONN data for subject/session
        connfile = f'{ROOTDIR}/{subject}/{session}/conn/results/firstlevel/SBC_01/resultsROI_Subject001_Condition001.mat'
        mat = scipy.io.loadmat(connfile)

        # Find the pairs and extract Z values
        r1count = len(mat['names'][0])
        r2count = len(mat['names'][0])
        for i in range(r1count):
            roi1 = str(mat['names'][0][i][0])

            if roi1 not in NAMES:
                continue

            for j in range(r2count):
                roi2 = str(mat['names2'][0][j][0])

                if roi2 not in NAMES:
                    continue
            
                pair = f'{NAME2CODE.get(roi1)}-{NAME2CODE.get(roi2)}'
        
                if pair not in PAIRS:
                    continue

                # Found a pair we want so save it
                record[pair] =  mat['Z'][i][j]

        # Append record
        data.append(record)

# Make a dataframe from records and save to csv
df = pd.DataFrame(data)
df.to_csv('/OUTPUTS/data.csv', index=False)
