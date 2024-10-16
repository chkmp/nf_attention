function roi_svm_perm_betweenrun(subject_idx)
    % This script performs ROI-based SVM classification with permutation testing 
    % on fMRI data for a specific subject, utilizing multiple masks.

    % Clear environment, but keep subject_idx
    clearvars -except subject_idx; close all; clc;

    % Set a fixed random seed for reproducibility
    rng(1);  % You can use any integer as the seed
    %for testing on server
    %subject_idx = 1
    
    % Define paths for data directories and scripts
    basepath = '/path/to/project/folder';
    datadirtrain = [basepath, '/IM2_glmsingle/run-05/'];
    datadirtest = [basepath, '/IM2_glmsingle/run-06/'];
    scriptdir = [basepath, '/repos/attention_nf_preprocessing/bin/im2'];

    % Change to the test data directory
    cd(datadirtest);
    
    % Find subject files using dir to match the pattern 'sub-CISC*'
    fl_struct = dir('sub-CISC*');  % Get the directory information
    fl = {fl_struct.name};  % Extract the file names into a cell array
    
    % Add the necessary classifier binaries to the path
    rootpath = '/path/to/project/folder/dependencies_for_cluster/matlab/toolbox';

    % Add the root path and all its subdirectories to the MATLAB path
    addpath(genpath(rootpath));

    % Determine the number of subjects
    n = numel(fl);
    
    % Change to script directory
    cd(scriptdir);
    
    % Get the specific subject ID based on the index
    subjectid = fl{subject_idx};
    
    % Print the subject being processed
    fprintf('Processing subject: %s (Index: %d)\n', subjectid, subject_idx);

    % Load Masks from predefined paths
    mask1 = load_untouch_nii([basepath, '/masks/visfAtlas_faces_places_combined_resampled_binarized.nii.gz']);
    mask1 = mask1.img;

    mask2 = load_untouch_nii([basepath, '/masks/prob_attention_mask_resampled_binarized.nii.gz']);
    mask2 = mask2.img;

    mask3 = load_untouch_nii([basepath, '/masks/MNI152_T1_2mm_brain_mask_resampled_binarized.nii.gz']);
    mask3 = mask3.img;

    % Construct the path to the subject-specific mask
    mask4_path = fullfile(basepath, 'IM2', 'derivatives', 'fmriprep_pilot', subjectid, 'anat', strcat(subjectid, '_space-MNI152NLin2009cAsym_res-2_label-GM_probseg_binarized.nii.gz'));
    mask5_path = fullfile(basepath, 'IM2', 'derivatives', 'first_level', 'simple_contrasts', 'run-01', subjectid, '+.feat', 'thresh_zstat5_temp_occ_bin.nii.gz');
    mask6_path = fullfile(basepath, 'IM2', 'derivatives', 'first_level', 'simple_contrasts', 'run-02', subjectid, '+.feat', 'thresh_zstat5_temp_occ_bin.nii.gz');

    % Load subject-specific GM mask and other masks
    maskHDR = load_untouch_nii(mask4_path);
    mask4 = maskHDR.img;
    mask5 = load_untouch_nii(mask5_path);
    mask5 = mask5.img;
    mask6 = load_untouch_nii(mask6_path);
    mask6 = mask6.img;
    mask7 = load_untouch_nii([basepath, '/masks/VentricleMask_resampled_binarized.nii.gz']);
    mask7 = mask7.img;

     % Store masks in a cell array for looping later
    masks = {mask1, mask2, mask3, mask4, mask5, mask6, mask7};

    % Define mask labels and number of masks
    mask_labels = {'visfAtlas_faces_places_combined_resampled','attention_mask_resampled', 'mni_brain_mask', 'subject_specific_gm_mask', 'video_localizer_mask', 'static_localizer_mask', 'ventricle_mask'};
    nmasks = numel(mask_labels);

    % Define classification labels
    labels = {'face', 'scene'};
    nlabels = numel(labels);

    % Initialize accuracy storage and confusion matrix
    all_accuracy = [];
    accuracy=[];
    pred=[];
    confusion_matrices = zeros(1, nmasks, nlabels, nlabels); % Adjust to 1 for subject level
    npredictions = 4; % Predictions per class, sets the color scale for plots
    wantsinglesubjectplots = 0;

    % Define classifiers and mask labels
    classifiers={@cosmo_classify_nn,...
        @cosmo_classify_naive_bayes,...
        @cosmo_classify_lda};

    % Use SVM classifiers, if present
    svm_name2func = struct();
    svm_name2func.libsvm = @cosmo_classify_libsvm;
    svm_name2func.svm = @cosmo_classify_svm;
    svm_names = fieldnames(svm_name2func);
    for k = 1:numel(svm_names)
        svm_name = svm_names{k};
        if cosmo_check_external(svm_name, false)
            classifiers{end + 1} = svm_name2func.(svm_name);
        else
            warning('Classifier %s skipped because not available', svm_name);
        end
    end

    % Select just libsvm for now
    classifiers = classifiers([4]);
    nclassifiers = numel(classifiers);

    % Initialize arrays to store accuracies
    original_accuracies = zeros(1, nmasks, nclassifiers); % Adjust to 1 for subject level

    % Load in GLMdenoise data
    datatrain = load([datadirtrain, filesep, subjectid, '/TYPED_FITHRF_GLMDENOISE_RR.mat']);
    datatrain = datatrain.modelmd;
    datatest = load([datadirtest, filesep, subjectid, '/TYPED_FITHRF_GLMDENOISE_RR.mat']);
    datatest = datatest.modelmd;

    % Concatenate the data from both runs
    data_combined = cat(4, datatrain, datatest);
    data = data_combined;

    % Load design matrix for training data
    design_file_train = matchfiles([datadirtrain, filesep, subjectid, '/design_variables*']);
    design_train = load(design_file_train{1});
    % Build condition index from design matrix
    condIndextrain = design_train.design;
    condIndextrain(condIndextrain(:, 2) == 1, 2) = 2;
    condIndextrain = sum(condIndextrain, 2);
    condIndextrain(condIndextrain == 0) = [];

    % Load design matrix for testing data
    design_file_test = matchfiles([datadirtest, filesep, subjectid, '/design_variables*']);
    design_test = load(design_file_test{1});
    % Build condition index from design matrix
    condIndextest = design_test.design;
    condIndextest(condIndextest(:, 2) == 1, 2) = 2;
    condIndextest = sum(condIndextest, 2);
    condIndextest(condIndextest == 0) = [];

    % Concatenate condition indices for train and test
    condIndex = cat(1, condIndextrain, condIndextest);

    % Initialize ROI data arrays
    roi_data1 = [];
    roi_data2 = [];
    roi_data3 = [];
    roi_data4 = [];
    roi_data5 = [];
    roi_data6 = [];
    roi_data7 = [];

    % Reshape data for t-test
    data_reshape=permute(data,[4 1 2 3]);
    data_reshape=reshape(data_reshape,size(data,4),[]);

    % Perform the t-test to create an active mask
    [h, p, ci, stats] = ttest(data_reshape);
    activemask = reshape(p < 0.01, [97 115 97]);

    % Loop over trials (columns) in data, extracting ROI data each time
    for i = 1:size(data, 4)
        data_tmp = squeeze(data(:, :, :, i));
        roi_data1(:, i) = double(data_tmp(logical(mask1) & activemask));
        roi_data2(:, i) = double(data_tmp(logical(mask2) & activemask));
        roi_data3(:, i) = double(data_tmp(logical(mask3) & activemask));
        roi_data4(:, i) = double(data_tmp(logical(mask4) & activemask));
        roi_data5(:, i) = double(data_tmp(logical(mask5) & activemask));
        roi_data6(:, i) = double(data_tmp(logical(mask6) & activemask));
        roi_data7(:, i) = double(data_tmp(logical(mask7))); %not constraining ventriclemask
    end

    % Save all constrained masks for potential inspection
    constrainedMasks = {};
    for mm = 1:numel(masks)
        constrainedMasks{mm} = logical(masks{mm}) & activemask;
        maskHDR.img = single(constrainedMasks{mm});
        maskHDR.fileprefix = [basepath, '/IM2_glmsingle/run-06/constrained_masks/', subjectid, '-', mask_labels{mm}];
        save_untouch_nii(maskHDR, [maskHDR.fileprefix]);
    end

    % Targets - list of condition types for CosmoMVPA
    targets = double(condIndex);

    % Count the number of each target
    numTargets(1) = (sum(targets == 1));
    numTargets(2) = (sum(targets == 2));

    % Chunks - Split data into chunks for train/test
    condIndexLength = length(condIndex);
    chunks = repelem(1, condIndexLength)';

    % Set the last 8 elements to chunk 2 if the total length is greater than 8
    if condIndexLength > 8
        chunks((end - 7):end) = 2;
    end

    % Print the resulting chunks vector
    disp(chunks);

    % Group ROI data into a cell array for looping
    roi_data = {roi_data1, roi_data2, roi_data3, roi_data4, roi_data5, roi_data6, roi_data7}; 

    % Little helper function to replace underscores by spaces
    underscore2space = @(x) strrep(x, '_', ' ');

    % Loop over masks for classification
    for m = 1:nmasks
        nVert = size(roi_data{m}, 1); % Find number of voxels in ROI
        
        ds = struct;
        ds.samples = roi_data{m}'; % Pull out ROI data
        ds.sa.targets = targets;
        ds.sa.chunks = chunks;

        mask_label = mask_labels{m};
        
        % Remove constant features
        ds = cosmo_remove_useless_data(ds);
        
        % Print dataset structure
        fprintf('Dataset input:\n');
        cosmo_disp(ds);
        
        % Initialize a struct with fields train_indices and test_indices as cell arrays
        partitions = struct('train_indices', cell(1), 'test_indices', cell(1));

        % Find the indices of chunk 1 for training
        train_indices = find(chunks == 1);
        % Find the indices of chunk 2 for testing
        test_indices = find(chunks == 2);

        % Store the train_indices and test_indices in cell arrays within the struct
        partitions.train_indices{1} = train_indices;
        partitions.test_indices{1} = test_indices;

        % Print the partition indices
        for partition_index = 1:numel(partitions.train_indices)
            fprintf('Partition %d:\n', partition_index);
            fprintf('.train_indices: %s\n', mat2str(partitions.train_indices{partition_index}));
            fprintf('.test_indices: %s\n', mat2str(partitions.test_indices{partition_index}));
        end

        % Loop over classifiers
        for k = 1:nclassifiers
            classifier = classifiers{k};
            
            % Get predictions and accuracy for each fold
            [pred(m, k, :, :), accuracy(m, k)] = cosmo_crossvalidate(ds, classifier, partitions);
            
            % Get confusion matrix for each fold
            confusion_matrix_folds = cosmo_confusion_matrix(ds.sa.targets, squeeze(pred(m, k, :, :)));
            
            % Sum confusion matrices
            confusion_matrix = sum(confusion_matrix_folds, 3);
        end
        confusion_matrices(1, m, :, :) = confusion_matrix; % Adjust to 1 for subject level
    end

    % Format and save accuracy results
    accuracy = accuracy(:);
    all_accuracy(1,:) = accuracy; % Adjust to 1 for subject level

    % Permutation Testing
    nPermutations = 1000; % Number of permutations

    % Loop over permutations
    for permIdx = 1:nPermutations
        disp(['Permutation ', num2str(permIdx)]);

        % Initialize and shuffle targets within each chunk
        shuffledTargets = zeros(size(targets));
        for chunk = 1:2
            chunk_indices = find(chunks == chunk);
            chunk_targets = targets(chunk_indices);
            shuffled_chunk_targets = chunk_targets(randperm(length(chunk_targets)));
            shuffledTargets(chunk_indices) = shuffled_chunk_targets;
        end

        % Store shuffled targets for this permutation
        shuffled_labels(permIdx, :) = shuffledTargets;

        % Initialize permuted accuracy
        permAccuracy = zeros(nmasks, nclassifiers);
        for m = 1:nmasks
            nVert = size(roi_data{m}, 1); % Find number of voxels in ROI
            
            ds = struct;
            ds.samples = roi_data{m}'; % Pull out ROI data
            ds.sa.targets = shuffledTargets; % Use shuffled labels
            ds.sa.chunks = chunks;

            mask_label = mask_labels{m};
            
            % Remove constant features
            ds = cosmo_remove_useless_data(ds);
            
            % Print dataset structure
            fprintf('Dataset input:\n');
            cosmo_disp(ds);

            partitions = struct('train_indices', cell(1), 'test_indices', cell(1));
            % Find the indices of chunk 1 for training
            train_indices = find(chunks == 1);
            % Find the indices of chunk 2 for testing
            test_indices = find(chunks == 2);
            % Store the train_indices and test_indices in cell arrays within the struct
            partitions.train_indices{1} = train_indices;
            partitions.test_indices{1} = test_indices;

            % Print the train and test indices
            fprintf('Permutation %d, Mask %d (%s), Partition %d:\n', permIdx, m, mask_label, 1);
            fprintf('Train indices: %s\n', mat2str(train_indices));
            fprintf('Test indices: %s\n', mat2str(test_indices));
        

            % Loop over classifiers
            for k = 1:nclassifiers
                classifier = classifiers{k};
                
                % Get predictions and accuracy for each fold during permutation
                [pred_perm(m, k, :, :), permAccuracy(m, k)] = cosmo_crossvalidate(ds, classifier, partitions);
                
                % Get confusion matrix for each fold during permutation
                confusion_matrix_folds_perm = cosmo_confusion_matrix(ds.sa.targets, squeeze(pred_perm(m, k, :, :)));
                
                % Sum confusion matrices across folds during permutation
                confusion_matrix_perm = sum(confusion_matrix_folds_perm, 3);
            end
            
            % Store the confusion matrix for this permutation
            confusion_matrices_perm(1, m, :, :, permIdx) = confusion_matrix_perm;
        end

        % Store the permutation accuracies (as before)
        permutation_accuracies(1, :, :, permIdx) = permAccuracy; % Adjust to 1 for subject level
    end

 
    % Original accuracy calculations
    for m = 1:nmasks
        for k = 1:nclassifiers
            original_accuracies(1, m, k) = all_accuracy(1, (m-1)*nclassifiers + k);  % Store the original accuracies
        end
    end
    
    % Permutation accuracy calculations
    for permIdx = 1:nPermutations
        for m = 1:nmasks
            for k = 1:nclassifiers
                all_permutation_accuracies(1, m, k, permIdx) = permutation_accuracies(1, m, k, permIdx); % Accuracy from permutations
            end
        end
    end

    % Compute p-values based on permutation results
    p_values = zeros(1, nmasks);
    for m = 1:nmasks
        %p_values(1, m) = sum(squeeze(all_permutation_accuracies(1, m, 1, :)) >= original_accuracies(1, m, 1)) / nPermutations;
        p_values(1, m) = (sum(squeeze(all_permutation_accuracies(1, m, 1, :)) >= original_accuracies(1, m, 1)) + 1) / (nPermutations + 1);
    end

    % Convert p-values to a table
    p_values_table = array2table(p_values, 'VariableNames', mask_labels, 'RowNames', {subjectid});

    % Prepare classifiers and mask labels for table entry
    classifier=[classifiers;classifiers;classifiers;classifiers;classifiers;classifiers; classifiers];
    classifier=classifier(:);
    mask=mask_labels';

    % Convert original accuracies to a table
    original_accuracies_table = array2table(original_accuracies, 'VariableNames', mask_labels, 'RowNames', {subjectid});

    % Save results
    scriptinfo=[mfilename,'_',date];
    subject_results_dir = fullfile(datadirtest, 'svm_results_1', subjectid);
    save_path = fullfile(subject_results_dir, strcat('roi_svm_perm_results_run-06_1_', subjectid, '.mat'));

    % Create the subject results directory if it doesn't exist
    if ~exist(subject_results_dir, 'dir')
        mkdir(subject_results_dir);
    end

    % Save specified variables
    save(save_path, 'original_accuracies_table', 'all_permutation_accuracies', 'p_values_table', 'confusion_matrices','confusion_matrices_perm', 'scriptinfo', 'fl', 'shuffled_labels');

    % Display a message confirming the save operation
    disp(['Results saved in ', save_path]);

end