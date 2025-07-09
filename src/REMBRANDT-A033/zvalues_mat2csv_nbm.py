import pandas as pd
from scipy.io import loadmat

# Outputs long format csv file, row per edge, with these columns:
#id,condition,region1num,region2num,region1name,region2name,zvalue

# Brodmann Area ~= Schaefer200
# BA8 ~= 92,94,95,181,195,197
# BA9 ~= 91,93,94,176,195,196
# BA10 ~= 67,88,89,171,192,194
# BA32 ~= 52,88,90,180,194
# BA46 ~=  51,66,68,172,174,175
# Also including 193 which actually overlaps with BA24/BA25

SOURCE_ROIS = ['DnSeg']

TARGET_ROIS = [
    'Schaefer200.51 7Networks_LH_SalVentAttn_PFCl_1',
    'Schaefer200.52 7Networks_LH_SalVentAttn_Med_1',
    'Schaefer200.66 7Networks_LH_Cont_PFCl_1',
    'Schaefer200.67 7Networks_LH_Cont_PFCl_2',
    'Schaefer200.68 7Networks_LH_Cont_PFCl_3',
    'Schaefer200.88 7Networks_LH_Default_PFC_6',
    'Schaefer200.89 7Networks_LH_Default_PFC_7',
    'Schaefer200.90 7Networks_LH_Default_PFC_8',
    'Schaefer200.91 7Networks_LH_Default_PFC_9',
    'Schaefer200.92 7Networks_LH_Default_PFC_10',
    'Schaefer200.93 7Networks_LH_Default_PFC_11',
    'Schaefer200.94 7Networks_LH_Default_PFC_12',
    'Schaefer200.95 7Networks_LH_Default_PFC_13',
    'Schaefer200.171 7Networks_RH_Cont_PFCl_2', 
    'Schaefer200.172 7Networks_RH_Cont_PFCl_3',
    'Schaefer200.174 7Networks_RH_Cont_PFCl_5', 
    'Schaefer200.175 7Networks_RH_Cont_PFCl_6', 
    'Schaefer200.176 7Networks_RH_Cont_PFCl_7',
    'Schaefer200.180 7Networks_RH_Cont_PFCmp_1', 
    'Schaefer200.181 7Networks_RH_Cont_PFCmp_2', 
    'Schaefer200.192 7Networks_RH_Default_PFCdPFCm_2',
    'Schaefer200.193 7Networks_RH_Default_PFCdPFCm_3',
    'Schaefer200.194 7Networks_RH_Default_PFCdPFCm_4',
    'Schaefer200.195 7Networks_RH_Default_PFCdPFCm_5',
    'Schaefer200.196 7Networks_RH_Default_PFCdPFCm_6',
    'Schaefer200.197 7Networks_RH_Default_PFCdPFCm_7',
]
ROOTDIR = '/OUTPUTS'
data = []

# load conditions
m = loadmat(f'{ROOTDIR}/conn/results/preprocessing/_list_conditions.mat')
conditions = [x[0] for x in m['allnames'][0]]

# load regions
m = loadmat(f'{ROOTDIR}/conn/results/firstlevel/SBC_01/_list_sources.mat')
if len(m['sourcenames']) > 0:
    print(m['sourcenames'])
    print(m['sourcenames'][0])
    sources = [x[0] for x in m['sourcenames'][0]]
else:
    # Load from main conn mat file 
    m = loadmat(f'{ROOTDIR}/conn.mat')
    sources = m['CONN_x']['Analyses'][0][0][0][0]['sources']
    sources = [x[0] for x in sources[0]]

print(f'{sources=}')

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

                # We only want dnseg to our chosen list
                if n1 not in SOURCE_ROIS or n2 not in TARGET_ROIS:
                    continue

                data.append({
                    'id': subject,
                    'condition': c,
                    'r1num': j,
                    'r2num': k,
                    'r1name': names1[j],
                    'r2name': names2[k],
                    'zvalue': m['Z'][j][k][s]
                })

# Save a csv
pd.DataFrame(data).to_csv(f'{ROOTDIR}/zvalues-DnSeg.csv', index=False)

print('DONE!')
