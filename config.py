# setting this to a positive value will show that frame every time it is generated
debug_show_frame = -1

positive_prompt = "positive prompt here"
negative_prompt = "negative prompt here"

workflow_json = "workflow_api.json"

video_path = "video/"
output_path = "output/"
ebsynth_path = "ebsynth/"
use_random_seed = True
comfyui_server_address = "127.0.0.1:8188"
# change this to your install path of your comfy ui
comfyui_input_path = "..\ComfyUI\input\input.png"

# how much will all of the denoise, reinforce, blend values be multiplied with per iteration, cfg will not be touched
iteration_multiplier = 0.666 # hail satan

steps = [
	{"step":"initialize",		"iterations": 1,	"cfg":8,	"denoise":0.25,	"reinforce_source":0,		"temporal_blend":0},
	{"step":"stabilize",		"iterations": 5,	"cfg":7,	"denoise":0.2,	"reinforce_source":0.5,		"temporal_blend":0.5},
	{"step":"finalize",			"iterations": 5,	"cfg":7,	"denoise":0.1,	"reinforce_source":0.2,		"temporal_blend":0.3},
]
