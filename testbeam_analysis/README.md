## Testbeam Analysis

The analysis can be run using the scripts in [`https://github.com/Edler1/UZH_CE65_Documentation/tree/main/testbeam_analysis`](https://github.com/Edler1/UZH_CE65_Documentation/tree/main/testbeam_analysis)

The scripts in the `testbeam_analysis` directory rely on an [`ITS3utils`](https://github.com/ajitkmaurya/ITS3utils/tree/main) directory that should exist as a subdirectory of where the code is being run. 
To initilize the submodule after having cloned the `UZH_CE65_Documentation` repo, simply run
```
git submodule update --init
```

To set up for the analysis, put the data files into `ITS3utils/SPS202404/data/<CHIPNAME>`. The files can be manually scp'd or copied using 
```
./copy_tb_files.sh 
```
where the user will be prompted for a username and a password to copy the files. The chips for which data should be copied can be specified by uncommenting the relevant lines in `copy_tb_files.sh`. e.g. for pcb18 this would be 
```
# chips["pcb18"]="STD225SQ" -> chips["pcb18"]="STD225SQ"
```

The analysis must be run within a docker container. First, start the docker container using [run_container.sh](https://github.com/Edler1/UZH_CE65_Documentation/blob/main/testbeam_analysis/run_container.sh):
```
./run_container.sh
```
The working directory is defined as wherever the script is run from. The only important thing is that `ITS3utils` be a visible subdirectory of the working directory. 


The analysis is run by calling
```
./run_tb_analysis.sh
```
The parameters of the analysis are defined in the beginning of the script.

Alternatively, paramters can be provided as a command line option via a .txt file. There are several examples in the [`https://github.com/Edler1/UZH_CE65_Documentation/blob/main/testbeam_analysis/params`](https://github.com/Edler1/UZH_CE65_Documentation/blob/main/testbeam_analysis/params) directories:
```
./run_tb_analysis.sh params/SPS202404/GAP225SQ/GAP225SQ.txt
```

### Scanning thresholds

To scan a suitable range of _e-_ thresholds (e.g. ["70", "90", "110", "130", "170", "210", "250", "290", "330", "370"]), the `params/SPS202404/GAP225SQ.txt` must be edited such that the seed and neighbour thresholds are given in _ADCu_

```
seedthr_analysis="429"
nbh_analysis="429"
```
for each corresponding _e-_ threshold value. 

In addition, the _cluster_ method is generally preferred when scanning thresholds, so the clusterisation method should be changed to
```
method_analysis="cluster"
```

At the moment the threshold scans are done in _e-_.


This can be done using the `scan_thresholds.sh` script if the `run_tb_analysis.sh` is being used for analysis, otherwise a similar script should be written for the corresponding analysis command (e.g. `corry -c some_config_file.conf`)

```
./scan_thresholds.sh 
```


<sub> _It is necessary to run the `run_tb_analysis.sh -a` with the `-a` option to prevent noisemap creation and (pre)alignment loops at the end of `run_tb_analysis.sh` as the telescope+chip should __not__ be realigned for every threshold._ </sub>


After each threshold value has been scanned there should be analysis output files in the `ITS3utils/SPS202404/output/GAP225SQ/` folder. These will be of the form `analysis_SPS-GAP225SQ_173004514_240424004519_seedthr400_nbh400_snr3_cluster.root` for each threshold value.

In order to extract the resolution and efficiency, the `hacky_edits.sh` script should be run in order to edit the `ITS3utils/corry/plot_*.py` plotting scripts such that these values are printed
```
./hacky_edits.sh
```

The `extract_eff_res.py` script extracts the resolution and efficiencies along with their errors to `.txt` files, where the following parameters should be set
```
66 working_dir = "/local/ITS3utils"
67 chip = "GAP225SQ"
...
72 seed_thresholds = ["70", "90", "110", "130", "170", "210", "250", "290", "330", "370"]   # in e-
...
76 factor=0.23287
```
as appropriate for the given analysis. The script is run as
```
python3 extract_eff_res.py
```

**To plot the efficiencies and resolutions the scripts provided in the `plotting_scripts` folder can be used.**

<sub>Throughout these examples _GAP225SQ_ was used, but the same holds for other chips. To extract efficiences and resolutions for all chips simply use `meta_extract.sh`.</sub>



