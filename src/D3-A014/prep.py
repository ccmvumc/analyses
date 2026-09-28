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

        sessions = [x for x in os.listdir(f'{input_dir}/{subj}') if os.path.isdir(f'{input_dir}/{subj}/{x}')]

        for sess in sorted(sessions):
            sess_dir = f'{output_dir}/{subj}/{sess}'

            try:
                sess_mat = glob(f'{input_dir}/{subj}/{sess}/assessors/*/conn_project.mat')[0]
            except:
                print(f'No conn_project.mat for subject/session:{subj}/{sess}')
                continue

            try:
                sess_zip = glob(f'{input_dir}/{subj}/{sess}/assessors/*/conn_project.zip')[0]
            except:
                print(f'No conn_project.zip for subject/session:{subj}/{sess}')
                continue

            # Extract from zip in inputs to outputs folder
            os.makedirs(sess_dir, exist_ok=True)
            try:
                with zipfile.ZipFile(sess_zip, "r") as z:
                    z.extractall(sess_dir)
            except Exception as err:
                print(f'Bad zip file:{sess_zip}')
                continue

            # Copy the mat to same folder
            shutil.copy(sess_mat, sess_dir)


if __name__ == '__main__':
    print('Prep')
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    _prep(input_dir, output_dir)
    print('DONE!')
