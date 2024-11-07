import zipfile
from glob import glob


for subj in filter(os.path.isdir, os.listdir('/INPUTS')):
    print(f'Prep {subj}')

    subj_dir = f'/OUTPUTS/{subj}'
    subj_mat = glob('/INPUTS/{subj}/assessors/*/*/CONN/conn_project.mat')[0]
    subj_zip = glob('/INPUTS/{subj}/assessors/*/*/CONN/conn_project.zip')[0]

    os.makedirs(subj_dir, exist_ok=True)

    with zipfile.ZipFile(subj_zip, "r") as z:
        z.extractall(subj_dir)

    shutil.copyfile(subj_mat, subj_dir)
