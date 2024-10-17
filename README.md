# nf_attention

Script repository for "Attention training with real-time fMRI neurofeedback: an optimised protocol" paper.

Collaborators: Will Strawson, Chris Racey

- **fmriprep.sh**  
  Script to preprocess fMRI data using fmriprep in a singularity container.

- **glm_nfattention_im.m**  
  Wrapper for GLM single trial analysis for a specified subject. Needs to be called with `glm_attention_im_cluster.sh`.

- **glm_nfattention_im_cluster.sh**  
  Job script to run `glm_nfattention_im.m` function on a compute cluster using SGE.
  
- **gm_mask.py**  
  Script to create subject-specific gray matter mask from fmriprep outputs.

- **roi_svm_perm_withinrun.m**  
  This script performs ROI-based SVM classification (within-run cross-fold validation) with permutation testing on fMRI data for a specific subject, utilizing multiple masks. Needs to be called with `roi_svm_perm_cluster.sh`.

- **roi_svm_perm_betweenrun.m**  
  This script performs ROI-based SVM classification (training on one run, testing on an independent) with permutation testing on fMRI data for a specific subject, utilizing multiple masks. Needs to be called with `roi_svm_perm_cluster.sh`.

- **roi_svm_perm_cluster.sh**  
  Job script to run `roi_svm_perm_*run.m` functions on a compute cluster using SGE.

- **blender.py**  
  This script is to create blended image stimuli for Experiment 1.

- **trimmed_means_anovas.r**  
  This script is to run the trimmed means anovas for run comparisons.

- **feedback.py**  
  Script for stimulus presentation during feedback runs.

