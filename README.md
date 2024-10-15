# nf_attention

Script repository for "Attention training with real-time fMRI neurofeedback: an optimised protocol" paper.

- **fmriprep.sh**  
  Script to preprocess fMRI data using fmriprep in a singularity container.

- **glm_nfattention_im.m**  
  Wrapper for GLM single trial analysis for a specified subject. Needs to be called with `glm_attention_im_cluster.sh`.

- **glm_nfattention_im_cluster.sh**  
  Job script to run `glm_nfattention_im.mat` function on a compute cluster using SGE.
  
- **gm_mask.py**  
  Script to create subject-specific gray matter mask from fmriprep outputs

