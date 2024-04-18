#!/bin/bash
set -e 

#looping over chips makes more sense now that we read .txt files from params folder

# pcbs=(08 18 19 06)
chips=("GAP225SQ" "STD225SQ" "GAP15SQ" "STD15SQ")
#for pcb in ${pcbs[@]}; do 
for chip in ${chips[@]}; do 
    ./run_tb_analysis.sh params/${chip}.txt &> logs/${chip}_log_analysis_retry.txt 
done
