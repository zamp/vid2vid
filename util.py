import os
import shutil
import render_pass_defaults

def copy_files_from_to(from_dir:str, to_dir:str, file_ext:str):
	files = os.listdir(from_dir)
	files = [f for f in files if os.path.isfile(from_dir+f) and f.endswith(file_ext)]

	if os.path.exists(to_dir):
		shutil.rmtree(to_dir)

	os.makedirs(to_dir)	

	for f in files:
		shutil.copy(from_dir+f, to_dir+f)

def get_png_files(from_path:str):
	files = os.listdir(from_path)
	files = [f for f in files if os.path.isfile(from_path+f) and f.endswith(".png")]
	return files

def get_min_max_frames(file_dir:str):
	files = get_png_files(file_dir)

	frame_max = 0
	for file in files:
		frame_max = max(int(file[:3]), frame_max)

	frame_min = frame_max
	for file in files:
		frame_min = min(int(file[:3]), frame_min)

	return frame_min, frame_max

def rp_gen_comfyui(input_dir:str = render_pass_defaults.input_dir, output_dir:str = render_pass_defaults.output_dir, video_dir:str = render_pass_defaults.video_dir, workflow:str = render_pass_defaults.workflow, model:str = render_pass_defaults.model, cfg:int = render_pass_defaults.cfg, denoise:float = render_pass_defaults.denoise, positive_prompt:str = render_pass_defaults.positive_prompt, negative_prompt:str = render_pass_defaults.negative_prompt):
	return {"type": "comfyui", "input_dir": input_dir, "video_dir": video_dir, "output_dir": output_dir, "workflow":workflow, "model":model, "cfg":cfg, "denoise": denoise, "positive_prompt": positive_prompt, "negative_prompt": negative_prompt }
def rp_gen_ebsynth_blend(input_dir:str = render_pass_defaults.input_dir, output_dir:str = render_pass_defaults.output_dir, video_dir:str = render_pass_defaults.video_dir, alpha:float = render_pass_defaults.alpha, frame_spread:int = render_pass_defaults.frame_spread, spread_alpha_multiplier:float = render_pass_defaults.spread_alpha_multiplier):
	return {"type": "ebsynth_blend", "input_dir": input_dir, "output_dir": output_dir, "video_dir": video_dir, "alpha": alpha, "frame_spread": frame_spread, "spread_alpha_multiplier": spread_alpha_multiplier }
def rp_gen_alpha_blend(input_dir:str = render_pass_defaults.input_dir, output_dir:str = render_pass_defaults.output_dir, video_dir:str = render_pass_defaults.video_dir, alpha:float = render_pass_defaults.alpha):
	return {"type": "alpha_blend", "input_dir": input_dir, "blend_dir": video_dir, "output_dir": output_dir, "alpha": alpha }