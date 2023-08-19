# comfy-temporal-stability

This is a python script that uses ebsynth to stabilize video made with stable diffusion.

## Install

Clone the repo somewhere and run 

```pip install -r "requirements.txt"```

## How to run

Start ComfyUI.

Put your video files in video directory. All files have to be named 000.png where 000 is the frame number. 001.png, 002.png, 003.png etc.

Tweak config.py to your liking.

Change the comfy ui input path to where your comfyui is installed.

```comfyui_input_path = "..\ComfyUI\input\input.png"```

Either run "run.bat" or "python main.py" from command line.

When re-running please delete output and ebsynth directories before firing it up again.

## How to do custom comfyui workflows

Enable developer options in comfyui and then save workflow api.

Save it to the root.

Change config to point to it.

For now you need to modify the values in comfyui.py. 

```
sampler = "14"
positive_input = "6"
negative_input = "7"
image_input = "10"
```

Set the numbers to whatever they're in the workflow_api.json

Try to avoid scaling output image in the workflow or ensure output is the exact same size as input.
