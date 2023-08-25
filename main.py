import os
import shutil
import processors
import util
import configparser
import comfyui

def main():
	config = configparser.ConfigParser()	
	config.read(["example.config.ini", "config.ini"])

	defaults = config["DEFAULT"]

	if not "VideoDir" in defaults:
		print(f"Error: Could not find VideoDir in config.")
		return

	frame_min,frame_max = util.get_min_max_frames(defaults.get("VideoDir"))

	print("Processing files from frame: " + str(frame_min).zfill(3) + " to: " + str(frame_max).zfill(3))

	temp_dir = defaults.get("TempDir")
	temp_file = defaults.get("TempFile")

	for cfg in config:
		if not cfg.startswith("RenderPass"):
			continue

		render_pass = config[cfg]

		type = render_pass.get("Type")

		print(f"Executing render pass: {type}")
		
		input_dir = render_pass.get("InputDir")
		output_dir = render_pass.get("OutputDir")

		if not os.path.exists(output_dir):
			os.makedirs(output_dir)
		
		util.copy_files_from_to(input_dir, temp_dir, ".png")

		if type == "comfyui":
			cfg = render_pass.get("Cfg")
			denoise = render_pass.get("Denoise")
			pos_prompt = render_pass.get("PositivePrompt")
			neg_prompt = render_pass.get("NegativePrompt")
			workflow = render_pass.get("Workflow")
			model = render_pass.get("Model")
			video_dir = render_pass.get("VideoDir")
			
			processors.process_comfyui(temp_dir, video_dir, output_dir, cfg, denoise, pos_prompt, neg_prompt, workflow, model)

		elif type == "ebsynth_blend":
			alpha = render_pass.get("Alpha")
			frame_spread = render_pass.get("FrameSpread")
			spread_alpha_multiplier = render_pass.get("FrameSpreadAlphaMultiplier")
			video_dir = render_pass.get("VideoDir")
			processors.process_ebsynth(temp_file, temp_dir, output_dir, video_dir, alpha, frame_spread, spread_alpha_multiplier)

		elif type == "alpha_blend":
			alpha = render_pass.get("Alpha")
			input_dir = render_pass.get("InputDir")
			processors.process_alpha_blend(temp_dir, input_dir, output_dir, alpha)

	shutil.rmtree(temp_dir)
	if os.path.isfile(temp_file):
		os.remove(temp_file)

	print("DONE!")
	return

try:	
	comfyui.connect()
	main()
finally:
	comfyui.close()