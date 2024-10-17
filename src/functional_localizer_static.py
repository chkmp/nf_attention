#Static functional Localizer script

# Import necessary libraries
from psychopy import visual, core, event, gui
import time
import random
import os 
import csv
from datetime import datetime
import random
from random import randint, shuffle
from expyriment.design.extras import StimulationProtocol 


######TBV THINGS###################################################

# BV prt protocol
protocol = StimulationProtocol("time") 
protocol.add_condition("rest")
protocol.add_condition("face")
protocol.add_condition("scene")
######GIU##########################################################

# Create a dialog box to collect participant information
dlg = gui.Dlg(title="Participant Information")
dlg.addField('Subject:')
dlg.addField('session', choices=['1', '2', '3', '4'])
dlg.addField('run', choices=['1', '2', '3', '4'])
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

#####SET UP WINDOW #################################################

# Set up window and fixation cross
win = visual.Window(size=(800, 600), fullscr=True, units='pix', winType='pyglet')
fixation = visual.TextStim(win, text='+', pos=(0, 0), color='white')

#### SET UP STIMULI ################################################

# define the relative path to the stimuli, csv, and protocol
repos_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
repo_path = os.path.join(repos_path, "nf_attention_imaging")
female_face_path = os.path.join(repo_path,'data/stimuli/female')
male_face_path = os.path.join(repo_path,'data/stimuli/male')
indoor_scene_path = os.path.join(repo_path,'data/stimuli/indoor')
outdoor_scene_path = os.path.join(repo_path,'data/stimuli/outdoor')
beh_path =  os.path.join(repo_path,"data", "responses", f"{sub_num}", f"{ses_num}")
protocol_path = os.path.join(repo_path,"data", "protocols", f"{sub_num}", f"{ses_num}")
if not os.path.isdir(beh_path):
    os.makedirs(beh_path)
# Create the directory if it does not exist
if not os.path.isdir(protocol_path):
    os.makedirs(protocol_path)

# load female and male face images
female_face_images = sorted([os.path.join(female_face_path, f) for f in os.listdir(female_face_path) if f.endswith('.jpg')])[:18]
male_face_images = sorted([os.path.join(male_face_path, f) for f in os.listdir(male_face_path) if f.endswith('.jpg')])[:18]

# load female and male face images
indoor_scene_images = sorted([os.path.join(indoor_scene_path, f) for f in os.listdir(indoor_scene_path) if f.endswith('.jpg')])[:18]
outdoor_scene_images = sorted([os.path.join(outdoor_scene_path, f) for f in os.listdir(outdoor_scene_path) if f.endswith('.jpg')])[:18]

##### SET UP BLOCKS ##################################################

# Set up blocks
block_order =   [0, 1, 0, 2, 0, 1, 0, 2, 0, 1, 0, 1, 0, 3, 2, 0, 1, 0, 2, 0, 3, 1, 0, 2, 0, 1, 0, 2, 0, 2, 0, 1, 0, 2, 0, 1, 0, 2, 0, 1, 0, 2, 0, 1, 0, 2, 0, 1, 0, 1, 0, 3, 2, 0, 2, 0, 1, 0, 2, 0, 1, 0, 2, 0]
num_blocks = len(block_order)
images_per_block = 9 #block_duration = 9 sec
image_duration = 0.8
fixation_duration = 9
fixation_duration_end = 1
interblock_fix = 0.2
fixation_null = 18 #(block duration + fixation_duration)

#### INSTRUCTIONS ######################################################

# Display instructions
welcome = visual.TextStim(win, text='During this task, you will be shown images of faces and scenes.\n\n If the image has a red dot, press the middle button.\n Please keep your eyes on the fixation cross.\n\n The task will last 10 minutes.', height=30, units='pix')
welcome.draw()
win.flip()
event.waitKeys(keyList='space')
win.flip()

###### CSV #############################################################

header = ['subject_num', 'session', 'run', 'block_order', 'block', 'stimulus', 'stimulus_onset', 'stimulus_duration', 'stimulus_path', 'dot_present', 'keypress', 'correct']

date_string = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"{sub_num}_{ses_num}_{run_num}_task-functional-localizer-static_beh.csv"
full_csv_path = os.path.join(beh_path, filename)

def write_data_to_csv(participant_info, block_order, block, stimulus, stimulus_onset, stimulus_duration, stimulus_path='', dot_present=None, keypress=None, correct=None):
    row = [sub_num, ses_num, run_num, block_order, block, stimulus, stimulus_onset, stimulus_duration, stimulus_path, dot_present, keypress, correct]
    with open(full_csv_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:
            writer.writerow(header)
        writer.writerow(row)

# Initialize variables to count correct responses and total trials
correct_responses = 0
total_trials = 0

########GENERAL###########################################################
# Initialize the monotonic clock
monotonicClock = core.MonotonicClock()

#set up a general info variable (dict of lists)
general_data = {'scriptStartUp': [],'vol_one': [], 'vol_two': [], 'vol_three': [], 'vol_four': [], 'vol_five': [], 'vol_six': [], 'experimentBegin': []}

wait_vols = ['vol_one', 'vol_two', 'vol_three', 'vol_four', 'vol_five', 'vol_six']

general_data['scriptStartUp'] = monotonicClock.getTime()
# Wait for 6 'S' and append time of each volume for quality reference
for vol in wait_vols:
    event.waitKeys(keyList='s')
    general_data[vol].append(monotonicClock.getTime())

    # Create a new instance of the monotonic clock to reset the timer
    monotonicClock = core.MonotonicClock()

# Get the start time of the experiment
experiment_begin = monotonicClock.getTime()
general_data['experimentBegin'] = experiment_begin

#######ADJUSTED IMAGE DURATION#############################################

# Define a function to calculate the adjusted image duration based on onset time
def get_adjusted_image_duration(image_start_time, target_interval=1):
    time_elapsed = image_start_time % target_interval
    adjusted_duration = image_duration - time_elapsed
    return adjusted_duration

def get_adjusted_fixation_duration(fixation_start_time, fixation_duration, target_interval=1):
    time_elapsed = fixation_start_time % target_interval
    adjusted_duration = fixation_duration - time_elapsed
    return adjusted_duration
###########DOT#############################################################

def add_red_dot(image, dot_size=5):
    dot_pos = (randint(-image.size[0] // 2 + dot_size, image.size[0] // 2 - dot_size),
               randint(-image.size[1] // 2 + dot_size, image.size[1] // 2 - dot_size))
    red_dot = visual.Circle(win, radius=dot_size, fillColor='red', pos=dot_pos)
    return red_dot

#######COUNT BLOCK AND DOT ASSIGNEMENTS#####################################

def count_blocks(block_order):
    num_face_blocks = block_order.count(1)
    num_scene_blocks = block_order.count(2)
    return {'face': num_face_blocks, 'scene': num_scene_blocks}


def generate_dot_assignments(num_blocks):
    one_dot_assignments = num_blocks // 2
    two_dot_assignments = num_blocks - one_dot_assignments
    dot_assignments = [1] * one_dot_assignments + [2] * two_dot_assignments
    shuffle(dot_assignments)
    return dot_assignments

block_count = count_blocks(block_order)
face_dot_assignments = generate_dot_assignments(block_count['face'])
scene_dot_assignments = generate_dot_assignments(block_count['scene'])
face_block_iter = 0
scene_block_iter = 0

###########CALCULATE SCORE####################################################

def calculate_score(filename):
    total_trials = 0
    correct_trials = 0

    with open(filename, newline='') as csvfile:
        datareader = csv.reader(csvfile, delimiter=',', quotechar='"')
        header = next(datareader, None)  # Read the header row
        
        if 'correct' not in header:
            raise ValueError("The 'correct' column is not present in the CSV file.")
        
        correct_column_index = header.index('correct')  # Find the index of the 'correct' column

        for row in datareader:
            if not row[correct_column_index]:  # Check if the 'correct' column is empty
                continue  # Skip the row if the column is empty

            total_trials += 1
            if int(row[correct_column_index]) == 1:
                correct_trials += 1

    score = (correct_trials / total_trials) * 100
    print(f"The participant's score is: {score:.2f}%")

#########BLOCK PRESENTATION ###############################################

for block in block_order:
    first_image_start_time = None
    last_image_end_time = None

    if block == 0:
        fixation_start_time = monotonicClock.getTime()
        adjusted_duration_fix = get_adjusted_fixation_duration(fixation_start_time, fixation_duration, target_interval=1)
        fixation_end_time = fixation_start_time + adjusted_duration_fix
        while monotonicClock.getTime() <fixation_end_time:
                fixation.draw()
                win.flip()
        write_data_to_csv(participant_info, block_order, block, "fixation", fixation_start_time, adjusted_duration_fix)
        protocol_fixation_start_time = int(fixation_start_time)*1000
        protocol_fixation_end_time= int(fixation_end_time)*1000
        protocol.add_event('rest', protocol_fixation_start_time, protocol_fixation_end_time, weight='null')

    elif block == 1:

        dot_count = face_dot_assignments[face_block_iter]
        face_block_iter += 1

        # Create two lists containing half the images from each directory
        half_female_faces = female_face_images[:len(female_face_images)//2]
        half_male_faces = male_face_images[:len(male_face_images)//2]
        remaining_female_faces = female_face_images[len(female_face_images)//2:]
        remaining_male_faces = male_face_images[len(male_face_images)//2:]
        
        # Randomly shuffle the two lists
        random.shuffle(half_female_faces)
        random.shuffle(half_male_faces)
        
        # Create an empty list to store the presented stimuli
        presented_faces = []

        dot_indices = random.sample(range(images_per_block), dot_count)

        # Display the first block of face images
        for i in range(images_per_block):

            if len(presented_faces) < len(half_female_faces) + len(half_male_faces):
                # Choose randomly between male and female faces from the half lists
                if i % 2 == 0:
                    face_dir = half_female_faces
                else:
                    face_dir = half_male_faces
            else:
                # Choose randomly between male and female faces from the remaining lists
                face_dir = random.choice([remaining_female_faces, remaining_male_faces])
            
            # Choose a random image from the selected directory
            face_image_path = random.choice(face_dir)
            
            # Check if the image has already been presented in this block
            while face_image_path in presented_faces:
                face_image_path = random.choice(face_dir)
            
            # Add the selected image to the list of presented stimuli
            presented_faces.append(face_image_path)

            image_start_time = monotonicClock.getTime() # record image start time
            if first_image_start_time is None:
                first_image_start_time = int(image_start_time)*1000
            
            # Calculate adjusted image duration based on onset time
            adjusted_duration = get_adjusted_image_duration(image_start_time)

            # Load and present the image
            image = visual.ImageStim(win, image=face_image_path)

            red_dot = None
            if i in dot_indices:
                red_dot = add_red_dot(image)

            # Calculate the end time of image presentation
            image_end_time = image_start_time + adjusted_duration
            response = None
            correct = None
            first_keypress = None
            while monotonicClock.getTime() < image_end_time:
                image.draw()
                fixation.draw()
                if red_dot is not None:
                    red_dot.draw()  # Add this line to draw the red dot
                win.flip()

                keys = event.getKeys(keyList=['b'])
                if keys and not first_keypress:
                    first_keypress = keys[0]
                    response = first_keypress

                    if response == 'escape':
                        core.quit()

                if red_dot is not None and first_keypress == 'b':
                    correct = 1
                elif red_dot is None and first_keypress is None:
                    correct = 1
                else:
                    correct = 0
            fixation_start_time = monotonicClock.getTime()
            adjusted_duration_fix = get_adjusted_fixation_duration(fixation_start_time, interblock_fix, target_interval=0.2)
            fixation_end_time = fixation_start_time + adjusted_duration_fix
            while monotonicClock.getTime() <fixation_end_time:
                fixation.draw()
                win.flip()
            write_data_to_csv(participant_info, block_order, block, "face", image_start_time, adjusted_duration, face_image_path, 1 if red_dot is not None else 0, first_keypress, correct)

        # Record the end time of the last fix to mark end of block for prt
        last_image_end_time = int(fixation_end_time)*1000
        protocol.add_event('face', first_image_start_time, last_image_end_time, weight='null')
            
    elif block == 2:

        dot_count = scene_dot_assignments[scene_block_iter]
        scene_block_iter += 1

        # Create two lists containing half the images from each directory
        half_indoor_scenes = indoor_scene_images[:len(indoor_scene_images)//2]
        half_outdoor_scenes = outdoor_scene_images[:len(outdoor_scene_images)//2]
        remaining_indoor_scenes = indoor_scene_images[len(indoor_scene_images)//2:]
        remaining_outdoor_scenes = outdoor_scene_images[len(outdoor_scene_images)//2:]
        
        # Randomly shuffle the two lists
        random.shuffle(half_indoor_scenes)
        random.shuffle(half_outdoor_scenes)
        
        # Create an empty list to store the presented stimuli
        presented_scenes = []
        
        dot_indices = random.sample(range(images_per_block), dot_count)

        # Display the first block of face images
        for i in range(images_per_block):
            if len(presented_scenes) < len(half_indoor_scenes) + len(half_outdoor_scenes):
                # Choose randomly between male and female faces from the half lists
                if i % 2 == 0:
                    scene_dir = half_indoor_scenes
                else:
                    scene_dir = half_outdoor_scenes
            else:
                # Choose randomly between male and female faces from the remaining lists
                scene_dir = random.choice([remaining_indoor_scenes, remaining_outdoor_scenes])
            
            # Choose a random image from the selected directory
            scene_image_path = random.choice(scene_dir)
            
            # Check if the image has already been presented in this block
            while scene_image_path in presented_scenes:
                scene_image_path = random.choice(scene_dir)
            
            # Add the selected image to the list of presented stimuli
            presented_scenes.append(scene_image_path)

            image_start_time = monotonicClock.getTime() # record image start time
            if first_image_start_time is None:
                first_image_start_time = int(image_start_time)*1000
                            
            # Calculate adjusted image duration based on onset time
            adjusted_duration = get_adjusted_image_duration(image_start_time)
            
            # Load and present the image
            image = visual.ImageStim(win, image=scene_image_path)

            red_dot = None
            if i in dot_indices:
                red_dot = add_red_dot(image)

            # Calculate the end time of image presentation
            image_end_time = image_start_time + adjusted_duration
            response = None
            correct = None
            first_keypress = None
            
            while monotonicClock.getTime() < image_end_time:
                image.draw()
                fixation.draw()
                if red_dot is not None:
                    red_dot.draw()  # Add this line to draw the red dot
                win.flip()

                keys = event.getKeys(keyList=['b'])
                if keys and not first_keypress:
                    first_keypress = keys[0]
                    response = first_keypress

                    if response == 'escape':
                        core.quit()

                if red_dot is not None and first_keypress == 'b':
                    correct = 1
                elif red_dot is None and first_keypress is None:
                    correct = 1
                else:
                    correct = 0
            fixation_start_time = monotonicClock.getTime()
            adjusted_duration_fix = get_adjusted_fixation_duration(fixation_start_time, interblock_fix, target_interval=0.2)
            fixation_end_time = fixation_start_time + adjusted_duration_fix
            while monotonicClock.getTime() <fixation_end_time:
                fixation.draw()
                win.flip()

            write_data_to_csv(participant_info, block_order, block, "scene", image_start_time, adjusted_duration, scene_image_path, 1 if red_dot is not None else 0, first_keypress, correct)
        # Record the end time of the last fix to mark end of block for prt
        last_image_end_time = int(fixation_end_time)*1000
        protocol.add_event('scene', first_image_start_time, last_image_end_time, weight='null')

    if block == 3:
        fixation_start_time = monotonicClock.getTime()
        adjusted_duration_fix = get_adjusted_fixation_duration(fixation_start_time, fixation_null, target_interval=1)
        fixation_end_time = fixation_start_time + adjusted_duration_fix
        while monotonicClock.getTime() <fixation_end_time:
                fixation.draw()
                win.flip()
        write_data_to_csv(participant_info, block_order, block, "null", fixation_start_time, adjusted_duration_fix)
        protocol_fixation_start_time = int(fixation_start_time)*1000
        protocol_fixation_end_time= int(fixation_end_time)*1000
        protocol.add_event('rest', protocol_fixation_start_time, protocol_fixation_end_time, weight='null')

##############CALCULATE THE SCORE#############
score =calculate_score(full_csv_path)
print(score)

###fixation to make prt end in an odd number ##
fixation_start_time = monotonicClock.getTime()
fixation_end_time = fixation_start_time + fixation_duration_end
while monotonicClock.getTime() <fixation_end_time:
        fixation.draw()
        win.flip()
write_data_to_csv(participant_info, block_order, block, "fixation", fixation_start_time, fixation_duration_end)
protocol_fixation_start_time = int(fixation_start_time)*1000
protocol_fixation_end_time= int(fixation_start_time + fixation_duration_end)*1000
protocol.add_event('rest', protocol_fixation_start_time, protocol_fixation_end_time, weight='null')

###############STIMULATION PROTOCOL TBV THINGS##
protocol_name = f"{sub_num}_{ses_num}_{run_num}_task-functional-localizer-static_protocol.prt"

protocol.export2brainvoyager(f"NF_Attention_Pilot_{sub_num}_{ses_num}_{run_num}_task-functional-localizer-static", os.path.join(protocol_path, protocol_name))
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

#########BYE SCREEN#####################################
instructions = visual.TextStim(win, text='Thank you for your attention.\n\n You have completed task 2 out of 6!', height=30, units='pix')
instructions.draw()
win.flip()
event.waitKeys(keyList='space')


# Flip the window when the trials are finished
win.flip()

# Close the window when the trials are finished
win.close()




