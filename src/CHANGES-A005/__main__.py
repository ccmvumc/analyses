import zipfile
from glob import glob
import os, shutil, sys


def _prep(input_dir, output_dir):
    subjects = [x for x in os.listdir(input_dir) if os.path.isdir(f'{input_dir}/{x}')]

    for subj in sorted(subjects):
        subj_dir = f'{output_dir}/{subj}'

        if os.path.exists(subj_dir):
            print(f'Already prepped:{subj_dir}')
            continue

        print(f'Prep {subj}')

        subj_mat = glob(f'{input_dir}/{subj}/*/*/*/CONN/conn_project.mat')[0]
        subj_zip = glob(f'{input_dir}/{subj}/*/*/*/CONN/conn_project.zip')[0]

        # Extract from zip in inputs to subject folder in outputs
        os.makedirs(subj_dir, exist_ok=True)
        with zipfile.ZipFile(subj_zip, "r") as z:
            z.extractall(subj_dir)

        # Copy the mat to same folder
        shutil.copy(subj_mat, subj_dir)


if __name__ == '__main__':
    print('Prep')
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    _prep(input_dir, output_dir)
    print('DONE!')

# run merge.m in matlab command line where conn toolbox is installed
