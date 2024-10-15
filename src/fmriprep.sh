#!/bin/bash

# Script to preprocess fMRI data using fmriprep in a singularity container
# Requires a configured job scheduler supporting SGE (Sun Grid Engine) environment variables

# Job settings for the scheduler
#$ -N pilot01            # Job name
#$ -pe openmp 5          # Parallel environment (number of parallel threads)
#$ -o /path/to/logs      # Output log directory (adjust as needed)
#$ -e /path/to/logs      # Error log directory (adjust as needed)
#$ -l m_mem_free=8G      # Memory requirement per core
#$ -l 'h=!node001&!node069&!node072&!node076&!node077' # Nodes to exclude
#$ -t 1                  # Task ID (for single subject use 1, adjust for multiple subjects e.g. 1-10)
#$ -tc 10                # Maximum simultaneous tasks

# Directories (replace these with the appropriate paths)
DATA_DIR=/path/to/Nifti                   # Directory containing Nifti files (BIDS format)
SCRATCH_DIR=/path/to/fmriprep_work_dir     # Working directory for fmriprep
OUT_DIR=/path/to/fmriprep_derivatives      # Output directory for fmriprep derivatives, i.e. where to output pre-processing
LICENSE=/path/to/license.txt               # Freesurfer license file

# Path to the fmriprep singularity image
FMRIPREP_IMG=/path/to/fmriprep_image.simg  # fmriprep singularity image (adjust path if needed)

# Move to the data directory to get the list of subjects
cd "${DATA_DIR}" || exit

# Obtain list of subject directories (assuming 'sub-*' directories in BIDS format)
SUBJLIST=$(find sub-* -maxdepth 0 -type d) 
# Get the number of subjects as a sanity check
len=${#SUBJLIST[@]}
echo "Number of subjects = $len"

# Return to the home directory for job execution
cd "${HOME}"

# Display the current task ID assigned by the job scheduler
echo "This is the task id $SGE_TASK_ID"

# Calculate index for the subject array (subtracting 1 from SGE_TASK_ID for zero-indexing)
i=$((SGE_TASK_ID - 1))
echo "This is i = $i"

# Define the subject for this task
arr=($SUBJLIST)
SUBJECT=${arr[i]}
echo "Processing subject: $SUBJECT"

# Run fmriprep using the singularity container
singularity run --cleanenv \
    -B "${DATA_DIR}:/data" \
    -B "${OUT_DIR}:/out" \
    -B "${SCRATCH_DIR}:/wd" \
    -B "${LICENSE}:/license" \
    "${FMRIPREP_IMG}" \
    --skip_bids_validation \
    --participant-label "${SUBJECT}" \
    --omp-nthreads 5 --nthreads 5 --mem_mb 30000 \
    --low-mem \
    --output-spaces MNI152NLin2009cAsym:res-2 fsLR:den-32k \
    --fs-license-file /license \
    --work-dir /wd \
    --cifti-output 91k \
    /data /out/ participant

echo "Processing for $SUBJECT completed"

# Notes:
# - 'output-spaces' flag requests specific brain spaces and resolutions.
# - '--fs-license-file' points to the FreeSurfer license, necessary for some outputs.
