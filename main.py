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

	for cfg in config:
		if not cfg.startswith("RenderPass"):
			continue

		render_pass = config[cfg]
		node_id = render_pass.get("NodeId")  # Extract node_id from the configuration

		type = render_pass.get("Type")

		print(f"Executing render pass: {cfg} ({type})")
		
		input_dir = render_pass.get("InputDir")
		output_dir = render_pass.get("OutputDir")

		if not os.path.exists(output_dir):
			os.makedirs(output_dir)
		
		util.copy_files_from_to(input_dir, temp_dir, ".png")

		if type == "comfyui":

			seed = render_pass.get("Seed")

			cfg = render_pass.getint("Cfg")
			denoise = render_pass.getfloat("Denoise")
			pos_prompt = render_pass.get("PositivePrompt")
			neg_prompt = render_pass.get("NegativePrompt")
			workflow = render_pass.get("Workflow")
			model = render_pass.get("Model")
			video_dir = render_pass.get("VideoDir")
			processors.process_comfyui(temp_dir, video_dir, output_dir, cfg, denoise, pos_prompt, neg_prompt, workflow, model, node_id, seed)

		elif type == "ebsynth_blend":
			alpha = render_pass.getfloat("Alpha")
			frame_spread = render_pass.getint("FrameSpread")
			spread_alpha_multiplier = render_pass.getfloat("FrameSpreadAlphaMultiplier")
			video_dir = render_pass.get("VideoDir")
			ebsynth_dir = defaults.get("EbsynthDir")
			ebsynth_exe = defaults.get("EbsynthExe")
			max_files = defaults.getint("MaxEbsynthFiles")
			automatic = defaults.getboolean("AutomateEbsynth")
			processors.process_ebsynth(automatic, max_files, ebsynth_exe, ebsynth_dir, temp_dir, output_dir, video_dir, alpha, frame_spread, spread_alpha_multiplier)

		elif type == "alpha_blend":
			alpha = render_pass.getfloat("Alpha")
			blend_dir = render_pass.get("BlendDir")
			output_dir = render_pass.get("OutputDir")
			processors.process_alpha_blend(temp_dir, blend_dir, output_dir, alpha)

	shutil.rmtree(temp_dir)

	print("DONE!")
	return

try:	
	comfyui.connect()
	main()
finally:
	comfyui.close()