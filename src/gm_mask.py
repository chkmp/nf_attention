import os
import nibabel as nib
import numpy as np

# Script to create subject-specific gray matter mask from fmriprep outputs

# Define the base directory
base_dir = '/path/to/your/fmriprep/output/directory'  # Change this to your actual directory

# Find all subject directories
subject_dirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]

# Iterate over each subject directory
for subject_dir in subject_dirs:
    subject_id = subject_dir.split('-')[-1]
    anat_path = os.path.join(base_dir, subject_dir, 'anat', f'sub-{subject_id}_space-MNI152NLin2009cAsym_res-2_label-GM_probseg.nii.gz')

    # Check if the anatomy file exists for the current subject
    if os.path.exists(anat_path):
        print(f'Processing subject {subject_id}')

        # Load the anatomical image
        img = nib.load(anat_path)
        data = img.get_fdata()

        # Binarize the image (convert to binary mask where GM > 0 is 1)
        binarized_data = np.where(data > 0, 1, 0)

        # Create a new NIfTI image with the binarized data
        binarized_img = nib.Nifti1Image(binarized_data, img.affine, img.header)

        # Save the binarized image
        binarized_path = os.path.join(base_dir, subject_dir, 'anat', f'sub-{subject_id}_space-MNI152NLin2009cAsym_res-2_label-GM_probseg_binarized.nii.gz')
        nib.save(binarized_img, binarized_path)

        print(f'Binarized image saved: {binarized_path}')
    else:
        print(f'Anatomy file not found for subject {subject_id}')
