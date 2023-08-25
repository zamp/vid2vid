workflow:str = "workflows/workflow_api.json"

# To disable sending these to ComfyUI uncomment the following line "blabla = None"
positive_prompt:str = "default positive prompt"
#rpd.positive_prompt = None

negative_prompt:str = "default negative prompt"
#rpd.negative_prompt = None

model:str = "flat2DAnimerge_v30.safetensors"
#rpd.model = None

# Change these only if you know what you're doing):
cfg:int = 8
denoise:float = 0.5
alpha:float = 0.5
frame_spread:int = 2
spread_alpha_multiplier:float = 0.5
video_dir:str = "video/"
output_dir:str = "output/"
input_dir:str = "output/"