from psychopy import visual, core, event, gui
import pandas as pd
import os 
import csv
import pyglet
from psychopy.hardware import keyboard
from datetime import datetime
import json
import glob
from pygame.locals import*

####### SET UP PATHS####################################################

###### CSV #############################################################

def create_csv(participant_info, beh_path, task_name):
    # convert participant_info[0] to an integer
    sub_num_int = int(participant_info[0])
    sub_ses_int = int(participant_info[1])
    sub_run_int = int(participant_info[2])
    # format the integer as a zero-padded two-digit string
    sub_num = f"sub-{sub_num_int:02d}"
    ses_num = f"ses-{sub_ses_int:02d}"
    run_num = f"run-{sub_run_int:02d}"

    header = ['subject_num', 'session', 'run', 'dimension', 'scale_low','scale_high', 'response', 'response_time', 'flip_time']
    #date_string = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{sub_num}_{ses_num}_{run_num}_{participant_info[3]}_{task_name}-esq_beh.csv"
    full_esq_response_csv = os.path.join(beh_path, filename)
    return full_esq_response_csv, header

def _write_data_to_csv(participant_info, dimension, scale_low, scale_high, response, response_time, flip_time, csv_info):
    full_esq_response_csv, header = csv_info
    row = [participant_info[0], participant_info[1], participant_info[2], dimension, scale_low, scale_high, response, response_time, flip_time]
    with open(full_esq_response_csv, mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:
            writer.writerow(header)
        writer.writerow(row)


def thought_probe(participant_info, starttime, win, csv_info, task_name):
    """
    Input: Experience sampling dataframe
    Present thought probes seqentially with a sliding response scale.
    Responses should be returned and passed to _csv_writer 
    """
    full_esq_response_csv, header = csv_info

    repos_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    
    esqs = os.path.join(repos_path, 'data/esqs')
    esqname = '14_item_experience_sampling_questions_final.csv'
    full_esq_path = os.path.join(esqs, esqname)
    df = pd.read_csv(full_esq_path)


    # TODO: run init_csv func in main script to access writer object 

    # create rating scale for user to rate thought probes.
    ratingScale = visual.RatingScale(win, low=0, high=10, markerStart=5.0,precision=10,
                leftKeys='r', rightKeys='y', acceptKeys='b', scale = None, labels = None, acceptPreText = 'Press key', tickMarks = [1,10])

    # create text stimulus for thought probe presentation. 
    QuestionText = visual.TextStim(win, color = [-1,-1,-1], alignHoriz = 'center', alignVert= 'top', pos =(0.0, 0.3), height=30, units='pix')
    # create text stimuli for low and high scale responses. 
    Scale_low = visual.TextStim(win, color ='black', pos=(-200, -150), height=30, units='pix')
    Scale_high = visual.TextStim(win, color ='black', pos=(200, -150), height=30, units='pix')



    # shuffle dataframe rows to randomly present questions
    #df = df.sample(frac=1).reset_index(drop=True)
    if task_name == 'training':
        df = df.head(14)  # Take the first 14 questions
        df = df.sample(frac=1).reset_index(drop=True)  # Shuffle the questions
    elif task_name == 'feedback':
        df_first_14 = df.head(14)  # Take the first 14 questions
        df_last_4 = df.tail(4)  # Take the last 4 questions
        df_first_14 = df_first_14.sample(frac=1).reset_index(drop=True)  # Shuffle the first 14 questions
        df = pd.concat([df_first_14, df_last_4], ignore_index=True)



    # Loop through each question 
    for idx in range(len(df)):    

        # extract relevent question information
        dimension = df.loc[idx].dimension
        question = df.loc[idx].question
        scale_low = df.loc[idx].scale_low
        scale_high = df.loc[idx].scale_high

        ratingScale.noResponse = True

        # section for keyboard handling. 
        key = pyglet.window.key
        keyState = key.KeyStateHandler()
        win.winHandle.activate() # to resolve mouse click issue. 
        win.winHandle.push_handlers(keyState)
        pos = ratingScale.markerStart
        inc = 0.1 

        kb = keyboard.Keyboard()
        
        # while there is no response from user, present thought probe and scale.
        while ratingScale.noResponse:

            # use 1 and 2 keys to move left and right along scale. 
            if keyState[K_r] is True:
                pos -= inc
            elif keyState[K_y] is True:
                pos += inc
            if pos > 10: 
                pos = 10
            elif pos < 1:
                pos = 1
            ratingScale.setMarkerPos(pos)

            # set text of probe and responses 
            QuestionText.setText(question)
            Scale_low.setText(scale_low)
            Scale_high.setText(scale_high)

            # draw text stimuli and rating scale
            QuestionText.draw()
            ratingScale.draw() 
            Scale_low.draw()
            Scale_high.draw()

            # store response using getRating function
            response = ratingScale.getRating()
           
            fliptime = win.flip()
           
        # reset marker to middle of scale each time probe is presented. 
        ratingScale.setMarkerPos((0.5))
        

        response_time = kb.clock.getTime()

        kb.clearEvents() # clear keyboard buffer so first trial doensn't detect presses from here 
        _write_data_to_csv(participant_info, dimension, scale_low, scale_high, response, response_time, fliptime, csv_info)


  
    
