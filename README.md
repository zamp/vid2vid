# temporal-stability [Ebsynth + ComfyUI]

This is a python script that uses ebsynth to stabilize video made with stable diffusion.

## Install

Clone the repo somewhere and run 

```pip install -r "requirements.txt"```

Install EbSynth somewhere. Get it from https://ebsynth.com/

## How to run

Start ComfyUI.

Put your video files in video directory. All files have to be named 000.png where 000 is the frame number. 001.png, 002.png, 003.png etc.

Files have to be sequential and cannot have gaps!

Create a config.ini file 
Rename example.config.ini to config.py and tweak it to your liking.

Either run "run.bat" or "python main.py" from command line.

Whenever ebsynth pops up press Run All and once done close it.

To run the provided workflow_api.json you need to have Flat-2D Animerge model installed. You can get it from https://civitai.com/models/35960/flat-2d-animerge. You can also just change the json to point to some other model or create your own workflow which is explained below.

## How to do custom ComfyUI workflows

Duplicate the ComfyUI/inputs/example.png twice and name these files "input.png" and "video.png"

Open workflows/workflow.json in ComfyUI and modify it as you want.

Set your image loader to load "input.png" (optionally you can also have a loader with "video.png" for ControlNets etc.)

**Enable developer options in ComfyUI (gear icon, toggle "Enable Dev mode Options") and then save workflow api.**

Save it to the workflows directory.

Change render_pass_default.py to point to it OR change the config.py render pass generators to also have workflow="your work flow path" as a parameter.

The script will try to find the sampler and positive/negative input fields automatically. But in case it can't find them you can change them in comfyui.py

To automatically find positive and negative prompt fields save them with "positive_prompt" and "negative_prompt" in the text field.

Currently supported nodes for automatic search:
Clip: ```CLIPTextEncode``` and  ```BNK_CLIPTextEncodeAdvanced```
Sampler: ```KSampler``` and ```BNK_TiledKSampler```
Image loader: ```LoadImage```
Model loader: ```CheckpointLoaderSimple```

If the search fails for some reason you can set these numbers to whatever they're in the workflow_api.json (open the json with notepad or similar) OR you can disable sending these values to ComfyUI in the config/render_pass_defaults.
```
sampler = "14"
positive_input = "6"
negative_input = "7"
image_input = "10"
```

Try to avoid scaling output image in the workflow or ensure output is the exact same size as input.
