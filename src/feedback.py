#Script for stimulus presentation during feedback runs

# Import necessary libraries
from psychopy import visual, core, event, gui
import random
import os 
import csv
from datetime import datetime
import json
import glob
from PIL import Image, ImageDraw
import numpy as np
import math
from utils.esqs import create_csv, thought_probe 
#####TBV THINGS#########
from expyriment.io.extras import TbvNetworkInterface
from expyriment.design.extras import StimulationProtocol
HOST = "10.179.243.75" #SCANNER
#HOST = "139.184.171.100" # WORK PC TEST 
PORT = 55555  # set in TBV, 55555 default
TR = 1000  # in ms
tbv = TbvNetworkInterface(HOST, PORT, timeout=TR/2) 

# BV prt protocol
protocol = StimulationProtocol("time")
protocol.add_condition("rest")
protocol.add_condition("face")
protocol.add_condition("scene")
protocol.add_condition("instructions")

######GUI##########################################################

# Create a dialog box to collect participant information
dlg = gui.Dlg(title="Participant Information")
dlg.addField('subject')
dlg.addField('session', choices=['1', '2', '3', '4'])
dlg.addField('run', choices=['1', '2', '3', '4'])
dlg.addField('group', choices=['male-indoor', 'male-outdoor', 'female-indoor', 'female-outdoor'])

participant_info = dlg.show()

# convert participant_info[0] to an integer
sub_num_int = int(participant_info[0])
sub_ses_int = int(participant_info[1])
sub_run_int = int(participant_info[2])
# format the integer as a zero-padded two-digit string
sub_num = f"sub-{sub_num_int:02d}"
ses_num = f"ses-{sub_ses_int:02d}"
run_num = f"run-{sub_run_int:02d}"
# If the user clicks "Cancel", exit the script
if not dlg.OK:
    core.quit()

# Extract participant info from dictionary
subject = participant_info[0]
session = participant_info[1]
run = participant_info[2]
group = participant_info[3]

#####SET UP WINDOW #################################################

# Set up window and fixation cross
win = visual.Window(size=(800, 600), fullscr=True, units='pix', winType='pyglet')
fixation = visual.TextStim(win, text='+', pos=(0, 0), color='white')

#### FIND JSON ################################################

repos_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
repo_path = os.path.join(repos_path, "nf_attention_imaging")
jsons = os.path.join(repo_path, 'data/jsons')
beh_path =  os.path.join(repo_path,"data", "responses", f"{sub_num}", f"{ses_num}")
# Create the directory if it does not exist
if not os.path.isdir(beh_path):
    os.makedirs(beh_path)
protocol_path = os.path.join(repo_path,"data", "protocols", f"{sub_num}", f"{ses_num}")
# Create the directory if it does not exist
if not os.path.isdir(protocol_path):
    os.makedirs(protocol_path)

# Construct filename and full path to JSON file
filename = f'sub-{subject}_ses-{session}_run-{run}_group-{group}_task-feedback.json'
json_path = os.path.join(jsons, filename)

#### SET UP STIMULI ################################################

# define the relative path to the stimuli
repos_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
repo_path = os.path.join(repos_path, "nf_attention_imaging")
stim_path = os.path.join(repo_path,'data/stimuli/')

csv_info = create_csv(participant_info, beh_path, 'feedback')

##### SET UP EXPERIMENT VARIABLES ###################################

image_duration = 1
fixation_duration = 6 #between blocks fixation, iti 6 for 50 trial
fixation_null_duration = 56 #for null blocks, null here needs to be block duration + iti
fixation_start_duration = 10 #10 volumes of fix
fixation_end_duration = 10 #10 volumes of fix
fixation_instr_duration = 1

null_blocks = [2,4]


#### INSTRUCTIONS ####################################################

# Display instructions
group_instr = group.split('-')
welcome = visual.TextStim(win, text=f'In this task you will be shown overlapping images of faces and scenes and you will need to attend either the face or the scene, depending on the instructions. All the images will have a colour border that will vary between shades of green and red.\n\n Your aim is to make the border green. \n\n When the instruction says "face", focus your attention to the face to turn the border green.  \n\n When the instruction says "scene", focus your attention to the scene to turn the border green.\n\n The greener the border, the better you are performing.\n\n If the border turns to a shade of red, try and focus your attention back to the instructed category.', height=20, units='pix')
welcome.draw()
win.flip()
event.waitKeys(keyList='space')
win.flip()

###### CSV #############################################################

header = ['subject_num', 'session', 'run', 'group', 'block_number','target_category', 'target_subcategory', 'stimulus_onset', 'stimulus_duration', 'blended_stimuli', 'response', 'response_time', 'accuracy']

date_string = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"{sub_num}_{ses_num}_{run_num}_{participant_info[3]}_task-feedback_beh.csv" #csv
textfilename = f"{sub_num}_{ses_num}_{run_num}_{participant_info[3]}_task-feedback_beh.txt" #text for terminal printing
full_csv_path = os.path.join(beh_path, filename)
full_txt_path = os.path.join(beh_path, textfilename)

def write_data_to_csv(participant_info, block_number,target_category, target_subcategory, stimulus_onset, stimulus_duration, blended_stimuli, response, response_time, accuracy):
    row = [sub_num, ses_num, run_num, participant_info[3], block_number, target_category, target_subcategory, stimulus_onset, stimulus_duration,blended_stimuli, response, response_time, accuracy]
    with open(full_csv_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:
            writer.writerow(header)
        writer.writerow(row)

#######ADJUSTED IMAGE AND FIXATION DURATION ############################################

# Define a function to calculate the adjusted video duration based on onset time
def get_adjusted_image_duration(image_start_time, target_interval=1):
    time_elapsed = image_start_time % target_interval
    adjusted_duration = image_duration - time_elapsed
    return adjusted_duration

def get_adjusted_fixation_duration(fixation_start_time, fixation_duration, target_interval=1):
    time_elapsed = fixation_start_time % target_interval
    adjusted_duration = fixation_duration - time_elapsed
    return adjusted_duration

#############BLEND IMAGES##############################################

def get_border_color(alpha_rect):
    if 0 <= alpha_rect <= 1:
        white_color = (255, 255, 255, int(255 * (1 - alpha_rect)))
        green_color = (0, 255, 0, int(255 * alpha_rect))
    elif -1 <= alpha_rect < 0:
        white_color = (255, 255, 255, int(255 * (1 + alpha_rect)))
        red_color = (255, 0, 0, int(255 * (-alpha_rect)))
    else:
        raise ValueError("Invalid alpha_rect value")

    if 0 <= alpha_rect <= 1:
        border_color = Image.alpha_composite(Image.new('RGBA', (1, 1), white_color), Image.new('RGBA', (1, 1), green_color)).getpixel((0, 0))
    else:
        border_color = Image.alpha_composite(Image.new('RGBA', (1, 1), white_color), Image.new('RGBA', (1, 1), red_color)).getpixel((0, 0))

    return border_color

def blend_images_with_rectangle(image1_filename, image2_filename, alpha_im=0.5, alpha_rect=0.8):
    # Determine the subdirectories to search
    category_im1 = ''
    if 'M' in image1_filename:
        category_im1 += 'male/'
    elif 'F' in image1_filename:
        category_im1 += 'female/'
    if 'I' in image1_filename:
        category_im1 += 'indoor/'
    elif 'O' in image1_filename:
        category_im1 += 'outdoor/'

    category_im2 = ''
    if 'M' in image2_filename:
        category_im2 += 'male/'
    elif 'F' in image2_filename:
        category_im2 += 'female/'
    if 'I' in image2_filename:
        category_im2 += 'indoor/'
    elif 'O' in image2_filename:
        category_im2 += 'outdoor/'

    # Locate the images in the subdirectory
    image1_path = os.path.join(stim_path, category_im1, image1_filename)
    image2_path = os.path.join(stim_path, category_im2, image2_filename)

    # Load the images
    image1 = Image.open(image1_path)
    image2 = Image.open(image2_path)

    # Blend the images using alpha blending
    blended_image = Image.blend(image1, image2, alpha_im)

    # Create a new image for the rectangle border
    width, height = blended_image.size
    border_width = 10  # Set the border width
    total_width = width + 2 * border_width
    total_height = height + 2 * border_width

    # Create a new image with extra space for the border
    bordered_image = Image.new('RGBA', (total_width, total_height), (0, 0, 0, 0))
    bordered_image.paste(blended_image, (border_width, border_width))

    # Draw the rectangle border with the specified alpha_rect value
    draw = ImageDraw.Draw(bordered_image)
    border_color = get_border_color(alpha_rect)
    draw.rectangle([(0, 0), (total_width - 1, total_height - 1)], outline=border_color, width=border_width)

    return bordered_image

###CORRECT RESPONSE#######################################

def get_correct_response(target_sub, pair):
    if target_sub == "male":
        if "M" in pair[0]:
            return 'b'
        elif "F" in pair[0]:
            return None
    elif target_sub == "female":
        if "F" in pair[0]:
            return 'b'
        elif "M" in pair[0]:
            return None
    elif target_sub == "indoor":
        if "I" in pair[0]:
            return 'b'
        elif "O" in pair[0]:
            return None
    elif target_sub == "outdoor":
        if "O" in pair[0]:
            return 'b'
        elif "I" in pair[0]:
            return None
    return None

#####SVM TO ALPHA VALUE#######################

# function to calculate sigmoid image blending alpha
def sigmoid(x):
    a = 2 # slope of curve # at a = 2 curve is sensitve for values between -1 and 1 (ish)
    # at a = 1.0 curve is sensitive to values between -4 to 4
    # at a = 2.8 curve is sensitive to values between -0.8 and 0.8 (ish)
    # at a = 1.5 curve is sensitive to values between -1.3 and 1.3 (ish)
    b = 0 # inflection point at x = 0 for b=0 # inflection point moves to x>0 for b>0
    sig_value = 1/(1 + np.exp((-a * x + a * b))) #Returns value from 0 - 1 approx.
    sig_val_scaled = (sig_value * 2.0) - 1.0# Scaling between -1 and 1.
    if sig_val_scaled < -1.0:
        return -1.0
    if sig_val_scaled > 1.0:
        return 1.0
    return sig_val_scaled

########GENERAL#########################################################

# Initialize the monotonic clock
monotonicClock = core.MonotonicClock()

general_data = {'scriptStartUp': [],'vol_one': [], 'vol_two': [], 'vol_three': [], 'vol_four': [], 'vol_five': [], 'vol_six': [], 'experimentBegin': []}

wait_vols = ['vol_one', 'vol_two', 'vol_three', 'vol_four', 'vol_five', 'vol_six']

general_data['scriptStartUp'] = monotonicClock.getTime()

# Wait for 6 'S' and append time of each volume for quality reference
for vol in wait_vols:
    event.waitKeys(keyList='s')
    general_data[vol].append(monotonicClock.getTime())

    # Create a new instance of the monotonic clock to reset the timer
    monotonicClock = core.MonotonicClock()
    lastCheck = monotonicClock.getTime()
# Get the start time of the experiment
experiment_begin = monotonicClock.getTime()
lasttbvtimepoint = -1
alpha_rect = 0

general_data['experimentBegin'] = experiment_begin

#####RUN STUDY#############################################

fixation_start_time = monotonicClock.getTime()
adjusted_duration_fix = get_adjusted_fixation_duration(fixation_start_time, fixation_start_duration)
fixation_end_time = fixation_start_time + adjusted_duration_fix
while monotonicClock.getTime() <fixation_end_time:
        fixation.draw()
        win.flip()
protocol_fixation_start_time = int(fixation_start_time)*1000
protocol_fixation_end_time= int(fixation_start_time + adjusted_duration_fix)*1000
protocol.add_event('rest', protocol_fixation_start_time, protocol_fixation_end_time, weight='null')

write_data_to_csv(participant_info, np.nan, "fixation", np.nan, fixation_start_time, adjusted_duration_fix, np.nan, np.nan, np.nan, np.nan)

# Open and read the json file
with open(json_path, 'r') as f:
    data = json.load(f)

# Loop over the keys in the json file
block_counter = 0
image_pairs = []
for key in data.keys():
    # Check if the key ends with "info"
    first_image_start_time = None
    last_image_end_time = None
    if key.endswith("info"):
        num_block = data[key][0]
        target_sub = data[key][1]
        non_target_sub = data[key][2]

        # Determine target category
        if "male" in target_sub or "female" in target_sub:
            target_cat = "face"
        elif "indoor" in target_sub or "outdoor" in target_sub:
            target_cat = "scene"
        else:
               target_cat = None
        # Display instructions for 1 second
        instructions = visual.TextStim(win, text=f"{target_cat}", height=30, units='pix')
        instructions_start_time = monotonicClock.getTime()
        instructions.draw()
        win.flip()
        core.wait(1) #hardcoded
        write_data_to_csv(participant_info, np.nan, "instructions", np.nan, instructions_start_time, "1", np.nan, np.nan, np.nan, np.nan)#hardcoded
        protocol_instruction_start_time = int(instructions_start_time)*1000
        protocol_instruction_end_time= int(instructions_start_time + 1)*1000 #careful instructions duration is hardcoded
        protocol.add_event('instructions', protocol_instruction_start_time, protocol_instruction_end_time, weight='null')
        fixation_start_time = monotonicClock.getTime()
        adjusted_duration_fix = get_adjusted_fixation_duration(fixation_start_time, fixation_instr_duration)
        fixation_end_time = fixation_start_time + adjusted_duration_fix
        while monotonicClock.getTime() <fixation_end_time:
                fixation.draw()
                win.flip()
        protocol_fixation_start_time = int(fixation_start_time)*1000
        protocol_fixation_end_time= int(fixation_start_time + adjusted_duration_fix)*1000
        protocol.add_event('rest', protocol_fixation_start_time, protocol_fixation_end_time, weight='null')
        write_data_to_csv(participant_info, np.nan, "fixation", np.nan, fixation_start_time, adjusted_duration_fix, np.nan, np.nan, np.nan, np.nan)
        # Increase the counter by 1
        block_counter += 1
    # Check if the key ends with "order"
    if key.endswith("order"):
        # Print all the pairs of images
        image_pairs = data[key]
        i=0
        lasttbvtimepoint = tbv.get_current_time_point()[0] #gets tbv lasttimepoint before it enters the image presentation loop
        with open(full_txt_path, "a") as f:
             f.write(f"lasttbv timepoint outside i loop: {lasttbvtimepoint}\n")
        currenttimepoint = lasttbvtimepoint
        with open(full_txt_path, "a") as f:
            f.write(f"current timepoint outside i loop: {currenttimepoint}\n")
        alpha_rect = 0
        for i, pair in enumerate(image_pairs):
            i += 1
            # Get the correct response for the current image
            with open(full_txt_path, "a") as f:
                f.write(f"image number [i]: {i}\n") #now i starts from 1
            correct_response = get_correct_response(target_sub, pair)
            image_start_time = monotonicClock.getTime()
            # Calculate the onset time for the current image
            adjusted_duration = get_adjusted_image_duration(image_start_time)
            image_end_time = image_start_time + adjusted_duration
            # If this is the first image, record the start time
            if first_image_start_time is None:
                first_image_start_time = int(image_start_time)*1000

            # Blend the images in the pair with the random alpha_rect value
            blended_image = blend_images_with_rectangle(pair[0], pair[1], alpha_im=0.5, alpha_rect= alpha_rect)
            
            # Display the blended image
            image = visual.ImageStim(win, image=blended_image)

            # Initialize the response, response time variables, tbv timings
            response = None
            response_time = None
            #We moved this upwards (before for loop) to ensure that we don't miss a volume
            #lasttbvtimepoint = tbv.get_current_time_point()[0] #gets tbv lasttimepoint before it enters the image presentation loop
            

            while monotonicClock.getTime() < image_end_time:
                keys = event.getKeys(keyList=['b'], timeStamped=monotonicClock)
                if keys and response is None:
                    response = keys[0][0]
                    response_time = (keys[0][1] - image_start_time) 
                    #print(f"Response received: {response} at time {keys[0][1]:.4f}, response time: {response_time:.4f} ms")
                
                if monotonicClock.getTime() - lastCheck > 0.1:
                    currenttimepoint = tbv.get_current_time_point()[0]
                    lastCheck = monotonicClock.getTime()
                    with open(full_txt_path, "a") as f:
                        f.write(f"current timepoint inside image presentation loop: {currenttimepoint}\n")
                if currenttimepoint > lasttbvtimepoint and i > 4:  #wait for 4 images before le feedback
                    try:
                        with open(full_txt_path, "a") as f: 
                            f.write(f"currenttimepoint > lasttbvtimepoint: {currenttimepoint} > {lasttbvtimepoint}\n")
                        lasttbvtimepoint = lasttbvtimepoint + 1 #Ensure that we don't miss a volume to update
                        mean = tbv.get_number_of_classes()[0]
                        #print('numberofclasses', mean)
                        if mean > 0: # if there is at least one class
                            mean = tbv.get_current_classifier_output()[0][1]
                            if math.isnan(mean):
                                mean = 0 #if mean =NaN, mean =0
                            with open(full_txt_path, "a") as f:
                                f.write(f"classifier output: {mean}, target_sub: {target_sub}\n")
                    
                        
                            if target_sub == 'male' or target_sub == 'female':
                                alpha_rect = sigmoid(mean)
                                with open(full_txt_path, "a") as f:
                                    f.write(f"alpharectmeanifface: {alpha_rect}\n")
                                blended_image = blend_images_with_rectangle(pair[0], pair[1], alpha_im=0.5, alpha_rect= alpha_rect) #alpha rect needs to be for -1 to 1 for the function of blending to work
                                image = visual.ImageStim(win, image=blended_imag)

                            else:
                                mean = -mean
                                alpha_rect = sigmoid(mean) 
                                f.write(f"alpharectmeanelsescene: {alpha_rect}\n")
                                blended_image = blend_images_with_rectangle(pair[0], pair[1], alpha_im=0.5, alpha_rect= alpha_rect) #alpha rect needs to be for -1 to 1 for the function of blending to work
                                image = visual.ImageStim(win, image=blended_image)

                    except:
                        pass 
                image.draw()
                win.flip()

            # Determine accuracy of response
            correct_response = get_correct_response(target_sub, pair)
            if correct_response is None:
                accuracy = 1 if response is None else 0
            elif correct_response == 'b':
                accuracy = 1 if response == 'b' else 0
            else:
                accuracy = 0
            write_data_to_csv(participant_info, num_block, target_cat, target_sub, image_start_time, adjusted_duration, pair, response, response_time, accuracy)
        # Record the end time of the last image
        last_image_end_time = int(image_end_time)*1000
        protocol.add_event(target_cat, first_image_start_time, last_image_end_time, weight='null')

        fixation_start_time = monotonicClock.getTime()
        adjusted_duration_fix = get_adjusted_fixation_duration(fixation_start_time, fixation_duration)
        fixation_end_time = fixation_start_time + adjusted_duration_fix
        while monotonicClock.getTime() <fixation_end_time:
                fixation.draw()
                win.flip()
        protocol_fixation_start_time = int(fixation_start_time)*1000
        protocol_fixation_end_time= int(fixation_start_time + adjusted_duration_fix)*1000
        protocol.add_event('rest', protocol_fixation_start_time, protocol_fixation_end_time, weight='null')
        write_data_to_csv(participant_info, np.nan, "fixation", np.nan, fixation_start_time, adjusted_duration_fix, np.nan, np.nan, np.nan, np.nan)
       
        if block_counter in null_blocks and i == len(image_pairs):
            fixation_start_time = monotonicClock.getTime()
            adjusted_duration_fix = get_adjusted_fixation_duration(fixation_start_time, fixation_null_duration)
            fixation_end_time = fixation_start_time + adjusted_duration_fix
            while monotonicClock.getTime() <fixation_end_time:
                    fixation.draw()
                    win.flip()
            protocol_fixation_start_time = int(fixation_start_time)*1000
            protocol_fixation_end_time= int(fixation_start_time + adjusted_duration_fix)*1000
            protocol.add_event('rest', protocol_fixation_start_time, protocol_fixation_end_time, weight='null')
            write_data_to_csv(participant_info, np.nan, "null", np.nan, fixation_start_time, adjusted_duration_fix, np.nan, np.nan, np.nan, np.nan)

fixation_start_time = monotonicClock.getTime()
adjusted_duration_fix = get_adjusted_fixation_duration(fixation_start_time, fixation_end_duration)
fixation_end_time = fixation_start_time + adjusted_duration_fix
while monotonicClock.getTime() <fixation_end_time:
        fixation.draw()
        win.flip()
protocol_fixation_start_time = int(fixation_start_time)*1000
protocol_fixation_end_time= int(fixation_start_time + adjusted_duration_fix)*1000
protocol.add_event('rest', protocol_fixation_start_time, protocol_fixation_end_time, weight='null')
write_data_to_csv(participant_info, np.nan, "fixation", np.nan, fixation_start_time, adjusted_duration_fix, np.nan, np.nan, np.nan, np.nan)

###############STIMULATION PROTOCOL TBV THINGS##

protocol_name = f"{sub_num}_{ses_num}_{run_num}_task-feedback_protocol.prt"

protocol.export2brainvoyager(f"NF_Attention_Pilot_{sub_num}_{ses_num}_{run_num}_task-feedback", os.path.join(protocol_path, protocol_name))

prt = os.path.join(protocol_path, protocol_name)
with open(prt, "r") as f:
    lines = f.readlines()

# Change FileVersion from 3 to 2
new_lines = [line.replace("FileVersion:        3", "FileVersion:        2") for line in lines]

# Remove "null" from the lines
for i, line in enumerate(new_lines):
    if "'null'" in line:
        new_lines[i] = line.replace("'null'", "")

# Remove ParametricWeights line and the empty line above it
idx = new_lines.index("ParametricWeights:  1\n")
new_lines = new_lines[:idx-1] + new_lines[idx+1:]

# Write the modified lines back to the file
with open(prt, "w") as f:
    f.writelines(new_lines)


################ THOUGHT PROBE PRESENTATION ##########
instructions_thought = visual.TextStim(win, text = 'Now we are going to ask you questions about your thoughts during the task you just completed. \n\n Use the right button to navigate to the right, left button to navigate to the left, and middle button to submit your reponse. \n\n Please press the middle button to continue.', height=30, units='pix')
instructions_thought.draw()
win.flip()
event.waitKeys(keyList='b')
thought_probe(participant_info, monotonicClock.getTime(), win, csv_info, 'feedback') 

#########BYE SCREEN#####################################
def get_instructions_end(session, run):
    if session == '1' and run == '1':
        instructions_text = 'Thank you for your attention.\n\n You have completed task 4 out of 6!'
    elif session == '1' and run == '2':
        instructions_text = 'Thank you for your attention.\n\n You have completed task 6 out of 6! \n\n We will come and get you shortly - you did FANTASTIC :-)'
    instructions = visual.TextStim(win, text=instructions_text, height=30, units='pix')
    return instructions

instructions = get_instructions_end(session, run)
instructions.draw()
win.flip()
event.waitKeys(keyList='space')

# Flip the window when the trials are finished
win.flip()

# Close the window when the trials are finished
win.close()













