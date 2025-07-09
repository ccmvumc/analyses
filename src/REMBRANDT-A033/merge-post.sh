# Delete merged pre-processed files since we only want 1st Level Results
rm -r /OUTPUTS/conn/results/preprocessing/[A-Za-z]*.mat
rm -r /OUTPUTS/conn/data/*.mat

# Extract Z matrix to csv with row per value
python /REPO/src/REMBRANDT-A033/zvalues_mat2csv_nbm.py
python /REPO/src/REMBRANDT-A033/zvalues_csv2csv_nbm.py
