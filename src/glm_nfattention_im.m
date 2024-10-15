function glm_nfattention_im(subject)
% Wrapper for GLM single trial analysis for a specified subject
% This script is tailored for single subject runs but can be adapted for other projects

% Set parameters
stimdur = 50;   % Stimulus duration (adjust as needed) % needs to be the same for all trials
tr = 1;         % TR (Repetition time)

% Add necessary paths
% Define the root path for dependencies
rootpath = '/path/to/matlab/toolbox';
addpath(genpath(rootpath));

%% Define Subject Directory
subjdir = '/path/to/derivatives/stripped_smooth_funcs/'; % Directory containing subject data in BIDS format

% Get the list of subjects by matching 'sub-CISC*' pattern in the directory
fileStruct = dir([subjdir, 'sub-CISC*']);
fileList = {fileStruct.name};

% Get the subject ID from the file list using the provided index
subjectid = fileList{subject};

%% Create output directory for GLM results
outputdir = ['/path/to/outputdir/', subjectid];
mkdir(outputdir);

%% Load fMRI data file for the subject
dataFilePath = ['/path/to/derivatives/stripped_smooth_funcs/', subjectid, '/func/', subjectid, '_task-nflong_run-1_space-MNI152NLin2009cAsym_res-2_desc-preproc_bold_sklstrp_smooth_sklstrp_reduced.nii.gz'];
data = load_untouch_nii(dataFilePath);
data_new = {data.img}; % Convert to cell array

%% Extract Task Name from File Path
slashIndices = strfind(dataFilePath, '/');
dataFileName = dataFilePath(slashIndices(end)+1:end); % Get file name

% Task name extraction
taskNameStart = strfind(dataFileName, '_task-') + 1;
taskNameEnd = strfind(dataFileName, '_space') - 1;
taskName = dataFileName(taskNameStart:taskNameEnd);

%% Load Design Matrix from CSV - needs to be a csv with two columns (face,scene) and 1s on the onset of each stimulus
csvFilename = ['/path/to/glmsingle_regressors/', subjectid, '/face_scene_modified_run06.csv'];
designTable = readtable(csvFilename);

% Extract the design matrix and column names (labels)
design = table2array(designTable);
design_new = {design};
labels = designTable.Properties.VariableNames;

%% Calculate Condition Index
% Initialize condIndex as an empty cell array
condIndex = cell(0, 1);

for i = 1:numel(labels)
    if contains(labels{i}, 'face', 'IgnoreCase', true)
        conditionLabel = 'face';
    elseif contains(labels{i}, 'scene', 'IgnoreCase', true)
        conditionLabel = 'scene';
    else
        conditionLabel = 'unknown';
    end
    
    % Find row indices where the condition is present
    rowIndices = find(design(:, i));

    % Create a structure for each condition with row indices and label
    for j = 1:length(rowIndices)
        condStruct = struct('row', rowIndices(j), 'label', conditionLabel);
        condIndex{end+1} = condStruct;
    end
end

%% Visualize Design Matrix
dm = figure;
imagesc(design_new{1}); 
colormap gray;
xlabel('Conditions');
ylabel('TRs');
xticks(1:size(design_new{1}, 2));
title(['Design matrix for ', subjectid, ' ', taskName]); 
xticklabels(labels);

%% Run GLM Single Trial
clear opt
opt = struct('wantmemoryoutputs', [1 1 1 1]);
[results] = GLMestimatesingletrial(design_new, data_new, stimdur, tr, outputdir, opt);

%% Save the Desgin Matrix figure with subjectid and taskName in the filename
figureFileName = fullfile(outputdir, ['design_matrix_', subjectid, '_', taskName, '.png']);
saveas(dm, figureFileName);


% Define the filename with all the variable
matFilename = fullfile(outputdir, ['design_variables_', subjectid, '_', taskName, '.mat']);

% Save the variables to a .mat file
save(matFilename, 'taskName', 'condIndex', 'subjectid', 'design', 'labels');

why