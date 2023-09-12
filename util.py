import os
import shutil

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

def get_frame_int(frame):
	return int(frame[:-4])	