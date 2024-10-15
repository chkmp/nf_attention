#!/bin/bash

# Job script to run glm_nfattention_im function on a compute cluster using SGE

# Job settings for the scheduler
#$ -N glm_nfattention_im          # Job name
#$ -pe openmp 5                          # Number of parallel threads (adjust as needed)
#$ -o /path/to/logs                      # Directory for output logs (adjust to preferred directory)
#$ -e /path/to/logs                      # Directory for error logs (adjust to preferred directory)
#$ -l m_mem_free=8G                      # Memory requirement per core
#$ -l 'h=!node001&!node069&!node072&!node076&!node077&!node019' # Nodes to exclude
#$ -t 1-10                               # Task array (adjust range to match number of subjects)
#$ -tc 25                                # Maximum simultaneous tasks

# Set directories (update these to match your data and script locations)
DATA_DIR=/path/to/derivatives/stripped_smooth_funcs   # Directory containing preprocessed derivatives
SCRIPT_DIR=/path/to/your/script  # Directory containing MATLAB script

# Load MATLAB module (adjust as needed)
module add matlab

# Navigate to script directory
cd "${SCRIPT_DIR}"

# Display task ID for verification
echo "This is the task id $SGE_TASK_ID"

# Run MATLAB script with task ID as an argument
matlab -nodisplay -nosplash -nodesktop -r "glm_nfattention_im($SGE_TASK_ID); exit;"

echo "Processing completed for task id $SGE_TASK_ID"
