from interact_v2 import start_gui_acquisition
from labequipment import HAMEG
import os, stat
import time
from datetime import date
import subprocess


########
#README# ==> We need to test to see if the script actually works still w/ v2 also (would think yes)
########
# - The above includes setting power supply and everything
# - Need to test if the analysis still works (probably it won't and we need to set thresholds)
# - Need to see how quickly data grows when lowering threshold for AC to 1600...
# - Need to actually see the response of the std 15 micron process...




## The idea of this script is to choose a voltage and set it in the power supply, then call the "start_gui_acquisition" function to take care of the rest...

## THIS SCRIPT IS ONLY MEANT FOR C4!!!

# known bug -> killing this script kills the analysis subprocess (use nohup?)

#VSUB = [0,3]
VSUB = [0]
VSUB_ch = 2

#HV = [0,1,2,3,4,10]
#HV = [10,0,2,4,6,8,15]
#$#HV = [10,0,2,4,6,8,15]
HV = [8,15] #These need to be done for STD225SQ !!! They failed!!!
HV_ch = 3


hameg_path="/dev/hmp2030"

h=HAMEG(hameg_path)

# Make sure the power supply is off before starting
h.power(False, 1)
h.power(False, VSUB_ch)
h.power(False, HV_ch)
h.power(False)
time.sleep(5)


##chip = "GAP225SQ"
##chip = "STD15SQ"
chip = "STD225SQ"
##chip = "GAP15SQ"
temp = 20 ## in degrees celcius, this should match the chiller. By default=20 Celcius


for _vsub in VSUB:
    for _hv in HV:
        
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
        fname=start_gui_acquisition(chip, _vsub, _hv, temp)
        
        time.sleep(5)
        
        # Power-cycling for next iteration
        h.power(False, 1)
        h.power(False, VSUB_ch)
        h.power(False, HV_ch)
        h.power(False)
        time.sleep(5)

        ce65_analysis_directory = "/home/fcc-ce65-testsetup/CE65/ce65_daq_v2/analysis"
        subprocess.Popen(["bash run_save_single_file.sh {0}".format(fname)], cwd=ce65_analysis_directory, shell=True)










