import zipfile
from glob import glob
import os, shutil

subjects = [x for x in os.listdir('/INPUTS') if os.path.isdir(f'/INPUTS/{x}')]

for subj in subjects:
    print(f'Prep {subj}')

    subj_dir = f'/OUTPUTS/{subj}'
    subj_mat = glob(f'/INPUTS/{subj}/assessors/*/*/CONN/conn_project.mat')[0]
    subj_zip = glob(f'/INPUTS/{subj}/assessors/*/*/CONN/conn_project.zip')[0]

    os.makedirs(subj_dir, exist_ok=True)

    with zipfile.ZipFile(subj_zip, "r") as z:
        z.extractall(subj_dir)

    shutil.copy(subj_mat, subj_dir)
