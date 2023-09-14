# vid2vid

This is a python script that uses ebsynth to stabilize video made with stable diffusion (comfyui).

![output](https://github.com/zamp/vid2vid/assets/1029645/b52f2eef-805d-41bc-b3af-3b96d8ec08f2)

## Install

Clone the repo somewhere and run 

```pip install -r "requirements.txt"```

Install EbSynth somewhere. Get it from https://ebsynth.com/

## How to run

Start ComfyUI.

Put your video files in video directory. All files have to be named XXX.png where XXX is the frame number. 001.png, 002.png, 003.png etc. Can start from any number and end with any number. Should support other formats like XXXX.png or XX.png, haven't tested that though.

Files have to be sequential and cannot have gaps!

**Read through configs/example.config.ini**

Either run "run.bat" or "python main.py" from command line.

To run the provided workflow_api.json you need to have Flat-2D Animerge model installed. You can get it from https://civitai.com/models/35960/flat-2d-animerge. You can also just change the config to point to some other model or create your own workflow which is explained below.

## How to do custom ComfyUI workflows

### IMPORTANT

Modify end of graphToPrompt() in comfyui/web/scripts/app.js to the following (You can find this around line 1450.)

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

This adds the node title into the api.json. **This tool will NOT work without it!**

Duplicate the ComfyUI/inputs/example.png twice and name these files "input.png" and "video.png". *This just makes them show up in the default image loader. If you're using another loader you can probably skip this step and just type in the file names.*

Open workflows/example.workflow.json in ComfyUI and modify it as you want.

Set your image loader to load "input.png" (you can also have a loader with "video.png" for ControlNets etc. and load both the input and video files separately for separate or combined processes.)

### Pro tip

Install WAS node suite (https://github.com/WASasquatch/was-node-suite-comfyui) and use the save image node from that with these settings (This way it will always overwrite the same file and you don't end up with gigabytes of half baked frames):
![image](https://github.com/zamp/comfy-temporal-stability/assets/1029645/6aca4944-6317-4061-87b6-75d0c6729256)

**Enable developer options in ComfyUI (gear icon, toggle "Enable Dev mode Options") and then save workflow api.**

Save it to the workflows directory.

Change the config.ini to point to your new workflow.

## Known issues

Preview nodes mess up getting correct file for processing. Workaround: don't have preview nodes or make sure save image is last node in json. (Duplicate save node and delete previous. Hook it back in.)

If you get an error about not finding scipy.libs when running emotion detection create an empty file (called scipy.libs) where it's looking for it.

## Gallery

You can find these videos and config for them under /examples/

https://github.com/zamp/vid2vid/assets/1029645/f9d561c7-0be2-4cd4-9654-71b627cc1949

Here's an easy scene to stylize. Not a lot of movement and has character in focus. Still, too high prompting for bearded man caused artefacts in reflections. Minor flickering in background.

https://github.com/zamp/vid2vid/assets/1029645/e9a06358-a8e5-4853-8945-f27915ebffef

Here's a hard scene to stylize. Loads of movement. Characters are not in focus and has multiple characters. Lots of flickering in background.

## TODO

- [ ] Support A1111
- [ ] Automatic keyframe detection
