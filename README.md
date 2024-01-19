# UZH CE65 Documentation

## Table of Contents
- [Lab Measurements](#heading-1)
  - [Hardware Setup](#subheading-2-1)
  - [Data Acquisition](#subheading-2-2)
  - [Analysis](#subheading-2-2)
- [Post-analysis and Fitting Spectra](#heading-2)
- [Testbeam Analysis](#heading-3)

## Lab Measurements
### Hardware Setup
![Alt text](images/setup.jpg)

The test setup consists of fundamentally three parts: the FPGA, the proxy board, and the carrier board (which houses the CE65 chip itself), as depicted in Figure INSERT REF. The FPGA board (name this properly...) must be connected via a USB interface to the computer which will act the bus for data transfer. The FPGA board is powered by the large green connector adjacent to the FPGA which is connected to the power supply. The FPGA board also houses the connectors to the SUB and PWELL, which are typically grounded. The HV_RESET connector is situated on the proxy board and provides the bias for the collection node (though only for the AC-coupled submatrix). Finally the carrier board sits beneath the Fe-55 source and should be handled with care. 
A summary of typical parameters for the different connectors is:

 - FPGA power = 5V
 - SUB = PWELL = 0V
 - HV_RESET = 10V 
 
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

The data acquisition code is located in `~/CE65/ce65_daq`. It functions via a GUI that can be started by running `./ce65_daq` from within the relevant directory. The GUI is straightforward to use, but there are some caveats
 - When specifying a file name, it is important to hit `Enter/Return` after one is done, else the changes will not take effect. We have been using the convention `testTree_CHIPNAME_PWELL_HV_TEMP_DATE`. For instance, for the STD225SQ chip at an HV_RESET = 8V, PWELL = 0V, at chiller setting of 20C, taken on the 19/12/2023, this would be `testTree_STD225SQ_0V_8V_20C_19122023`. It is important to follow the naming convention for compatibility and book-keeping, though the ordering of the fields does not matter. 
