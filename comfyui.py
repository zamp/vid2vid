import websocket
import uuid
import json
import urllib.request
import urllib.parse
import config
from PIL import Image
import io
import random
import requests

client_id = str(uuid.uuid4())
ws = websocket.WebSocket()

def queue_prompt(prompt):
	p = {"prompt": prompt, "client_id": client_id}
	data = json.dumps(p).encode('utf-8')
	req =  urllib.request.Request("http://{}/prompt".format(config.comfyui_server_address), data=data)
	return json.loads(urllib.request.urlopen(req).read())

def get_image(filename, subfolder, folder_type):
	data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
	url_values = urllib.parse.urlencode(data)
	with urllib.request.urlopen("http://{}/view?{}".format(config.comfyui_server_address, url_values)) as response:
		return response.read()

def get_history(prompt_id):
	with urllib.request.urlopen("http://{}/history/{}".format(config.comfyui_server_address, prompt_id)) as response:
		return json.loads(response.read())
	
def upload_image(image_path):
	files = {"image": ("input.png", open(image_path, 'rb'), 'image/png', {'Expires': '0'})}
	data = {"overwrite": "true"}
	result = requests.post("http://{}/upload/image".format(config.comfyui_server_address), files=files, data=data)
	#print(result.text)
	return json.loads(result.text)

def get_images(ws, prompt):
	prompt_id = queue_prompt(prompt)['prompt_id']
	output_images = {}
	while True:
		out = ws.recv()
		if isinstance(out, str):
			message = json.loads(out)
			if message['type'] == 'executing':
				data = message['data']
				if data['node'] is None and data['prompt_id'] == prompt_id:
					break #Execution is done
		else:
			continue #previews are binary data

	history = get_history(prompt_id)[prompt_id]
	for o in history['outputs']:
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
	ws.connect("ws://{}/ws?clientId={}".format(config.comfyui_server_address, client_id))

def close():
	ws.close()

def process_image(image_path, cfg, denoise):
	response = upload_image(image_path)
	file_name = response["name"]
	sub_dir = response["subfolder"]

	#print("upload file {}{}".format(file_name, sub_dir))

	prompt = json.load(open(config.workflow_json))

	# todo: read json class name and pick these out from that
	sampler = "14"
	positive_input = "6"
	negative_input = "7"
	image_input = "10"

	INPUTS = "inputs"
	CLASS_TYPE = "class_type"

	for key in prompt:
		if prompt[key][CLASS_TYPE] == "LoadImage":
			image_input = key
		if prompt[key][CLASS_TYPE] == "KSampler":
			sampler = key
		if prompt[key][CLASS_TYPE] == "CLIPTextEncode" or prompt[key][CLASS_TYPE] == "BNK_CLIPTextEncodeAdvanced":
			if prompt[key][INPUTS]["text"] == "positive_prompt":
				positive_input = key
			if prompt[key][INPUTS]["text"] == "negative_prompt":
				negative_input = key

	if config.use_random_seed:
		prompt[sampler][INPUTS]["seed"] = random.randint(1,18446744073709551616)
	else:
		prompt[sampler][INPUTS]["seed"] = 69 # nice

	prompt[sampler][INPUTS]["cfg"] = cfg
	prompt[sampler][INPUTS]["denoise"] = denoise

	prompt[image_input][INPUTS]["image"] = file_name

	prompt[positive_input][INPUTS]["text"] = config.positive_prompt
	prompt[negative_input][INPUTS]["text"] = config.negative_prompt

	images = get_images(ws, prompt)

	for node_id in images:
		for image_data in images[node_id]:
			return Image.open(io.BytesIO(image_data)).convert("RGB")