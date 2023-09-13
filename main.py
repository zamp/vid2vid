import os
import shutil
import processors
import util
import configparser
import uuid

def fix_config(config):
	if not os.path.exists(config):	
		return
	
	file = open(config, "r")
	lines = file.readlines()
	for index in range(0, len(lines)):
		line = lines[index]
		if line.startswith("[RenderPass"):
			line = line[1:-2]
			arr = line.split(".")
			if len(arr) < 3:
				arr.append(0)
			arr[2] = f"{uuid.uuid4()}"
			lines[index] = f"[{'.'.join(arr)}]\r\n"
		if line.startswith("[ExtraPrompt"):
			line = line[1:-2]
			lines[index] = f"[{line}.{uuid.uuid4()}]\r\n"

	file.close()
	return "".join(lines)

def main():
	config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())

	config.read_string(fix_config("config/example.config.ini"))
	config.read_string(fix_config("config/config.ini"))

	defaults = config["DEFAULT"]

	if defaults.getboolean("UseExampleRenderPasses"):
		config.read_string(fix_config("config/example.renderpasses.ini"))

	if not "VideoDir" in defaults:
		print(f"Error: Could not find VideoDir in config.")
		return

	frame_min,frame_max = util.get_min_max_frames(defaults.get("VideoDir"))

	copy_temp = defaults.getboolean("CopyOutputToTempBetweenPasses")

	emotion_tokens = None
	if defaults.getboolean("DetectEmotions", fallback=False):
		print("Processing emotions...")
		import analyze_face
		emotion_tokens = analyze_face.analyze_face_tokens_from_files(defaults.get("VideoDir"))

	print("Processing files from frame: " + str(frame_min).zfill(3) + " to: " + str(frame_max).zfill(3))

	for config_name in config:
		if not config_name.startswith("RenderPass"):
			continue

		arr = config_name.split(".")
		name = arr[0]
		type = arr[1]

		print(f"Executing pass: {name} ({type})")

		rp_config = config[config_name]

		if type == "del_files":
			dir = rp_config.get("Dir")
			if os.path.exists(dir):
				shutil.rmtree(dir)

		if type == "copy_files":
			fromdir = rp_config.get("From")
			todir = rp_config.get("To")
			util.copy_files_from_to(fromdir, todir, ".png")

		if type == "comfyui":
			processors.process_comfyui(rp_config, config, emotion_tokens)

		elif type == "ebsynth_blend":
			processors.process_ebsynth(rp_config)

		elif type == "alpha_blend":
			processors.process_alpha_blend(rp_config)

		if copy_temp:
			if os.path.exists(defaults.get("OutputDir")):
				util.copy_files_from_to(defaults.get("OutputDir"), defaults.get("TempDir"), ".png")

		if rp_config.getboolean("WaitForUserInput", fallback=False):
			input("Press enter to continue...")

	print("DONE!")
	return

main()