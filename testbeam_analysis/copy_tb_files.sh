#/bin/bash
set -e


testbeam="SPS202404"

if [ "$testbeam" != "SPS202404" ]; then #-o [ "$testbeam" != "DESY202311" ]; then
    echo -e "\e[1;31mTestbeam -> \"${testbeam}\" not recognized\e[0m"
    exit
fi


# Idea here is copy the .raw files to the correct dir for bookkeeping and just to have them around. 

# Start by listing the target files in low letters since that is the convention
# We create an associate array for the pcb numbs
# uncomment all chips whose data you wish to have:
declare -A chips
# chips["pcb08"]="GAP225SQ"
# chips["pcb02"]="GAP18SQ"
# chips["pcb19"]="GAP15SQ"
# chips["pcb05"]="GAP225HSQ"
# chips["pcb03"]="GAP18HSQ"
# chips["pcb18"]="STD225SQ"
# chips["pcb23"]="STD18SQ"
# chips["pcb06"]="STD15SQ"
chips["pcb07"]="GAP225SQ"

# We then create a list for the hv's that we want to copy
#hvs=( "0" "2" "4" "10" "15" )
hvs=( "10" "4" )


## We then check for the ITS3utils dir
its3_utils_path=`find . -type d -name "ITS3utils"`
if [ -n "$its3_utils_path" ]; then
    its3_utils_path=`realpath $its3_utils_path`
else 
    echo "Cannot find dir \"ITS3utils\". Please make sure it is visible from within \"`pwd`\"."
    exit
fi

echo "${its3_utils_path}"

## Here we take user input for the username and password of the relevant acc..
echo "Please enter username (e.g. username@lxplus.cern.ch):"
echo "(For SPS202404 this will default to \"alice\")"
read username
echo "Please enter password:"
read password



# We then craft the command and loop to copy the files over
_chips=("${!chips[@]}")
for chip in ${_chips[@]}; do
    echo Starting copying of ${chips["${chip}"]}
    for hv in ${hvs[@]}; do
        
        if [ ! -d ${its3_utils_path}/${testbeam}/data/${chips["${chip}"]} ]; then 
            mkdir ${its3_utils_path}/${testbeam}/data/${chips["${chip}"]}
        fi
        if [ "${testbeam}" = "DESY202311" ]; then
            sshpass -p "${password}" rsync -P --ignore-existing ${username}@lxplus.cern.ch:/eos/project/a/aliceits3/ITS3-WP3/Testbeams/2023-11_DESY/beam/ce65v2_${chip}_hv${hv}_beam_run* ${its3_utils_path}/${testbeam}/data/${chips["${chip}"]}/ 
            sshpass -p "${password}" rsync -P --ignore-existing ${username}@lxplus.cern.ch:/eos/project/a/aliceits3/ITS3-WP3/Testbeams/2023-11_DESY/noise/ce65v2_${chip}_hv${hv}_noise_run* ${its3_utils_path}/${testbeam}/data/${chips["${chip}"]}/
        elif [ "${testbeam}" = "SPS202404" ]; then
            username="alice"
            sshpass -p "${password}" rsync -P --ignore-existing ${username}@sbgat497.cern.ch:/run/media/alice/Beamtest/SPS_2024_04/ce65v2_${chip}_hv${hv}_beam_run* ${its3_utils_path}/${testbeam}/data/${chips["${chip}"]}/ 
            sshpass -p "${password}" rsync -P --ignore-existing ${username}@sbgat497.cern.ch:/run/media/alice/Beamtest/SPS_2024_04/ce65v2_${chip}_hv${hv}_noise_run* ${its3_utils_path}/${testbeam}/data/${chips["${chip}"]}/ 
        fi
    done
done



