import matplotlib.pyplot as plt
import numpy as np
import json
import datetime
from plot_util_mpl import draw_chip, draw_configuration, draw_preliminary
import argparse

def parseInput():

    parser = argparse.ArgumentParser(description="Arg parser for Efficiency/Resolution plotting script.")

    # parser.add_argument('filename', type=str, help='The file to process')


    parser.add_argument('-a', '--approval', action='store_true', help="Set approval flag (True or False)")

    args = parser.parse_args()
    return args


# Philosophy -> Plotting script for efficiency vs threshold. Takes .txt files with column-wise "threshold" "efficiency" "uncertainty" information. Meant to be run for a variety of pitches(15um, 18um, 22.5um) for a given process (GAP, STD, BLK).


##############
# Parameters #
##############

# Testbeam to be plotted (SPS, DESY)
testbeam = "SPS"

# Process to be plotted (GAP, STD, BLK)
process = "GAP"

# Matrix arrangement (SQ, HSQ)
matrix_arrangement = "SQ"

# HV applied
hv = "10"

# Parsing input for approval flag
pass
# If approval option is set then .json files (CHIP_PCB_VSUB_HV_TEMP_date.json) must be specified
json_files = {"GAP15SQ" : "data/GAP15SQ_PCB19_0V_10V_15122023.json",
        "GAP225SQ" : "data/GAP225SQ_PCB10_0V_10V_16112023.json", 
        "STD15SQ" : "data/STD15SQ_PCB06_0V_10V_21112023.json",
        "STD225SQ" : "data/STD225SQ_PCB18_0V_10V_13122023.json"}

# .txt directory filepath (empty by default as .txt files are assumed to be in pwd)
filepath = "data"
filepath = filepath if (filepath.endswith("/") or not bool(filepath)) else filepath+"/"

# Load the Okabe Ito color palette from JSON
with open("okabe_ito.json") as jf:
    colors_dict = json.load(jf)
colors = list(colors_dict.values())
colors_names = list(colors_dict.keys())

# Apply wp3 style
plt.style.use('wp3.mplstyle')

# Define label dict
label_dict = {"GAP" : "Mod. w/ Gap", "STD" : "Standard", "BLK" : "Modified"}


# Create subplots
# fig, (plt, ax2) = plt.subplots(1, 2, figsize=(12, 6))
# fig, ax1 = plt.subplots(figsize=(12, 8))
# fig, ax1 = plt.subplots(figsize=(13, 6))
fig, ax1 = plt.subplots(figsize=(14, 6))
# fig = plt.figure(figsize=(6, 6))
# fig = plt.figure()
# ax1 = plt.subplot(111)

# Declaring dicts for data
chip_225um_charge_in_es = []
chip_225um_effs = []
chip_225um_err_effs = []

chip_18um_charge_in_es = []
chip_18um_effs = []
chip_18um_err_effs = []

chip_15um_charge_in_es = []
chip_15um_effs = []
chip_15um_err_effs = []


f4 = open(f'{filepath}{testbeam}_{process}225{matrix_arrangement}_HV{hv}_adc_eff_err.txt', 'r')  # We need to re-open the file
for line in f4:
    line = line.strip()
    columns = line.split()
    chip_225um_adc_value = float(columns[0])
    chip_225um_charge_in_e_value = chip_225um_adc_value
    chip_225um_eff_value = float(columns[1]) # * 100.0
    chip_225um_err_eff_value = float(columns[2]) # * 100.0
    chip_225um_charge_in_es.append(chip_225um_charge_in_e_value)
    chip_225um_effs.append(chip_225um_eff_value)
    chip_225um_err_effs.append(chip_225um_err_eff_value)
f4.close()

# f5 = open(f'{filepath}{testbeam}_{process}18{matrix_arrangement}_HV{hv}_adc_eff_err.txt', 'r')  # We need to re-open the file
# for line in f5:
#     line = line.strip()
#     columns = line.split()
#     # print(columns)
#     chip_18um_adc_value = float(columns[0])
#     chip_18um_charge_in_e_value = chip_18um_adc_value
#     chip_18um_eff_value = float(columns[1]) # * 100.0
#     chip_18um_err_eff_value = float(columns[2]) # * 100.0
#     chip_18um_charge_in_es.append(chip_18um_charge_in_e_value)
#     chip_18um_effs.append(chip_18um_eff_value)
#     chip_18um_err_effs.append(chip_18um_err_eff_value)
# f5.close()

f6 = open(f'{filepath}{testbeam}_{process}15{matrix_arrangement}_HV{hv}_adc_eff_err.txt', 'r')  # We need to re-open the file
for line in f6:
    line = line.strip()
    columns = line.split()
    # print(columns)
    chip_15um_adc_value = float(columns[0])
    chip_15um_charge_in_e_value = chip_15um_adc_value
    chip_15um_eff_value = float(columns[1]) # * 100.0
    chip_15um_err_eff_value = float(columns[2]) # * 100.0
    chip_15um_charge_in_es.append(chip_15um_charge_in_e_value)
    chip_15um_effs.append(chip_15um_eff_value)
    chip_15um_err_effs.append(chip_15um_err_eff_value)
f6.close()


# ### Constrain values range for noise + too high threshold e-
upper_e_bound = 410

chip_225um_effs = np.array(chip_225um_effs).astype(float)
chip_225um_err_effs = np.array(chip_225um_err_effs).astype(float)
chip_225um_charge_in_es = np.array(chip_225um_charge_in_es).astype(float)
chip_225um_effs = chip_225um_effs[(chip_225um_charge_in_es>50)&(chip_225um_charge_in_es<400)]
chip_225um_err_effs = chip_225um_err_effs[(chip_225um_charge_in_es>50)&(chip_225um_charge_in_es<400)]
chip_225um_charge_in_es = chip_225um_charge_in_es[(chip_225um_charge_in_es>50)&(chip_225um_charge_in_es<400)]

# chip_18um_effs = np.array(chip_18um_effs).astype(float)
# chip_18um_err_effs = np.array(chip_18um_err_effs).astype(float)
# chip_18um_charge_in_es = np.array(chip_18um_charge_in_es).astype(float)
# chip_18um_effs = chip_18um_effs[(chip_18um_charge_in_es>50)&(chip_18um_charge_in_es<400)]
# chip_18um_err_effs = chip_18um_err_effs[(chip_18um_charge_in_es>50)&(chip_18um_charge_in_es<400)]
# chip_18um_charge_in_es = chip_18um_charge_in_es[(chip_18um_charge_in_es>50)&(chip_18um_charge_in_es<400)]

chip_15um_effs = np.array(chip_15um_effs).astype(float)
chip_15um_err_effs = np.array(chip_15um_err_effs).astype(float)
chip_15um_charge_in_es = np.array(chip_15um_charge_in_es).astype(float)
chip_15um_effs = chip_15um_effs[(chip_15um_charge_in_es>50)&(chip_15um_charge_in_es<400)]
chip_15um_err_effs = chip_15um_err_effs[(chip_15um_charge_in_es>50)&(chip_15um_charge_in_es<400)]
chip_15um_charge_in_es = chip_15um_charge_in_es[(chip_15um_charge_in_es>50)&(chip_15um_charge_in_es<400)]


ax1.errorbar(chip_225um_charge_in_es, chip_225um_effs, yerr=chip_225um_err_effs, color=colors[3], label=label_dict[process]+r' (22.5 $\mu$m)', marker = '*', markersize=8,linestyle='-')
# ax1.errorbar(chip_18um_charge_in_es, chip_18um_effs, yerr=chip_18um_err_effs, color=colors[5], label=label_dict[process]+r' (22.5 $\mu$m)', marker = '^', markersize=8,linestyle='-')
ax1.errorbar(chip_15um_charge_in_es, chip_15um_effs, yerr=chip_15um_err_effs, color=colors[4], label=label_dict[process]+r' (15 $\mu$m)', marker = 's', markersize=8,linestyle='-')

ax1.plot([0, upper_e_bound], [99, 99], color='gray', linestyle='--', label='99% Efficiency')
ax1.set_xlabel('Seed Threshold ($\it{e}^{-}$)')
ax1.set_ylabel('Efficiency (%)')
# ax1.set_xlim(0, 350)
ax1.set_xlim(0, upper_e_bound)
ax1.set_ylim(65, 100.5)
box = ax1.get_position()
ax1.set_position([box.x0, box.y0, box.width * 0.6, box.height])
# ax1.legend(loc='upper left', bbox_to_anchor=(1.05, 0.6))
ax1.legend(loc='upper left', bbox_to_anchor=(1.03, 0.4))
# ax1.legend(loc='upper left', bbox_to_anchor=(0.05, 0.45))
ax1.set_yticks([65, 70, 75, 80, 85, 90, 95, 99, 100])
ax1.grid(True)

# Add ALICE beam test preliminary
draw_preliminary(ax1)


# Add chip info
process_alias = {"STD": "Standard", "GAP": "Modified w/ Gap", "BLK": "Blanket"}
draw_chip(ax1, pitch="15 $\mu$m, 22.5", process=process_alias[process])


# Add biasing info
draw_configuration(ax1)
# Add biasing info
if ((parseInput()).approval): 
    # If approval then read config from associated .json file
    try:
        # Filename convention of data/CHIP_PCB_VSUB_HV_TEMP_date.json, e.g. data/GAP15SQ_PCB19_0V_10V_15122023.json
        # Importantly, we assume biasing params are the same for different pitches
        with open(json_files[process+"15"+matrix_arrangement], 'r') as json_file:
            config = json.load(json_file)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"{e}\nHint: For the \"--approval\" flag a config.json file is required. Each testbeam measurement requires a separate config.json file. Please follow the naming convention above.")
    draw_configuration(ax1, sub='AC', ac_hv=config['ac']['hv'], ac_ipmos=config['ac']['ipmos'], vsub=config['vsub'], imat=config['imat'], icol=config['icol'], voffset=config['voff'], temp=config['temp'])
else:
    draw_configuration(ax1)



# Adjust layout and save/show plot
# plt.tight_layout()
# plt.subplots_adjust(left=0.08, right=0.75, top=0.97, bottom=0.13)
ax1.set_position([0.1, 0.14, 0.57, 0.81])
# plt.subplots_adjust(left=0.1)
plt.savefig(f"styled_efficiency_plot_{process}.pdf")  # Save the plot as an image
plt.show()  # Display the plot
