# comfy-temporal-stability

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

To run the provided workflow_api.json you need to have Flat-2D Animerge model installed. You can get it from https://civitai.com/models/35960/flat-2d-animerge. You can also just change the json to point to some other model or create your own workflow which is explained below.

## How to do custom ComfyUI workflows

### IMPORTANT

Modify comfyui/web/scripts/app.js to the following

```
async graphToPrompt() {
    ...
    output[String(node.id)] = {
        title: node.title,
        inputs,
        class_type: node.comfyClass,
    };
}
```

This adds the node title into the api.json. This tool will NOT work without it!

Duplicate the ComfyUI/inputs/example.png twice and name these files "input.png" and "video.png"

Open workflows/example.workflow.json in ComfyUI and modify it as you want.

Set your image loader to load "input.png" (optionally you can also have a loader with "video.png" for ControlNets etc.)

**Enable developer options in ComfyUI (gear icon, toggle "Enable Dev mode Options") and then save workflow api.**

Save it to the workflows directory.

Change the config.ini Workflow = "your work flow path" (Without quotes)