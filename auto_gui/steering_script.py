from interact import start_gui_acquisition
from labequipment import HAMEG
import os, stat
import time
from datetime import date
import subprocess

## The idea of this script is to choose a voltage and set it in the power supply, then call the "start_gui_acquisition" function to take care of the rest...

## THIS SCRIPT IS ONLY MEANT FOR C4!!!

# known bug -> killing this script kills the analysis subprocess (use nohup?)

#VSUB = [0,3]
VSUB = [3, 0]
VSUB_ch = 2

HV = [0,1,2,3,4,10]
HV_ch = 3

# Here we make list of dicts instead to be able to go in any order
##voltages = [{"_vsub":0, "_hv":10}, 
##        {"_vsub":3, "_hv":1},
##        {"_vsub":3, "_hv":2},
##        {"_vsub":3, "_hv":3},
##        {"_vsub":3, "_hv":4},
##        {"_vsub":0, "_hv":0},
##        {"_vsub":0, "_hv":1},
##        {"_vsub":0, "_hv":3},
##        {"_vsub":0, "_hv":4},
##        {"_vsub":0, "_hv":2},
##        {"_vsub":3, "_hv":0},
##        {"_vsub":3, "_hv":10},
##        ]

voltages = [{"_vsub":0, "_hv":10}, 
        {"_vsub":0, "_hv":0},
        {"_vsub":0, "_hv":1},
        {"_vsub":0, "_hv":2},
        {"_vsub":0, "_hv":3},
        {"_vsub":0, "_hv":4},
        ]

hameg_path="/dev/hmp2030"

h=HAMEG(hameg_path)

# Make sure the power supply is off before starting
h.power(False, 1)
h.power(False, VSUB_ch)
h.power(False, HV_ch)
h.power(False)
time.sleep(5)

#print("////////////////////")
#print("////////////////////")
#print("ONLY 3 RUNS FOR NOW")
#print("////////////////////")
#print("////////////////////")

_chip = "D4"
_temp = "24"

for voltage in voltages:
    _vsub = voltage["_vsub"]
    _hv = voltage["_hv"]
    
    ##if( not ((_vsub==0 and _hv==2) or (_vsub==3 and _hv==0) or (_vsub==3 and _hv==10))): 
    ##    continue
    print("Starting run : VSUB = {0}, HV = {1}".format(_vsub, _hv))


    # Setting the voltages
    h.set_volt(VSUB_ch, _vsub)
    h.set_volt(HV_ch, _hv)
    h.power(True, 1)
    time.sleep(5)
    h.power(True, VSUB_ch)
    time.sleep(5)
    h.power(True, HV_ch)
    time.sleep(5)
    
    # Starting the configuration of the fpga & daq
    #print("HERE WE WOULD CALL THE FNC")
    fname=start_gui_acquisition(_chip, _vsub, _hv, _temp)
    
    time.sleep(5)
    
    # Power-cycling for next iteration
    h.power(False, 1)
    h.power(False, VSUB_ch)
    h.power(False, HV_ch)
    h.power(False)
    time.sleep(5)


    ## This part is optional and just for my laziness
    ##formatted_date = str(date.today().day//10)+str(date.today().day%10)+str(date.today().month//10)+str(date.today().month%10)+str(date.today().year)

    ###fname="testTree_C4_21072023_3V_10V.root"
    ##fname="testTree_{0}_{1}_{2}V_{3}V".format("C4", formatted_date, _vsub, _hv)


    ce65_analysis_directory = "/home/fcc-ce65-testsetup/CE65/ce-65-daq-software-uzh-edits/analysis"
    subprocess.Popen(["bash run_save_single_file.sh {0}".format(fname)], cwd=ce65_analysis_directory, shell=True)










#for _vsub in VSUB:
#    for _hv in HV:
#        if( not ((_vsub==0 and _hv==2) or (_vsub==3 and _hv==0) or (_vsub==3 and _hv==10))): 
#            continue
#        print("Starting run : VSUB = {0}, HV = {1}".format(_vsub, _hv))
#        
#        # Setting the voltages
#        h.set_volt(VSUB_ch, _vsub)
#        h.set_volt(HV_ch, _hv)
#        h.power(True, 1)
#        time.sleep(5)
#        h.power(True, VSUB_ch)
#        time.sleep(5)
#        h.power(True, HV_ch)
#        time.sleep(5)
#        
#        # Starting the configuration of the fpga & daq
#        #print("HERE WE WOULD CALL THE FNC")
#        start_gui_acquisition("C4", _vsub, _hv)
#        
#        time.sleep(5)
#        
#        # Power-cycling for next iteration
#        h.power(False, 1)
#        h.power(False, VSUB_ch)
#        h.power(False, HV_ch)
#        h.power(False)
#        time.sleep(5)

