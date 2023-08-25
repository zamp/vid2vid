# Setting this to a positive value will show that frame every time it is generated
debug_show_frame = -1

temp_dir = "temp/"
video_dir = "video/"
output_dir = "output/"

seed = -1 # Set to -1 for random or a value between 0 and 18446744073709551616
comfyui_server_address = "127.0.0.1:8188"

upload_input_filename = "input.png"
upload_video_filename = None # Set to ex. "video.png" if you want the current video frame to be uploaded to comfyui

wf = "workflows/workflow_api.json"
pp = "masterpiece, perfect anime illustration, best quality, 8k, highres, "
np = "(embedding:easynegative:1), low quality,"
mdl = "flat2DAnimerge_v30.safetensors"

pp = None # Uncomment to not override workflow value and just use what's in workflow
np = None # Uncomment to not override workflow value and just use what's in workflow
mdl = None # Uncomment to not override workflow value and just use what's in workflow

# Modify the values of these as you see fit, explanation is below
render_passes = [
    {"type": "comfyui", "input_dir": video_dir, "video_dir": video_dir, "output_dir": output_dir, "workflow":wf, "model":mdl, "cfg":8, "denoise": 0.5, "positive_prompt": pp, "negative_prompt": np },
    {"type": "ebsynth_blend", "input_dir": output_dir, "output_dir": output_dir, "alpha": 0.5, "frame_spread": 2, "spread_alpha_multiplier": 0.5 },
	{"type": "alpha_blend", "input_dir": output_dir, "blend_dir": video_dir, "output_dir": output_dir, "alpha": 0.5 },

    {"type": "comfyui", "input_dir": video_dir, "video_dir": video_dir, "output_dir": output_dir, "workflow":wf, "model":mdl, "cfg":8, "denoise": 0.4, "positive_prompt": pp, "negative_prompt": np },
    {"type": "ebsynth_blend", "input_dir": output_dir, "output_dir": output_dir, "alpha": 0.5, "frame_spread": 2, "spread_alpha_multiplier": 0.25 },
	{"type": "alpha_blend", "input_dir": output_dir, "blend_dir": video_dir, "output_dir": output_dir, "alpha": 0.25 },

    {"type": "comfyui", "input_dir": video_dir, "video_dir": video_dir, "output_dir": output_dir, "workflow":wf, "model":mdl, "cfg":8, "denoise": 0.25, "positive_prompt": pp, "negative_prompt": np },
    {"type": "ebsynth_blend", "input_dir": output_dir, "output_dir": output_dir, "alpha": 0.5, "frame_spread": 2, "spread_alpha_multiplier": 0.125 },
	{"type": "alpha_blend", "input_dir": output_dir, "blend_dir": video_dir, "output_dir": output_dir, "alpha": 0.125 },
]

# Common settings:
# input_dir
# directory to use as source files for this pass
# output_dir
# directory to save output of this pass

# comfyui
# Runs comfyui pass with given workflow, model, cfg, denoise, and positive & negative prompts.

# ebsynth_blend
# Runs ebsynth on each frame. 
# alpha = how much to blend ebsynth result into input file
# frame_spread = how many frames to spread for ebsynth
# spread_alpha_multiplier = how much will alpha be multiplied with based on how far the frame has spread
#   Example: 
#       You have 10 video frames, frame_spread = 5, alpha = 5, spread_alpha_multiplier = 5
#       The alpha will drop based on the multiplier per spread frame
#       When this pass is processing frame 5 it will blend frames 4,6 first at 0.5 alpha, then 3,7 at 0.25 alpha, then 2,8 at 0.125 alpha, then 1,9 at 0.0625 alpha, then 0,10 at 0.03125 alpha

# alpha blend
# Alpha blends blend_dir into input_dir
# alpha = how much to blend