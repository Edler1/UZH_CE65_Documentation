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

#### Approval Plots

The approval plots include the noise, seed/cluster charge, cluster shape, and finally the x/y tracking residuals. These are all plotted using the `plot_preliminary` function of `approval_plots_preliminary_v2.py`. The output is in .pdf and .root format. The candidate runs for plotting should be passed to the `database` dict as:
```
40       'noise':'output/SPS-GAP225SQ_HV10-noisemap.root',
...
45         'file':'output/analysis_SPS-GAP225SQ_173004514_240424004519_seedthr400_nbh100_snr3_window.root',
```
for each of the chips. The parent classes are defined as `'variant': ['GAP225SQ', 'STD225SQ']`, each of which contains subclasses corresponding to each different chip pitch `'pitches': ['225', '15']`.

The script is simply run as 
```
python3 approval_plots_preliminary_v2.py
```



