#Dynamic functional Localizer script adapted by (https://www.sciencedirect.com/science/article/pii/S1053811911003466#bb0200)

# Import necessary libraries
from psychopy import visual, core, event, gui
import random
import os 
import csv
from datetime import datetime
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
face_path = os.path.join(repo_path,'data/stimuli/stimuli_video/faces')
scene_path = os.path.join(repo_path,'data/stimuli/stimuli_video/scenes')
beh_path =  os.path.join(repo_path,"data", "responses", f"{sub_num}", f"{ses_num}")#

# Create the directory if it does not exist
if not os.path.isdir(beh_path):
    os.makedirs(beh_path)
protocol_path = os.path.join(repo_path,"data", "protocols", f"{sub_num}", f"{ses_num}")
# Create the directory if it does not exist
if not os.path.isdir(protocol_path):
    os.makedirs(protocol_path)

# load face and scene video clips
face_videos = [os.path.join(face_path, f) for f in os.listdir(face_path)]
scene_videos = [os.path.join(scene_path, f) for f in os.listdir(scene_path)]

# create a list to hold the stimuli presented
presented_videos = []

##### SET UP EXPERIMENT VARIABLES ###################################

# Set up blocks
#block_order = [0,1,0] #for test
block_order =   [0, 1, 0, 2, 0, 1, 0, 2, 0, 1, 0, 1, 0, 3, 2, 0, 1, 0, 2, 0, 3, 1, 0, 2, 0, 1, 0, 2, 0, 2, 0, 1, 0, 2, 0, 1, 0, 2, 0, 1, 0, 2, 0, 1, 0, 2, 0, 1, 0, 1, 0, 3, 2, 0, 2, 0, 1, 0, 2, 0, 1, 0, 2, 0]
videos_per_block = 3 #block_duration = 9 sec
video_duration = 3
fixation_duration = 9
fixation_duration_end = 1
fixation_null = 18 #(block_duration + fixation duration)
#### INSTRUCTIONS ####################################################

# Display instructions
welcome = visual.TextStim(win, text='During this task, you will be shown videos of faces and scenes.\n\n Please pay attention to the videos.\n\n The task will last 10 minutes.' , height=30, units='pix')
welcome.draw()
win.flip()
event.waitKeys(keyList='space')
win.flip()

###### CSV #############################################################

header = ['subject_num', 'session', 'run', 'block_order', 'block', 'stimulus', 'stimulus_onset', 'stimulus_duration', 'stimulus_path']

date_string = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"{sub_num}_{ses_num}_{run_num}_task-functional-localizer-video_beh.csv"
full_csv_path = os.path.join(beh_path, filename)

def write_data_to_csv(participant_info, block_order, block, stimulus, stimulus_onset, stimulus_duration, stimulus_path=''):
    row = [sub_num, ses_num, run_num, block_order, block, stimulus, stimulus_onset, stimulus_duration, stimulus_path]
    with open(full_csv_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:
            writer.writerow(header)
        writer.writerow(row)

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

# Get the start time of the experiment
experiment_begin = monotonicClock.getTime()
general_data['experimentBegin'] = experiment_begin

#######ADJUSTED VIDEO DURATION ############################################

# Define a function to calculate the adjusted video duration based on onset time
def get_adjusted_video_duration(video_start_time, target_interval=1):
    time_elapsed = video_start_time % target_interval
    adjusted_duration = video_duration - time_elapsed
    return adjusted_duration
def get_adjusted_fixation_duration(fixation_start_time, fixation_duration, target_interval=1):
    time_elapsed = fixation_start_time % target_interval
    adjusted_duration = fixation_duration - time_elapsed
    return adjusted_duration

######### DISPLAY BLOCKS ###################################################

for block in block_order:
    first_video_start_time = None
    last_video_end_time = None
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
        # Display the first video of face videos
        for i in range(videos_per_block):

            face_video_indices = random.sample([i for i in range(len(face_videos)) if face_videos[i] not in presented_videos],1)
            for video_index in face_video_indices:

                # add the stimulus to the list of presented stimuli
                presented_videos.append(face_videos[video_index])

                video_start_time = monotonicClock.getTime() # record video start time
            
                # Calculate adjusted video duration based on onset time
                adjusted_duration = get_adjusted_video_duration(video_start_time)

                video_end_time = video_start_time + adjusted_duration
                # If this is the first video, record the start time
                if first_video_start_time is None:
                    first_video_start_time = int(video_start_time)*1000

            # For face videos
            video = visual.MovieStim3(win, face_videos[video_index], flipVert=False)
            write_data_to_csv(participant_info, block_order, block, "face", video_start_time, adjusted_duration, video.filename) 
            while monotonicClock.getTime() < video_end_time:
                video.draw()
                win.flip()

        # Record the end time of the last video
        last_video_end_time = int(video_end_time)*1000
        protocol.add_event('face', first_video_start_time, last_video_end_time, weight='null')

    elif block == 2:
        # Display the first video of scene videos
        for i in range(videos_per_block):

            scene_video_indices = random.sample([i for i in range(len(scene_videos)) if scene_videos[i] not in presented_videos],1)
            for video_index in scene_video_indices:

                # add the stimulus to the list of presented stimuli
                presented_videos.append(scene_videos[video_index])

                video_start_time = monotonicClock.getTime() # record video start time
            
                # Calculate adjusted video duration based on onset time
                adjusted_duration = get_adjusted_video_duration(video_start_time)

                video_end_time = video_start_time + adjusted_duration
                # If this is the first video, record the start time
                if first_video_start_time is None:
                    first_video_start_time = int(video_start_time)*1000

            # For scene videos
            video = visual.MovieStim3(win, scene_videos[video_index], flipVert=False)
            write_data_to_csv(participant_info, block_order, block, "scene", video_start_time, adjusted_duration, video.filename)
            video_end_time = video_start_time + video_duration
            while monotonicClock.getTime() < video_end_time:
                video.draw()
                win.flip()

        # Record the end time of the last video
        last_video_end_time = int(video_end_time)*1000
        protocol.add_event('scene', first_video_start_time, last_video_end_time, weight='null') 

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
protocol_name = f"{sub_num}_{ses_num}_{run_num}_task-functional-localizer-video_protocol.prt"

protocol.export2brainvoyager(f"NF_Attention_Pilot_{sub_num}_{ses_num}_{run_num}_task-functional-localizer-video", os.path.join(protocol_path, protocol_name))

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

instructions = visual.TextStim(win, text='Thank you for your attention.\n\n You have completed task 1 out of 6!', height=30, units='pix')
instructions.draw()
win.flip()
event.waitKeys(keyList='space')

# Flip the window when the trials are finished
win.flip()

# Close the window when the trials are finished
win.close()
