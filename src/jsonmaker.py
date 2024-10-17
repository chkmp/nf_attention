#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import glob
import random
import json
from psychopy import gui
# JSON maker. This script creates a dictionary of image file names depending on participant group, to be read and used by training.py and feedback.py during stimulus presentation.

# define the options for the drop-down menu
options = ['male-indoor', 'male-outdoor', 'female-indoor', 'female-outdoor']

# create a dialog box to get subject ID and group
dlg = gui.Dlg(title="Experiment Information")
dlg.addField('Subject ID:')
dlg.addField('Group:', choices=options)
dlg.addField('Counterbalance:', choices=['1', '2'])
# show the dialog box and wait for user input
ok_data = dlg.show()

subid = ok_data[0]
group = ok_data[1]
counterb =ok_data [2]
print('counterb',counterb)


# Define number of training and feedback runs for each session
sessions_info = {
    '1': {
        'training_runs': 2,
        'feedback_runs': 2,
    },
}

block_order_training_mini= [1, 1, 2, 1, 2, 2, 2, 1, 1, 2, 2, 1, 2, 1, 1, 2, 1, 2, 2, 2, 1, 2, 1, 2, 1, 2, 1, 1, 1, 1, 2, 2, 1, 2, 1, 2, 1, 2, 1, 1, 1, 2, 2, 2, 2, 1, 2, 1, 1, 2, 1, 2, 1, 2, 1, 1, 1, 2, 2, 2] #final  TR=1s
block_order_training_long= [1, 2, 2, 1, 1, 2, 1, 2] 
block_order_feedback= [1, 2, 2, 1, 1, 2, 1, 2] 
n_trials_training_mini = 6
n_trials_training_long = 50 
n_trials_feedback = 50

def jsonmaker(subid, session, run, group, training_or_feedback, block_order, n_trials, non_lure_trials, lure_trials):
    #print(f'block_order: {block_order}')
    repos_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    repo_path = os.path.join(repos_path, "nf_attention_imaging")
    stimdirs = os.path.join(repo_path,'data/stimuli')
    jsondict = {}
    # loop over each block 
    for i, block in enumerate(block_order):
        attended_imgs = []
        attended_lure_imgs  = []
        unattended_imgs = []
        unattended_lure_imgs = []

        block_nr = i+1
        # use modulus operator to switch between attended catagories 
        # this will switch between the catagories, 0 and 1 each loop 
        if block == 1:
            attended_cat = group.split('-')[0]
            unattended_cat = group.split('-')[1]
            print(f'attended_cat: {attended_cat}, unattended_cat: {unattended_cat}')

        elif block == 2:
            attended_cat = group.split('-')[1]
            unattended_cat = group.split('-')[0]
            print(f'attended_cat: {attended_cat}, unattended_cat: {unattended_cat}')

        
        jsondict[f'block_{block_nr}_info']=[block_nr, attended_cat, unattended_cat]

        # create attended catagory lure list and add to attended images list 
        if attended_cat == 'female':
            attended_cat_lure = 'male'
        elif attended_cat == 'male':
            attended_cat_lure = 'female'
        elif attended_cat == 'indoor':
            attended_cat_lure = 'outdoor'
        elif attended_cat == 'outdoor':
            attended_cat_lure = 'indoor'
        print('ATTENDED_CAT', attended_cat)
        print('ATTENDED_CAT_LURE',attended_cat_lure)
            
        if unattended_cat == 'female':
            unattended_cat_lure = 'male'
        elif unattended_cat == 'male':
            unattended_cat_lure = 'female'
        elif unattended_cat == 'indoor':
            unattended_cat_lure = 'outdoor'
        elif unattended_cat == 'outdoor':
            unattended_cat_lure = 'indoor'
        print('UNATTENDED_CAT', unattended_cat)
        print('UNATTENDED_CAT_LURE',unattended_cat_lure)

        # create attended_cat stimuli list 
        attended_dir = os.path.join(stimdirs, attended_cat)
        attended_imgs = glob.glob(os.path.join(attended_dir,'*.jpg'))
        random.shuffle(attended_imgs)
        attended_imgs = attended_imgs[:round(n_trials * non_lure_trials)] # ensure that 90% of trials are not lure
        print('attended_cat_imgs', attended_imgs)
        #print(f'Number of attended imgs: {len(attended_imgs)}')

        # create attended catagory stimuli list 
        attended_dir_lure = os.path.join(stimdirs, attended_cat_lure)
        attended_lure_imgs = glob.glob(os.path.join(attended_dir_lure,'*.jpg'))
        random.shuffle(attended_lure_imgs)
        attended_lure_imgs = attended_lure_imgs[:round(n_trials * lure_trials)] # ensure 10% of trials are lure 
        print('attended_lure_imgs', attended_lure_imgs)
        #print(f'Number of attended lure imgs: {len(attended_lure_imgs)}')

        # join attended images lists (lure and non lures)
        attended_paths = attended_imgs + attended_lure_imgs 
        #random.shuffle(attended_paths)
        assert len(attended_paths) == n_trials
        print('attended_paths', attended_paths)


        # Now do the same for the unnattended 
        # create attended catagory stimuli list 
        unattended_dir = os.path.join(stimdirs, unattended_cat)
        unattended_imgs = glob.glob(os.path.join(unattended_dir,'*.jpg'))
        random.shuffle(unattended_imgs)
        unattended_imgs = unattended_imgs[:round(n_trials * non_lure_trials)] 
        print('unattended_imgs', unattended_imgs)
        #print(f'Number of unattended  imgs: {len(unattended_imgs)}')

        # create attended catagory stimuli list 
        unattended_dir_lure = os.path.join(stimdirs, unattended_cat_lure)
        unattended_lure_imgs = glob.glob(os.path.join(unattended_dir_lure,'*.jpg'))
        # shuffle list and choose 20 
        random.shuffle(unattended_lure_imgs)
        unattended_lure_imgs=unattended_lure_imgs[:round(n_trials * lure_trials)]
        print('unattended_lure_imgs', unattended_lure_imgs)
        #print(f'Number of unattended lure imgs: {len(unattended_lure_imgs)}')


        # join attended images lists (lure and non lures)
        unattended_paths = unattended_imgs + unattended_lure_imgs 
        #random.shuffle(unattended_paths)
        assert len(unattended_paths) == n_trials
        print('unattended_paths', unattended_paths)
        #assert len(unattended_paths) == n_trials

        # join attennded and unattended paths in parralel 2x200 
        img_pairs = []
        for attended_img, unattended_img in zip(attended_paths, unattended_paths):
            img_pairs.append([os.path.basename(attended_img), os.path.basename(unattended_img)])
        random.shuffle(img_pairs)
        
        jsondict[f'block_{block_nr}_order'] = img_pairs 
        f = os.path.join(repo_path,f'data/jsons/sub-{subid}_ses-{session}_run-{run}_group-{group}_task-{training_or_feedback}.json')
    with open(f, 'w') as fp:
        json.dump(jsondict, fp)

# Loop over all sessions and runs to create JSON files
for session_name, session_info in sessions_info.items():
    n_training_runs = session_info['training_runs']
    n_feedback_runs = session_info['feedback_runs']
    
    for run in range(1, n_training_runs+1):
        if run ==1 and counterb =='1':
            jsonmaker(subid, session_name, 1, group, 'training', block_order_training_mini, n_trials_training_mini, 0.6, 0.4)
        elif run ==2 and counterb =='1':
            jsonmaker(subid, session_name, 2, group, 'training', block_order_training_long, n_trials_training_long, 0.9, 0.1)    
        if run ==1 and counterb =='2':
            jsonmaker(subid, session_name, 1, group, 'training', block_order_training_long, n_trials_training_long, 0.9, 0.1)
        elif run ==2 and counterb =='2':
            jsonmaker(subid, session_name, 2, group, 'training', block_order_training_mini, n_trials_training_mini, 0.6, 0.4)    

    for run in range(1, n_feedback_runs+1):
        jsonmaker(subid, session_name, run, group, 'feedback', block_order_feedback, n_trials_feedback, 0.9, 0.1)





















