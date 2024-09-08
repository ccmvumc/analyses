# unzip the conn projects
for i in /INPUTS/*/*/CONN/;do unzip ${i}CONN/conn_project.zip -d ${i}CONN/;done

# convert covars
python /REPO/src/CONN/covariate_csv2mat.py
