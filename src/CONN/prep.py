import zipfile
from glob import glob
import os, shutil

subjects = [x for x in os.listdir('/INPUTS') if os.path.isdir(f'/INPUTS/{x}')]

for subj in sorted(subjects):
    print(f'Prep {subj}')

    subj_dir = f'/OUTPUTS/{subj}'

    try:
        subj_mat = glob(f'/INPUTS/{subj}/**/CONN/conn_project.mat', recursive=True)[0]
    except:
       print(f'No conn_project.mat for subject:{subj}')
        continue

    try:
        subj_zip = glob(f'/INPUTS/{subj}/**/CONN/conn_project.zip', recursive=True)[0]
    except:
        print(f'No conn_project.zip for subject:{subj}')
        continue

    os.makedirs(subj_dir, exist_ok=True)

    with zipfile.ZipFile(subj_zip, "r") as z:
        z.extractall(subj_dir)

    shutil.copy(subj_mat, subj_dir)
