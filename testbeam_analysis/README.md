The analysis can be run using the scripts in [`https://github.com/Edler1/UZH_CE65_Documentation/tree/main/testbeam_analysis`](https://github.com/Edler1/UZH_CE65_Documentation/tree/main/testbeam_analysis)

The scripts in the `testbeam_analysis` directory rely on an [`ITS3utils`](https://github.com/ajitkmaurya/ITS3utils/tree/main) directory that should exist as a subdirectory of where the code is being run. 

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
./run_tb_analysis.sh params/GAP225SQ_SPS.txt
```
