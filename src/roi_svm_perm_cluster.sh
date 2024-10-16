#!/bin/bash
#$ -N roi_svm_perm_run05 # job name 
#$ -pe openmp 5 # parralel environment #how many parallel enviroments
#$ -o /path/to/logs # need to be a path? #where to store the -o outputs and -e outputs. put it in the cisc volumes or in my cluster home directory
#$ -e /path/to/logs
#$ -l m_mem_free=8G 
#$ -l 'h=!node001&!node069&!node072&!node076&!node077&!node019' # nodes NOT to use 
#$ -t 1-10 #This sets SGE_TASK_ID! Set it equal to number of subjects #you can put 1 or 1-n
#$ -tc 25 #maximum tasks running simultaeneously .

DATA_DIR=/path/to/project/data/ #preprocessed derivatives directory #same as datadir in .m script
SCRIPT_DIR=/path/to/script/directory/ #where to run scripts from #same as scriptdir in m. script

module add matlab

cd ${SCRIPT_DIR}

echo This is the task id $SGE_TASK_ID

matlab -nodisplay -nosplash -nodesktop -r "roi_svm_perm_*($SGE_TASK_ID) ;exit;" # wildcard needs to set this as the same name as the function (either betweenrun or withinrun)

echo Done
