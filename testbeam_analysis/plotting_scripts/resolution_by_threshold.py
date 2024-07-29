import matplotlib.pyplot as plt
import numpy as np
import json
import datetime


# Philosophy -> Plotting script for resolution vs threshold. Takes .txt files with column-wise "threshold" "resolution" "uncertainty" information. Meant to be run for a variety of pitches(15um, 18um, 22.5um) for a given process (GAP, STD, BLK).


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

# .txt directory filepath (empty by default as .txt files are assumed to be in pwd)
filepath = ""
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
fig, ax1 = plt.subplots(figsize=(9, 6))
# fig = plt.figure(figsize=(6, 6))
# fig = plt.figure()
# ax1 = plt.subplot(111)


# Declaring dicts for data
chip_225um_charge_in_es = []
chip_225um_res = []
chip_225um_err_res = []

chip_18um_charge_in_es = []
chip_18um_res = []
chip_18um_err_res = []

chip_15um_charge_in_es = []
chip_15um_res = []
chip_15um_err_res = []

f4 = open(f'{filepath}{testbeam}_{process}225{matrix_arrangement}_HV{hv}_adc_res_err.txt', 'r')  # We need to re-open the file
for line in f4:
    line = line.strip()
    columns = line.split()
    chip_225um_adc_value = float(columns[0])
    chip_225um_charge_in_e_value = chip_225um_adc_value*0.23287
    chip_225um_res_value = float(columns[1]) # * 100.0
    chip_225um_err_res_value = float(columns[2]) # * 100.0
    chip_225um_charge_in_es.append(chip_225um_charge_in_e_value)
    chip_225um_res.append(chip_225um_res_value)
    chip_225um_err_res.append(chip_225um_err_res_value)
f4.close()

# f5 = open(f'{filepath}{testbeam}_{process}18{matrix_arrangement}_HV{hv}_adc_res_err.txt', 'r')  # We need to re-open the file
# for line in f5:
#     line = line.strip()
#     columns = line.split()
#     # print(columns)
#     chip_18um_adc_value = float(columns[0])
#     chip_18um_charge_in_e_value = chip_18um_adc_value*0.23716  # PCB24 B4
#     chip_18um_res_value = float(columns[1]) # * 100.0
#     chip_18um_err_res_value = float(columns[2]) # * 100.0
#     chip_18um_charge_in_es.append(chip_18um_charge_in_e_value)
#     chip_18um_res.append(chip_18um_res_value)
#     chip_18um_err_res.append(chip_18um_err_res_value)
# f5.close()

f6 = open(f'{filepath}{testbeam}_{process}15{matrix_arrangement}_HV{hv}_adc_res_err.txt', 'r')  # We need to re-open the file
for line in f6:
    line = line.strip()
    columns = line.split()
    # print(columns)
    chip_15um_adc_value = float(columns[0])
    chip_15um_charge_in_e_value = chip_15um_adc_value*0.23716  # PCB24 B4
    chip_15um_res_value = float(columns[1]) # * 100.0
    chip_15um_err_res_value = float(columns[2]) # * 100.0
    chip_15um_charge_in_es.append(chip_15um_charge_in_e_value)
    chip_15um_res.append(chip_15um_res_value)
    chip_15um_err_res.append(chip_15um_err_res_value)
f6.close()


# ### Constrain values range for noise + too high threshold e-
upper_e_bound = 410

chip_225um_res = np.array(chip_225um_res).astype(float)
chip_225um_err_res = np.array(chip_225um_err_res).astype(float)
chip_225um_charge_in_es = np.array(chip_225um_charge_in_es).astype(float)
chip_225um_res = chip_225um_res[(chip_225um_charge_in_es>50)&(chip_225um_charge_in_es<400)]
chip_225um_err_res = chip_225um_err_res[(chip_225um_charge_in_es>50)&(chip_225um_charge_in_es<400)]
chip_225um_charge_in_es = chip_225um_charge_in_es[(chip_225um_charge_in_es>50)&(chip_225um_charge_in_es<400)]

# chip_18um_res = np.array(chip_18um_res).astype(float)
# chip_18um_err_res = np.array(chip_18um_err_res).astype(float)
# chip_18um_charge_in_es = np.array(chip_18um_charge_in_es).astype(float)
# chip_18um_res = chip_18um_res[(chip_18um_charge_in_es>50)&(chip_18um_charge_in_es<400)]
# chip_18um_err_res = chip_18um_err_res[(chip_18um_charge_in_es>50)&(chip_18um_charge_in_es<400)]
# chip_18um_charge_in_es = chip_18um_charge_in_es[(chip_18um_charge_in_es>50)&(chip_18um_charge_in_es<400)]

chip_15um_res = np.array(chip_15um_res).astype(float)
chip_15um_err_res = np.array(chip_15um_err_res).astype(float)
chip_15um_charge_in_es = np.array(chip_15um_charge_in_es).astype(float)
chip_15um_res = chip_15um_res[(chip_15um_charge_in_es>50)&(chip_15um_charge_in_es<400)]
chip_15um_err_res = chip_15um_err_res[(chip_15um_charge_in_es>50)&(chip_15um_charge_in_es<400)]
chip_15um_charge_in_es = chip_15um_charge_in_es[(chip_15um_charge_in_es>50)&(chip_15um_charge_in_es<400)]


ax1.errorbar(chip_225um_charge_in_es, chip_225um_res, yerr=chip_225um_err_res, color=colors[3], label=label_dict[process]+r' (22.5 $\mu$m)', marker = '*', markersize=8,linestyle='-')
# ax1.errorbar(chip_18um_charge_in_es, chip_18um_res, yerr=chip_18um_err_res, color=colors[5], label=label_dict[process]+r' (22.5 $\mu$m)', marker = '^', markersize=8,linestyle='-')
ax1.errorbar(chip_15um_charge_in_es, chip_15um_res, yerr=chip_15um_err_res, color=colors[4], label=label_dict[process]+r' (15 $\mu$m)', marker = 's', markersize=8,linestyle='-')




##?ax1.plot([0, 350], [99, 99], color='gray', linestyle='--', label='99% Efficiency')
ax1.set_xlabel('Seed Threshold ($\it{e}^{-}$)')
ax1.set_ylabel(r'Resolution ($\mu m$) ')
# ax1.set_xlim(0, 350)
ax1.set_xlim(0, upper_e_bound)
ax1.set_ylim(0.0, 6.0)
box = ax1.get_position()
ax1.set_position([box.x0, box.y0, box.width * 0.6, box.height])
# ax1.legend(loc='upper left', bbox_to_anchor=(1.05, 0.6))
# ax1.legend(loc='upper left', bbox_to_anchor=(0.05, 0.4))
ax1.legend(loc='upper left', bbox_to_anchor=(0.35, 0.35))
##?ax1.set_yticks([65, 70, 75, 80, 85, 90, 95, 99, 100])
ax1.grid(True)

# Add text annotation to B4HV10 plot
# ax1.annotate('ALICE ITS3-WP3 beam test preliminary\n@CERN-PS May 2022, 10 GeV/c π-', xy=(0.05, 0.10), xycoords='axes fraction', fontsize=15, color='black')
# ax1.annotate('Beam test preliminary\n@CERN-SPS April 2024, 120 GeV/c π-', xy=(0.05, 0.10), xycoords='axes fraction', fontsize=15, color='black')
ax1.annotate(r'$\mathbf{ALICE}$ $\mathbf{ITS3}$$\mathbf{-}$$\mathbf{WP3}$ beam test $\mathit{Work}$ $\mathit{in}$ $\mathit{Progress}$', xy=(0.05, 0.10), xycoords='axes fraction', fontsize=15, color='black')
ax1.annotate('@CERN-SPS April 2024, 120 GeV/c π-', xy=(0.10, 0.05), xycoords='axes fraction', fontsize=13, color='black')
# ax1.annotate(datetime.datetime.now().strftime("Plotted on %d %b %Y"), xy=(0.05, 0.05), xycoords='axes fraction', fontsize=15, color='black')

# ax1.annotate('V$_{sub}$ = P$_{well}$ = 0\nI$_{mat}$ = 5 mA, I$_{col}$ = 100 $\mu$ A, V$_{offset}$ = 0.4 V\nAC Amp: HV = 10 V, I$_{pmos}$ = 1 $\mu$A\nDC Amp: I$_{pmos}$ = 1 $\mu$A\nSF: I$_{nmos}$ = 1 $\mu$A, V$_{reset}$ = 3.3 V',xy=(1.05, 0.8), xycoords='axes fraction', fontsize=10, color='black')

# Adjust layout and save/show plot
plt.tight_layout()
plt.savefig(f"styled_resolution_plot_{process}.png")  # Save the plot as an image
plt.show()  # Display the plot
