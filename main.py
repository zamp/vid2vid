import config
import ebsynth
import os
import shutil
from PIL import Image
import cv2
import comfyui
import threading

# ensure directories exist
if not os.path.exists(config.output_path):
	os.makedirs(config.output_path)
if not os.path.exists(config.ebsynth_path):
	os.makedirs(config.ebsynth_path)

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

	if os.path.exists(guide0) and os.path.exists(guide1):
		eb = ebsynth.ebsynth(style, [(guide0, guide1)])
		result = cv2.cvtColor(eb.run(), cv2.COLOR_BGR2RGB)
		result = Image.fromarray(result)
		result.save(frame_dir+get_filename(frame + offset))

def apply_ebsynth(img, frame, offset, alpha):
	frame_dir = get_frame_dir(frame)
	if not os.path.exists(frame_dir):
		return img
	style = frame_dir+get_filename(frame+offset)	

	style_img = Image.open(style).convert("RGB")

	return Image.blend(img, style_img, alpha)

def process_frames(frame_min, frame_max, temporal_blend, reinforce_source_alpha, cfg, denoise):
	if temporal_blend > 0:
		print("\tGenerating ebsynth...")

		# copy output to ebsynth directories
		for i in range(frame_min, frame_max+1):
			frame_dir = get_frame_dir(i)
			if not os.path.exists(frame_dir):
				os.makedirs(frame_dir)
			shutil.copy(config.output_path+get_filename(i), frame_dir+get_filename(i))

		for i in range(frame_min, frame_max+1):
			run_ebsynth(i)

		# threads = []
		#for i in range(frame_min, frame_max+1):
		#	new_thread = threading.Thread(target=, args=(i,))
		#	threads.append(new_thread)
		#	new_thread.start()
		#	if len(threads) > config.max_ebsynth_threads:
		#		threads[0].join()
		#		del threads[0]
		#for thread in threads:
		#	thread.join()

	for i in range(frame_min, frame_max+1):
		frame_path = config.output_path+get_filename(i)
		video_frame_path = config.video_path+get_filename(i)

		if temporal_blend > 0 or reinforce_source_alpha > 0:
			frame = Image.open(frame_path).convert("RGB")

			if temporal_blend > 0.0:
				print("\tApplying ebsynth: {}".format(frame_path))
				
				frame = apply_ebsynth(frame, i - 1, 1, temporal_blend)
				frame = apply_ebsynth(frame, i + 1, -1, temporal_blend)
				frame = apply_ebsynth(frame, i - 2, 2, temporal_blend * 0.5)
				frame = apply_ebsynth(frame, i + 2, -2, temporal_blend * 0.5)
			else:
				print("\tTemporal blend 0. Skipping ebsynth.")

			if reinforce_source_alpha > 0.0:
				print("\tReinforcing source: {} into {}".format(video_frame_path, frame_path))
				video_frame = Image.open(video_frame_path).convert("RGB")
				frame = Image.blend(frame, video_frame, reinforce_source_alpha)
			else:
				print("\tReinforce source 0. Skipping reinforcing.")

			frame.save(frame_path)
		
		run_stable_diffusion(frame_path, frame_path, cfg, denoise)

		if config.debug_show_frame == i:
			frame = Image.open(frame_path).convert("RGB")
			frame.show("frame")

def run_stable_diffusion(input_file_path, output_file_path, cfg, denoise):
	print("\tRunning stable diffusion: {}".format(input_file_path))
	image = comfyui.process_image(input_file_path, cfg, denoise)
	# for some reason the images come out different size than put in?
	img = Image.open(input_file_path)
	if img.width != image.width or img.height != image.height:
		image = image.resize((img.width, img.height))
	image.save(output_file_path)

try:
	comfyui.connect()

	files = os.listdir(config.video_path)
	files = [f for f in files if os.path.isfile(config.video_path+f) and f.endswith(".png")]

	frame_max = 0
	for file in files:
		frame_max = max(int(file[:3]), frame_max)

	frame_min = frame_max
	for file in files:
		frame_min = min(int(file[:3]), frame_min)

	print("Video files from frame: " + str(frame_min).zfill(3) + " to: " + str(frame_max).zfill(3))

	for file in files:	
		if os.path.exists(config.output_path+file):
			continue

		shutil.copy(config.video_path+file, config.output_path+file)

	for step in config.steps:
		multiplier = 1
		for i in range(step["iterations"]):
			print("Running: {} {}/{}".format(step["step"], i+1, step["iterations"]))
			process_frames(frame_min, frame_max, step["temporal_blend"] * multiplier, step["reinforce_source"] * multiplier, step["cfg"], step["denoise"] * multiplier)
			multiplier *= config.iteration_multiplier

	print("DONE!")
finally:
	comfyui.close()