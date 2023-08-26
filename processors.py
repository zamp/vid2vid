from PIL import Image
import comfyui
import util
from ebsynth import EBSynthProject
import os
import shutil
import subprocess
import numpy as np

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

def divide_chunks(l, n):
	for i in range(0, len(l), n):
		yield l[i:i + n]

def blend_img(ebsynth_dir, input_dir, frame, offset_frame, file_name_length, ext, alpha):
	warped_img_path = f"{ebsynth_dir}{str(offset_frame).zfill(file_name_length)}/{str(frame).zfill(file_name_length)}{ext}"
	output_img_path = f"{input_dir}{str(frame).zfill(file_name_length)}{ext}"

	if not os.path.exists(warped_img_path) or not os.path.exists(output_img_path):
		return

	warped_img = Image.open(warped_img_path).convert("RGB")
	output_img = Image.open(output_img_path).convert("RGB")

	offset = abs(int(frame) - int(offset_frame))

	a = alpha / offset

	output_img = Image.blend(output_img, warped_img, a)
	output_img.save(f"{input_dir}{str(frame).zfill(file_name_length)}{ext}")

def run_ebsynth(project, ebsynth_exe):
	ebs_file = "generated.ebs"
	project.WriteToFile(ebs_file)

	project.keyFrames = []

	# TODO: make this script press Run-All button and wait for processing to complete
	o = subprocess.Popen(['cmd','/c',f"{ebsynth_exe} {os.path.abspath(ebs_file)}"])
	o.wait()

	os.remove(ebs_file)

def process_ebsynth(max_ebsynth_files:int, ebsynth_exe:str, ebsynth_dir:str, input_dir:str, output_dir:str, video_dir:str, alpha:float, frame_spread:int, spread_alpha_multiplier:float):
	if os.path.exists(ebsynth_dir):
		shutil.rmtree(ebsynth_dir)
	os.makedirs(ebsynth_dir)

	input_files = util.get_png_files(input_dir)
	input_file = input_files[0]
	file_name_length = len(input_file[:-4])
	ext = input_file[-4:]
	filenumber_hashes = ""
	for i in range(file_name_length):
		filenumber_hashes += "#"

	min_frame, max_frame = util.get_min_max_frames(input_dir)

	keys_path = f"{input_dir}[{filenumber_hashes}]{ext}"
	video_path = f"{video_dir}[{filenumber_hashes}]{ext}"

	project = EBSynthProject(video_path, keys_path, "", False)

	for file in input_files:
		frame = int(file[:-4])

		ebsynth_output_dir = f"{ebsynth_dir}{str(frame).zfill(file_name_length)}/[{filenumber_hashes}]{ext}"
		
		minframe = frame - frame_spread
		maxframe = frame + frame_spread

		use_min_frame = True
		use_max_frame = True

		if minframe < min_frame:
			minframe = min_frame
			use_min_frame = False
		if maxframe > max_frame:
			maxframe = max_frame
			use_max_frame = False

		project.AddKeyFrame(use_min_frame, use_max_frame, minframe, frame, maxframe, ebsynth_output_dir)

		if len(project.keyFrames) >= max_ebsynth_files:
			run_ebsynth(project, ebsynth_exe)

	run_ebsynth(project, ebsynth_exe)

	# blend ebsynth files now that they are generated
	for file in input_files:
		frame = int(file[:-4])
		for offset in range(1, frame_spread+1):
			blend_img(ebsynth_dir, input_dir, frame, frame - offset, file_name_length, ext, alpha)
			blend_img(ebsynth_dir, input_dir, frame, frame + offset, file_name_length, ext, alpha)
	
	shutil.rmtree(ebsynth_dir)

	util.copy_files_from_to(input_dir, output_dir, ".png")

def process_alpha_blend(input_dir, blend_dir, output_dir, alpha):
	files = util.get_png_files(input_dir)
	for file in files:
		src = Image.open(input_dir+file).convert("RGB")
		img = Image.open(blend_dir+file).convert("RGB")
		src = Image.blend(src, img, float(alpha))
		src.save(output_dir+file)