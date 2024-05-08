#!/bin/bash
set -e

##########
# Params #
##########

testbeam="SPS202404"
chip="GAP225SQ"
pcb="pcb07"
#HV=()
HV="10"
chillerTemp="" # Default "", for SPS 2024 TB. For DESY 2024 TB use "_t0"
windowSize="" # Default "", for SPS 2024 TB. For DESY 2024 TB use "_winNxN" with N the size of the readout window
momentum=120   #GeV
#(optional, leave blank)
run_number_beam=""
run_number_noise=""
number_of_events=2000
# number_of_events=-1

seedthr_alignment="350"
nbh_alignment="100"
snr_seed_alignment="9"
snr_neighbor_alignment="3"

seedthr_analysis="350"
nbh_analysis="100"
snr_seed_analysis="3"
snr_neighbor_analysis="3"

method_alignment="cluster"
method_analysis="window"


niter_prealign_tel=1
niter_align_tel=1
niter_prealign_dut=1
niter_align_dut=1


## Allow passing of params via command-line specified .txt file
if [[ $# -eq 1 && -f "$1" ]]; then
    source $1
else 
    echo "No params .txt file passed. Running with script defaults."
fi


## Below we just define the associative array from "copy_tb_files.sh" to check that chip and pcb match... 
declare -A chips
chips["pcb08"]="GAP225SQ"
chips["pcb02"]="GAP18SQ"
chips["pcb19"]="GAP15SQ"
chips["pcb05"]="GAP225HSQ"
chips["pcb03"]="GAP18HSQ"
chips["pcb18"]="STD225SQ"
chips["pcb23"]="STD18SQ"
chips["pcb06"]="STD15SQ"
chips["pcb07"]="GAP225SQ"
if [ ! ${chips["${pcb}"]} == ${chip} ]; then 
    echo "CHIP-PCB mismatch. Please check params."
    exit
fi


## Allow calling from a steering script also
if [ "${1:0:3}" == "pcb" ]; then
    pcb=$1
    chip=${chips["${pcb}"]}
fi


## Extract number of pixels to read in x and y
pattern='_win([0-9]+)x([0-9]+)'
if [[ $windowSize =~ $pattern ]]; then
    # Extract the numbers into variables
    nx="${BASH_REMATCH[1]}" # Extract the first captured group
    ny="${BASH_REMATCH[2]}" # Extract the second captured group

    echo "Using window size of ..."
    echo "nx: $nx"
    echo "ny: $ny"
else
    echo "Window size not defined, use full window of NX=48 and NY=24. Continuing!"
    nx=48
    ny=24
fi

## Replacing window size in CE65RawEvent2StdEventConverter class and recompile
sed -i "s/X_MX_SIZE = 48/X_MX_SIZE = $nx/" /opt/eudaq2/user/ITS3/module/src/CE65RawEvent2StdEventConverter.cc
sed -i "s/Y_MX_SIZE = 24/Y_MX_SIZE = $ny/" /opt/eudaq2/user/ITS3/module/src/CE65RawEvent2StdEventConverter.cc
cd /opt/eudaq2/build/
cmake ..
make install
cd -

## We start by checking for the ITS3utils dir
its3_utils_path=`find .. -type d -name "ITS3utils"`
if [ -n "$its3_utils_path" ]; then
    its3_utils_path=`realpath $its3_utils_path`
else 
    echo "Cannot find dir \"ITS3utils\". Please make sure it is visible from within \"`pwd`\"."
    exit
fi


## Find beam+noise files
if [ ! -n "${run_number_beam}" ]; then
    datafile_beam=`ls -1S ${its3_utils_path}/${testbeam}/data/${chip}/ce65v2_${pcb}_hv${HV}${chillerTemp}_beam${windowSize}_run[0-9]*_[0-9]*.raw | head -1`
else
    datafile_beam=`ls -1S ${its3_utils_path}/${testbeam}/data/${chip}/ce65v2_${pcb}_hv${HV}${chillerTemp}_beam${windowSize}_run${run_number_beam}.raw | head -1`
fi
if [ ! -n "${datafile_beam}" ]; then
    echo "Failed to find file(s) : \"${its3_utils_path}/${testbeam}/data/${chip}/ce65v2_${pcb}_hv${HV}${chillerTemp}_beam${windowSize}_run[0-9]*_[0-9]*.raw \". Have you ran \"copy_tb_files.sh\" already?"
    exit
fi
datafile_beam=`echo "${datafile_beam}" | sed "s/.*\/\([a-zA-Z0-9_.]*$\)/\1/"`
run_number_beam=`echo "${datafile_beam}" | sed "s/.*run\([0-9]*_[0-9]*\)\.raw/\1/g"`

if [ ! -n "${run_number_noise}" ]; then
    datafile_noise=`ls -1S ${its3_utils_path}/${testbeam}/data/${chip}/ce65v2_${pcb}_hv${HV}${chillerTemp}_noise${windowSize}_run[0-9]*_[0-9]*.raw | head -1`
else
    datafile_noise=`ls -1S ${its3_utils_path}/${testbeam}/data/${chip}/ce65v2_${pcb}_hv${HV}${chillerTemp}_noise${windowSize}_run${run_number_noise}.raw | head -1`
fi
if [ ! -n "${datafile_noise}" ]; then
    echo "Failed to find file(s) : \"${its3_utils_path}/${testbeam}/data/${chip}/ce65v2_${pcb}_hv${HV}${chillerTemp}_noise${windowSize}_run[0-9]*_[0-9]*.raw \". Have you ran \"copy_tb_files.sh\" already?"
    exit
fi
datafile_noise=`echo "${datafile_noise}" | sed "s/.*\/\([a-zA-Z0-9_.]*$\)/\1/"`
run_number_noise=`echo "${datafile_noise}" | sed "s/.*run\([0-9]*_[0-9]*\)\.raw/\1/g"`





#########
# MKDIR #
#########

cd "${its3_utils_path}/${testbeam}"
dirs=( config geometry masks qa output data )
for dir in ${dirs[@]}; do
    if [ ! -d "${dir}/${chip}" ]; then 
        mkdir -p ${dir}/${chip}
    fi
    if [ "${dir}" == "masks" ]; then 
        for i in {0..5}; do 
           touch masks/${chip}/ref-plane${i}_HV${HV}.txt 
       done
    fi
done 

testbeam_alphabetic=`echo "${testbeam}" | egrep -o "^[A-Z]+"`




## Now we copy over the files and use `sed` to edit them
## By convention the prototype for each of the copies will be in the parent directory of the class (e.g. masks/ref-plane0.txt)




#################
# Geometry file #
#################
# copy file from prototype
#cp "geometry/GAP225SQ/prealignment_tel_${testbeam_alphabetic}-GAP225SQ_HV10.geo" "geometry/${chip}/prealignment_tel_${testbeam_alphabetic}-${chip}_HV${HV}.geo"
cp "geometry/${testbeam_alphabetic}-GAP18SQ_HV10.geo" "geometry/${chip}/${testbeam_alphabetic}-${chip}_HV${HV}.geo"

# replace masks into chip subdir
sed -i "s/DESY202311\/masks/${testbeam}\/masks\/${chip}/g" geometry/${chip}/${testbeam_alphabetic}-${chip}_HV${HV}.geo
# add hv to mask names
sed -i "s/\(plane[0-5]\)/\1_HV${HV}/g" geometry/${chip}/${testbeam_alphabetic}-${chip}_HV${HV}.geo

# write correct CE65V2 pixel-pitch
pitch=`echo "${chip}" | egrep -o "[0-9]+"`
if [ "${pitch}" -gt "100" ]; then
    ## Container doesn't have bc installed by default... Let's hardcode for now.
    #pitch=`echo "scale=1;${pitch}/10" | bc`
    pitch=`echo "22.5"`
fi
sed -i "s/pixel_pitch = 18um, 18um/pixel_pitch = ${pitch}um, ${pitch}um/g" geometry/${chip}/${testbeam_alphabetic}-${chip}_HV${HV}.geo

# point to correct noisemap file
#sed -i "s/GAP18SQ_HV10-noisemap/${chip}_HV${HV}-noisemap/g" geometry/${chip}/${testbeam_alphabetic}-${chip}_HV${HV}.geo
sed -i "s/qa\/DESY-GAP18SQ_HV10-noisemap\.root/..\/qa\/${chip}\/${testbeam_alphabetic}-${chip}_HV${HV}-noisemap.root/g" geometry/${chip}/${testbeam_alphabetic}-${chip}_HV${HV}.geo

############################
# Prealign-tel config file #
############################
# copy file from prototype
cp "config/prealign_tel_${testbeam_alphabetic}-GAP18SQ_HV10.conf" "config/${chip}/prealign_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf"


# update detectors_file(s) file name
sed -i "s/geometry\/DESY-GAP18SQ_HV10/..\/geometry\/${chip}\/${testbeam_alphabetic}-${chip}_HV${HV}/g" config/${chip}/prealign_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# update output file name
#sed -i "s/prealignment/fox\/prealignment/g" config/${chip}/prealign_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf
sed -i "s/prealignment/${chip}\/prealign/g" config/${chip}/prealign_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# update file name (should only apply to .root at this point)
sed -i "s/DESY-GAP18SQ_HV10/${testbeam_alphabetic}-${chip}_HV${HV}/g" config/${chip}/prealign_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set number_of_events
sed -i "s/number_of_events.*$/number_of_events = ${number_of_events}/g" config/${chip}/prealign_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# replace inputfilename
sed -i "s/data\/ce65v2_pcb02_hv10_beam_run482100624_231128100629\.raw/..\/data\/${chip}\/ce65v2_${pcb}_hv${HV}${chillerTemp}_beam${windowSize}_run${run_number_beam}\.raw/g" config/${chip}/prealign_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf

#########################
# Align-tel config file #
#########################
# copy file from prototype
cp "config/align_tel_${testbeam_alphabetic}-GAP18SQ_HV10.conf" "config/${chip}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf"

# update detectors_file(s) file name
sed -i "s/geometry\/DESY-GAP18SQ_HV10/..\/geometry\/${chip}\/${testbeam_alphabetic}-${chip}_HV${HV}/g" config/${chip}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# update output file name
sed -i "s/alignment/${chip}\/align/g" config/${chip}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# update file name (should only apply to .root at this point)
sed -i "s/DESY-GAP18SQ_HV10/${testbeam_alphabetic}-${chip}_HV${HV}/g" config/${chip}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set number_of_events
sed -i "s/number_of_events.*$/number_of_events = ${number_of_events}/g" config/${chip}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# replace inputfilename
sed -i "s/data\/ce65v2_pcb02_hv10_beam_run482100624_231128100629\.raw/..\/data\/${chip}\/ce65v2_${pcb}_hv${HV}${chillerTemp}_beam${windowSize}_run${run_number_beam}\.raw/g" config/${chip}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf


# set momentum
sed -i "s/momentum=4GeV/momentum=${momentum}GeV/g" config/${chip}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf


############################
# Prealign-dut config file #
############################
# copy file from prototype
cp "config/prealign_dut_${testbeam_alphabetic}-GAP18SQ_HV10.conf" "config/${chip}/prealign_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf"

# update detectors_file(s) file name
sed -i "s/geometry\/DESY-GAP18SQ_HV10/..\/geometry\/${chip}\/${testbeam_alphabetic}-${chip}_HV${HV}/g" config/${chip}/prealign_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# update output file name
sed -i "s/prealignment/${chip}\/prealign/g" config/${chip}/prealign_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# update file name (should only apply to .root at this point)
sed -i "s/DESY-GAP18SQ_HV10/${testbeam_alphabetic}-${chip}_HV${HV}/g" config/${chip}/prealign_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf


# set number_of_events
sed -i "s/number_of_events.*$/number_of_events = ${number_of_events}/g" config/${chip}/prealign_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# replace inputfilename
sed -i "s/data\/ce65v2_pcb02_hv10_beam_run482100624_231128100629\.raw/..\/data\/${chip}\/ce65v2_${pcb}_hv${HV}${chillerTemp}_beam${windowSize}_run${run_number_beam}\.raw/g" config/${chip}/prealign_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set threshold_seed
sed -i "s/threshold_seed.*$/threshold_seed = ${seedthr_alignment}/g" config/${chip}/prealign_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set threshold_neighbor
sed -i "s/threshold_neighbor.*$/threshold_neighbor = ${nbh_alignment}/g" config/${chip}/prealign_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set thresholdSNR_seed
sed -i "s/thresholdSNR_seed.*$/thresholdSNR_seed = ${snr_seed_alignment}/g" config/${chip}/prealign_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set thresholdSNR_neighbor
sed -i "s/thresholdSNR_neighbor.*$/thresholdSNR_neighbor = ${snr_neighbor_alignment}/g" config/${chip}/prealign_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set method
sed -i "s/^method=cluster.*$/method = ${method_alignment}/g" config/${chip}/prealign_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf


#########################
# Align-dut config file #
#########################
# copy file from prototype
cp "config/align_dut_${testbeam_alphabetic}-GAP18SQ_HV10.conf" "config/${chip}/align_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf"

# update detectors_file(s) file name
sed -i "s/geometry\/DESY-GAP18SQ_HV10/..\/geometry\/${chip}\/${testbeam_alphabetic}-${chip}_HV${HV}/g" config/${chip}/align_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# update output file name
sed -i "s/alignment/${chip}\/align/g" config/${chip}/align_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# update file name (should only apply to .root at this point)
sed -i "s/DESY-GAP18SQ_HV10/${testbeam_alphabetic}-${chip}_HV${HV}/g" config/${chip}/align_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set number_of_events
sed -i "s/number_of_events.*$/number_of_events = ${number_of_events}/g" config/${chip}/align_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# replace inputfilename
sed -i "s/data\/ce65v2_pcb02_hv10_beam_run482100624_231128100629\.raw/..\/data\/${chip}\/ce65v2_${pcb}_hv${HV}${chillerTemp}_beam${windowSize}_run${run_number_beam}\.raw/g" config/${chip}/align_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set momentum
sed -i "s/momentum=4GeV/momentum=${momentum}GeV/g" config/${chip}/align_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set threshold_seed
sed -i "s/threshold_seed.*$/threshold_seed = ${seedthr_alignment}/g" config/${chip}/align_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set threshold_neighbor
sed -i "s/threshold_neighbor.*$/threshold_neighbor = ${nbh_alignment}/g" config/${chip}/align_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set thresholdSNR_seed
sed -i "s/thresholdSNR_seed.*$/thresholdSNR_seed = ${snr_seed_alignment}/g" config/${chip}/align_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set thresholdSNR_neighbor
sed -i "s/thresholdSNR_neighbor.*$/thresholdSNR_neighbor = ${snr_neighbor_alignment}/g" config/${chip}/align_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf


# set method
sed -i "s/^method=cluster.*$/method = ${method_alignment}/g" config/${chip}/align_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf



#########################
# Analysis config file #
#########################
# copy file from prototype
cp "config/analysis_${testbeam_alphabetic}-GAP18SQ_HV10.conf" "config/${chip}/analysis_${testbeam_alphabetic}-${chip}_HV${HV}.conf"

# update firstly histogram name
sed -i "s/analysis_DESY-GAP18SQ_HV10_482100624_231128100629_seedthr200_nbh50_snr3_cluster\.root/${chip}\/analysis_${testbeam_alphabetic}-${chip}_${run_number_beam}_seedthr${seedthr_analysis}_nbh${nbh_analysis}_snr${snr_seed_analysis}_${method_analysis}.root/g" config/${chip}/analysis_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# update detectors_file(s) file name
sed -i "s/geometry\/DESY-GAP18SQ_HV10/..\/geometry\/${chip}\/${testbeam_alphabetic}-${chip}_HV${HV}/g" config/${chip}/analysis_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# update file name (should only apply to .root at this point)
sed -i "s/DESY-GAP18SQ_HV10/${testbeam_alphabetic}-${chip}_HV${HV}/g" config/${chip}/analysis_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set number_of_events
sed -i "s/number_of_events.*$/number_of_events = ${number_of_events}/g" config/${chip}/analysis_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# replace inputfilename
sed -i "s/data\/ce65v2_pcb02_hv10_beam_run482100624_231128100629\.raw/..\/data\/${chip}\/ce65v2_${pcb}_hv${HV}${chillerTemp}_beam${windowSize}_run${run_number_beam}\.raw/g" config/${chip}/analysis_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set momentum
sed -i "s/momentum=4GeV/momentum=${momentum}GeV/g" config/${chip}/analysis_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set threshold_seed
sed -i "s/threshold_seed.*$/threshold_seed = ${seedthr_analysis}/g" config/${chip}/analysis_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set threshold_neighbor
sed -i "s/threshold_neighbor.*$/threshold_neighbor = ${nbh_analysis}/g" config/${chip}/analysis_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set thresholdSNR_seed
sed -i "s/thresholdSNR_seed.*$/thresholdSNR_seed = ${snr_seed_analysis}/g" config/${chip}/analysis_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set thresholdSNR_neighbor
sed -i "s/thresholdSNR_neighbor.*$/thresholdSNR_neighbor = ${snr_neighbor_analysis}/g" config/${chip}/analysis_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set method
sed -i "s/^method=cluster.*$/method = ${method_analysis}/g" config/${chip}/analysis_${testbeam_alphabetic}-${chip}_HV${HV}.conf




############
# Noisemap #
############

##VERIFY COMMANDS -> qa +  also output paths!

echo -e "\n\n\n\033[1;95mStarting DUMP\033[0m"
../eudaq/CE65V2Dump.py data/${chip}/${datafile_noise} -o qa/${chip}/${testbeam_alphabetic}-${chip}_HV${HV}-noise --qa --nx ${nx} --ny ${ny}

../eudaq/analog_qa_ce65v2.py qa/${chip}/${testbeam_alphabetic}-${chip}_HV${HV}-noise-qa.root -o qa/${chip}/${testbeam_alphabetic}-${chip}_HV${HV}-noisemap

####################
# Prealignment-tel #
####################

echo -e "\n\n\n\033[1;95m############################################################################\033[0m"
echo -e "\033[1;95m# execution : corry -c config/${chip}/prealign_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf #\033[0m"
echo -e "\033[1;95m############################################################################\033[0m\n\n\n\033[0m"

## Idea now is to introduce the number of iters.
# Start by defining necessary conf files. Geo files will be written out.
# Then call iterative process...
i=1
## it starts from 1. Thus every config file should be subscripted? else we will have too many else conditions...
while [ $i -le ${niter_prealign_tel} ]; do 
    cp config/${chip}/prealign_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf config/${chip}/prealign_tel_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
    sed -i "s/detectors_file_updated = \(.*\)\.conf/detectors_file_updated = \1_iter${i}.conf/g" config/${chip}/prealign_tel_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
    sed -i "s/histogram_file\(.*\)\.root/histogram_file\1_iter${i}.root/g" config/${chip}/prealign_tel_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
    if [ ${i} -gt 1 ]; then 
        sed -i "s/detectors_file \(.*\)\.geo/detectors_file \1_prealigned_tel_iter$((i-1)).conf/g" config/${chip}/prealign_tel_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
    fi
    corry -c config/${chip}/prealign_tel_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
    i=$((i+1))
done 
../corry/plot_analog_ce65v2.py -f output/${chip}/prealign_tel_${testbeam_alphabetic}-${chip}_HV${HV}_iter${niter_prealign_tel}.root --noisy-freq 0.95


#################
# Alignment-tel #
#################

echo -e "\n\n\n\033[1;95m#########################################################################\033[0m"
echo -e "\033[1;95m# execution : corry -c config/${chip}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf #\033[0m"
echo -e "\033[1;95m#########################################################################\033[0m\n\n\n"
i=1
#config/${chip}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf
## it starts from 1. Thus every config file should be subscripted? else we will have too many else conditions...
while [ $i -le ${niter_align_tel} ]; do 
    cp config/${chip}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf config/${chip}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
    sed -i "s/detectors_file_updated = \(.*\)\.conf/detectors_file_updated = \1_iter${i}.conf/g" config/${chip}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
    sed -i "s/histogram_file\(.*\)\.root/histogram_file\1_iter${i}.root/g" config/${chip}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
    if [ ${i} -gt 1 ]; then 
        sed -i "s/detectors_file \(.*\)\_prealigned_tel.conf/detectors_file \1_aligned_tel_iter$((i-1)).conf/g" config/${chip}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
    else 
        sed -i "s/detectors_file \(.*\)\.conf/detectors_file \1_iter${niter_prealign_tel}.conf/g" config/${chip}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
    fi
    corry -c config/${chip}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
    i=$((i+1))
done 
../corry/plot_analog_ce65v2.py -f output/${chip}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}_iter${niter_align_tel}.root --noisy-freq 0.95


####################
# Prealignment-dut #
####################

echo -e "\n\n\n\033[1;95m############################################################################\033[0m"
echo -e "\033[1;95m# execution : corry -c config/${chip}/prealign_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf #\033[0m"
echo -e "\033[1;95m############################################################################\033[0m\n\n\n"
i=1
while [ $i -le ${niter_prealign_dut} ]; do 
    cp config/${chip}/prealign_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf config/${chip}/prealign_dut_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
    sed -i "s/detectors_file_updated = \(.*\)\.conf/detectors_file_updated = \1_iter${i}.conf/g" config/${chip}/prealign_dut_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
    sed -i "s/histogram_file\(.*\)\.root/histogram_file\1_iter${i}.root/g" config/${chip}/prealign_dut_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
    if [ ${i} -gt 1 ]; then 
        sed -i "s/detectors_file \(.*\)\_aligned_tel.conf/detectors_file \1_prealigned_dut_iter$((i-1)).conf/g" config/${chip}/prealign_dut_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
    else 
        sed -i "s/detectors_file \(.*\)\.conf/detectors_file \1_iter${niter_align_tel}.conf/g" config/${chip}/prealign_dut_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
    fi
    corry -c config/${chip}/prealign_dut_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
    i=$((i+1))
done 

../corry/plot_analog_ce65v2.py -f output/${chip}/prealign_dut_${testbeam_alphabetic}-${chip}_HV${HV}_iter${niter_prealign_dut}.root --noisy-freq 0.95

#################
# Alignment-dut #
#################

echo -e "\n\n\n\033[1;95m#########################################################################\033[0m"
echo -e "\033[1;95m# execution : corry -c config/${chip}/align_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf #\033[0m"
echo -e "\033[1;95m#########################################################################\033[0m\n\n\n"
i=1
while [ $i -le ${niter_align_dut} ]; do 
    cp config/${chip}/align_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf config/${chip}/align_dut_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
    sed -i "s/detectors_file_updated = \(.*\)\.conf/detectors_file_updated = \1_iter${i}.conf/g" config/${chip}/align_dut_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
    sed -i "s/histogram_file\(.*\)\.root/histogram_file\1_iter${i}.root/g" config/${chip}/align_dut_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
    if [ ${i} -gt 1 ]; then 
        sed -i "s/detectors_file \(.*\)\_prealigned_dut.conf/detectors_file \1_aligned_dut_iter$((i-1)).conf/g" config/${chip}/align_dut_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
    else 
        sed -i "s/detectors_file \(.*\)\.conf/detectors_file \1_iter${niter_prealign_dut}.conf/g" config/${chip}/align_dut_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
    fi
    corry -c config/${chip}/align_dut_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
    i=$((i+1))
done 

../corry/plot_analog_ce65v2.py -f output/${chip}/align_dut_${testbeam_alphabetic}-${chip}_HV${HV}_iter${niter_align_dut}.root --noisy-freq 0.95

############
# Analysis #
############
echo -e "\n\n\n\033[1;95m############################################################\033[0m"
echo -e "\033[1;95m# corry -c config/${chip}/analysis_${testbeam_alphabetic}-${chip}_HV${HV}.conf #\033[0m"
echo -e "\033[1;95m############################################################\033[0m\n\n\n"


## Below is only necessary since I implemented the niters hackily...
sed -i "s/detectors_file \(.*\)\.conf/detectors_file \1_iter${niter_align_dut}.conf/g" config/${chip}/analysis_${testbeam_alphabetic}-${chip}_HV${HV}.conf
sed -i "s/detectors_file_updated = \(.*\)_aligned_dut_analysed.conf/detectors_file_updated = \1_aligned_dut_iter${niter_align_dut}_analysed.conf/g" config/${chip}/analysis_${testbeam_alphabetic}-${chip}_HV${HV}.conf
nx_prime=$((nx-1))
ny_prime=$((ny-1))
sed -i '/type = "ce65v2"/a\
roi = [[0,0],[0,'"$ny_prime"'],['"$nx_prime"','"$ny_prime"'],['"$nx_prime"',0]]' geometry/${chipWithRunNumber}/${testbeam_alphabetic}-${chipWithRunNumber}_HV${HV}_aligned_dut_iter${niter_align_dut}.conf

corry -c config/${chip}/analysis_${testbeam_alphabetic}-${chip}_HV${HV}.conf
../corry/plot_analog_ce65v2.py -f output/${chip}/analysis_${testbeam_alphabetic}-${chip}_${run_number_beam}_seedthr${seedthr_analysis}_nbh${nbh_analysis}_snr${snr_seed_analysis}_${method_analysis}.root


echo -e "\n\n\n\033[1;95m-FINISHED EXECUTION-\033[0m\n\n\n"












