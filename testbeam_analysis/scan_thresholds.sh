#!/bin/bash
set -e

####################
#Conversion factors#
####################


# Choose chip on which to scan thresholds
chip="GAP225SQ"


# Calibration factors from
# https://docs.google.com/document/d/19Fcl0ddjLbrOKS4Pklz0K1czCOLfNEMVHt0L1k96xvo/edit

declare -A factors
factors["GAP225SQ"]=0.23287
factors["GAP15SQ"]=0.23716
factors["STD225SQ"]=0.23528
factors["STD15SQ"]=0.24094

factor=${factors["${chip}"]}


thresholds_e=(70 90 110 130 170 210 250 290 330 370)


# Write thresholds to params dir
: > params/SPS202404/${chip}/threshold_scan.txt

for threshold_e in ${thresholds_e[@]}; do

    echo "Processing threshold e -> ${threshold_e}"

    threshold_adu=$(awk "BEGIN {print int(${threshold_e} / ${factor} + 0.5)}")

    cp params/SPS202404/${chip}/${chip}.txt params/SPS202404/${chip}/${chip}_${threshold_adu}.txt
    sed -i "s/method_analysis=.*/method_analysis=\"cluster\"/g" params/SPS202404/${chip}/${chip}_${threshold_adu}.txt
    sed -i "s/seedthr_analysis=.*/seedthr_analysis=\"${threshold_adu}\"/g" params/SPS202404/${chip}/${chip}_${threshold_adu}.txt
    sed -i "s/nbh_analysis=.*/nbh_analysis=\"${threshold_adu}\"/g" params/SPS202404/${chip}/${chip}_${threshold_adu}.txt

    # Running run_tb_analysis.sh without alignment (assuming it has already been performed at least once for this run)
    # Can run w/ tag for different files
    # ./run_tb_analysis.sh --tag 032190 params/SPS202404/${chip}/${chip}_${threshold_adu}.txt
    ./run_tb_analysis.sh params/SPS202404/${chip}/${chip}_${threshold_adu}.txt -a -b
    echo "${threshold_adu}" >> params/SPS202404/${chip}/threshold_scan.txt


done
    



