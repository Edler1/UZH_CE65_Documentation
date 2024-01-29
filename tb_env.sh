#!/bin/bash
set -e


### Set path for eudaq2 and corry
export PATH=/opt/eudaq2/bin:$PATH
export PATH=/opt/corryvreckan/bin:$PATH
export PYTHONPATH=/opt/eudaq2/lib:$PYTHONPATH
export EUDAQ2PATH=/opt/eudaq2:$EUDAQ2PATH
export CORRYPATH=/opt/corryvreckan:$CORRYPATH
echo "::TB Env has been set::"
