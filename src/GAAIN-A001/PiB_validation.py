# -*- coding: utf-8 -*-
"""
Created on Mon Dec  4 15:02:36 2023

@author: russj13
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import seaborn as sns
from sklearn.metrics import r2_score
import os


#Set path where data is stored
data_path = '/OUTPUTS/DATA'
os.chdir(data_path)

#: Import CSV
pib_gaain_df = pd.read_csv("standard_centiloid_suvrs.csv")
validation_df = pd.read_csv("validation dataset.csv")

#Split df to young and AD
pib_hc_df = pib_gaain_df[pib_gaain_df['ID'].str.contains('YC')].copy()
pib_AD_df = pib_gaain_df[pib_gaain_df['ID'].str.contains('AD')].copy()

# Average SUVR for HC
hc_mean_suvr = pib_hc_df["SUVR"].mean()

# Average SUVR for AD
AD_mean_suvr = pib_AD_df["SUVR"].mean()

#AD - HC:
ad_hc_dif = AD_mean_suvr - hc_mean_suvr

#Establish centiloid equation CL = 100(PiBSUVRind - PiBSUVRYC)/(PiBSUVRAD100 - PiBSUVRYC)
print(f"Healthy control mean SUVr: {hc_mean_suvr} \nAD mean SUVr: {AD_mean_suvr} \nKlunk equation: CL = 100(SUVr - {hc_mean_suvr})/({ad_hc_dif})")


CLs=[]

#Calculate individual CL values
for x in range(pib_gaain_df['ID']):
    cl = 100*(pib_gaain_df.iloc[x,2] - hc_mean_suvr)/(ad_hc_dif)
    CLs.append(cl)
    
pib_gaain_df["Calculated CLs"]=CLs
pib_gaain_df["Klunk CLs"] = validation_df["Cls"]

# Plot individual CL values against SUVR and establish slope (0.98<c<1.02), intercept (-2<m<2), and R2>0.98
fig = sns.lmplot(data=pib_gaain_df, x="Klunk CLs", y="Calculated CLs")
slope, intercept, r_value, p_value, std_err = stats.linregress(pib_gaain_df['Klunk CLs'],pib_gaain_df['Calculated CLs'])
coefficient_of_dermination = r2_score(pib_gaain_df["Calculated CLs"], pib_gaain_df['Klunk CLs'])

plt.annotate(f"Slope (target: 0.98<c<1.02) = {np.round(slope, 5)}",
             xy=(50, 5), xycoords='axes points', fontsize=8, color='red')
plt.annotate(f"Intercept (target: -2<m<2) = {np.round(intercept,5)}",
             xy=(50, 15), xycoords='axes points', fontsize=8, color='red')
plt.annotate(f"R2 (target: >0.98) = {np.round(coefficient_of_dermination, 10)}",
             xy=(50, 25), xycoords='axes points', fontsize=8, color='red')
plt.savefig("PiB Centiloid validation with GAAIN data.png")
plt.clf()
