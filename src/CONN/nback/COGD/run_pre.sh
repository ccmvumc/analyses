echo "Making conditions.mat from edat.txt"
python extract_conditions.py

echo "Making trials.csv from edat.txt"
python extract_trials.py

echo "Making behavior.txt from trials.csv"
python extract_behavior.py

echo "Making contrasts.mat"
python make_contrasts.py

echo "ALL DONE!"
