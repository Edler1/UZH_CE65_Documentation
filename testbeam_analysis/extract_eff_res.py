import numpy as np
import subprocess
import os
import re
import sys

# Function to extract the residuals 
def extract_residuals(process_output):
    residual_x = subprocess.run(['egrep', '-A 10', 'DEBUG - Pad 7 : residualsX'], input=process_output, capture_output=True, text=True)
    residual_x = subprocess.run(['egrep', 'Sigma'], input=residual_x.stdout, capture_output=True, text=True)
    residual_x_val = subprocess.run(['awk', '{print $3}'], input=residual_x.stdout, capture_output=True, text=True)
    residual_x_val = residual_x_val.stdout.strip()
    residual_x_err = subprocess.run(['awk', '{print $5}'], input=residual_x.stdout, capture_output=True, text=True)
    residual_x_err = residual_x_err.stdout.strip()
    
    residual_y = subprocess.run(['egrep', '-A 10', 'DEBUG - Pad 8 : residualsY'], input=process_output, capture_output=True, text=True)
    residual_y = subprocess.run(['egrep', 'Sigma'], input=residual_y.stdout, capture_output=True, text=True)
    residual_y_val = subprocess.run(['awk', '{print $3}'], input=residual_y.stdout, capture_output=True, text=True)
    residual_y_val = residual_y_val.stdout.strip()
    residual_y_err = subprocess.run(['awk', '{print $5}'], input=residual_y.stdout, capture_output=True, text=True)
    residual_y_err = residual_y_err.stdout.strip()

    return residual_x_val, residual_x_err, residual_y_val, residual_y_err

# Function to extract efficiencies (requires the efficiencies be printed below the word "Efficiencies")
def extract_efficiency(process_output):
    efficiency = subprocess.run(['egrep', '-A 1', 'Efficiencies'], input=process_output, capture_output=True, text=True)
    efficiency = subprocess.run(['tail', '-1'], input=efficiency.stdout, capture_output=True, text=True)
    efficiency_val = subprocess.run(['awk', '{print $1}'], input=efficiency.stdout, capture_output=True, text=True)
    efficiency_val = efficiency_val.stdout.strip()
    efficiency_err_plus = subprocess.run(['awk', '{print $2}'], input=efficiency.stdout, capture_output=True, text=True)
    efficiency_err_plus = efficiency_err_plus.stdout.strip()
    efficiency_err_minus = subprocess.run(['awk', '{print $3}'], input=efficiency.stdout, capture_output=True, text=True)
    efficiency_err_minus = efficiency_err_minus.stdout.strip()
    
    # We take simple average of plus minus contributions to error
    efficiency_err = (float(efficiency_err_plus)+float(efficiency_err_minus))/2

    return efficiency_val, efficiency_err

# Function to compute total residual and its error (telescope subtraction should happen in a separate function...)
def compute_position_resolution(residual_x_val, residual_x_err, residual_y_val, residual_y_err, tel_resolution = 2.2, tel_resolution_err = 0.):

    # Typecast arguments into floats
    residual_x_val = float(residual_x_val)
    residual_x_err = float(residual_x_err)
    residual_y_val = float(residual_y_val)
    residual_y_err = float(residual_y_err)

    # Start by computing total residual, a la APTS+DPTS
    residual_tot_val = (residual_x_val+residual_y_val)/2

    # Compute total error by summing in quadrature
    residual_tot_err = (1/2)*np.sqrt(residual_x_err**2 + residual_y_err**2)

    # Substract telescope resolution and compute associated error
    position_resolution_val = np.sqrt(residual_tot_val**2 - tel_resolution**2)
    position_resolution_err = (1/position_resolution_val)*np.sqrt((residual_tot_val**2)*(residual_tot_err**2) - (tel_resolution**2)*(tel_resolution_err**2))
    return position_resolution_val, position_resolution_err


########
#PARAMS#
########

#working_dir = "/ada_mnt/ada/user/eploerer/UZH_CE65_Documentation/testbeam_analysis/ITS3utils"
working_dir = "/user/eploerer/UZH_CE65_Documentation/testbeam_analysis/ITS3utils"
chip = "STD15SQ"
if len(sys.argv)==2: chip = sys.argv[1]
#seed_thresholds = ["200", "400", "600", "800", "1000", "1200", "1400", "1600", "1800", "2000"]
seed_thresholds = ["100", "200", "300", "400", "500", "600", "700", "800", "900", "1000", "1100", "1200", "1300", "1400", "1500", "1600", "1700", "1800", "1900", "2000"]


os.chdir(working_dir)

# Here we find that file(s) that we want to loop over -> Basically a final step cause we should do this on remote server...
print(os.getcwd())


# This script is meant to be run remotely, with the output .txt files being copied over
# ssh -o ServerAliveInterval=100 eploerer@mshort.iihe.ac.be

file_list = []
for threshold in seed_thresholds:
    #source_file = subprocess.run(['ls', 'SPS202404/output/GAP15SQ/analysis_SPS-GAP15SQ_*_seedthr[0-9]*_nbh[0-9]*_cluster.root'], capture_output=True, text=True)
    source_file = subprocess.run(['ls SPS202404/output/'+chip+'/analysis_SPS-'+chip+'_*_seedthr'+threshold+'_nbh'+threshold+'*_cluster.root'], shell=True, capture_output=True, text=True)
    # Below is for window method where the neighbour threshold is fixed.
    #source_file = subprocess.run(['ls SPS202404/output/'+chip+'/analysis_SPS-'+chip+'_*_seedthr'+threshold+'_nbh'+'100'+'*_window.root'], shell=True, capture_output=True, text=True)
    source_file = source_file.stdout.strip()
    slicing_index = source_file.find("analysis") 
    source_file = source_file[slicing_index:]
    file_list.append(source_file)



# Use numpy arrays here instead of lists, since they may need to be rearranged
seed_th_array = np.array([])
pos_res_array = np.array([])
pos_res_err_array = np.array([])
eff_array = np.array([])
eff_err_array = np.array([])
for file in file_list:
    print('SPS202404/output/'+chip+'/'+file)

    plotting_output = subprocess.run([working_dir+'/corry/plot_analog_ce65v2.py', '-f', 'SPS202404/output/'+chip+'/'+file], capture_output=True, text=True)
    plotting_output = plotting_output.stdout

    seed = re.search(r'seedthr(\d+)', file).group(1)
    pos_res, pos_res_err = compute_position_resolution(*extract_residuals(plotting_output))

    eff, eff_err = extract_efficiency(plotting_output)

    seed_th_array = np.append(seed_th_array, seed)
    pos_res_array = np.append(pos_res_array, str(pos_res))
    pos_res_err_array = np.append(pos_res_err_array, str(pos_res_err))
    eff_array = np.append(eff_array, str(eff))
    eff_err_array = np.append(eff_err_array, str(eff_err))

# Sort arrays in ascending order for plotting later
sort_by_seed_indices = np.argsort(seed_th_array.astype(float))

seed_th_array = seed_th_array[sort_by_seed_indices]
pos_res_array = pos_res_array[sort_by_seed_indices]
pos_res_err_array = pos_res_err_array[sort_by_seed_indices]
eff_array = eff_array[sort_by_seed_indices]
eff_err_array = eff_err_array[sort_by_seed_indices]


# SPS_STD225SQ_HV10_adc_res_err.txt
out_dir = "SPS202404/output"
fname_res = "SPS_"+chip+"_HV10_adc_res_err.txt"
fname_eff = "SPS_"+chip+"_HV10_adc_eff_err.txt"

with open(out_dir+"/"+fname_res, "w") as file:
    for i in range(len(seed_th_array)):
        file.write(seed_th_array[i]+" "+pos_res_array[i]+" "+pos_res_err_array[i]+"\n")

with open(out_dir+"/"+fname_eff, "w") as file:
    for i in range(len(seed_th_array)):
        file.write(seed_th_array[i]+" "+eff_array[i]+" "+eff_err_array[i]+"\n")


