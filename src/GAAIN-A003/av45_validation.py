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
data_path = '/Users/jasonrussell/Documents/OUTPUTS/gaain_A003'
os.chdir(data_path)

#: Import CSV
pib_gaain_df = pd.read_csv("pib_centiloid_suvrs.csv")
fbp_gaain_df = pd.read_csv("av45_centiloid_suvrs.csv")
validation_df = pd.read_csv("/Users/jasonrussell/Documents/Covariates for pipelines/GAAIN-A003-av45_validation/covariates.csv")

#Split df to young and AD
pib_hc_df = validation_df[validation_df['ID'].str.contains('YC')].copy()
pib_AD_df = validation_df[validation_df['ID'].str.contains('AD')].copy()

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
for index, row in validation_df.iterrows():
    cl = 100 * (row['SUVR'] - hc_mean_suvr) / ad_hc_dif
    CLs.append(cl)
    
validation_df["Calculated CLs"]=CLs


# Plot individual CL values against SUVR and establish slope (0.98<c<1.02), intercept (-2<m<2), and R2>0.98
fig = sns.lmplot(data=validation_df, x="Klunk CLs", y="Calculated CLs")
slope, intercept, r_value, p_value, std_err = stats.linregress(validation_df['Klunk CLs'],validation_df['Calculated CLs'])
coefficient_of_dermination = r2_score(validation_df["Calculated CLs"], validation_df['Klunk CLs'])

plt.annotate(f"Slope (target: 0.98<c<1.02) = {np.round(slope, 5)}",
             xy=(50, 5), xycoords='axes points', fontsize=8, color='red')
plt.annotate(f"Intercept (target: -2<m<2) = {np.round(intercept,5)}",
             xy=(50, 15), xycoords='axes points', fontsize=8, color='red')
plt.annotate(f"R2 (target: >0.98) = {np.round(coefficient_of_dermination, 10)}",
             xy=(50, 25), xycoords='axes points', fontsize=8, color='red')
plt.savefig(f"{data_path}/PiB Centiloid validation with GAAIN data.png")
plt.clf()

#add pib suvrs to av45_df
fbp_gaain_df['pib_suvr'] = pib_gaain_df['SUVR']

# Plot fbp vs PiB suvr and calculate equation of line
fig = sns.lmplot(data=fbp_gaain_df, x="SUVR", y="pib_suvr")
slope_fbp, intercept_fbp, r_value_fbp, p_value_fbp, std_err_fbp = stats.linregress(fbp_gaain_df['SUVR'],fbp_gaain_df['pib_suvr'])

plt.annotate(f" PiB SUVR = {np.round(slope_fbp, 3)} x FBP SUVR + {np.round(intercept_fbp, 3)}",
             xy=(50, 5), xycoords='axes points', fontsize=8, color='red')
plt.savefig("FBP vs PiB SUVR with GAAIN data.png")
plt.clf()

#calculated PiB SUVRs from FBP

fbp_gaain_df["Calculated PiB SUVR"] = slope_fbp * fbp_gaain_df["SUVR"] + intercept_fbp

fig = sns.lmplot(data=fbp_gaain_df, x="Calculated PiB SUVR", y="pib_suvr")
coefficient_of_dermination_fbp_pib_calc = r2_score(fbp_gaain_df["Calculated PiB SUVR"], fbp_gaain_df['pib_suvr'])

plt.annotate(f"R2 (target: >0.70) = {np.round(coefficient_of_dermination_fbp_pib_calc, 10)}",
             xy=(50, 5), xycoords='axes points', fontsize=8, color='red')
plt.savefig("PiB vs PiB Calc with GAAIN data.png")
plt.clf()

#calculate centiloid from pib calc

fbp_gaain_df["Centiloids"] = 100*(fbp_gaain_df["Calculated PiB SUVR"] - hc_mean_suvr)/(ad_hc_dif)

#plot Amyvid to Centiloid
fig = sns.lmplot(data=fbp_gaain_df, x="SUVR", y="Centiloids")
slope_fbp_cl, intercept_fbp_cl, r_value_fbp_cl, p_value_fbp_cl, std_err_fbp_cl = stats.linregress(fbp_gaain_df['SUVR'],fbp_gaain_df['Centiloids'])

plt.annotate(f" Centiloids (florbetabir) = {np.round(slope_fbp_cl, 3)} x FBP SUVR + {np.round(intercept_fbp_cl, 3)}",
             xy=(50, 5), xycoords='axes points', fontsize=8, color='red')
plt.savefig("FBP to CL with GAAIN data.png")
plt.clf()

#Establish centiloid equation from FBP CL = 100(PiBSUVRind - PiBSUVRYC)/(PiBSUVRAD100 - PiBSUVRYC)
print(f"FBP CL = {slope_fbp_cl}*SUVr(FBP) + {intercept_fbp_cl}")
