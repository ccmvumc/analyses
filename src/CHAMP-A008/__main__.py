import zipfile
from glob import glob
import os, shutil, sys


def _prep(input_dir, output_dir):
    subjects = [x for x in os.listdir(input_dir) if os.path.isdir(f'{input_dir}/{x}')]

    for subj in sorted(subjects):
        print(f'Prep {subj}')

        try:
            subj_mat = glob(f'{input_dir}/{subj}/assessors/*/*/CONN/conn_project.mat')[0]
        except:
            try:    
                subj_mat = glob(f'{input_dir}/{subj}/assessors/*/CONN/conn_project.mat')[0]
            except:
                print(f'No conn_project.mat for subject:{subj}')
                continue

        try:
            subj_zip = glob(f'{input_dir}/{subj}/assessors/*/*/CONN/conn_project.zip')[0]
        except:
            try:
                subj_zip = glob(f'{input_dir}/{subj}/assessors/*/CONN/conn_project.zip')[0]
            except:
                print(f'No conn_project.zip for subject:{subj}')
                continue

        # Extract from zip in inputs to subject folder in outputs
        subj_dir = f'{output_dir}/{subj}'
        os.makedirs(subj_dir, exist_ok=True)
        with zipfile.ZipFile(subj_zip, "r") as z:
            z.extractall(subj_dir)

        # Copy the mat to same folder
        shutil.copy(subj_mat, subj_dir)


if __name__ == '__main__':
    if False:
        print('Prep')
        _prep(sys.argv[1], sys.argv[2])

    print('DONE!')
