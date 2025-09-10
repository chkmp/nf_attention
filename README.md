# nf_attention

Script repository for "Attention training with real-time fMRI neurofeedback: an optimised protocol" paper.

Collaborators: Will Strawson, Chris Racey, Michael Luehrs, Andreas Bressler

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

- **lmms.r**  
  This is an example script of the code used to run the LMMs for run comparisons (i.e., glmmTMB(accuracy ~ design * ROI + (1 | sub), family = beta_family(link = "logit"))). 

- **feedback.py**  
  Script for stimulus presentation during feedback runs.

- **functional_localizer_static.py**  
  Script for stimulus presentation for the static functional localizer.

- **functional_localizer_video.py**  
  Script for stimulus presentation for the dynamic functional localizer.

- **training.py**  
Script for stimulus presentation during training runs.

- **jsonmaker.py**  
Script to create the json files for `training.py` and `feedback.py`.

- **esqs.py**  
Script for thought probs, gets called within `training.py` and `feedback.py`.
