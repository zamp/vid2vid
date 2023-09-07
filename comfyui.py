import websocket
import uuid
import json
import urllib.request
import urllib.parse
from PIL import Image
import io
import random
import requests
from configparser import SectionProxy

client_id = str(uuid.uuid4())
ws = websocket.WebSocket()

def queue_prompt(server_addr, prompt):
	p = {"prompt": prompt, "client_id": client_id}
	data = json.dumps(p).encode('utf-8')
	req =  urllib.request.Request("http://{}/prompt".format(server_addr), data=data)
	return json.loads(urllib.request.urlopen(req).read())

def get_image(server_addr, filename, subfolder, folder_type):
	data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
	url_values = urllib.parse.urlencode(data)
	with urllib.request.urlopen("http://{}/view?{}".format(server_addr, url_values)) as response:
		return response.read()

def get_history(server_addr, prompt_id):
	with urllib.request.urlopen("http://{}/history/{}".format(server_addr, prompt_id)) as response:
		return json.loads(response.read())
	
def upload_image(server_addr, image_path, filename):
	files = {"image": (filename, open(image_path, 'rb'), 'image/png', {'Expires': '0'})}
	data = {"overwrite": "true"}
	result = requests.post("http://{}/upload/image".format(server_addr), files=files, data=data)
	#print(result.text)
	return json.loads(result.text)

def get_images(server_addr, ws, prompt):
	prompt_id = queue_prompt(server_addr, prompt)['prompt_id']
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

	history = get_history(server_addr, prompt_id)[prompt_id]	
	for node_id in history['outputs']:
		node_output = history['outputs'][node_id]
		if 'images' in node_output:
			images_output = []
			for image in node_output['images']:
				image_data = get_image(server_addr, image['filename'], image['subfolder'], image['type'])
				images_output.append(image_data)
		output_images[node_id] = images_output

	return output_images

def connect(server_addr):	
	ws.connect(f"ws://{server_addr}/ws?clientId={client_id}")

def close():
	ws.close()

def parse_key(json, key):
	arr = key.split(".")
	title = str(arr[1]).lower()
	input = str(arr[2]).lower()
	for key in json:
		if str(json[key]["title"]).lower() == title.lower():
			for json_input in json[key]["inputs"]:
				if str(json_input).lower() == input:
					return (title, json_input)
	return (None, None)

def get_api_id(json, title):
	for key in json:
		if json[key]["title"] == title:
			return key
	return -1

def process_image(image_path:str, video_path:str, config:SectionProxy):
	# get config values	
	workflow = config.get("Workflow")

	#print(image_path, video_path)

	workflow_json = json.load(open(workflow))

	# parse comfyui parameters	
	for key in config.keys():
		if key.startswith("comfyuiparam."):
			(title, input) = parse_key(workflow_json, key)
			if title == None or input == None:
				continue

			api_id = get_api_id(workflow_json, title)
			if api_id == -1:
				continue
			value = config.get(key)			

			# parse correct type into json
			if value.isdigit():
				# handle seed randomization
				if str(input).lower() == "seed" and value == -1:
					value = random.randint(1,18446744073709551616)
				workflow_json[api_id]["inputs"][input] = int(value)
			elif value.replace('.','',1).isdigit() and value.count('.') < 2:
				workflow_json[api_id]["inputs"][input] = float(value)
			else:
				workflow_json[api_id]["inputs"][input] = value

	server_addr = config.get("ComfyUI_ServerAddress")
	upload_image(server_addr, image_path, "input.png")
	if config.getboolean("UploadVideoFile"):
		upload_image(server_addr, video_path, config.get("UploadVideoFileName"))

	#print(workflow_json)

	images = get_images(server_addr, ws, workflow_json)

	for node_id in images:
		for image_data in images[node_id]:
			return Image.open(io.BytesIO(image_data)).convert("RGB")