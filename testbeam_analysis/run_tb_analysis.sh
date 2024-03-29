#!/bin/bash
set -e

##########
# Params #
##########

# Maybe re-order some of these, they look awkward
testbeam="DESY202311"
chip="STD15SQ"
#chip="GAP15SQ"
pcb="pcb06"
#HV=()
HV="10"
momentum=4   #GeV
#(optional, leave blank)
run_number_beam=""
run_number_noise=""
number_of_events=500
#number_of_events=-1
#number_of_events=9000 # only works for 9k events in GAP225SQ
## apparently not???
seedthr="350"
nbh="100"
snr_seed="9"
snr_neighbor="3"
method="cluster"

niter_prealign_tel=2
niter_align_tel=6
niter_prealign_dut=1
niter_align_dut=4







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



## We start by checking for the ITS3utils dir
its3_utils_path=`find .. -type d -name "ITS3utils"`
if [ -n "$its3_utils_path" ]; then
    its3_utils_path=`realpath $its3_utils_path`
else 
    echo "Cannot find dir \"ITS3utils\". Please make sure it is visible from within \"`pwd`\"."
    exit
fi

#echo "${its3_utils_path}"


#file_name = "../data/debug/ce65v2_pcb02_hv10_beam_run482100624_231128100629.raw"
#sed "s/\(.*\)/\L\1/g"

## Find beam+noise files
if [ ! -n "${run_number_beam}" ]; then
    datafile_beam=`ls -1S ${its3_utils_path}/${testbeam}/data/${chip}/ce65v2_${pcb}_hv${HV}_beam_run[0-9]*_[0-9]*.raw | head -1`
else
    datafile_beam=`ls -1S ${its3_utils_path}/${testbeam}/data/${chip}/ce65v2_${pcb}_hv${HV}_beam_run${run_number_beam}.raw | head -1`
fi
if [ ! -n "${datafile_beam}" ]; then
    echo "Failed to find file(s) : \"${its3_utils_path}/${testbeam}/data/${chip}/ce65v2_${pcb}_hv${HV}_beam_run[0-9]*_[0-9]*.raw \". Have you ran \"copy_tb_files.sh\" already?"
    exit
fi
datafile_beam=`echo "${datafile_beam}" | sed "s/.*\/\([a-zA-Z0-9_.]*$\)/\1/"`
run_number_beam=`echo "${datafile_beam}" | sed "s/.*run\([0-9]*_[0-9]*\)\.raw/\1/g"`

if [ ! -n "${run_number_noise}" ]; then
    datafile_noise=`ls -1S ${its3_utils_path}/${testbeam}/data/${chip}/ce65v2_${pcb}_hv${HV}_noise_run[0-9]*_[0-9]*.raw | head -1`
else
    datafile_noise=`ls -1S ${its3_utils_path}/${testbeam}/data/${chip}/ce65v2_${pcb}_hv${HV}_noise_run${run_number_noise}.raw | head -1`
fi
if [ ! -n "${datafile_noise}" ]; then
    echo "Failed to find file(s) : \"${its3_utils_path}/${testbeam}/data/${chip}/ce65v2_${pcb}_hv${HV}_noise_run[0-9]*_[0-9]*.raw \". Have you ran \"copy_tb_files.sh\" already?"
    exit
fi
datafile_noise=`echo "${datafile_noise}" | sed "s/.*\/\([a-zA-Z0-9_.]*$\)/\1/"`
run_number_noise=`echo "${datafile_noise}" | sed "s/.*run\([0-9]*_[0-9]*\)\.raw/\1/g"`






## We then copy over the necessary files 
#prealign + align tel
#prealign + align dut

#########
# MKDIR #
#########

cd "${its3_utils_path}/${testbeam}"
dirs=( config geometry masks qa output )
for dir in ${dirs[@]}; do
    if [ ! -d "${dir}/${chip}" ]; then 
        mkdir ${dir}/${chip}
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
sed -i "s/masks/masks\/${chip}/g" geometry/${chip}/${testbeam_alphabetic}-${chip}_HV${HV}.geo
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
sed -i "s/data\/ce65v2_pcb02_hv10_beam_run482100624_231128100629\.raw/..\/data\/${chip}\/ce65v2_${pcb}_hv${HV}_beam_run${run_number_beam}\.raw/g" config/${chip}/prealign_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf

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
sed -i "s/data\/ce65v2_pcb02_hv10_beam_run482100624_231128100629\.raw/..\/data\/${chip}\/ce65v2_${pcb}_hv${HV}_beam_run${run_number_beam}\.raw/g" config/${chip}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf


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
sed -i "s/data\/ce65v2_pcb02_hv10_beam_run482100624_231128100629\.raw/..\/data\/${chip}\/ce65v2_${pcb}_hv${HV}_beam_run${run_number_beam}\.raw/g" config/${chip}/prealign_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set threshold_seed
sed -i "s/threshold_seed.*$/threshold_seed = ${seedthr}/g" config/${chip}/prealign_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set threshold_neighbor
sed -i "s/threshold_neighbor.*$/threshold_neighbor = ${nbh}/g" config/${chip}/prealign_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set thresholdSNR_seed
sed -i "s/thresholdSNR_seed.*$/thresholdSNR_seed = ${snr_seed}/g" config/${chip}/prealign_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set thresholdSNR_neighbor
sed -i "s/thresholdSNR_neighbor.*$/thresholdSNR_neighbor = ${snr_neighbor}/g" config/${chip}/prealign_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set method
sed -i "s/^method=cluster.*$/method = ${method}/g" config/${chip}/prealign_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf


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
sed -i "s/data\/ce65v2_pcb02_hv10_beam_run482100624_231128100629\.raw/..\/data\/${chip}\/ce65v2_${pcb}_hv${HV}_beam_run${run_number_beam}\.raw/g" config/${chip}/align_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set momentum
sed -i "s/momentum=4GeV/momentum=${momentum}GeV/g" config/${chip}/align_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set threshold_seed
sed -i "s/threshold_seed.*$/threshold_seed = ${seedthr}/g" config/${chip}/align_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set threshold_neighbor
sed -i "s/threshold_neighbor.*$/threshold_neighbor = ${nbh}/g" config/${chip}/align_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set thresholdSNR_seed
sed -i "s/thresholdSNR_seed.*$/thresholdSNR_seed = ${snr_seed}/g" config/${chip}/align_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set thresholdSNR_neighbor
sed -i "s/thresholdSNR_neighbor.*$/thresholdSNR_neighbor = ${snr_neighbor}/g" config/${chip}/align_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf


# set method
sed -i "s/^method=cluster.*$/method = ${method}/g" config/${chip}/align_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf



#########################
# Analysis config file #
#########################
# copy file from prototype
cp "config/analysis_${testbeam_alphabetic}-GAP18SQ_HV10.conf" "config/${chip}/analysis_${testbeam_alphabetic}-${chip}_HV${HV}.conf"

# update firstly histogram name
sed -i "s/analysis_DESY-GAP18SQ_HV10_482100624_231128100629_seedthr200_nbh50_snr3_cluster\.root/${chip}\/analysis_${testbeam_alphabetic}-${chip}_${run_number_beam}_seedthr${seedthr}_nbh${nbh}_snr${snr}_${method}.root/g" config/${chip}/analysis_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# update detectors_file(s) file name
sed -i "s/geometry\/DESY-GAP18SQ_HV10/..\/geometry\/${chip}\/${testbeam_alphabetic}-${chip}_HV${HV}/g" config/${chip}/analysis_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# update file name (should only apply to .root at this point)
sed -i "s/DESY-GAP18SQ_HV10/${testbeam_alphabetic}-${chip}_HV${HV}/g" config/${chip}/analysis_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set number_of_events
sed -i "s/number_of_events.*$/number_of_events = ${number_of_events}/g" config/${chip}/analysis_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# replace inputfilename
sed -i "s/data\/ce65v2_pcb02_hv10_beam_run482100624_231128100629\.raw/..\/data\/${chip}\/ce65v2_${pcb}_hv${HV}_beam_run${run_number_beam}\.raw/g" config/${chip}/analysis_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set momentum
sed -i "s/momentum=4GeV/momentum=${momentum}GeV/g" config/${chip}/analysis_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set threshold_seed
sed -i "s/threshold_seed.*$/threshold_seed = ${seedthr}/g" config/${chip}/analysis_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set threshold_neighbor
sed -i "s/threshold_neighbor.*$/threshold_neighbor = ${nbh}/g" config/${chip}/analysis_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set thresholdSNR_seed
sed -i "s/thresholdSNR_seed.*$/thresholdSNR_seed = ${snr_seed}/g" config/${chip}/analysis_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set thresholdSNR_neighbor
sed -i "s/thresholdSNR_neighbor.*$/thresholdSNR_neighbor = ${snr_neighbor}/g" config/${chip}/analysis_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set method
sed -i "s/^method=cluster.*$/method = ${method}/g" config/${chip}/analysis_${testbeam_alphabetic}-${chip}_HV${HV}.conf





############
# Noisemap #
############

##VERIFY COMMANDS -> qa +  also output paths!

echo "Starting DUMP"
../eudaq/CE65V2Dump.py data/${chip}/${datafile_noise} -o qa/${chip}/${testbeam_alphabetic}-${chip}_HV${HV}-noise --qa 

../eudaq/analog_qa_ce65v2.py qa/${chip}/${testbeam_alphabetic}-${chip}_HV${HV}-noise-qa.root -o qa/${chip}/${testbeam_alphabetic}-${chip}_HV${HV}-noisemap

####################
# Prealignment-tel #
####################

echo "################################################################################"
echo "# execution : corry -c config/${chip}/prealign_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf #"
echo "################################################################################"

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

echo "################################################################################"
echo "# execution : corry -c config/${chip}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf #"
echo "################################################################################"
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

#corry -c config/${chip}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf
#../corry/plot_analog_ce65v2.py -f output/${chip}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}.root

####################
# Prealignment-dut #
####################

echo "################################################################################"
echo "execution : corry -c config/${chip}/prealign_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf"
echo "################################################################################"
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
##corry -c config/${chip}/prealign_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf
##../corry/plot_analog_ce65v2.py -f output/${chip}/prealign_dut_${testbeam_alphabetic}-${chip}_HV${HV}.root --noisy-freq 0.95

#################
# Alignment-dut #
#################

echo "################################################################################"
echo "execution : corry -c config/${chip}/align_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf"
echo "################################################################################"
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
#corry -c config/${chip}/align_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf
#../corry/plot_analog_ce65v2.py -f output/${chip}/align_dut_${testbeam_alphabetic}-${chip}_HV${HV}.root

############
# Analysis #
############
echo "################################################################################"
echo "# corry -c config/${chip}/analysis_${testbeam_alphabetic}-${chip}_HV${HV}.conf #"
echo "################################################################################"

### It is important to specify the roi in the analysis geometry file prior to analysis
sed -i '/type = "ce65v2"/a\
roi = [[0,0],[0,24],[47,24],[47,0]]' geometry/${chip}/DESY-${chip}_HV${HV}_aligned_dut.conf

## Below is only necessary since I implemented the niters hackily...
sed -i "s/detectors_file \(.*\)\.conf/detectors_file \1_iter${niter_align_dut}.conf/g" config/${chip}/analysis_${testbeam_alphabetic}-${chip}_HV${HV}.conf
sed -i "s/detectors_file_updated = \(.*\)_aligned_dut_analysed.conf/detectors_file_updated = \1_aligned_dut_iter${niter_align_dut}_analysed.conf/g" config/${chip}/analysis_${testbeam_alphabetic}-${chip}_HV${HV}.conf
sed -i '/type = "ce65v2"/a\
roi = [[0,0],[0,24],[47,24],[47,0]]' geometry/${chip}/DESY-${chip}_HV${HV}_aligned_dut_iter${niter_align_dut}.conf

corry -c config/${chip}/analysis_${testbeam_alphabetic}-${chip}_HV${HV}.conf
../corry/plot_analog_ce65v2.py -f output/${chip}/analysis_${testbeam_alphabetic}-${chip}_${run_number_beam}_seedthr${seedthr}_nbh${nbh}_snr${snr}_${method}.root


echo "-FINISHED EXECUTION-"












