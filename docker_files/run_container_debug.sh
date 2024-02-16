#!/bin/bash


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


docker run --rm -it \
       -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix -e XAUTHORITY=$XAUTHORITY -v $XAUTHORITY:$XAUTHORITY \
       --mount type=bind,source="$(pwd)"/,target=/local \
       edler1/ce65v2_desy_2023-11:v1.1 \
       /bin/bash -c "
       export PATH=${EUDAQINSTALL}/bin:\$PATH &&
       export PATH=${CORRYINSTALL}/bin:\$PATH &&
       export PYTHONPATH=${EUDAQINSTALL}/lib:\$PYTHONPATH &&
       export EUDAQ2PATH=${EUDAQINSTALL}:\$EUDAQ2PATH &&
       export CORRYPATH=${CORRYINSTALL}:\$CORRYPATH &&
       #echo ::TB Env has been set:: &&
       echo ::TB \& LabTest Env has been set:: &&
       exec bash"

### For running the ce65_daq code remember to have "apts-dpts-ce65-daq-software" in same dir and compile C code. 
### CE65 DAQ code can then be copied over and compiled normally in container...

