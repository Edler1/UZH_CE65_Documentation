#/bin/bash
set -e


testbeam="DESY202311"

# Idea here is copy the .raw files to the correct dir for bookkeeping and just to have them around. 

# Start by listing the target files in low letters since that is the convention
# We create an associate array for the pcb numbs
declare -A chips
chips["pcb08"]="GAP225SQ"
#chips["pcb02"]="GAP18SQ"
chips["pcb19"]="GAP15SQ"
#chips["pcb05"]="GAP225HSQ"
#chips["pcb03"]="GAP18HSQ"
chips["pcb18"]="STD225SQ"
#chips["pcb23"]="STD18SQ"
chips["pcb06"]="STD15SQ"
#chips["pcb07"]="GAP225SQ"

# We then create a list for the hv's that we want to copy
#hvs=( "0" "2" "4" "10" "15" )
hvs=( "10" )


## We then check for the ITS3utils dir
its3_utils_path=`find . -type d -name "ITS3utils"`
if [ -n "$its3_utils_path" ]; then
    its3_utils_path=`realpath $its3_utils_path`
else 
    echo "Cannot find dir \"ITS3utils\". Please make sure it is visible from within \"`pwd`\"."
    exit
fi

echo "${its3_utils_path}"


# We then craft the command and loop to copy the files over
_chips=("${!chips[@]}")
for chip in ${_chips[@]}; do
    echo Starting copying of ${chips["${chip}"]}
    for hv in ${hvs[@]}; do
        
        if [ ! -d ${its3_utils_path}/${testbeam}/data/${chips["${chip}"]} ]; then 
            mkdir ${its3_utils_path}/${testbeam}/data/${chips["${chip}"]}
        fi
        sshpass -p "$2" rsync -P --ignore-existing $1@lxplus.cern.ch:/eos/project/a/aliceits3/ITS3-WP3/Testbeams/2023-11_DESY/beam/ce65v2_${chip}_hv${hv}_beam_run* ${its3_utils_path}/${testbeam}/data/${chips["${chip}"]}/ 
        sshpass -p "$2" rsync -P --ignore-existing $1@lxplus.cern.ch:/eos/project/a/aliceits3/ITS3-WP3/Testbeams/2023-11_DESY/noise/ce65v2_${chip}_hv${hv}_noise_run* ${its3_utils_path}/${testbeam}/data/${chips["${chip}"]}/
    done
done



