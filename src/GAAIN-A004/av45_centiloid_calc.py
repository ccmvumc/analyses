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
data_path = '/Users/jasonrussell/Documents/OUTPUTS/gaain_A004'
out_dir = '/Users/jasonrussell/Documents/OUTPUTS/gaain_A004'
os.chdir(data_path)

#: Import CSV
pib_gaain_df = pd.read_csv('/Users/jasonrussell/Documents/Covariates for pipelines/GAAIN-A004-av45_centiloid_calculation/pib_centiloid_suvrs.csv')
fbp_gaain_df = pd.read_csv('/Users/jasonrussell/Documents/Covariates for pipelines/GAAIN-A004-av45_centiloid_calculation/av45_centiloid_suvrs.csv')
validation_df = pd.read_csv('/Users/jasonrussell/Documents/Covariates for pipelines/GAAIN-A004-av45_centiloid_calculation/gaain_validation.csv')

#import suvrs for conversion
fbp_suvr_df = pd.read_csv('standard_centiloid_suvrs.csv')

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

#add pib suvrs to av45_df
fbp_gaain_df['pib_suvr'] = pib_gaain_df['SUVR']

# Plot fbp vs PiB suvr and calculate equation of line
slope_fbp, intercept_fbp, r_value_fbp, p_value_fbp, std_err_fbp = stats.linregress(fbp_gaain_df['SUVR'],fbp_gaain_df['pib_suvr'])


#calculated PiB SUVRs from FBP

fbp_suvr_df["Calculated PiB SUVR"] = slope_fbp * fbp_suvr_df["SUVR"] + intercept_fbp

#calculate centiloid from pib calc

fbp_suvr_df["Centiloids"] = 100*(fbp_suvr_df["Calculated PiB SUVR"] - hc_mean_suvr)/(ad_hc_dif)


fbp_suvr_df.to_csv(f'{out_dir}/Centiloids.csv', index=False)



