#!/bin/bash

# We start by checking the container is actually on the fs
script_dir=`pwd`
url="https://cernbox.cern.ch/remote.php/dav/public-files/Kkku8XhpyUdASaE/ce65v2_desy_2023-11-latest.sif"
if [ -d ${script_dir}/container ]; then
    if [ -f ${script_dir}/container/ce65v2_desy_2023-11-latest.sif ]; then
        :
    else 
        cd ${script_dir}/container
        wget ${url}
    fi
else 
    echo "Cannot find container in pwd. Please confirm it is the first time running the container (y/n):"
    read answer
    if [ ${answer} != "y" ]; then
        echo "Please run the script from the parent directory of the \"container\" folder."
        exit 1
    fi
    mkdir ${script_dir}/container
    cd ${script_dir}/container
    wget ${url}
fi
cd ${script_dir}



# These are the default installations inside the container
EUDAQINSTALL="/opt/eudaq2"
CORRYINSTALL="/opt/corryvreckan"

# Set the two variables below to the location of the custom eudaq2 and corry installs
# Should be visible from within the directory the container is run
# These should be installed from ~within~ the container
LOCALEUDAQ="/local/template/eudaq2"
LOCALCORRY="/local/template/corryvreckan"

if [ "$LOCALEUDAQ" != "/local/template/eudaq2" ]; then
    EUDAQINSTALL="$LOCALEUDAQ"
fi
if [ "$LOCALCORRY" != "/local/template/corryvreckan" ]; then
    CORRYINSTALL="$LOCALCORRY"
fi


singularity exec --bind `pwd` container/ce65v2_desy_2023-11-latest.sif /bin/bash -c "
       export PATH=${EUDAQINSTALL}/bin:\$PATH &&
       export PATH=${CORRYINSTALL}/bin:\$PATH &&
       export PYTHONPATH=${EUDAQINSTALL}/lib:\$PYTHONPATH &&
       export EUDAQ2PATH=${EUDAQINSTALL}:\$EUDAQ2PATH &&
       export CORRYPATH=${CORRYINSTALL}:\$CORRYPATH &&
       echo ::TB Env has been set:: &&
       exec bash"


