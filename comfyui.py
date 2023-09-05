import websocket
import uuid
import json
import urllib.request
import urllib.parse
from PIL import Image
import io
import random
import requests
import configparser

client_id = str(uuid.uuid4())
ws = websocket.WebSocket()

config = configparser.ConfigParser()
config.read(["example.config.ini", "config.ini"])

defaults = config["DEFAULT"]

def queue_prompt(prompt):
	p = {"prompt": prompt, "client_id": client_id}
	data = json.dumps(p).encode('utf-8')
	req =  urllib.request.Request("http://{}/prompt".format(defaults.get("ComfyUI_ServerAddress")), data=data)
	return json.loads(urllib.request.urlopen(req).read())

def get_image(filename, subfolder, folder_type):
	data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
	url_values = urllib.parse.urlencode(data)
	with urllib.request.urlopen("http://{}/view?{}".format(defaults.get("ComfyUI_ServerAddress"), url_values)) as response:
		return response.read()

def get_history(prompt_id):
	with urllib.request.urlopen("http://{}/history/{}".format(defaults.get("ComfyUI_ServerAddress"), prompt_id)) as response:
		return json.loads(response.read())
	
def upload_image(image_path, filename):
	files = {"image": (filename, open(image_path, 'rb'), 'image/png', {'Expires': '0'})}
	data = {"overwrite": "true"}
	result = requests.post("http://{}/upload/image".format(defaults.get("ComfyUI_ServerAddress")), files=files, data=data)
	#print(result.text)
	return json.loads(result.text)

def get_images(ws, prompt):
    prompt_id = queue_prompt(prompt)['prompt_id']
    output_images = {}  # Initialize the output_images dictionary
    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message['type'] == 'executing':
                data = message['data']
                if data['node'] is None and data['prompt_id'] == prompt_id:
                    break  # Execution is done
        else:
            continue  # previews are binary data

    history = get_history(prompt_id)[prompt_id]
    for node_id in history['outputs']:
        node_output = history['outputs'][node_id]
        if 'images' in node_output:
            images_output = []
            for image in node_output['images']:
                image_data = get_image(image['filename'], image['subfolder'], image['type'])
                images_output.append(image_data)
            output_images[node_id] = images_output

    return output_images


def connect():
	address = defaults.get("ComfyUI_ServerAddress")
	ws.connect(f"ws://{address}/ws?clientId={client_id}")

def close():
	ws.close()

def process_image(image_path, video_path, cfg, denoise, positive_prompt, negative_prompt, workflow_json, model, seed):
	upload_image(image_path, "input.png")	
	if defaults.getboolean("UploadVideoFile"):
		upload_image(video_path, defaults.get("UploadVideoFileName"))

	prompt = json.load(open(workflow_json))

	# modify these if the search fails
	sampler = "14"
	positive_input = "6"
	negative_input = "7"
	image_input = "10"
	model_loader = "4"

	INPUTS = "inputs"
	CLASS_TYPE = "class_type"

	for key in prompt:
		if prompt[key][CLASS_TYPE] == "CheckpointLoaderSimple":
			model_loader = key
		if prompt[key][CLASS_TYPE] == "LoadImage":
			image_input = key
		if prompt[key][CLASS_TYPE] == "KSampler" or prompt[key][CLASS_TYPE] == "BNK_TiledKSampler":
			sampler = key
		if prompt[key][CLASS_TYPE] == "CLIPTextEncode" or prompt[key][CLASS_TYPE] == "BNK_CLIPTextEncodeAdvanced":
			if prompt[key][INPUTS]["text"] == "positive_prompt":
				positive_input = key
			if prompt[key][INPUTS]["text"] == "negative_prompt":
				negative_input = key

	# if seed == None:
	# 	prompt[sampler][INPUTS]["seed"] = random.randint(1,18446744073709551616)
	# 	print(prompt[sampler][INPUTS]["seed"])
			
	# else:
	#  	prompt[sampler][INPUTS]["Seed"] = seed
	#  	print(seed)

	if seed == None:
		seed = random.randint(1,18446744073709551616)
	
	prompt[sampler][INPUTS]["Seed"] = seed

	print("Seed: " + str(seed))


	# if seed != None:
	# 	seed = defaults.getint("Seed")

	# if seed == -1:
	# 	prompt[sampler][INPUTS]["seed"] = random.randint(1,18446744073709551616)
	# 	print(prompt[sampler][INPUTS]["seed"])
	# else:
	# 	prompt[sampler][INPUTS]["seed"] = seed
	# 	print(seed)

	

	prompt[sampler][INPUTS]["cfg"] = cfg
	prompt[sampler][INPUTS]["denoise"] = denoise

	if positive_prompt != None:
		if positive_input in prompt:
			prompt[positive_input][INPUTS]["text"] = positive_prompt
		else:
			print("Could not find positive prompt field in workflow. Make sure positive prompt field has 'positive_prompt' text.")		
	if negative_prompt != None:
		if negative_input in prompt:
			prompt[negative_input][INPUTS]["text"] = negative_prompt
		else:
			print("Could not find negative prompt field in workflow. Make sure positive prompt field has 'negative_prompt' text.")		
	if model != None:
		prompt[model_loader][INPUTS]["ckpt_name"] = model

	images = get_images(ws, prompt)

	for node_id in images:
		for image_data in images[node_id]:
			return Image.open(io.BytesIO(image_data)).convert("RGB")