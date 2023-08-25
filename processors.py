import config
import shutil
import os
from PIL import Image
from run_ebsynth import run_ebsynth
from run_ebsynth import apply_ebsynth
from run_ebsynth import generate_ebsynth_from
import threading
import comfyui

def get_filename(i):
	return str(i).zfill(3)+".png"
def get_frame_dir(i):
	return config.ebsynth_path+str(i).zfill(3)+"/"

def run_stable_diffusion(input_file_path, src_file_path, output_file_path, cfg, denoise, positive_prompt, negative_prompt, workflow_json, model):
	image = comfyui.process_image(input_file_path, src_file_path, cfg, denoise, positive_prompt, negative_prompt, workflow_json, model)
	# for some reason the images come out different size than put in?
	img = Image.open(input_file_path)
	if img.width != image.width or img.height != image.height:
		image = image.resize((img.width, img.height))
	image.save(output_file_path)

def process_frames(frame_min, frame_max, temporal_blend, reinforce_source_alpha, cfg, denoise, positive_prompt, negative_prompt, workflow_json, model):
	if temporal_blend > 0:
		# delete old ebsynth files
		if os.path.exists(config.ebsynth_path):
			shutil.rmtree(config.ebsynth_path)
		os.makedirs(config.ebsynth_path)

		# copy output to ebsynth directories
		for i in range(frame_min, frame_max+1):
			frame_dir = get_frame_dir(i)
			if not os.path.exists(frame_dir):
				os.makedirs(frame_dir)
			shutil.copy(config.output_path+get_filename(i), frame_dir+get_filename(i))

	stable_diffusion_thread = None

	for i in range(frame_min, frame_max+1):
		print(f"Processing frame: {get_filename(i)}")

		frame_path = config.output_path+get_filename(i)
		video_frame_path = config.video_path+get_filename(i)

		if temporal_blend > 0 or reinforce_source_alpha > 0:			
			run_ebsynth(i)
			run_ebsynth(i+1)
			run_ebsynth(i+2)
			run_ebsynth(i-1)
			run_ebsynth(i-2)

			if stable_diffusion_thread != None:
				stable_diffusion_thread.join() # wait for stable diffusion to complete
				stable_diffusion_thread = None

			frame = Image.open(frame_path).convert("RGB")

			if temporal_blend > 0.0:
				frame = apply_ebsynth(frame, i - 1, 1, temporal_blend)
				frame = apply_ebsynth(frame, i + 1, -1, temporal_blend)
				frame = apply_ebsynth(frame, i - 2, 2, temporal_blend * 0.5)
				frame = apply_ebsynth(frame, i + 2, -2, temporal_blend * 0.5)

			if reinforce_source_alpha > 0.0:
				video_frame = Image.open(video_frame_path).convert("RGB")
				frame = Image.blend(frame, video_frame, reinforce_source_alpha)

			frame.save(frame_path)

		if stable_diffusion_thread != None:
			stable_diffusion_thread.join() # wait for stable diffusion to complete
			stable_diffusion_thread = None
		
		stable_diffusion_thread = threading.Thread(target=run_stable_diffusion, args=(frame_path, video_frame_path, frame_path,cfg,denoise,positive_prompt,negative_prompt,workflow_json, model))
		stable_diffusion_thread.start()

		if config.debug_show_frame == i:
			stable_diffusion_thread.join()
			stable_diffusion_thread = None
			frame = Image.open(frame_path).convert("RGB")
			frame.show("frame")
	stable_diffusion_thread.join()

def append_frame_pairs(list_: list[int], start, end):
    stack = [(start, end)]
    
    while stack:
        start, end = stack.pop()
        if abs(start - end) < 2:
            continue
        
        middle = (start + end) // 2
        list_.append((start, middle))
        list_.append((middle, end))
        
        stack.append((start, middle))
        stack.append((middle, end))
	
def alpha_blend_images(src, blend, dst, alpha):
	src_img = Image.open(src).convert("RGB")
	if alpha > 0.0:
		blend_img = Image.open(blend).convert("RGB")
		src_img = Image.blend(src_img, blend_img, alpha)
	src_img.save(dst)

def process_frames_fast_tb(frame_min, frame_max, temporal_blend, reinforce_source_alpha, cfg, denoise, positive_prompt, negative_prompt, workflow_json, model):
	if temporal_blend > 0:
		# delete old ebsynth files
		if os.path.exists(config.ebsynth_path):
			shutil.rmtree(config.ebsynth_path)
		os.makedirs(config.ebsynth_path)

		# copy output to ebsynth directories
		for i in range(frame_min, frame_max+1):
			frame_dir = get_frame_dir(i)
			if not os.path.exists(frame_dir):
				os.makedirs(frame_dir)
			shutil.copy(config.output_path+get_filename(i), frame_dir+get_filename(i))
		
	# make frame pairs
	pairs = []
	append_frame_pairs(pairs, frame_min, frame_max)

	#print(pairs)
	threads = []

	for (start,end) in pairs:
		print(f"Processing frame pair {start}/{end}")
		start_path = config.output_path+get_filename(start)
		end_path = config.output_path+get_filename(end)

		ebsynth_start_path = config.ebsynth_path+get_filename(start)
		ebsynth_end_path = config.ebsynth_path+get_filename(end)

		guide0_path = config.video_path+get_filename(start)
		guide1_path = config.video_path+get_filename(end)

		if temporal_blend > 0:
			generate_ebsynth_from(start_path, guide0_path, guide1_path, ebsynth_start_path, True)
			generate_ebsynth_from(end_path, guide1_path, guide0_path, ebsynth_end_path, True)

			alpha_blend_images(start_path, ebsynth_start_path, ebsynth_start_path, temporal_blend)
			alpha_blend_images(end_path, ebsynth_end_path, ebsynth_end_path, temporal_blend)
		else:
			print("fast_tb running with 0 temporal blend. This makes no sense! fast_tb will only work if temporal blend is > 0!")

		for thread in threads:
			thread.join()
		threads.clear()

		#threads.append(threading.Thread(target=run_stable_diffusion, args=(ebsynth_start_path, guide0_path, start_path,cfg,denoise,positive_prompt,negative_prompt,workflow_json, model)))
		#threads.append(threading.Thread(target=run_stable_diffusion, args=(ebsynth_end_path, guide0_path, end_path,cfg,denoise,positive_prompt,negative_prompt,workflow_json, model)))		

		for thread in threads:
			thread.start()

	for thread in threads:
		thread.join()
	return

	for i in range(frame_min, frame_max+1):
		print(f"Processing frame: {get_filename(i)}")

		frame_path = config.output_path+get_filename(i)
		video_frame_path = config.video_path+get_filename(i)

		if temporal_blend > 0 or reinforce_source_alpha > 0:			
			run_ebsynth(i)
			run_ebsynth(i+1)
			run_ebsynth(i+2)
			run_ebsynth(i-1)
			run_ebsynth(i-2)

			if stable_diffusion_thread != None:
				stable_diffusion_thread.join() # wait for stable diffusion to complete
				stable_diffusion_thread = None

			frame = Image.open(frame_path).convert("RGB")

			if temporal_blend > 0.0:
				frame = apply_ebsynth(frame, i - 1, 1, temporal_blend)
				frame = apply_ebsynth(frame, i + 1, -1, temporal_blend)
				frame = apply_ebsynth(frame, i - 2, 2, temporal_blend * 0.5)
				frame = apply_ebsynth(frame, i + 2, -2, temporal_blend * 0.5)

			if reinforce_source_alpha > 0.0:
				video_frame = Image.open(video_frame_path).convert("RGB")
				frame = Image.blend(frame, video_frame, reinforce_source_alpha)

			frame.save(frame_path)

		if stable_diffusion_thread != None:
			stable_diffusion_thread.join() # wait for stable diffusion to complete
			stable_diffusion_thread = None
		
		stable_diffusion_thread = threading.Thread(target=run_stable_diffusion, args=(frame_path, video_frame_path, frame_path,cfg,denoise,positive_prompt,negative_prompt,workflow_json, model))
		stable_diffusion_thread.start()

		if config.debug_show_frame == i:
			stable_diffusion_thread.join()
			stable_diffusion_thread = None
			frame = Image.open(frame_path).convert("RGB")
			frame.show("frame")
	
	stable_diffusion_thread.join()