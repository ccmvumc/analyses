import numpy as np
import nibabel as nib
from nilearn.maskers import NiftiLabelsMasker
from nilearn import datasets


def extract(image_file, text_file):
    # Load atlas
    schaefer_atlas = datasets.fetch_atlas_schaefer_2018(n_rois=200)

    # Initialize the NiftiLabelsMasker
    masker = NiftiLabelsMasker(labels_img=schaefer_atlas.maps)

    # Load image
    nib_image = nib.load(image_file)

    # Extract timeseries
    timeseries = masker.fit_transform(nib_image)

    # Save text file separated by two spaces to match output from FSL fslmeants
    np.savetxt(
        text_file,
        timeseries.T,
        fmt="%.8f",
        delimiter="  ",
    )


if __name__ == '__main__':
    import sys

    extract(
        sys.argv[1], 
        sys.argv[2]
    )
    print('DONE!')
