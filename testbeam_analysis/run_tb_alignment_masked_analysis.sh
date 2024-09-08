#!/bin/bash
set -e
set -x


# Philosophy: This script is basically just "run_tb_analysis.sh", but altered to run a couple different (telescope) alignments

# Syntax: This script is run within the container as "./run_tb_alignment.sh --tag 007 params/SPS202404/ament_tests/STD225SQ/007/STD225SQ.txt" 



date


## Require passing of the tag via command line hackily
if [[ ! "$1" = "--tag" ]]; then
    echo "No \"--tag\" option passed. Please pass (numerical) tag via \"--tag 01293\"!"
    exit 1
else 
    if echo "$2" | grep -Eq '^[0-9]+$'; then
        tag="$2"
    else
        echo "Error parsing the tag!"
        exit 1
    fi
fi


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

spatial_cuts=(100 100 75 75 50 50 25 25)

absolute_filepath=""




## Allow passing of params via command-line specified .txt file
if [[ $# -eq 3 && -f "$3" ]]; then
    source $3
else 
    echo "No params .txt file passed. Exiting since this is required for this script."
    exit 1
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
chips["pcb10"]="GAP225SQ"
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

    ## Replacing window size in CE65RawEvent2StdEventConverter class and recompile
    sed -i "s/X_MX_SIZE = 48/X_MX_SIZE = $nx/" /opt/eudaq2/user/ITS3/module/src/CE65RawEvent2StdEventConverter.cc
    sed -i "s/Y_MX_SIZE = 24/Y_MX_SIZE = $ny/" /opt/eudaq2/user/ITS3/module/src/CE65RawEvent2StdEventConverter.cc
    cd /opt/eudaq2/build/
    cmake ..
    make install
    cd -
else
    #echo "Window size not defined, use full window of NX=48 and NY=24. Continuing!"
    nx=48
    ny=24
fi


## We start by checking for the ITS3utils dir
its3_utils_path=`find . -type d -name "ITS3utils"`
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

# Very similar to before but now inside ament_tests dir
if [ ! -d "${its3_utils_path}/${testbeam}/ament_tests" ]; then 
    mkdir ${its3_utils_path}/${testbeam}/ament_tests
fi
cd "${its3_utils_path}/${testbeam}/ament_tests"
# cd "${its3_utils_path}/${testbeam}"
dirs=( config geometry masks qa output data )
for dir in ${dirs[@]}; do

    # if [ ! -d "ament_tests/${dir}/${chip}/${tag}" ]; then 
    #     mkdir -p "ament_tests/${dir}/${chip}/${tag}"
    if [ ! -d "${dir}/${chip}/${tag}" ]; then 
        mkdir -p "${dir}/${chip}/${tag}"
    fi

    if [ "${dir}" == "masks" ]; then 
        for i in {0..5}; do 
           touch masks/${chip}/${tag}/ref-plane${i}_HV${HV}.txt 
           # touch ament_tests/masks/${chip}/${tag}/ref-plane${i}_HV${HV}.txt 
       done
    fi
done 

# Need to create subdirs within output folder just to avoid hassle
# if [ ! -d "${its3_utils_path}/${testbeam}/output/ament_tests/${chip}/${tag}" ]; then 
#     mkdir -p "${its3_utils_path}/${testbeam}/output/ament_tests/${chip}/${tag}"
# fi

testbeam_alphabetic=`echo "${testbeam}" | egrep -o "^[A-Z]+"`




# Now we copy over the files and use `sed` to edit them
## By convention the prototype for each of the copies will be in the parent directory of the class (e.g. masks/ref-plane0.txt)



#######################
# Define source files #
#######################
geo_source="../geometry/${testbeam_alphabetic}-GAP18SQ_HV10.geo" 
prealign_source="../config/prealign_tel_${testbeam_alphabetic}-GAP18SQ_HV10.conf" 
align_source="../config/align_tel_${testbeam_alphabetic}-GAP18SQ_HV10.conf" 
prealign_dut_source="../config/prealign_dut_${testbeam_alphabetic}-GAP18SQ_HV10.conf" 
align_dut_source="../config/align_dut_${testbeam_alphabetic}-GAP18SQ_HV10.conf" 

# check tag passed through params file matches command line tag
ptag=$(echo `dirname "$3"` | cut -d'/' -f5)
if [ ! ${ptag} = ${tag} ]; then 
    echo "Tag mismatch. Please match tags passed in command line and params file."
fi

# redefine source files if they have been passed
if [ -e $its3_utils_path/../`dirname "$3"`/${testbeam_alphabetic}-GAP18SQ_HV10.geo ]; then 
    geo_source=$its3_utils_path/../`dirname "$3"`/${testbeam_alphabetic}-GAP18SQ_HV10.geo 
fi
if [ -e $its3_utils_path/../`dirname "$3"`/prealign_tel_${testbeam_alphabetic}-GAP18SQ_HV10.conf ]; then 
    prealign_source=$its3_utils_path/../`dirname "$3"`/prealign_tel_${testbeam_alphabetic}-GAP18SQ_HV10.conf 
fi
if [ -e $its3_utils_path/../`dirname "$3"`/align_tel_${testbeam_alphabetic}-GAP18SQ_HV10.conf ]; then 
    align_source=$its3_utils_path/../`dirname "$3"`/align_tel_${testbeam_alphabetic}-GAP18SQ_HV10.conf 
fi
if [ -e $its3_utils_path/../`dirname "$3"`/prealign_dut_${testbeam_alphabetic}-GAP18SQ_HV10.conf ]; then 
    prealign_dut_source=$its3_utils_path/../`dirname "$3"`/prealign_dut_${testbeam_alphabetic}-GAP18SQ_HV10.conf 
fi
if [ -e $its3_utils_path/../`dirname "$3"`/align_dut_${testbeam_alphabetic}-GAP18SQ_HV10.conf ]; then 
    align_dut_source=$its3_utils_path/../`dirname "$3"`/align_dut_${testbeam_alphabetic}-GAP18SQ_HV10.conf 
fi

#####################################################
# Check if absolute path is provided in params file #
#####################################################




#################
# Geometry file #
#################
# copy file from prototype
cp ${geo_source} "geometry/${chip}/${tag}/${testbeam_alphabetic}-${chip}_HV${HV}.geo"

# If geo_source is default, then we must alter it. Otherwise it is assumed to be correct.
if [ "${geo_source}" == "../geometry/${testbeam_alphabetic}-GAP18SQ_HV10.geo" ]; then

    # replace masks into chip subdir
    sed -i "s/DESY202311\/masks/..\/..\/${testbeam}\/ament_tests\/masks\/${chip}\/${tag}/g" geometry/${chip}/${tag}/${testbeam_alphabetic}-${chip}_HV${HV}.geo
    # add hv to mask names
    sed -i "s/\(plane[0-5]\)/\1_HV${HV}/g" geometry/${chip}/${tag}/${testbeam_alphabetic}-${chip}_HV${HV}.geo
    
    # write correct CE65V2 pixel-pitch
    pitch=`echo "${chip}" | egrep -o "[0-9]+"`
    if [ "${pitch}" -gt "100" ]; then
        pitch=`echo "22.5"`
    fi
    sed -i "s/pixel_pitch = 18um, 18um/pixel_pitch = ${pitch}um, ${pitch}um/g" geometry/${chip}/${tag}/${testbeam_alphabetic}-${chip}_HV${HV}.geo
    
    
    # Note that here we are actually keeping the old noisemap file
    sed -i "s/qa\/DESY-GAP18SQ_HV10-noisemap\.root/..\/..\/..\/qa\/${chip}\/${testbeam_alphabetic}-${chip}_HV${HV}-noisemap.root/g" geometry/${chip}/${tag}/${testbeam_alphabetic}-${chip}_HV${HV}.geo

fi


############################
# Prealign-tel config file #
############################
# copy file from prototype
# cp "config/prealign_tel_${testbeam_alphabetic}-GAP18SQ_HV10.conf" "ament_tests/config/${chip}/${tag}/prealign_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf"
cp ${prealign_source} "config/${chip}/${tag}/prealign_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf"


# update detectors_file(s) file name
# sed -i "s/geometry\/DESY-GAP18SQ_HV10/..\/..\/..\/ament_tests\/geometry\/${chip}\/${tag}\/${testbeam_alphabetic}-${chip}_HV${HV}/g" ament_tests/config/${chip}/${tag}/prealign_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf
sed -i "s/geometry\/DESY-GAP18SQ_HV10/..\/..\/..\/ament_tests\/geometry\/${chip}\/${tag}\/${testbeam_alphabetic}-${chip}_HV${HV}/g" config/${chip}/${tag}/prealign_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# update output file name
#sed -i "s/prealignment/fox\/prealignment/g" config/${chip}/prealign_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf
# sed -i "s/prealignment/ament_tests\/${chip}\/${tag}\/prealign/g" ament_tests/config/${chip}/${tag}/prealign_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf
sed -i "s/prealignment/${chip}\/${tag}\/prealign/g" config/${chip}/${tag}/prealign_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# update file name (should only apply to .root at this point)
# sed -i "s/DESY-GAP18SQ_HV10/${testbeam_alphabetic}-${chip}_HV${HV}/g" ament_tests/config/${chip}/${tag}/prealign_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf
sed -i "s/DESY-GAP18SQ_HV10/${testbeam_alphabetic}-${chip}_HV${HV}/g" config/${chip}/${tag}/prealign_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set number_of_events
# sed -i "s/number_of_events.*$/number_of_events = ${number_of_events}/g" ament_tests/config/${chip}/${tag}/prealign_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf
sed -i "s/number_of_events.*$/number_of_events = ${number_of_events}/g" config/${chip}/${tag}/prealign_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# replace inputfilename
# sed -i "s/data\/ce65v2_pcb02_hv10_beam_run482100624_231128100629\.raw/..\/data\/${chip}\/ce65v2_${pcb}_hv${HV}${chillerTemp}_beam${windowSize}_run${run_number_beam}\.raw/g" ament_tests/config/${chip}/${tag}/prealign_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf
if [ -n "${absolute_filepath}" ]; then
    # sed w/ abs filepath
    sed -i "s/\.\.\/data\/ce65v2_pcb02_hv10_beam_run482100624_231128100629\.raw/${absolute_filepath}/g" config/${chip}/${tag}/prealign_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf
else
    sed -i "s/data\/ce65v2_pcb02_hv10_beam_run482100624_231128100629\.raw/..\/..\/..\/data\/${chip}\/ce65v2_${pcb}_hv${HV}${chillerTemp}_beam${windowSize}_run${run_number_beam}\.raw/g" config/${chip}/${tag}/prealign_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf
fi


#########################
# Align-tel config file #
#########################
# copy file from prototype
# cp "config/align_tel_${testbeam_alphabetic}-GAP18SQ_HV10.conf" "ament_tests/config/${chip}/${tag}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf"
cp ${align_source} "config/${chip}/${tag}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf"

# update detectors_file(s) file name
# sed -i "s/geometry\/DESY-GAP18SQ_HV10/..\/ament_tests\/geometry\/${chip}\/${tag}\/${testbeam_alphabetic}-${chip}_HV${HV}/g" ament_tests/config/${chip}/${tag}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf
sed -i "s/geometry\/DESY-GAP18SQ_HV10/..\/..\/..\/ament_tests\/geometry\/${chip}\/${tag}\/${testbeam_alphabetic}-${chip}_HV${HV}/g" config/${chip}/${tag}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# update output file name
# sed -i "s/alignment/${chip}\/${tag}\/align/g" ament_tests/config/${chip}/${tag}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf
sed -i "s/alignment/${chip}\/${tag}\/align/g" config/${chip}/${tag}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# update file name (should only apply to .root at this point)
# sed -i "s/DESY-GAP18SQ_HV10/${testbeam_alphabetic}-${chip}_HV${HV}/g" ament_tests/config/${chip}/${tag}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf

sed -i "s/DESY-GAP18SQ_HV10/${testbeam_alphabetic}-${chip}_HV${HV}/g" config/${chip}/${tag}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set number_of_events
# sed -i "s/number_of_events.*$/number_of_events = ${number_of_events}/g" ament_tests/config/${chip}/${tag}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf
sed -i "s/number_of_events.*$/number_of_events = ${number_of_events}/g" config/${chip}/${tag}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# replace inputfilename
# sed -i "s/data\/ce65v2_pcb02_hv10_beam_run482100624_231128100629\.raw/..\/data\/${chip}\/ce65v2_${pcb}_hv${HV}${chillerTemp}_beam${windowSize}_run${run_number_beam}\.raw/g" ament_tests/config/${chip}/${tag}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf
if [ -n "${absolute_filepath}" ]; then
    # sed w/ abs filepath
    sed -i "s/\.\.\/data\/ce65v2_pcb02_hv10_beam_run482100624_231128100629\.raw/${absolute_filepath}/g" config/${chip}/${tag}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf
else
    sed -i "s/data\/ce65v2_pcb02_hv10_beam_run482100624_231128100629\.raw/..\/..\/..\/data\/${chip}\/ce65v2_${pcb}_hv${HV}${chillerTemp}_beam${windowSize}_run${run_number_beam}\.raw/g" config/${chip}/${tag}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf
fi

# set momentum
# sed -i "s/momentum=4GeV/momentum=${momentum}GeV/g" ament_tests/config/${chip}/${tag}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf
sed -i "s/momentum=4GeV/momentum=${momentum}GeV/g" config/${chip}/${tag}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf




############################
# Prealign-dut config file #
############################
# copy file from prototype
cp ${prealign_dut_source} "config/${chip}/${tag}/prealign_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf"

# update detectors_file(s) file name
sed -i "s/geometry\/DESY-GAP18SQ_HV10/..\/..\/..\/ament_tests\/geometry\/${chip}\/${tag}\/${testbeam_alphabetic}-${chip}_HV${HV}/g" config/${chip}/${tag}/prealign_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# update output file name
sed -i "s/prealignment/${chip}\/${tag}\/prealign/g" config/${chip}/${tag}/prealign_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# update file name (should only apply to .root at this point)
sed -i "s/DESY-GAP18SQ_HV10/${testbeam_alphabetic}-${chip}_HV${HV}/g" config/${chip}/${tag}/prealign_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf


# set number_of_events
sed -i "s/number_of_events.*$/number_of_events = ${number_of_events}/g" config/${chip}/${tag}/prealign_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# replace inputfilename
if [ -n "${absolute_filepath}" ]; then
    # sed w/ abs filepath
    sed -i "s/\.\.\/data\/ce65v2_pcb02_hv10_beam_run482100624_231128100629\.raw/${absolute_filepath}/g" config/${chip}/${tag}/prealign_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf
else
    sed -i "s/data\/ce65v2_pcb02_hv10_beam_run482100624_231128100629\.raw/..\/..\/..\/data\/${chip}\/ce65v2_${pcb}_hv${HV}${chillerTemp}_beam${windowSize}_run${run_number_beam}\.raw/g" config/${chip}/${tag}/prealign_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf
fi

# set threshold_seed
sed -i "s/threshold_seed.*$/threshold_seed = ${seedthr_alignment}/g" config/${chip}/${tag}/prealign_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set threshold_neighbor
sed -i "s/threshold_neighbor.*$/threshold_neighbor = ${nbh_alignment}/g" config/${chip}/${tag}/prealign_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set thresholdSNR_seed
sed -i "s/thresholdSNR_seed.*$/thresholdSNR_seed = ${snr_seed_alignment}/g" config/${chip}/${tag}/prealign_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set thresholdSNR_neighbor
sed -i "s/thresholdSNR_neighbor.*$/thresholdSNR_neighbor = ${snr_neighbor_alignment}/g" config/${chip}/${tag}/prealign_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set method
sed -i "s/^method=cluster.*$/method = ${method_alignment}/g" config/${chip}/${tag}/prealign_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf


#########################
# Align-dut config file #
#########################
# copy file from prototype
cp ${align_dut_source} "config/${chip}/${tag}/align_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf"

# update detectors_file(s) file name
sed -i "s/geometry\/DESY-GAP18SQ_HV10/..\/..\/..\/ament_tests\/geometry\/${chip}\/${tag}\/${testbeam_alphabetic}-${chip}_HV${HV}/g" config/${chip}/${tag}/align_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# update output file name
sed -i "s/alignment/${chip}\/${tag}\/align/g" config/${chip}/${tag}/align_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# update file name (should only apply to .root at this point)
sed -i "s/DESY-GAP18SQ_HV10/${testbeam_alphabetic}-${chip}_HV${HV}/g" config/${chip}/${tag}/align_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set number_of_events
sed -i "s/number_of_events.*$/number_of_events = ${number_of_events}/g" config/${chip}/${tag}/align_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# replace inputfilename
if [ -n "${absolute_filepath}" ]; then
    # sed w/ abs filepath
    sed -i "s/\.\.\/data\/ce65v2_pcb02_hv10_beam_run482100624_231128100629\.raw/${absolute_filepath}/g" config/${chip}/${tag}/align_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf
else
    sed -i "s/data\/ce65v2_pcb02_hv10_beam_run482100624_231128100629\.raw/..\/..\/..\/data\/${chip}\/ce65v2_${pcb}_hv${HV}${chillerTemp}_beam${windowSize}_run${run_number_beam}\.raw/g" config/${chip}/${tag}/align_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf
fi

# set momentum
sed -i "s/momentum=4GeV/momentum=${momentum}GeV/g" config/${chip}/${tag}/align_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set threshold_seed
sed -i "s/threshold_seed.*$/threshold_seed = ${seedthr_alignment}/g" config/${chip}/${tag}/align_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set threshold_neighbor
sed -i "s/threshold_neighbor.*$/threshold_neighbor = ${nbh_alignment}/g" config/${chip}/${tag}/align_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set thresholdSNR_seed
sed -i "s/thresholdSNR_seed.*$/thresholdSNR_seed = ${snr_seed_alignment}/g" config/${chip}/${tag}/align_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set thresholdSNR_neighbor
sed -i "s/thresholdSNR_neighbor.*$/thresholdSNR_neighbor = ${snr_neighbor_alignment}/g" config/${chip}/${tag}/align_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf


# set method
sed -i "s/^method=cluster.*$/method = ${method_alignment}/g" config/${chip}/${tag}/align_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf



#########################
# Analysis config file #
#########################
# copy file from prototype
cp "../config/analysis_${testbeam_alphabetic}-GAP18SQ_HV10.conf" "config/${chip}/${tag}/analysis_${testbeam_alphabetic}-${chip}_HV${HV}.conf"

# update firstly histogram name
sed -i "s/analysis_DESY-GAP18SQ_HV10_482100624_231128100629_seedthr200_nbh50_snr3_cluster\.root/${chip}\/${tag}\/analysis_${testbeam_alphabetic}-${chip}_${run_number_beam}_seedthr${seedthr_analysis}_nbh${nbh_analysis}_snr${snr_seed_analysis}_${method_analysis}.root/g" config/${chip}/${tag}/analysis_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# update detectors_file(s) file name
sed -i "s/geometry\/DESY-GAP18SQ_HV10/..\/..\/geometry\/${chip}\/${tag}\/${testbeam_alphabetic}-${chip}_HV${HV}/g" config/${chip}/${tag}/analysis_${testbeam_alphabetic}-${chip}_HV${HV}.conf



# update file name (should only apply to .root at this point)
sed -i "s/DESY-GAP18SQ_HV10/${testbeam_alphabetic}-${chip}_HV${HV}/g" config/${chip}/${tag}/analysis_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set number_of_events
sed -i "s/number_of_events.*$/number_of_events = ${number_of_events}/g" config/${chip}/${tag}/analysis_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# replace inputfilename
# sed -i "s/data\/ce65v2_pcb02_hv10_beam_run482100624_231128100629\.raw/..\/..\/data\/${chip}\/${tag}\/ce65v2_${pcb}_hv${HV}${chillerTemp}_beam${windowSize}_run${run_number_beam}\.raw/g" config/${chip}/${tag}/analysis_${testbeam_alphabetic}-${chip}_HV${HV}.conf
# replace inputfilename
if [ -n "${absolute_filepath}" ]; then
    # sed w/ abs filepath
    sed -i "s/\.\.\/data\/ce65v2_pcb02_hv10_beam_run482100624_231128100629\.raw/${absolute_filepath}/g" config/${chip}/${tag}/analysis_${testbeam_alphabetic}-${chip}_HV${HV}.conf
else
    sed -i "s/data\/ce65v2_pcb02_hv10_beam_run482100624_231128100629\.raw/..\/..\/..\/data\/${chip}\/ce65v2_${pcb}_hv${HV}${chillerTemp}_beam${windowSize}_run${run_number_beam}\.raw/g" config/${chip}/${tag}/analysis_${testbeam_alphabetic}-${chip}_HV${HV}.conf
fi

# set momentum
sed -i "s/momentum=4GeV/momentum=${momentum}GeV/g" config/${chip}/${tag}/analysis_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set threshold_seed
sed -i "s/threshold_seed.*$/threshold_seed = ${seedthr_analysis}/g" config/${chip}/${tag}/analysis_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set threshold_neighbor
sed -i "s/threshold_neighbor.*$/threshold_neighbor = ${nbh_analysis}/g" config/${chip}/${tag}/analysis_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set thresholdSNR_seed
sed -i "s/thresholdSNR_seed.*$/thresholdSNR_seed = ${snr_seed_analysis}/g" config/${chip}/${tag}/analysis_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set thresholdSNR_neighbor
sed -i "s/thresholdSNR_neighbor.*$/thresholdSNR_neighbor = ${snr_neighbor_analysis}/g" config/${chip}/${tag}/analysis_${testbeam_alphabetic}-${chip}_HV${HV}.conf

# set method
sed -i "s/^method=cluster.*$/method = ${method_analysis}/g" config/${chip}/${tag}/analysis_${testbeam_alphabetic}-${chip}_HV${HV}.conf




# ############
# # Noisemap #
# ############
#
# ##VERIFY COMMANDS -> qa +  also output paths!
#
# echo -e "\n\n\n\033[1;95mStarting DUMP\033[0m"
# ../../eudaq/CE65V2Dump.py ../data/${chip}/${datafile_noise} -o qa/${chip}/${testbeam_alphabetic}-${chip}_HV${HV}-noise --qa --nx ${nx} --ny ${ny}
#
# ../../eudaq/analog_qa_ce65v2.py qa/${chip}/${testbeam_alphabetic}-${chip}_HV${HV}-noise-qa.root -o qa/${chip}/${testbeam_alphabetic}-${chip}_HV${HV}-noisemap
#
# exit




####################
# Prealignment-tel #
####################

echo -e "\n\n\n\033[1;95m############################################################################\033[0m"
# echo -e "\033[1;95m# execution : corry -c ament_tests/config/${chip}/${tag}/prealign_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf #\033[0m"
echo -e "\033[1;95m# execution : corry -c config/${chip}/${tag}/prealign_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf #\033[0m"
echo -e "\033[1;95m############################################################################\033[0m\n\n\n\033[0m"

## Idea now is to introduce the number of iters.
# Start by defining necessary conf files. Geo files will be written out.
# Then call iterative process...
i=1
## it starts from 1. Thus every config file should be subscripted? else we will have too many else conditions...
while [ $i -le ${niter_prealign_tel} ]; do 
    # cp ament_tests/config/${chip}/${tag}/prealign_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf ament_tests/config/${chip}/${tag}/prealign_tel_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
    cp config/${chip}/${tag}/prealign_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf config/${chip}/${tag}/prealign_tel_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
    # sed -i "s/detectors_file_updated = \(.*\)\.conf/detectors_file_updated = \1_iter${i}.conf/g" ament_tests/config/${chip}/${tag}/prealign_tel_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
    sed -i "s/detectors_file_updated = \(.*\)\.conf/detectors_file_updated = \1_iter${i}.conf/g" config/${chip}/${tag}/prealign_tel_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
    # sed -i "s/histogram_file\(.*\)\.root/histogram_file\1_iter${i}.root/g" ament_tests/config/${chip}/${tag}/prealign_tel_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
    sed -i "s/histogram_file\(.*\)\.root/histogram_file\1_iter${i}.root/g" config/${chip}/${tag}/prealign_tel_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
    if [ ${i} -gt 1 ]; then 
        # sed -i "s/detectors_file \(.*\)\.geo/detectors_file \1_prealigned_tel_iter$((i-1)).conf/g" ament_tests/config/${chip}/${tag}/prealign_tel_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
        sed -i "s/detectors_file \(.*\)\.geo/detectors_file \1_prealigned_tel_iter$((i-1)).conf/g" config/${chip}/${tag}/prealign_tel_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
    fi
    # corry -c config/${chip}/${tag}/prealign_tel_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
    ../../corry/plot_analog_ce65v2.py -f output/${chip}/${tag}/prealign_tel_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.root --noisy-freq 0.95
    i=$((i+1))
done 
../../corry/plot_analog_ce65v2.py -f output/${chip}/${tag}/prealign_tel_${testbeam_alphabetic}-${chip}_HV${HV}_iter${niter_prealign_tel}.root --noisy-freq 0.95


#################
# Alignment-tel #
#################

echo -e "\n\n\n\033[1;95m#########################################################################\033[0m"
# echo -e "\033[1;95m# execution : corry -c ament_tests/config/${chip}/${tag}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf #\033[0m"
echo -e "\033[1;95m# execution : corry -c config/${chip}/${tag}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf #\033[0m"
echo -e "\033[1;95m#########################################################################\033[0m\n\n\n"
i=1
#config/${chip}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf



if [ "${spatial_cut_iterations}" == "True" ]; then
    niter_align_tel=${#spatial_cuts[@]}
fi
## it starts from 1. Thus every config file should be subscripted? else we will have too many else conditions...
while [ $i -le ${niter_align_tel} ]; do 
    # cp ament_tests/config/${chip}/${tag}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf ament_tests/config/${chip}/${tag}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
    cp config/${chip}/${tag}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}.conf config/${chip}/${tag}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
    # sed -i "s/detectors_file_updated = \(.*\)\.conf/detectors_file_updated = \1_iter${i}.conf/g" ament_tests/config/${chip}/${tag}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
    sed -i "s/detectors_file_updated = \(.*\)\.conf/detectors_file_updated = \1_iter${i}.conf/g" config/${chip}/${tag}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
    # sed -i "s/histogram_file\(.*\)\.root/histogram_file\1_iter${i}.root/g" ament_tests/config/${chip}/${tag}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
    sed -i "s/histogram_file\(.*\)\.root/histogram_file\1_iter${i}.root/g" config/${chip}/${tag}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
    # Iteratively decrease spatial_cut if spatial_cut_iterations variable set to true
    if [ "${spatial_cut_iterations}" == "True" ]; then
        sed -i "s/spatial_cut_abs=.*/spatial_cut_abs=${spatial_cuts[$((i-1))]}um,${spatial_cuts[$((i-1))]}um/g" config/${chip}/${tag}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
    fi
    if [ ${i} -gt 1 ]; then 
        # sed -i "s/detectors_file \(.*\)\_prealigned_tel.conf/detectors_file \1_aligned_tel_iter$((i-1)).conf/g" ament_tests/config/${chip}/${tag}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
        sed -i "s/detectors_file \(.*\)\_prealigned_tel.conf/detectors_file \1_aligned_tel_iter$((i-1)).conf/g" config/${chip}/${tag}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
    else 
        # sed -i "s/detectors_file \(.*\)\.conf/detectors_file \1_iter${niter_prealign_tel}.conf/g" ament_tests/config/${chip}/${tag}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
        sed -i "s/detectors_file \(.*\)\.conf/detectors_file \1_iter${niter_prealign_tel}.conf/g" config/${chip}/${tag}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
    fi
    # corry -c config/${chip}/${tag}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
    ../../corry/plot_analog_ce65v2.py -f output/${chip}/${tag}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.root --noisy-freq 0.95
    i=$((i+1))
done 
# ../corry/plot_analog_ce65v2.py -f ament_tests/output/${chip}/${tag}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}_iter${niter_align_tel}.root --noisy-freq 0.95
../../corry/plot_analog_ce65v2.py -f output/${chip}/${tag}/align_tel_${testbeam_alphabetic}-${chip}_HV${HV}_iter${niter_align_tel}.root --noisy-freq 0.95


####################
# Prealignment-dut #
####################

echo -e "\n\n\n\033[1;95m############################################################################\033[0m"
echo -e "\033[1;95m# execution : corry -c config/${chip}/${tag}/prealign_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf #\033[0m"
echo -e "\033[1;95m############################################################################\033[0m\n\n\n"
i=1
while [ $i -le ${niter_prealign_dut} ]; do 
    cp config/${chip}/${tag}/prealign_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf config/${chip}/${tag}/prealign_dut_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
    sed -i "s/detectors_file_updated = \(.*\)\.conf/detectors_file_updated = \1_iter${i}.conf/g" config/${chip}/${tag}/prealign_dut_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
    sed -i "s/histogram_file\(.*\)\.root/histogram_file\1_iter${i}.root/g" config/${chip}/${tag}/prealign_dut_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
    if [ ${i} -gt 1 ]; then 
        sed -i "s/detectors_file \(.*\)\_aligned_tel.conf/detectors_file \1_prealigned_dut_iter$((i-1)).conf/g" config/${chip}/${tag}/prealign_dut_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
    else 
        sed -i "s/detectors_file \(.*\)\.conf/detectors_file \1_iter${niter_align_tel}.conf/g" config/${chip}/${tag}/prealign_dut_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
    fi
    # corry -c config/${chip}/${tag}/prealign_dut_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
    i=$((i+1))
done 

../../corry/plot_analog_ce65v2.py -f output/${chip}/${tag}/prealign_dut_${testbeam_alphabetic}-${chip}_HV${HV}_iter${niter_prealign_dut}.root --noisy-freq 0.95

#################
# Alignment-dut #
#################

echo -e "\n\n\n\033[1;95m#########################################################################\033[0m"
echo -e "\033[1;95m# execution : corry -c config/${chip}/${tag}/align_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf #\033[0m"
echo -e "\033[1;95m#########################################################################\033[0m\n\n\n"
i=1
while [ $i -le ${niter_align_dut} ]; do 
    cp config/${chip}/${tag}/align_dut_${testbeam_alphabetic}-${chip}_HV${HV}.conf config/${chip}/${tag}/align_dut_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
    sed -i "s/detectors_file_updated = \(.*\)\.conf/detectors_file_updated = \1_iter${i}.conf/g" config/${chip}/${tag}/align_dut_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
    sed -i "s/histogram_file\(.*\)\.root/histogram_file\1_iter${i}.root/g" config/${chip}/${tag}/align_dut_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
    if [ ${i} -gt 1 ]; then 
        sed -i "s/detectors_file \(.*\)\_prealigned_dut.conf/detectors_file \1_aligned_dut_iter$((i-1)).conf/g" config/${chip}/${tag}/align_dut_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
    else 
        sed -i "s/detectors_file \(.*\)\.conf/detectors_file \1_iter${niter_prealign_dut}.conf/g" config/${chip}/${tag}/align_dut_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
    fi
    # corry -c config/${chip}/${tag}/align_dut_${testbeam_alphabetic}-${chip}_HV${HV}_iter${i}.conf
    i=$((i+1))
done 

../../corry/plot_analog_ce65v2.py -f output/${chip}/${tag}/align_dut_${testbeam_alphabetic}-${chip}_HV${HV}_iter${niter_align_dut}.root --noisy-freq 0.95

############
# Analysis #
############
echo -e "\n\n\n\033[1;95m############################################################\033[0m"
echo -e "\033[1;95m# corry -c config/${chip}/${tag}/analysis_${testbeam_alphabetic}-${chip}_HV${HV}.conf #\033[0m"
echo -e "\033[1;95m############################################################\033[0m\n\n\n"


## Below is only necessary since I implemented the niters hackily...
sed -i "s/detectors_file \(.*\)\.conf/detectors_file \1_iter${niter_align_dut}.conf/g" config/${chip}/${tag}/analysis_${testbeam_alphabetic}-${chip}_HV${HV}.conf
sed -i "s/detectors_file_updated = \(.*\)_aligned_dut_analysed.conf/detectors_file_updated = \1_aligned_dut_iter${niter_align_dut}_analysed.conf/g" config/${chip}/${tag}/analysis_${testbeam_alphabetic}-${chip}_HV${HV}.conf
nx_prime=$((nx-1))
ny_prime=$((ny-1))
sed -i '/type = "ce65v2"/a\
roi = [[0,0],[0,'"$ny_prime"'],['"$nx_prime"','"$ny_prime"'],['"$nx_prime"',0]]' geometry/${chip}/${tag}/${testbeam_alphabetic}-${chip}_HV${HV}_aligned_dut_iter${niter_align_dut}.conf

corry -c config/${chip}/${tag}/analysis_${testbeam_alphabetic}-${chip}_HV${HV}.conf
../../corry/plot_analog_ce65v2.py -f output/${chip}/${tag}/analysis_${testbeam_alphabetic}-${chip}_${run_number_beam}_seedthr${seedthr_analysis}_nbh${nbh_analysis}_snr${snr_seed_analysis}_${method_analysis}.root


echo -e "\n\n\n\033[1;95m-FINISHED EXECUTION-\033[0m\n\n\n"


date










