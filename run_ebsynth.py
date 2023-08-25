import config
import os
import ebsynth
import cv2
from PIL import Image

def get_filename(i):
	return str(i).zfill(3)+".png"
def get_frame_dir(i):
	return config.ebsynth_path+str(i).zfill(3)+"/"

def run_ebsynth(frame):
	frame_dir = get_frame_dir(frame)
	generate_ebsynth(frame_dir, frame, -1)
	generate_ebsynth(frame_dir, frame - 1, -1)
	generate_ebsynth(frame_dir, frame, 1)
	generate_ebsynth(frame_dir, frame + 1, 1)

def generate_ebsynth(frame_dir, frame, offset):	
	guide0 = config.video_path+get_filename(frame)
	guide1 = config.video_path+get_filename(frame + offset)
	style = frame_dir+get_filename(frame)
	if not os.path.exists(style):
		style = config.video_path+get_filename(frame)

	output_path = frame_dir+get_filename(frame + offset)
	generate_ebsynth_from(style, guide0, guide1, output_path)

def generate_ebsynth_from(style_path, guide0_path, guide1_path, output_path, override_output = False):
	if override_output or not os.path.exists(output_path): # don't run ebsynth if output is already generated
		if os.path.exists(style_path) and os.path.exists(guide0_path) and os.path.exists(guide1_path):
			eb = ebsynth.ebsynth(style_path, [(guide0_path, guide1_path)])
			result = cv2.cvtColor(eb.run(), cv2.COLOR_BGR2RGB)
			result = Image.fromarray(result)
			result.save(output_path)

def apply_ebsynth(img, frame, offset, alpha):
	frame_dir = get_frame_dir(frame)
	if not os.path.exists(frame_dir):
		return img
	style = frame_dir+get_filename(frame+offset)	

	style_img = Image.open(style).convert("RGB")

	return Image.blend(img, style_img, alpha)