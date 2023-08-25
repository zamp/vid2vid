import config
import os
import shutil
from PIL import Image
import comfyui
import processors
import util
import render_pass_defaults as rpd

try:
	comfyui.connect()

	frame_min,frame_max = util.get_min_max_frames(rpd.video_dir)

	print("Processing files from frame: " + str(frame_min).zfill(3) + " to: " + str(frame_max).zfill(3))

	for render_pass in config.render_passes:
		type = render_pass["type"]

		print(f"Executing render pass: {type}")
		
		input_dir = render_pass["input_dir"]
		output_dir = render_pass["output_dir"]

		if not os.path.exists(output_dir):
			os.makedirs(output_dir)
		
		util.copy_files_from_to(input_dir, config.temp_dir, ".png")

		if type == "comfyui":
			cfg = render_pass["cfg"]
			denoise = render_pass["denoise"]
			pos_prompt = render_pass["positive_prompt"]
			neg_prompt = render_pass["negative_prompt"]
			workflow = render_pass["workflow"]
			model = render_pass["model"]
			video_dir = render_pass["video_dir"]
			
			processors.process_comfyui(config.temp_dir, video_dir, output_dir, cfg, denoise, pos_prompt, neg_prompt, workflow, model)

		elif type == "ebsynth_blend":
			alpha = render_pass["alpha"]
			frame_spread = render_pass["frame_spread"]
			spread_alpha_multiplier = render_pass["spread_alpha_multiplier"]
			video_dir = render_pass["video_dir"]
			processors.process_ebsynth(config.temp_dir, output_dir, video_dir, alpha, frame_spread, spread_alpha_multiplier)

		elif type == "alpha_blend":
			alpha = render_pass["alpha"]
			blend_dir = render_pass["blend_dir"]
			processors.process_alpha_blend(config.temp_dir, blend_dir, output_dir, alpha)

	shutil.rmtree(config.temp_dir)
	if os.path.isfile(config.temp_file):
		os.remove(config.temp_file)

	print("DONE!")
finally:
	comfyui.close()