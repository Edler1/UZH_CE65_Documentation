#!/bin/bash
set -e



# Idea here is to have a script that combines the analysis of the given file with uploading to cernbox


#source_dir="/home/fcc-ce65-testsetup/CE65/ce-65-daq-software-uzh-edits/data"
#source_dir="/media/fcc-ce65-testsetup/Elements/Hardware_ce65/Latest"
source_dir="/media/fcc-ce65-testsetup/b0430c20-0584-49e4-8f7a-7a11acb1d9ff/Hardware/D4_hv_scans"

data_run="testTree_D4_14072023"
data_run=$1

ce65_dir="/home/fcc-ce65-testsetup/CE65/ce-65-daq-software-uzh-edits/analysis"

eos_dir="/eos/user/e/eploerer/Hardware/High_Activity/wave_files"

cd ${ce65_dir}


#ls ${data_run}_[0-8].root > file_list_${data_run}.txt
#ls ${data_run}.root >> file_list_${data_run}.txt
#file=${source_dir}/file_list_${data_run}.txt
#cd ${ce65_dir}
#while read line; do
#	line=`echo "$line" | cut -d'.' -f1`
#	echo "Starting analysis on ${line}..."
#	./run_basic_analysis ${source_dir}/${line} &> ${line}.log &
#done < $file


# Here we start the analysis
echo "Starting analysis on ${data_run}..."
./run_basic_analysis ${source_dir}/${data_run} &> logs/${data_run}.log

# Here we upload to cernbox
## Seems to work for now... Will have to see how it meshes with the analysis script
echo "Starting analysis on ${data_run}..."
ps=`cat /home/fcc-ce65-testsetup/Documents/cern_pass.txt`
sshpass -p $ps scp ${source_dir}/${data_run}_wave.root eploerer@lxplus.cern.ch:${eos_dir}/
#./run_basic_analysis ${data_run} &> ${data_run}.log




