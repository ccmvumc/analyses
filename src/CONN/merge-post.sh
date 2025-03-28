rm /OUTPUTS/xvfb.auth
rm /OUTPUTS/xvfb.err

# Delete merged pre-processed files since we only want 1st Level Results
rm -r /OUTPUTS/conn/results/preprocessing/[A-Za-z]*.mat
rm -r /OUTPUTS/conn/results/preprocessing/*.nii
rm -r /OUTPUTS/conn/results/preprocessing/*.matc
rm -r /OUTPUTS/conn/data/*.mat
rm -r /OUTPUTS/conn/data/*.matc

# Extract Z matrix to csv with row per value
python /REPO/src/CONN/zvalues_mat2csv.py

# Make PDF report
python /REPO/src/CONN/make_pdf.py
