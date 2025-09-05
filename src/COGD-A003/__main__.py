'''COGD RSFC from regions of interest, loads data processed by CONN toolbox'''
# INPUTS (per subject): conn_project.zip
# OUTPUTS: .csv


import os, sys

import scipy.io
import pandas as pd
import glob


ROOTDIR = '/INPUTS'

# Map names as saved in CONN file to our shorter codes
NAME2CODE = {
    'Schaefer100.37\t7Networks_LH_Cont_Cing_1': 'L_ACC',
    'Schaefer100.35\t7Networks_LH_Cont_PFCl_1': 'L_DLPFC',
    'Schaefer100.34\t7Networks_LH_Cont_Par_1':  'L_PPC',
    'Schaefer100.87\t7Networks_RH_Cont_Cing_1': 'R_ACC',
    'Schaefer100.84\t7Networks_RH_Cont_PFCl_2': 'R_DLPFC',
    'Schaefer100.82\t7Networks_RH_Cont_Par_2':  'R_PPC',
}

#    'Schaefer100.36\t7Networks_LH_Cont_pCun_1': 'L_PCUN',
#    'Schaefer100.89\t7Networks_RH_Cont_pCun_1': 'R_PCUN',

# dlpfc 35  7Networks_LH_Cont_PFCl_1
# dlpfc 84  7Networks_RH_Cont_PFCl_2
# cingulate 37  7Networks_LH_Cont_Cing_1
# cingulate 87  7Networks_RH_Cont_Cing_1
# parietal 34  7Networks_LH_Cont_Par_1
# parietal 82  7Networks_RH_Cont_Par_2
# precuneus 36  7Networks_LH_Cont_pCun_1
# precuneus 89  7Networks_RH_Cont_pCun_1


def main(input_dir, output_dir):
    # Get just the codes/names names
    NAMES = list(NAME2CODE.keys())
    CODES = list(NAME2CODE.values())

    # Get the unique pairs
    PAIRS = [f'{x}-{y}' for i, x in enumerate(CODES) for y in CODES[i + 1:]]
    print(PAIRS)

    # Initialize list of records
    data = []

    # Load CONN file for each subject/session
    for subject in sorted(os.listdir(input_dir)):
        if not os.path.isdir(f'{input_dir}/{subject}'):
            continue

        print(subject)

        # Initialze new record for subject/session
        record1 = {'SUBJECT': subject, 'SESSION': 'Baseline'}
        record2 = {'SUBJECT': subject, 'SESSION': 'Week5'}

        # Load the CONN data for subject
        try:
            connfile1 = glob.glob(f'{input_dir}/{subject}/assessors/*/*/CONN/conn_project/results/firstlevel/SBC_01/resultsROI_Condition001.mat')[0]
            connfile2 = glob.glob(f'{input_dir}/{subject}/assessors/*/*/CONN/conn_project/results/firstlevel/SBC_01/resultsROI_Condition002.mat')[0]
            mat1 = scipy.io.loadmat(connfile1)
            mat2 = scipy.io.loadmat(connfile2)
        except Exception as err:
            print(f'failed to load connfile:{subject}:{err}')
            continue

        # Find the pairs and extract Z values
        r1count = len(mat1['names'][0])
        r2count = len(mat1['names'][0])
        for i in range(r1count):
            roi1 = str(mat1['names'][0][i][0])

            if roi1 not in NAMES:
                continue

            for j in range(r2count):
                roi2 = str(mat1['names2'][0][j][0])

                if roi2 not in NAMES:
                    continue

                pair = f'{NAME2CODE.get(roi1)}-{NAME2CODE.get(roi2)}'

                if pair not in PAIRS:
                    continue

                # Found a pair we want so save it
                record1[pair] = mat1['Z'][i][j]
                record2[pair] = mat2['Z'][i][j]


        # Append record for subject
        data.append(record1)
        data.append(record2)

    # Make a dataframe from records and save to csv
    df = pd.DataFrame(data)

    # Mean across hemis
    df['ACC_DLPFC'] = df[['L_ACC-L_DLPFC', 'L_ACC-R_DLPFC', 'L_DLPFC-R_ACC', 'R_ACC-R_DLPFC']].mean(axis=1)
    df['ACC_PPC'] =   df[['L_ACC-L_PPC',   'L_ACC-R_PPC',   'L_PPC-R_ACC',   'R_ACC-R_PPC']].mean(axis=1)
    df['DLPFC_PPC'] = df[['L_DLPFC-L_PPC', 'L_DLPFC-R_PPC', 'L_PPC-R_DLPFC', 'R_DLPFC-R_PPC']].mean(axis=1)
    #df['ACC_PCUN'] = ''
    #df['DLPFC_PCUN'] =  ''
    #df['PCUN_PPC'] = '' 
    df = df.drop(columns=[
        'L_ACC-L_DLPFC', 'L_ACC-R_DLPFC', 'L_ACC-L_PPC',   'L_ACC-R_PPC',   'L_ACC-L_PPC',     'L_ACC-R_PPC', 
        'L_DLPFC-R_ACC', 'R_ACC-R_DLPFC', 'L_PPC-R_ACC',   'R_ACC-R_PPC',   'L_PPC-R_ACC',     'R_ACC-R_PPC',
        'L_PPC-R_PPC',   'L_PPC-R_DLPFC', 'L_DLPFC-L_PPC', 'L_DLPFC-R_PPC', 'L_DLPFC-R_DLPFC', 'L_ACC-R_ACC', 'R_DLPFC-R_PPC',
       ])

    # Save final to file
    df.to_csv(f'{output_dir}/data.csv', index=False)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
    print('DONE!')
