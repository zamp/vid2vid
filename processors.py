from PIL import Image
import comfyui
import util
from ebsynth import EBSynthProject
import os
import shutil
import subprocess
import threading
import ebsynth_window
from configparser import SectionProxy
from configparser import ConfigParser
from glob import glob

def run_stable_diffusion(input_file_path:str, src_file_path:str, output_file_path:str, config:SectionProxy, extra_config:SectionProxy, emotion_tokens:str):
	try:
		comfyui.connect(config.get("ComfyUI_ServerAddress"))
		image = comfyui.process_image(input_file_path, src_file_path, config, extra_config, emotion_tokens)

		# for some reason the images come out different size than put in?
		img = Image.open(input_file_path)
		if img.width != image.width or img.height != image.height:
			print("Warning: comfyui output file resolution is not the same as input resolution. Resizing to match input file resolution.")
			image = image.resize((img.width, img.height))
		image.save(output_file_path)
	finally:
		comfyui.close()

def get_extra_prompts(frame:int, extra_prompts:dict):
	ep = extra_prompts.get(frame)
	if ep != None:
		return (ep.positive, ep.negative)
	return (None, None)

def is_in_extra_frames(frame:int, frames:str):
	if frame == None:
		return False
	if frames == None:
		return False
	frame_ranges = str.split(frames, ",")
	for cur_range in frame_ranges:
		if str.find(cur_range, "-") == -1: # not a range
			if int(cur_range) == frame:
				return True
		else:
			cur_range_split = str.split(cur_range, "-")
			start = int(cur_range_split[0])
			end = int(cur_range_split[1])
			if frame >= start and frame <= end:
				return True			
			
	return False

def get_extra_config(frame:int, config:ConfigParser):
	for config_name in config:
		if not config_name.startswith("ExtraPrompt"):
			continue
		ep_config = config[config_name]
		if ep_config.getint("Frame") == frame:
			return ep_config
		if is_in_extra_frames(frame, ep_config.get("Frames")):
			return ep_config
	return None

def get_tokens_for_frame(frame:int, emotion_tokens:dict):
	if emotion_tokens == None:
		return ""
	if frame in emotion_tokens:
		return emotion_tokens[frame]
	return None

def process_comfyui(config:SectionProxy, full_config:ConfigParser, emotion_tokens:dict):
	input_dir = config.get("InputDir")
	output_dir = config.get("OutputDir")
	video_dir = config.get("VideoDir")

	if not os.path.exists(output_dir):
		os.makedirs(output_dir)

	if config.getboolean("PingPong", fallback=False):
		files = util.get_png_files(video_dir)

		first = files[0]
		extra_config = get_extra_config(util.get_frame_int(first), full_config)
		
		run_stable_diffusion(input_dir+first, video_dir+first, output_dir+first, config, extra_config, get_tokens_for_frame(util.get_frame_int(first), emotion_tokens))

		last = files[len(files)-1]
		extra_config = get_extra_config(util.get_frame_int(last), full_config)
		run_stable_diffusion(input_dir+last, video_dir+last, output_dir+last, config, extra_config, get_tokens_for_frame(util.get_frame_int(last), emotion_tokens))
	else:
		limit_frames = config.getint("SkipFrames", fallback=0) + 1
		files = util.get_png_files(video_dir)
		start_frame = config.getint("StartFrame", fallback=int(files[0][:-4]))
		for file in files:
			frame = util.get_frame_int(file)

			# skip frames that are outside of limit
			if (frame - start_frame) % limit_frames != 0:
				continue

			extra_config = get_extra_config(frame, full_config)
			run_stable_diffusion(input_dir+file, video_dir+file, output_dir+file, config, extra_config, get_tokens_for_frame(frame, emotion_tokens))

def clamp(num, min_value, max_value):
   return max(min(num, max_value), min_value)	

def divide_chunks(l, n):
	for i in range(0, len(l), n):
		yield l[i:i + n]

def wait_for_ebsynth_to_complete(automatic, process:subprocess.Popen):
	if automatic:
		ebsynth_window.wait_and_kill()
	else:
		process.wait()

def run_ebsynth(automatic, project, ebsynth_exe):
	if not os.path.exists(ebsynth_exe):
		print("Error: Could not find ebsynth executable.")

	ebs_file = "generated.ebs"
	project.WriteToFile(ebs_file)

	process = subprocess.Popen(['cmd','/c',f"{ebsynth_exe} {os.path.abspath(ebs_file)}"])	
	thread = threading.Thread(target=wait_for_ebsynth_to_complete, args=[automatic, process])
	thread.start()
	thread.join()
	
	os.remove(ebs_file)

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

def average_img(imlist):
    N = len(imlist)
    avg=Image.open(imlist[0]).convert("RGB")
    for i in range(1,N):
        img=Image.open(imlist[i]).convert("RGB")
        avg=Image.blend(avg,img,1.0/float(i+1))
    return avg

def process_ebsynth(config:SectionProxy):
	ebsynth_dir = config.get("EbsynthDir")
	video_dir = config.get("VideoDir")
	input_dir = config.get("InputDir")
	output_dir = config.get("OutputDir")

	frame_spread = config.getint("FrameSpread")
	ebsynth_exe = config.get("EbsynthExe")
	max_ebsynth_files = config.getint("MaxEbsynthFiles")
	automatic = config.getboolean("AutomateEbsynth")

	if os.path.exists(ebsynth_dir):
		shutil.rmtree(ebsynth_dir)
	os.makedirs(ebsynth_dir)

	input_files = util.get_png_files(video_dir)
	input_file = input_files[0]
	file_name_length = len(input_file[:-4])
	ext = input_file[-4:]
	filenumber_hashes = ""
	for i in range(file_name_length):
		filenumber_hashes += "#"

	min_frame, max_frame = util.get_min_max_frames(video_dir)

	keys_path = f"{input_dir}[{filenumber_hashes}]{ext}"
	video_path = f"{video_dir}[{filenumber_hashes}]{ext}"

	project = EBSynthProject(video_path, keys_path, "", False)
	project.keyFrames = []

	limit_frames = config.getint("SkipFrames", fallback=1)+1
	frame_spread = max(limit_frames, frame_spread)

	start_frame = config.getint("StartFrame", fallback=int(input_files[0][:-4]))

	if config.getboolean("PingPong", fallback=False):
		ebsynth_output_dir = f"{ebsynth_dir}{str(min_frame).zfill(file_name_length)}/[{filenumber_hashes}]{ext}"
		project.AddKeyFrame(False, True, min_frame, min_frame, max_frame, ebsynth_output_dir)
		ebsynth_output_dir = f"{ebsynth_dir}{str(max_frame).zfill(file_name_length)}/[{filenumber_hashes}]{ext}"
		project.AddKeyFrame(True, False, min_frame, max_frame, max_frame, ebsynth_output_dir)
	else:
		for file in input_files:
			frame = util.get_frame_int(file)

			ebsynth_output_dir = f"{ebsynth_dir}{str(frame).zfill(file_name_length)}/[{filenumber_hashes}]{ext}"

			# skip frames that are outside of limit
			if (frame - start_frame) % limit_frames != 0:
				continue

			if not os.path.exists(input_dir+file):
				print(f"Error: Could not find file {file} for ebsynth. Make sure SkipFrames is the same as previous comfyui pass.")
				continue
			
			if config.getboolean("ForwardOnly", fallback=False):
				minframe = frame
			else:
				minframe = frame - frame_spread
			maxframe = frame + frame_spread

			use_min_frame = True
			use_max_frame = True

			if minframe < min_frame:
				minframe = min_frame
				if minframe == frame:
					use_min_frame = False
			if maxframe > max_frame:
				maxframe = max_frame
				if maxframe == frame:
					use_max_frame = False

			project.AddKeyFrame(use_min_frame, use_max_frame, minframe, frame, maxframe, ebsynth_output_dir)

			if len(project.keyFrames) >= max_ebsynth_files:
				run_ebsynth(automatic, project, ebsynth_exe)
				project.keyFrames = []

	if len(project.keyFrames) > 0:
		run_ebsynth(automatic, project, ebsynth_exe)

	# blend ebsynth files now that they are generated

	files = []
	start_dir = ebsynth_dir
	pattern = f"*{ext}"

	for dir,_,_ in os.walk(start_dir):
		files.extend(glob(os.path.join(dir,pattern))) 

	alpha = config.getfloat("Alpha", fallback=1)

	for file in input_files:
		blendable_files = []

		for blend_file in files:
			f = blend_file[-(file_name_length + 4):]
			if f == file:
				blendable_files.append(blend_file)
		
		#print(file, blendable_files)
		avg = average_img(blendable_files)

		input_path = f"{input_dir}{file}"
		output_path = f"{output_dir}{file}"

		if os.path.exists(input_path):
			output_img = Image.open(input_path).convert("RGB")
			output_img = Image.blend(output_img, avg, alpha)
			output_img.save(output_path)
		else:
			avg.save(output_path)
	
	shutil.rmtree(ebsynth_dir)

def process_alpha_blend(config:SectionProxy):
	alpha = config.getfloat("Alpha")
	input_dir = config.get("InputDir")
	blend_dir = config.get("BlendDir")
	output_dir = config.get("OutputDir")


	files = util.get_png_files(input_dir)
	for file in files:
		src = Image.open(input_dir+file).convert("RGB")
		img = Image.open(blend_dir+file).convert("RGB")
		src = Image.blend(src, img, float(alpha))
		src.save(output_dir+file)