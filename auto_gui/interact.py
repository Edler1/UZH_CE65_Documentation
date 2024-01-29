import pyautogui
import json
import time
import subprocess
from datetime import date

### This is supposed to interact with the gui and not be a full fledged script yet. We implement the recipe as in the notes

## To make it a full fledged script I need to do the following things (as per usual I should avoid interacting with the gui...)

## Power on power supply...

## Set the relevant Voltages...

## Do the startup sequence...

## Start the gui (and bring its window to focus)

## Set relevant gui parameters and start the acquisition...

## (After 5h, or w/e relevant, shorter for debug...) Bring the window into focus, end the acquisition, close the gui

## Power cycle somehow -> can we just turn off the power supply output??? Else set all voltages to 0V

## Now we repeat the above for whatever other voltages I would like to consider...


def start_gui_acquisition(chip="C4", VSUB=0, HV=10, temp=20):
    

    if(not(chip=="C4" or chip=="D4")):
        raise NotImplementedError("C4/D4 chip selection is hardcoded for now...")
    formatted_date = str(date.today().day//10)+str(date.today().day%10)+str(date.today().month//10)+str(date.today().month%10)+str(date.today().year)

    #fname="testTree_C4_21072023_3V_10V.root"
    fname="testTree_{0}_{1}V_{2}V_{3}C_{4}".format(chip, VSUB, HV, temp, formatted_date)
    
    with open("coords.json", "r") as json_file:
        coords = json.load(json_file)
    
    print(coords["start"])
    
    
    ## We try here to start the gui itself...
    
    #####pyautogui.hotkey("ctrl", "alt", "t")
    #####
    #####time.sleep(2)
    #####
    #####pyautogui.typewrite("cd $CE65", interval=0.1)
    #####pyautogui.press("enter")
    #####time.sleep(1)
    #####pyautogui.typewrite("./ce65_daq", interval=0.1)
    #####pyautogui.press("enter")
    
    
    
    ce65_directory = "/home/fcc-ce65-testsetup/CE65/ce-65-daq-software-uzh-edits"
    
    # We power on the fpga
    subprocess.run(["program_fpga"], cwd=ce65_directory, shell=True, check=True)
    
    # We start the gui
    #subprocess.run(["./ce65_daq"], cwd=ce65_directory, shell=True, check=True)
    ##subprocess.run(["./ce65_daq"], cwd=ce65_directory, shell=True, check=True)
    subprocess.Popen(["./ce65_daq"], cwd=ce65_directory, shell=True)
    
    time.sleep(15)
    
    # Now we check the pid of the ce65_daq gui
    pid = subprocess.check_output(['xdotool search --name "CE65 DAQ"'], shell=True, text=True).rstrip("\n")
    
    # We maximize the gui
    subprocess.run(['xdotool windowsize {0} 100% 100%'.format(pid)], shell=True, check=True)
    
    # We bring the gui into focus
    subprocess.run(['xdotool windowactivate {0}'.format(pid)], shell=True, check=True)
    
    
    
    
    ###########
    
    
    # We begin by sleeping so we have time to bring the gui into focus
    #time.sleep(7)
    
    # chip variant click
    #pyautogui.hotkey("alt", "f10")
    time.sleep(1)
    pyautogui.click(*tuple(coords["chip_variant"]))
    time.sleep(1)
    if(chip=="C4"): 
        pyautogui.click(*tuple(coords["chip_variant_C4"]))
    elif (chip=="D4"):
        pyautogui.click(*tuple(coords["chip_variant_D4_legacy"]))
    else:
        raise ValueError("Invalid chip selection: "+chip)
    time.sleep(1)
    pyautogui.click(*tuple(coords["proxy_board"]))
    time.sleep(1)
    pyautogui.click(*tuple(coords["proxy_board_006"]))
    time.sleep(1)
    pyautogui.click(*tuple(coords["threshold_cuts"]))
    time.sleep(1)
    pyautogui.click(*tuple(coords["configure"]))
    time.sleep(1)
    pyautogui.click(*tuple(coords["file_name"]))
    time.sleep(1)
    for _ in range(30):
        pyautogui.press("backspace")
        time.sleep(0.05)
    pyautogui.typewrite(fname, interval=0.1)
    pyautogui.press("enter")
    time.sleep(1)
    pyautogui.click(*tuple(coords["start"]))
    
    # 9h runs for now...
    ##time.sleep(9*3600)
    # 3h runs for D4 hv scan...
    time.sleep(3*3600)
    

    #print("DEBUG MODE XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    #print("DEBUG MODE XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    #print("DEBUG MODE XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    #print("DEBUG MODE XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    #time.sleep((1/120)*3600)
    ##time.sleep((2)*3600)
    
    # Now we check the pid of the ce65_daq gui
    pid = subprocess.check_output(['xdotool search --name "CE65 DAQ"'], shell=True, text=True).rstrip("\n")
    time.sleep(1)
    
    # We maximize the gui
    subprocess.run(['xdotool windowsize {0} 100% 100%'.format(pid)], shell=True, check=True)
    time.sleep(1)
    
    # We bring the gui into focus
    subprocess.run(['xdotool windowactivate {0}'.format(pid)], shell=True, check=True)
    time.sleep(1)
    
    pyautogui.click(*tuple(coords["stop"]))
    time.sleep(10)
    pyautogui.click(*tuple(coords["x"]))
    time.sleep(5)
    return fname
