# UZH CE65 Documentation

## Table of Contents
- [Lab Measurements](#heading-1)
  - [Hardware Setup](#subheading-2-1)
  - [Data Acquisition](#subheading-2-2)
  - [Analysis](#subheading-2-2)
- [Post-analysis and Fitting Spectra](#heading-2)
- [Testbeam Analysis](#heading-3)
- [Miscellaneous](#heading-4)

## Lab Measurements
### Hardware Setup
![Alt text](images/setup.jpg)

The test setup consists of fundamentally three parts: the FPGA, the proxy board, and the carrier board (which houses the CE65 chip itself), as depicted in Figure INSERT REF. The FPGA board (name this properly...) must be connected via a USB interface to the computer which will act the bus for data transfer. The FPGA board is powered by the large green connector adjacent to the FPGA which is connected to the power supply. The FPGA board also houses the connectors to the SUB and PWELL, which are typically grounded. The HV_RESET connector is situated on the proxy board and provides the bias for the collection node (though only for the AC-coupled submatrix). Finally the carrier board sits beneath the Fe-55 source and should be handled with care. 
A summary of typical parameters for the different connectors is:

 - FPGA power = 5V
  - Current compliance = 1.2 A
 - SUB = PWELL = 0V
  - Current compliance = 4.0 mA
 - HV_RESET = 10V 
  - Current compliance = 1.0 mA
 
It is important that the polarity of the HV_RESET, SUB, PWELL connections is not reversed (though irrelevant for SUB/PWELL when at 0V). 

When choosing a CE65 chip (V1 or V2) for which data is to be taken it is helpful to follow the following SOP: 

 - If not already done, power off everything which can be done by simply stopping output from the power supply. 
 - Wearing gloves, slightly unscrew the tallest screw (not completely, only until you can slide the metal sheet underneath) on the Fe55 source holder. Slide the separating sheet in and screw in the tall screw until it is secure. The source is now blocked. 
 - Carefully (but sometimes some force is required) slide the source away from the base of the aluminum setup holder. This should expose the carrier board and the CE65 chip. Unscrew the white screws securing the carrier board and store the chip in one of the plastic chip boxes. Always be careful when handling carrier boards, and the wire bonds on the chip are very fragile and any contact is likely to destroy them. After this is done select the chip that is to be tested and plug it into the proxy board, before re-screwing the white plastic screws (do not tighten them much, as they will break).  
 - Slide the source holder back over the setup holder. Remember to unlock the Fe55 source which you can do by again unscrewing the tallest screw on the source holder and sliding the metal sheet out, until the second screw hole can be felt, and screwing the screw back in. Afterwards place the black plastic box over the source, where is should be slightly touching the proxy board and the metal sheet of the source holder. Finally, place the black cloth over the black box such that no light could be reflected into the CE65 chip. 
 - The setup is now ready for data taking, which is described in the next section. 

#### Data Acquisition

Due to the ephemeral nature of FPGA programming, the firmware must be reloaded every time the FPGA board is power cycled. The can be done using the `program_fpga` command. Each firmware is specific to a CE65 version. By default the V2 firmware will be loaded. The source code is available here `link_this?`.

Prior to programming the FPGA, verify that the voltage in Channel 1 (the one powering the board) hovers at around `~250 mV`. After the programming is complete, the voltage should increase to `~400 mV`.

The data acquisition code is located in `~/CE65/ce65_daq_v2`. It functions via a GUI that can be started by running `./ce65_daq` from within the relevant directory. The GUI is straightforward to use, but there are some caveats
 - When specifying a file name, it is important to hit `Enter/Return` after one is done, else the changes will not take effect. We have been using the convention `testTree_CHIPNAME_PWELL_HV_TEMP_DATE`. For instance, for the STD225SQ chip at an HV_RESET = 8V, PWELL = 0V, at chiller setting of 20C, taken on the 19/12/2023, this would be `testTree_STD225SQ_0V_8V_20C_19122023`. It is important to follow the naming convention for compatibility and book-keeping, though the ordering of the fields does not matter. 
 - Next select the correct `Proxy board id` from the drop down menu: ours is `CE65-006`. The `Chip variant` depends on the CE65 chip being tested and should be matched to the correct variant. For now only the V1 options are implemented, and for all V2 chips `D` should be selected.
 - Hit `Configure`. The voltage on Channel 1 should increase from `~400 mV` to `~650 mV`. The chip is now powered on. 
 - Hit `Start` to begin data taking. The data will be saved as a `.root` file in the directory specified as `DEFAULT_OUTPUT_DATA_PATH` in `~/CE65/ce65_daq_v2/src/globals.h`. By default this is `~/CE65/ce65_daq_v2/data/`.  
 - Once enough data is acquired (this typically ranges from 30 mins - 10 hours depending on purpose), hit `Stop`. A message in white text detailing the runtime should appear on command line. After this simply exit out of the GUI. 

#### Analysis

The output `.root` file consists of unstructured `ce65_frame`s, the details of which can be found in `~/CE65/ce65_daq_v2/src/*`. In order to analyse the spectra it is necessary to extract the signal, perform clusterization, and histogram the data. This is done in the analysis step, which is implemented within the `~/CE65/ce65_daq_v2/analysis/` folder. The basic syntax for beginning an analysis on some file `~/CE65/ce65_daq_v2/data/testTree_STD225SQ_0V_8V_20C_19122023.root` is `./run_basic_analysis ../data/testTree_STD225SQ_0V_8V_20C_19122023 900 300`, where 900 and 300 represent the seed threshold and the neighbour threshold, respectively. 
The output of the analysis step will be a file `~/CE65/ce65_daq_v2/data/testTree_STD225SQ_0V_8V_20C_19122023_wave.root` that contains relevant histograms, and can/should be inspected in TBrowser. 

### Post-analysis and Fitting Spectra

After obtaining the histograms from the Fe-55 source scan in the `*_wave.root` file, the natural next step is to fit the spectra for the given run. Plotting scripts can be found in the `~/CE65/ce65_daq_v2/analysis/plotting_scripts/` folder. The most important of these is `histo_1d_root_dev.py`. The syntax of this script is `python3 histo_1d_root_dev.py ../../data/testTree_STD225SQ_0V_8V_20C_19122023_wave.root h_mxAmpAC_quick_spectra`. Note that the file name may of course be changed to whatever location the file has. Likewise the histogram name `h_mxAmpAC_quick_spectra` may also be changed to any histogram appearing in the `*_wave.root` file, though the parameters for the plotting/fitting should be defined in the revelant file `~/CE65/ce65_daq_v2/analysis/plotting_scripts/plotting_params_CHIPNAME.py`.

The output of `histo_1d_root_dev.py` is a .pdf file in a directory `~/CE65/ce65_daq_v2/analysis/plotting_scripts/CHIPNAME`.







#### Thresholds
#### Chiller and Temperature Control
#### Automation
#### Docker
#### ?
#### Compilation (or should this already appear before?)
#### Data Storage? HD + Cluster

#### Could also explain somewhat what the output histograms of the analysis step are. That is somewhat non-trivial. 
#### Could also explain somewhere what the data actually is and what precisely we mean by "signal". Need these things for thesis anyway. Could maybe make a "details" folder.
