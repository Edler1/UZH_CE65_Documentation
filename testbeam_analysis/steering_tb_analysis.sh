#!/bin/bash
set -e 

#looping over chips makes more sense now that we read .txt files from params folder

testbeam="SPS202404"

pcbs=(08 18 19 06)
#chips=("GAP225SQ" "STD225SQ" "GAP15SQ" "STD15SQ")
chips=("GAP15SQ" "STD225SQ")
#for pcb in ${pcbs[@]}; do 
for chip in ${chips[@]}; do 
    #./run_tb_analysis.sh params/pcb${pcb}
    #./run_tb_analysis.sh params/${chip}.txt &> logs/${chip}_log.txt
    # ./run_tb_analysis.sh params/${testbeam}/${chip}.txt &> logs/${chip}_log_analysis
    ./run_tb_analysis.sh params/${testbeam}/${chip}.txt 
done
