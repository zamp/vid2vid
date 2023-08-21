# comfy-temporal-stability

This is a python script that uses ebsynth to stabilize video made with stable diffusion.

## Install

Clone the repo somewhere and run 

```pip install -r "requirements.txt"```

## How to run

Start ComfyUI.

Put your video files in video directory. All files have to be named 000.png where 000 is the frame number. 001.png, 002.png, 003.png etc.

Files have to be sequential and cannot have gaps!

Rename example.config.py to config.py and tweak it to your liking.

Either run "run.bat" or "python main.py" from command line.

When re-running please delete output and ebsynth directories before firing it up again.

To run the provided workflow_api.json you need to have Flat-2D Animerge model installed. You can get it from https://civitai.com/models/35960/flat-2d-animerge. You can also just change the json to point to some other model or create your own workflow which is explained below.

## How to do custom comfyui workflows

Open workflow.json in ComfyUI and modify it as you want.

Enable developer options in comfyui and then save workflow api.

Save it to the root.

Change config to point to it.

It will try to find the sampler and positive/negative input fields automatically. But in case it can't find them you can change them in comfyui.py

```
sampler = "14"
positive_input = "6"
negative_input = "7"
image_input = "10"
```

To automatically find positive and negative prompt fields save them with "positive_prompt" and "negative_prompt" in the text field.

Currently supported for automatic search:
Clip: ```CLIPTextEncode and BNK_CLIPTextEncodeAdvanced```
Sampler: ```KSampler```
Image loader: ```LoadImage```


Set the numbers to whatever they're in the workflow_api.json

Try to avoid scaling output image in the workflow or ensure output is the exact same size as input.
