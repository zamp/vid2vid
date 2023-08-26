import win32gui
import time
from pynput.mouse import Button, Controller
import ctypes
from PIL import ImageGrab
from PIL import Image
import os
import wmi
import pythoncom

def activate_window(hwnd):
    user32 = ctypes.windll.user32
    user32.SetForegroundWindow(hwnd)
    if user32.IsIconic(hwnd):
        user32.ShowWindow(hwnd, 9)

def wait_and_kill():
    pythoncom.CoInitialize()
    f = wmi.WMI() 
    found = False
    while (not found):
        for process in f.Win32_Process():
            if process.Name == "EbSynth.exe":
                found = True
                break
        time.sleep(0.5)
    
    hwnd = win32gui.FindWindow(None, "EbSynth Beta [generated.ebs]")
    rect = win32gui.GetWindowRect(hwnd)

    # bottom right corner of window
    win_x = rect[0]
    win_y = rect[1]
    win_w = rect[2] - win_x
    win_h = rect[3] - win_y

    #print(win_x,win_y,win_w,win_h)

    pos = (win_x + win_w - 65, win_y + win_h - 42)

    mouse = Controller()
    
    start_x = win_w - 35
    start_y = win_h - 70

    old_position = mouse.position

    started = False
    while (not started):
        mouse.position = pos

        activate_window(hwnd)

        mouse.press(Button.left)
        time.sleep(0.01)
        mouse.release(Button.left)

        img = ImageGrab.grab((win_x, win_y, win_x + win_w, win_y + win_h))
        px = img.load()

        started = True
        for y in range(0, win_h - 350, 30):
            #mouse.position = (x, start_y - y)
            color = px[start_x, start_y - y]
            if color[0] == 0 and color[1] == 157 and color[2] == 123:
                started = False

        time.sleep(0.1)    

    mouse.position = old_position

    time.sleep(1)

    done = False
    while (not done):
        img = ImageGrab.grab((win_x, win_y, win_x + win_w, win_y + win_h))
        px = img.load()

        done = True

        for y in range(0, win_h - 350, 30):
            #mouse.position = (x, start_y - y)
            color = px[start_x, start_y - y]
            if color[0] != 0 and color[1] != 157 and color[2] != 123:
                done = False

        time.sleep(0.5)

    time.sleep(1)

    os.system("taskkill /f /im  EbSynth.exe")