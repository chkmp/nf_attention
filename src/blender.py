#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import glob
import random
from PIL import Image, ImageDraw


# This script is to create blended image stimuli for Experiment 1
# The nature of these stimuli will differ depending on the Group participants in 

# F1 - tell the script where to look for images 
# Return - parent source directory as string
def stimpath():
    current_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    return os.path.join(current_path, 'data/stimuli')

def _singleblend(stimdir, target, nontarget, block):
	"""
	Function to return 50 filepaths, composed of 45 target and 5 non-target pictures 
	"""
	# Choose images for blend a 
	target_path = os.path.join(stimdir, target)
	all_targets = glob.glob(os.path.join(target_path, '*'))

	# Images in different blocks from the same category should not be drawn from the same pool
	if block == 'face':
		all_targets = all_targets[:45]
	elif block == 'scene':
		all_targets = all_targets[45:]

	random.shuffle(all_targets)
	blend_a_targets = all_targets
	assert len(blend_a_targets) == 45

	# Select 5 images from non-target directory 
	nontarget_path = os.path.join(stimdir, nontarget)
	all_nontargets = glob.glob(os.path.join(nontarget_path, '*'))
	if block == 'face':
		all_nontargets = all_nontargets[:45]
	elif block == 'scene':
		all_nontargets = all_nontargets[45:]

	random.shuffle(all_nontargets)
	blend_a_nontargets = all_nontargets[:5]
	assert len(blend_a_nontargets) == 5

	# Combine target and non-target lists
	return [*blend_a_targets, *blend_a_nontargets]

# F2 - Return 100 filepaths (ingredients to create a block of 50 blended images)
def image_paths(stimdir, group, block):
	"""
	Function to return 2 x 50 file paths for blending - one block's worth of images
	The file paths depend on the group and block 
	Group = ('male_indoor', 'male_outdoor', 'female_indoor', 'female_outdoor')
	Block = ('face', 'scene')
	"""
	# For blocks of face stimuli
	if block == 'face':
		if group == 'male_indoor':
			blend_a = _singleblend(stimdir, 'male', 'female', block)
			blend_b = _singleblend(stimdir, 'indoor', 'outdoor', block)
			return blend_a, blend_b 

		elif group == 'male_outdoor':
			blend_a = _singleblend(stimdir, 'male', 'female', block)
			blend_b = _singleblend(stimdir, 'outdoor', 'indoor', block)
			return blend_a, blend_b 

		elif group == 'female_indoor':
			blend_a = _singleblend(stimdir, 'female', 'male', block)
			blend_b = _singleblend(stimdir, 'outdoor', 'indoor', block)
			return blend_a, blend_b 		

		elif group == 'female_outdoor':
			blend_a = _singleblend(stimdir, 'male', 'female', block)
			blend_b = _singleblend(stimdir, 'outdoor', 'indoor', block)
			return blend_a, blend_b 				

	elif block == 'scene':
		if group == 'male_indoor':
			blend_a = _singleblend(stimdir, 'indoor', 'outdoor', block)
			blend_b = _singleblend(stimdir, 'male', 'female', block)
			return blend_a, blend_b 

		elif group == 'male_outdoor':
			blend_a = _singleblend(stimdir, 'outdoor', 'indoor', block)
			blend_b = _singleblend(stimdir, 'male', 'female', block)
			return blend_a, blend_b 

		elif group == 'female_indoor':
			blend_a = _singleblend(stimdir, 'indoor', 'outdoor', block)
			blend_b = _singleblend(stimdir, 'female', 'male', block)
			return blend_a, blend_b 		

		elif group == 'female_outdoor':
			blend_a = _singleblend(stimdir, 'outdoor', 'indoor', block)
			blend_b = _singleblend(stimdir, 'female', 'male', block)
			return blend_a, blend_b
		
def _imagemerge(a, b):
	"""
	Function to merge two images 
	"""
	im1 = Image.open(a)
	im2 = Image.open(b)
	assert im1.size == im2.size 
	return Image.blend(Image.open(a),Image.open(b),alpha=0.5)

def _fixationcross(imageobject):
	"""
	Function to draw fixation cross
	"""
	im = imageobject
	draw = ImageDraw.Draw(im)
	crosssize = 10
	draw.line((im.size[0]/2, im.size[1]/2 + crosssize, im.size[0]/2, im.size[1]/2 - crosssize), fill=0, width=5)
	draw.line((im.size[0]/2 + crosssize, im.size[1]/2, im.size[0]/2 - crosssize, im.size[1]/2), fill=0, width=5)
	return im 

# F3 - Blend the images
def blend(path_dict, group, block):
    for i in range(5):
        suffix = '_' + str(i + 1)
        block_name = block + suffix 
        current_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        output_dir = os.path.join(current_path, 'data/derivatives/output', group, block_name)
        os.makedirs(output_dir, exist_ok=True)

		kys = [i for i in path_dict.keys()]
		random.shuffle(path_dict[kys[0]]) 
		random.shuffle(path_dict[kys[1]]) 

		for a,b in zip(path_dict[kys[0]],path_dict[kys[1]]):		
		# Blend a with b
			# generate output name from paths 
			# get category of a 
			parent_a = os.path.split(a)[0]
			category_a = os.path.split(parent_a)[1]
			# get image ID for a 
			id_a = os.path.split(a)[1].split('.')[0]
			# combine category and ID 

			# get category of b 
			parent_b = os.path.split(b)[0]
			category_b = os.path.split(parent_b)[1]		
			# get image ID for a 
			id_b = os.path.split(b)[1].split('.')[0]

			# generate output name 
			id_blended = category_a + id_a + '_' + category_b + id_b + '.jpeg'

			# blend the images 
			blended = _imagemerge(a,b)

			# combine output directory and the stim ID
			output_path = os.path.join(output_dir, id_blended)

			# save 
			blended.save(output_path)



############ RUN FUNCTIONS ############

groups = ['male_indoor', 'male_outdoor', 'female_indoor', 'female_outdoor']
blocks = ['scene', 'face']

sp = stimpath()

for group in groups:
	for block in blocks:
		print('Creating Stimuli for group: {}, block: {}'.format(group,block))
		paths_a, paths_b = image_paths(sp, group, block)
		blend_dict = {'blend_a': paths_a, 'blend_b': paths_b}
		blend(blend_dict, group, block)
		print('Check derivatives directory for blended stimuli.')
