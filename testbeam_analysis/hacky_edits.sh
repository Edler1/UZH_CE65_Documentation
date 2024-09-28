#!/bin/bash
set -e
# set -x

# Script to edit the plotting scripts for threshold scans in ITS3utils without requiring a submodule update




## We start by checking for the ITS3utils dir
its3_utils_path=`find . -type d -name "ITS3utils"`
if [ -n "$its3_utils_path" ]; then
    its3_utils_path=`realpath $its3_utils_path`
else 
    echo "Cannot find dir \"ITS3utils\". Please make sure it is visible from within \"`pwd`\"."
    exit
fi


cp plotting_scripts/plot_util.py ${its3_utils_path}/corry/plot_util.py


# Legacy approach

# # Edit corry/plot_util.py to print efficiencies
# res_captured=`sed -n '609p' ${its3_utils_path}/corry/plot_util.py`
# if [ "${res_captured}" == "    if(optGaus):" ]; then
#     echo -e "Seems like file \"plot_util.py\" has already been edited."
# else
#     sed -i '609d' ${its3_utils_path}/corry/plot_util.py
#     sed -i '608a\
# \ \ \ \ if(optGaus):\
# \ \ \ \ \ \ tmp_gaus = self.optimise_hist_gaus(htmp, scale)\
# \ \ \ \ \ \ print(tmp_gaus)' ${its3_utils_path}/corry/plot_util.py
# fi
#
# # Edit corry/plot_analog_ce65v2.py to print efficiencies
# eff_captured=`sed -n '458p' ${its3_utils_path}/corry/plot_analog_ce65v2.py`
# if [ "${eff_captured}" == "  # Printing efficiencies for computing efficiency vs threshold plots" ]; then
#     echo -e "Seems like file \"plot_analog_ce65v2.py\" has already been edited."
# else
#     sed -i '456a\
# \
# \ \ # Printing efficiencies for computing efficiency vs threshold plots\
# \ \ print(\"Efficiencies\")\
# \ \ print(str(eff*100)+\" \"+str(uerr*100)+\" \"+str(lerr*100))\
# ' ${its3_utils_path}/corry/plot_analog_ce65v2.py
# fi

