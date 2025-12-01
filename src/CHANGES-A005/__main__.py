import zipfile
from glob import glob
import os, shutil, sys

from CONN import covariates2mat, prep, merge_projects


if __name__ == '__main__':
    print('Prep')
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    # Copy conn .mat file to output dir and unzips .zip to same dir
    prep(input_dir, output_dir)
    print('DONE!')

    # if covariates file found, convert to mat and save to outputs
    if os.path.exists(f'{input_dir}/covariates.csv'):
        covariates2mat(
            f'{input_dir}/covariates.csv',
            f'{output_dir}/covariates.mat'
        )

    # contrasts?

    # run merge.m in matlab command line where conn toolbox is installed
    merge_projects(f'{output_dir}/', f'{output_dir}/CONN')

    # write subjects.txt

