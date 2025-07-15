echo "Making conditions.mat from edat.txt"
python make_conditions.py

echo "Making trials.csv from edat.txt"
python make_trials.py

echo "Making behavior.txt from trials.csv"
python make_behavior.py

echo "Making contrasts.mat"
python make_contrasts.py

echo "ALL DONE!"
