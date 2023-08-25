import config
import os
import shutil
from PIL import Image
import comfyui
import processors

# ensure directories exist
if not os.path.exists(config.output_path):
	os.makedirs(config.output_path)

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

	print("Processing files from frame: " + str(frame_min).zfill(3) + " to: " + str(frame_max).zfill(3))

	for file in files:	
		if os.path.exists(config.output_path+file):
			continue

		if config.width != None and config.height != None:			
			img = Image.open(config.video_path+file)
			if img.width != config.width or img.height != config.height:
				print("\tResizing {} to {}x{}".format(config.video_path+file, config.width, config.height))
				img = img.resize((config.width, config.height))
				img.save(config.video_path+file)
		
		shutil.copy(config.video_path+file, config.output_path+file)

	total_iterations = 0
	iterations_run = 0
	for render_pass in config.render_passes:
		total_iterations += render_pass["iterations"]

	for render_pass in config.render_passes:
		multiplier = render_pass["it_multiplier"]
		iterations = render_pass["iterations"]
		name = render_pass["name"]
		tp = render_pass["temporal_blend"] * multiplier
		rs = render_pass["reinforce_source"] * multiplier
		cfg = render_pass["cfg"]
		denoise = render_pass["denoise"] * multiplier
		pp = render_pass["positive_prompt"]
		np = render_pass["negative_prompt"]
		wf = render_pass["workflow_json"]
		mdl = render_pass["model"]
		type = render_pass["type"]

		print(f"Running render pass {name} ({type}) temporal blend: {tp} reinforce source: {rs} cfg: {cfg} denoise: {denoise}")
		
		for i in range(iterations):
			if type == "default":
				processors.process_frames(frame_min, frame_max, tp, rs, cfg, denoise, pp, np, wf, mdl)
			elif type == "fast_tb":
				processors.process_frames_fast_tb(frame_min, frame_max, tp, rs, cfg, denoise, pp, np, wf, mdl)

			multiplier *= config.iteration_multiplier

			iterations_run += 1

	print("DONE!")
finally:
	comfyui.close()