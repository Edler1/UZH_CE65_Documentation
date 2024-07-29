#!/bin/bash

set -e

chips=("GAP225SQ" "GAP15SQ" "STD225SQ" "STD15SQ")

for chip in ${chips[@]}; do
    python3 extract_eff_res.py ${chip}
done
