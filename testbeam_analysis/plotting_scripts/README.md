### Plotting scripts

In this folder are plotting scripts related to testbeam analyses. 

#### Plotting Efficiency and Resolution as a function of threshold

To plot the effciency for a given process (GAP, STD, BLK) for different pitches (22.5um, 18um, 15um) the `efficiency_by_threshold.py` script can be used. The directory containing the `.txt` files produced by `extract_eff_res.py` should be specified as `filepath`, along with the setting of the correct parameters in the `Parameters` section. The script is run as
```
python3 efficiency_by_threshold.py
```
Analogously, the resolution can be plotted for a given process as 
```
python3 resolution_by_threshold.py
```

