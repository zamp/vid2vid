# Setting this to a positive value will show that frame every time it is generated
debug_show_frame = -1

# set these to scale source video to this resolution, set to None to disable scaling
width = None
height = None

video_path = "video/"
output_path = "output/"
ebsynth_path = "ebsynth/"
seed = -1 # Set to -1 for random or a value between 0 and 18446744073709551616
comfyui_server_address = "127.0.0.1:8188"

upload_input_filename = "input.png"
upload_video_filename = None # Set to ex. "video.png" if you want the current video frame to be uploaded to comfyui

wf = "workflows/workflow_api.json"
pp = "YOUR POSITIVE PROMPT HERE" # Set to None to not override workflow value and just use what's in workflow
np = "YOUR NEGATIVE PROMPT HERE" # Set to None to not override workflow value and just use what's in workflow
mdl = "flat2DAnimerge_v30.safetensors" # Set to None to not override workflow value and just use what's in workflow

# Modify the values of these as you see fit, explanation is below
render_passes = [
	{"name": "initialize", "type": "default", "iterations": 1, "it_multiplier": 0.8, "workflow_json": wf, "model": mdl, "reinforce_source":0,    "temporal_blend":0,     "cfg":7, "denoise":0.5,  "positive_prompt": pp, "negative_prompt": np},
    {"name": "reinforce",  "type": "default", "iterations": 2, "it_multiplier": 0.8, "workflow_json": wf, "model": mdl, "reinforce_source":0.65, "temporal_blend":0.3, "cfg":7, "denoise":0.43, "positive_prompt": pp, "negative_prompt": np},
    {"name": "stabilize",  "type": "default", "iterations": 3, "it_multiplier": 0.8, "workflow_json": wf, "model": mdl, "reinforce_source":0,    "temporal_blend":0.6, "cfg":7, "denoise":0.25, "positive_prompt": pp, "negative_prompt": np},
    {"name": "stylize",    "type": "default", "iterations": 1, "it_multiplier": 0.8, "workflow_json": wf, "model": mdl, "reinforce_source":0,    "temporal_blend":0.1, "cfg":9, "denoise":0.35, "positive_prompt": pp, "negative_prompt": np}
]

# "name" 
# Name of the pass, has no other use than to print to console

# "type"
# Type of the pass.
# default = pass where each frame is processed sequentially. Temporal blend will blend frames +1,+2,-1,-2 offset from current
# fast_tb = EXPERIMENTAL!!! Fast temporal blend pass. Blending occurs first<->middle<->last. Then the frame between first/middle, middle/last will be processed, etc.

# "iterations"
# How many times wil this render pass be run

# "it_multiplier"
# How much will all of the denoise, reinforce, blend values be multiplied with per iteration, cfg will not be touched

# "workflow_json"
# The workflow json file to load in comfyui

# "model"
# The model to use in comfyui, set to None to not override workflow

# "reinforce_source"
# How much of the original video frame is alpha blended back into the currently processed frame before SD is run. Range 0 - 1. 0 = fully transparent and 1 = fully opaque (think layer opacity in photoshop)

# "temporal_blend"
# How much of the ebsynth guess frame is alpha blended back into the currently processed frame before SD is run. Range 0 - 1. 0 = fully transparent and 1 = fully opaque (think layer opacity in photoshop)

# "cfg"
# Config value for comfyui sampler

# "denoise"
# Denoise value for comfyui sampler

# "positive_prompt"
# Positive for comfyui text clip. Set to None to disable and use what is in workflow.json

# "negative_prompt"
# Positive for comfyui text clip. Set to None to disable and use what is in workflow.json