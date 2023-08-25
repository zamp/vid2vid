from PIL import Image
import comfyui
import util
import ebsynth
import cv2
import os
import shutil
import config

def generate_ebsynth(style_path, guide0_path, guide1_path):
	if not os.path.exists(style_path):
		print(f"ERROR: could not find file {style_path}")
		return
	if not os.path.exists(guide0_path):
		print(f"ERROR: could not find file {guide0_path}")
		return
	if not os.path.exists(guide1_path):
		print(f"ERROR: could not find file {guide1_path}")
		return

	eb = ebsynth.ebsynth(style_path, [(guide0_path, guide1_path)])
	result = cv2.cvtColor(eb.run(), cv2.COLOR_BGR2RGB)
	return Image.fromarray(result).convert("RGB")

def run_stable_diffusion(input_file_path:str, src_file_path:str, output_file_path:str, cfg:int, denoise:float, positive_prompt:str, negative_prompt:str, workflow_json:str, model:str):
	image = comfyui.process_image(input_file_path, src_file_path, cfg, denoise, positive_prompt, negative_prompt, workflow_json, model)
	# for some reason the images come out different size than put in?
	img = Image.open(input_file_path)
	if img.width != image.width or img.height != image.height:
		image = image.resize((img.width, img.height))
	image.save(output_file_path)

def process_comfyui(input_dir:str, video_dir:str, output_dir:str, cfg:int, denoise:float, positive_prompt:str, negative_prompt:str, workflow_json:str, model:str):
	files = util.get_png_files(input_dir)
	for file in files:
		run_stable_diffusion(input_dir+file, video_dir+file, output_dir+file, cfg, denoise, positive_prompt, negative_prompt, workflow_json, model)

def clamp(num, min_value, max_value):
   return max(min(num, max_value), min_value)

def process_ebsynth(input_dir, output_dir, video_dir, alpha, frame_spread, spread_alpha_multiplier):
	files = util.get_png_files(input_dir)

	min_frame, max_frame = util.get_min_max_frames(input_dir)

	for file in files:
		filename = file[:-4]
		ext = file[-4:]
		frame_number = int(filename)

		shutil.copy(input_dir+file, config.temp_file)

		sa = spread_alpha_multiplier*2

		for spread in range(1, frame_spread + 1):
			a = alpha * (sa / spread)
			
			spread_file = f"{str(clamp(frame_number + spread, min_frame, max_frame)).zfill(len(filename))}{ext}"
			if spread_file != file:
				src = Image.open(config.temp_file).convert("RGB")
				img = generate_ebsynth(input_dir+spread_file, video_dir+spread_file, video_dir+file)
				src = Image.blend(src, img, a)
				src.save(config.temp_file)			

			spread_file = f"{str(clamp(frame_number - spread, min_frame, max_frame)).zfill(len(filename))}{ext}"
			if spread_file != file:
				src = Image.open(config.temp_file).convert("RGB")
				img = generate_ebsynth(input_dir+spread_file, video_dir+spread_file, video_dir+file)
				src = Image.blend(src, img, a)
				src.save(config.temp_file)

		shutil.copy(config.temp_file, output_dir+file)

def process_alpha_blend(input_dir, blend_dir, output_dir, alpha):
	files = util.get_png_files(input_dir)
	for file in files:
		src = Image.open(input_dir+file).convert("RGB")
		img = Image.open(blend_dir+file).convert("RGB")
		src = Image.blend(src, img, alpha)
		src.save(output_dir+file)