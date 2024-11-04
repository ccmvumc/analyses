import pandas as pd
from scipy.io import loadmat

# Outputs csv file with these columns:
#id,condition,region1,region2,zvalue

ROOTDIR = '/OUTPUTS'
data = []

# load conditions
m = loadmat(f'{ROOTDIR}/conn/results/preprocessing/_list_conditions.mat')
conditions = [x[0] for x in m['allnames'][0]]

# load regions
m = loadmat(f'{ROOTDIR}/conn/results/firstlevel/SBC_01/_list_sources.mat')
sources =  [x[0] for x in m['sourcenames'][0]]

# Load subjects
with open(f'{ROOTDIR}/subjects.txt', 'r') as f:
    subjects = f.read().splitlines()

# Load zvalues for each condition
for i, c in enumerate(conditions):
    m = loadmat(f'{ROOTDIR}/conn/results/firstlevel/SBC_01/resultsROI_Condition{i+1:03}.mat')

    # Extract ROI names from m mat
    names1 = [x[0] for x in m['names'][0]]
    names2 = [x[0] for x in m['names2'][0]]

    # Extract the z values for pairs
    for s, subject in enumerate(subjects):
        for j, n1 in enumerate(names1):
            for k, n2 in enumerate(names2):
                if n1 == n2:
                    continue

                data.append({
                    'id': subject,
                    'condition': c,
                    'region1num': j,
                    'region2num': k,
                    'region1name': names1[j],
                    'region2name': names2[k],
                    'zvalue': m['Z'][j][k][s]
                })

# Save a csv
pd.DataFrame(data).to_csv(f'{ROOTDIR}/zvalues.csv', index=False)

print('DONE!')
