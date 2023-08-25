import util
import render_pass_defaults as rpd

temp_dir = "temp/"
temp_file = "temp.png"

seed = -1 # Set to -1 for random or a value between 0 and 18446744073709551616
comfyui_server_address = "127.0.0.1:8188"

upload_input_filename = "input.png"
upload_video_filename = None # Set to ex. "video.png" if you want the current video frame to be uploaded to comfyui

# Change these to your liking
positive_prompt = "best quality"
negative_prompt = "very bad quality"

# If you want to do global modifications to render passes please change the render_pass_defaults.py

# Modify the values of these as you see fit, explanation is below
render_passes = [
	util.rp_gen_comfyui(input_dir = rpd.video_dir, cfg=8, denoise=0.3, positive_prompt=positive_prompt, negative_prompt=negative_prompt),
	util.rp_gen_ebsynth_blend(alpha = 0.5),
    util.rp_gen_alpha_blend(alpha = 0.3),
    
	util.rp_gen_comfyui(cfg=8, denoise=0.2, positive_prompt=positive_prompt, negative_prompt=negative_prompt),
	util.rp_gen_ebsynth_blend(alpha = 0.25),
    util.rp_gen_alpha_blend(alpha = 0.15),
    
	util.rp_gen_comfyui(cfg=8, denoise=0.1, positive_prompt=positive_prompt, negative_prompt=negative_prompt),
	util.rp_gen_ebsynth_blend(alpha = 0.125),
    util.rp_gen_alpha_blend(alpha = 0.075),
    
	util.rp_gen_comfyui(cfg=8, denoise=0.05, positive_prompt=positive_prompt, negative_prompt=negative_prompt)
]

# Common settings:
# input_dir
# directory to use as source files for this pass
# output_dir
# directory to save output of this pass
# video_dir
# directory where the original video is

# comfyui / rp_gen_comfyui
# Runs comfyui pass with given workflow, model, cfg, denoise, and positive & negative prompts.

# ebsynth_blend / rp_gen_ebsynth_blend
# Runs ebsynth on each frame. 
# alpha = how much to blend ebsynth result into input file
# frame_spread = how many frames to spread for ebsynth
# spread_alpha_multiplier = how much will alpha be multiplied with based on how far the frame has spread
#   Example: 
#       You have 10 video frames, frame_spread = 5, alpha = 5, spread_alpha_multiplier = 5
#       The alpha will drop based on the multiplier per spread frame
#       When this pass is processing frame 5 it will blend frames 4,6 first at 0.5 alpha, then 3,7 at 0.25 alpha, then 2,8 at 0.125 alpha, then 1,9 at 0.0625 alpha, then 0,10 at 0.03125 alpha

# alpha blend / rp_gen_alpha_blend
# Alpha blends blend_dir into input_dir
# alpha = how much to blend
