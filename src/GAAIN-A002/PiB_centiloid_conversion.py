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
data_path = '/Users/jasonrussell/Documents/OUTPUTS/gaain_validation'
os.chdir(data_path)
out_dir = '/Users/jasonrussell/Documents/OUTPUTS/gaain_A002'

#: Import CSV
suvr_df = pd.read_csv("standard_centiloid_suvrs.csv")
pib_gaain_df  = pd.read_csv("/Users/jasonrussell/Documents/Covariates for pipelines/GAAIN-A002-centiloid_calculation/covariates.csv")

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
for index, row in suvr_df.iterrows():
    cl = 100 * (row['SUVR'] - hc_mean_suvr) / ad_hc_dif
    CLs.append(cl)
    
suvr_df["Calculated CLs"]=CLs

suvr_df.to_csv(f'{out_dir}/centiloids.csv', index=False)
