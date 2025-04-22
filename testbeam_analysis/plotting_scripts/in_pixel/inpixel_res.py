#!/usr/bin/env python3

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import patches as pat
from plotting_utils import plot_parameters, add_beam_info
import os
import ROOT
# from utils import utils
import re
import matplotlib.style as style
style.use('wp3_res.mplstyle')
from datetime import date, datetime
import argparse
import yaml
import math

# Scale of x axis, min_eff = min(eff) #AF20 B6: 82 #AF10 B4 86
min_eff = 0

#Font size of the axis, numbers and legend of the plots
font_size_plots = 26
font_size_tot_res = 26
font_size_plot_text = 26
font_size_tacking_res = 20

# x and y position of tracking resolution circel thing, AF10: 2.0,-2.0, AF20: -4, 4.5
x_pos_tracking = 2.5
y_pos_tracking = -2.5

res_max = 8.0

plot_date = str(date.today().day) + ' ' + datetime.now().strftime("%b") + ' ' + str(date.today().year)

parser = argparse.ArgumentParser()
parser.add_argument("config", help="Path to the YAML configuration file")
args = parser.parse_args()

with open(os.path.expandvars(args.config), 'r') as stream:
    try:
        params = yaml.full_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

script_dir=os.path.dirname(os.path.realpath(__file__))

CHIP = params["CHIP"]
NBINS = params["NBINS"]
TRACKINGRESOLUTION = params["TRACKINGRESOLUTION"]
FILE_PATH = params["FILE_PATH"]
pitch = params["PITCH"]
thr = params["THR"]

tot_res = params["TOT_RES"]

data = ROOT.TFile(FILE_PATH,"read")
subdir = data.Get("AnalysisCE65")
key_list = subdir.GetListOfKeys()
dir_list = []
for key in key_list:
    if key.GetClassName() == "TDirectoryFile":
        dir_list.append(key.GetName())

efficiency = data.Get("AnalysisCE65/CE65_6/rmsxyvsxmym")

# Save efficiency as a numpy array with errors
efficiency_array = np.zeros((NBINS, NBINS))
efficiency_errors = np.zeros((NBINS, NBINS))

for i in range(1, NBINS + 1):
    for j in range(1, NBINS + 1):
        efficiency_array[i-1, j-1] = efficiency.GetBinContent(i, j)
        efficiency_errors[i-1, j-1] = efficiency.GetBinError(i, j)


# Subtract in squares TRACKINGRESOLUTION
for i in range(NBINS):
    for j in range(NBINS):
        content = efficiency_array[i, j]
        content_err = efficiency_errors[i, j]
        if content < TRACKINGRESOLUTION/1000.:
            efficiency_array[i, j] = 0.0
            efficiency_errors[i, j] = 0.0
        else:
            squared_difference = content**2 - (TRACKINGRESOLUTION/1000.)**2
            efficiency_array[i, j] = math.sqrt(squared_difference)
            efficiency_errors[i, j] = content_err

# Update the histogram with the modified values

new_hist = ROOT.TH2F("new_efficiency", "Efficiency Histogram", NBINS, 0, NBINS, NBINS, 0, NBINS)

# Update the new histogram with the modified values
for i in range(1, NBINS + 1):
    for j in range(1, NBINS + 1):
        new_hist.SetBinContent(i, j, efficiency_array[i-1, j-1])
        new_hist.SetBinError(i, j, efficiency_errors[i-1, j-1])

new_hist.Scale(1000)


def integrate(hist):
    for i in range(1,int(NBINS/2)+1):
        #cross
        tot = hist.GetBinContent(int(NBINS/2)+1 +i,int(NBINS/2)+1 )
        tot += hist.GetBinContent(int(NBINS/2)+1 -i,int(NBINS/2)+1 )
        tot += hist.GetBinContent(int(NBINS/2)+1 ,int(NBINS/2)+1 +i)
        tot += hist.GetBinContent(int(NBINS/2)+1 ,int(NBINS/2)+1 -i)

        hist.SetBinContent(int(NBINS/2)+1 ,int(NBINS/2)+1 +i,int(tot))
        #hist.SetBinError(int(NBINS/2)+1 ,int(NBINS/2)+1 +i,math.sqrt(int(tot)))
        hist.SetBinContent(int(NBINS/2)+1 ,int(NBINS/2)+1 -i,int(tot))
        #hist.SetBinError(int(NBINS/2)+1 ,int(NBINS/2)+1 -i,math.sqrt(int(tot)))
        hist.SetBinContent(int(NBINS/2)+1 -i,int(NBINS/2)+1 ,int(tot))
        #hist.SetBinError(int(NBINS/2)+1 -i,int(NBINS/2)+1 ,math.sqrt(int(tot)))
        hist.SetBinContent(int(NBINS/2)+1 +i,int(NBINS/2)+1 ,int(tot))
        #hist.SetBinError(int(NBINS/2)+1 +i,int(NBINS/2)+1 ,math.sqrt(int(tot)))
        
    for i in range(1,int(NBINS/2)+1 ):
        #diagonale
        tot = hist.GetBinContent(int(NBINS/2)+1 +i,int(NBINS/2)+1 +1)
        tot += hist.GetBinContent(int(NBINS/2)+1 -i,int(NBINS/2)+1 -1)
        tot += hist.GetBinContent(int(NBINS/2)+1 -i,int(NBINS/2)+1 +i)
        tot += hist.GetBinContent(int(NBINS/2)+1 +i,int(NBINS/2)+1 -i)
        hist.SetBinContent(int(NBINS/2)+1 +i,int(NBINS/2)+1 +i,int(tot))
        #hist.SetBinError(int(NBINS/2)+1 +i,int(NBINS/2)+1 +i,math.sqrt(int(tot)))
        hist.SetBinContent(int(NBINS/2)+1 -i,int(NBINS/2)+1 -i,int(tot))
        #hist.SetBinError(int(NBINS/2)+1 -i,int(NBINS/2)+1 -i,math.sqrt(int(tot)))


    for i in range(1,int(NBINS/2)):
        ####spigolo
        tot = hist.GetBinContent(int(NBINS/2)+1 +i,NBINS)
        tot += hist.GetBinContent(int(NBINS/2)+1 -i,NBINS)
        tot += hist.GetBinContent(int(NBINS/2)+1 +i,1)
        tot += hist.GetBinContent(int(NBINS/2)+1 -i,1)
        #alto destra
        hist.SetBinContent(int(NBINS/2)+1 +i,NBINS,int(tot))
        #hist.SetBinError(int(NBINS/2)+1 +i,NBINS,math.sqrt(int(tot)))
        #alto sinistra
        hist.SetBinContent(int(NBINS/2)+1 -i,NBINS,int(tot))
        #hist.SetBinError(int(NBINS/2)+1 -i,NBINS,math.sqrt(int(tot)))
        #basso destra
        hist.SetBinContent(int(NBINS/2)+1 +i,1,int(tot))
        #hist.SetBinError(int(NBINS/2)+1 +i,1,math.sqrt(int(tot)))
        #basso sinistra
        hist.SetBinContent(int(NBINS/2)+1 -i,1,int(tot))
        #hist.SetBinError(int(NBINS/2)+1 -i,1,math.sqrt(int(tot)))
        hist.SetBinContent(NBINS,int(NBINS/2)+1 +i,int(tot))
        #hist.SetBinError(NBINS,int(NBINS/2)+1 +i,math.sqrt(int(tot)))
        hist.SetBinContent(NBINS,int(NBINS/2)+1 -i,int(tot))
        #hist.SetBinError(NBINS,int(NBINS/2)+1 -1,math.sqrt(int(tot)))
        hist.SetBinContent(1,int(NBINS/2)+1 +i,int(tot))
        #hist.SetBinError(1,int(NBINS/2)+1 +i,math.sqrt(int(tot)))
        hist.SetBinContent(1,int(NBINS/2)+1 -i,int(tot))
        #hist.SetBinError(1,int(NBINS/2)+1 -i,math.sqrt(int(tot)))

    return hist

counter = 0
eff_merged = []
errup_merged = []
errlow_merged = []
for j in range(0,NBINS):
    for i in range(0,NBINS):
        counter +=1
        eff_merged.append(new_hist.GetBinContent(i+(NBINS+2)*j+NBINS+3))
        errup_merged.append(new_hist.GetBinErrorUp(i+(NBINS+2)*j+NBINS+3))
        errlow_merged.append(new_hist.GetBinErrorLow(i+(NBINS+2)*j+NBINS+3))

eff_merged = np.array(eff_merged).reshape(NBINS,NBINS)
errup_merged = np.array(errup_merged).reshape(NBINS,NBINS)
errlow_merged = np.array(errlow_merged).reshape(NBINS,NBINS)
print(np.shape(eff_merged))
##plot
eff = []
errup = []
errlow = []

counter = 0
for j in range(0,NBINS):
    for i in range(0,NBINS):
        eff.append(new_hist.GetBinContent(i+(NBINS+2)*j+NBINS+3))
        errup.append(new_hist.GetBinErrorUp(i+(NBINS+2)*j+NBINS+3))
        errlow.append(new_hist.GetBinErrorLow(i+(NBINS+2)*j+NBINS+3))
        
# # min_eff = min(eff) #AF20 B6: 68 #AF10 B4 86
# min_eff = 86

eff = np.array(eff).reshape(NBINS,NBINS)
errup = np.array(errup).reshape(NBINS,NBINS)
errlow = np.array(errlow).reshape(NBINS,NBINS)

#c = ['tab:red','tab:blue','tab:green']
c = ["#56B4E9", "#E69F00", "#009E73"]

# #Font size of the axis, numbers and legend of the plots
# font_size_plots = 18

d = NBINS/2.
na = int(NBINS/2)

d_p = pitch/2.
na_p = int(pitch/2.)

fig,ax=plt.subplots(1,2,figsize=(35,13))
plt.subplots_adjust(wspace=0.27,top=0.98,left=0.07,right=0.8,bottom=0.03)
plt.sca(ax[0])
im = plt.imshow(eff,extent=[-pitch/2.,pitch/2.,-pitch/2.,pitch/2.],vmin=min_eff,vmax=res_max,origin='lower')
cb = plt.colorbar(im,pad=0.015,fraction=0.0474)
cb.ax.tick_params(labelsize=font_size_plots)  # Adjust the font size as needed

for i in range(na_p):
    plt.arrow(0,i*d_p/na_p,0,d_p/na_p,head_width=0.3, head_length=0.3,color=c[0],length_includes_head=True,zorder=100,clip_on=False)
    plt.arrow(i*d_p/na_p,d_p,d_p/na_p,0,head_width=0.3, head_length=0.3,color=c[1],length_includes_head=True,zorder=100,clip_on=False)
    plt.arrow(d_p-i*d_p/na_p, d_p-i*d_p/na_p, -d_p/na_p, -d_p/na_p,head_width=0.3, head_length=0.3,color=c[2],length_includes_head=True,zorder=100,clip_on=False)
plt.plot([0],[0],marker='.',color=c[0],zorder=99,clip_on=False)
plt.plot([0],[d_p],marker='.',color=c[1],zorder=99,clip_on=False)
plt.plot([d_p],[d_p],marker='.',color=c[2],zorder=99,clip_on=False)

# Get the limits of the axes
xlim = ax[0].get_xlim()
ylim = ax[0].get_ylim()

# Calculate the position of the lower right corner
x_lower_right = xlim[1]
y_lower_right = ylim[0]

if pitch == 22.5:
    # Define the distance from the lower right corner
    distance_x = 6.3  # for example
    distance_y = 5.175  # for example
    
if pitch == 20:
    # Define the distance from the lower right corner
#     distance_x = 3.3  # for example
#     distance_y = 2.3  # for example
    distance_x = 5.6  # for example
    distance_y = 4.6  # for example

if pitch == 15:
    # Define the distance from the lower right corner
    distance_x = 4.2  # for example
    distance_y = 3.45  # for example

if pitch == 10:
    # Define the distance from the lower right corner
    distance_x = 2.8  # for example
    distance_y = 2.3  # for example

# Calculate the position of the circle
x_pos_tracking = x_lower_right - distance_x
y_pos_tracking = y_lower_right + distance_y

# Use this position when adding the circle
ax[0].add_patch(pat.Circle((x_pos_tracking, y_pos_tracking), TRACKINGRESOLUTION, color='white', alpha=0.33))

# ax[0].add_patch(pat.Circle((x_pos_tracking,y_pos_tracking),TRACKINGRESOLUTION,color='white',alpha=0.33))
plt.annotate(f'Tracking\nresolution\n$\\sigma={TRACKINGRESOLUTION}$ µm', (x_pos_tracking, y_pos_tracking), color='white', horizontalalignment='center', verticalalignment='center', fontsize=font_size_tacking_res)
plt.annotate('A', (0,0), color=c[0], fontweight="bold", xytext=(0,-4), textcoords='offset points', horizontalalignment='center', verticalalignment='top')
plt.annotate('B', (0,d_p), color=c[1], fontweight="bold", xytext=(0,2), textcoords='offset points', horizontalalignment='center',  verticalalignment='bottom')
plt.annotate('C', (d_p,d_p), color=c[2], fontweight="bold", xytext=(0,2), textcoords='offset points', horizontalalignment='center', verticalalignment='bottom')
cb.set_label("Mean absolute deviation ($\\sqrt{\\Delta x^2+\\Delta y^2}$) [µm]", fontsize=font_size_plots)
plt.xticks([-pitch/2,-pitch/3,-pitch/6,0,pitch/6,pitch/3,pitch/2], fontsize=font_size_plots)
plt.yticks([-pitch/2,-pitch/3,-pitch/6,0,pitch/6,pitch/3,pitch/2], fontsize=font_size_plots)
plt.xlabel("In-pixel track intercept x (µm)", fontsize=font_size_plots)
plt.ylabel("In-pixel track intercept y (µm)", fontsize=font_size_plots)
plt.xlim(-pitch/2,pitch/2)
plt.ylim(-pitch/2,pitch/2)

n = 10000

def matrix_to_path(mat):
    return np.array([
        [mat[int(NBINS/2.)][int(NBINS/2.)+int(round(dx))] for dx in np.linspace(0,d-1,n,endpoint=False)],
        [mat[int(NBINS/2.)+int(round(dx))][-1] for dx in np.linspace(0,d-1,n,endpoint=False)],
        [mat[int(NBINS/2.)+int(round(dx))][int(NBINS/2.)+int(round(dx))] for dx in np.linspace(0,d-1,n,endpoint=False)[::-1]],
    ])

y     = matrix_to_path(eff_merged)
yelow = matrix_to_path(errlow_merged)
yeup  = matrix_to_path(errup_merged)
d = d*pitch/NBINS
x = np.array([
    np.linspace(0,d,n,endpoint=False),
    np.linspace(d,2*d,n,endpoint=False),
    np.linspace(2*d,2*d+d*np.sqrt(2),n,endpoint=False)
])

plt.sca(ax[1])
for i in range(3):
    plt.fill([*x[i],*x[i][::-1]],[*(yeup[i]+y[i]),*(-yelow[i]+y[i])[::-1]],c=c[i],alpha=.3)
    plt.plot(x[i],y[i],color=c[i])

# Set a fixed starting point for the x-axis of the right plot
fixed_x_start = 0  # Change this value to set your desired starting point
plt.xlim(fixed_x_start, x[-1][-1])  # This line ensures the x-axis starts at the specified value

# plt.xlim(x[0][0]-0.1,x[-1][-1])
plt.xticks([0,pitch/2,pitch,pitch*3/2], fontsize=font_size_plots)
plt.yticks(fontsize=font_size_plots)
plt.ylim(min_eff,res_max)
plt.grid(axis='both')
plt.xlabel("Distance along the path (µm)", fontsize=font_size_plots)
plt.ylabel("Mean absolute deviation ($\sqrt{\Delta x^2+\Delta y^2}$) [µm]", fontsize=font_size_plots)
secax = ax[1].secondary_xaxis('top')
secax.set_xticks([x[0][0],x[1][0],x[2][0],x[2][-1]])
for i,t in enumerate(secax.set_xticklabels(['A','B','C','A'])):
    t.set_color(c[i%3])
# plt.axhline(tot_res,linestyle='dotted',color='grey', linewidth=3.5)
plt.sca(ax[1])
# plt.text(0.08, tot_res - 0.4, "Total resolution", fontsize=font_size_tot_res, color='grey')
# plt.text(14.5,tot_res,f"Total efficiency",ha='center', va='bottom',color='grey', fontsize=font_size_plots)

# Determine the coordinates for the lower left corner
# x_start = ax[1].get_xlim()[0] + 0.5  # Add a bit of padding
x_start = ax[1].get_xlim()[0] + 8.5  # Add a bit of padding

y_start = ax[1].get_ylim()[0] + 0.25  # Add a bit of padding

if pitch == 22.5:
    # Add the patches and annotations at the new coordinates
    ax[1].add_patch(pat.Rectangle((x_start, y_start), 6.7*2.25, 1.8, facecolor="white", edgecolor="grey", linewidth=0.5, zorder=9))
    ax[1].add_patch(pat.Rectangle((x_start + 0.5*2.25, y_start + 0.4), 1*2.25, 1, color=c[0], alpha=0.3, zorder=9))
    ax[1].add_patch(pat.Rectangle((x_start + 1.5*2.25, y_start + 0.4), 1*2.25, 1, color=c[1], alpha=0.3, zorder=9))
    ax[1].add_patch(pat.Rectangle((x_start + 2.5*2.25, y_start + 0.4), 1*2.25, 1, color=c[2], alpha=0.3, zorder=9))
    
if pitch == 20:
    # Add the patches and annotations at the new coordinates
    ax[1].add_patch(pat.Rectangle((x_start, y_start), 6.7*2, 1.8, facecolor="white", edgecolor="grey", linewidth=0.5, zorder=9))
    ax[1].add_patch(pat.Rectangle((x_start + 0.5*2, y_start + 0.4), 1*2, 1, color=c[0], alpha=0.3, zorder=9))
    ax[1].add_patch(pat.Rectangle((x_start + 1.5*2, y_start + 0.4), 1*2, 1, color=c[1], alpha=0.3, zorder=9))
    ax[1].add_patch(pat.Rectangle((x_start + 2.5*2, y_start + 0.4), 1*2, 1, color=c[2], alpha=0.3, zorder=9))
    
    ax[1].plot([x_start + 0.5*2, x_start + 0.5*2 + 2], [y_start + 0.4 + 0.5, y_start + 0.4 + 0.5], color=c[0], linestyle='-', linewidth=1, zorder=10)
    ax[1].plot([x_start + 1.5*2, x_start + 1.5*2 + 2], [y_start + 0.4 + 0.5, y_start + 0.4 + 0.5], color=c[1], linestyle='-', linewidth=1, zorder=10)
    ax[1].plot([x_start + 2.5*2, x_start + 2.5*2 + 2], [y_start + 0.4 + 0.5, y_start + 0.4 + 0.5], color=c[2], linestyle='-', linewidth=1, zorder=10)
    
    plt.annotate(xy=(x_start + 4*2, y_start + 0.9), text="Stat. error", verticalalignment="center", zorder=9, fontsize=font_size_tot_res)
if pitch == 15:
    # Add the patches and annotations at the new coordinates
    ax[1].add_patch(pat.Rectangle((x_start, y_start), 6.7 * 15 / 10, 1.8, facecolor="white", edgecolor="grey", linewidth=0.5, zorder=9))
    ax[1].add_patch(pat.Rectangle((x_start + 0.5 * 15 / 10, y_start + 0.4), 1 * 15 / 10, 1, color=c[0], alpha=0.3, zorder=9))
    ax[1].add_patch(pat.Rectangle((x_start + 1.5 * 15 / 10, y_start + 0.4), 1 * 15 / 10, 1, color=c[1], alpha=0.3, zorder=9))
    ax[1].add_patch(pat.Rectangle((x_start + 2.5 * 15 / 10, y_start + 0.4), 1 * 15 / 10, 1, color=c[2], alpha=0.3, zorder=9))
    
    ax[1].plot([x_start + 0.5 * 15 / 10, x_start + 0.5 * 15 / 10 + 2], [y_start + 0.4 + 0.5, y_start + 0.4 + 0.5], color=c[0], linestyle='-', linewidth=1, zorder=10)
    ax[1].plot([x_start + 1.5 * 15 / 10, x_start + 1.5 * 15 / 10 + 2], [y_start + 0.4 + 0.5, y_start + 0.4 + 0.5], color=c[1], linestyle='-', linewidth=1, zorder=10)
    ax[1].plot([x_start + 2.5 * 15 / 10, x_start + 2.5 * 15 / 10 + 2], [y_start + 0.4 + 0.5, y_start + 0.4 + 0.5], color=c[2], linestyle='-', linewidth=1, zorder=10)
    
    plt.annotate(xy=(x_start + 3.75 * 15 / 10, y_start + 0.9), text="Stat. error", verticalalignment="center", zorder=9, fontsize=font_size_tot_res)
if pitch == 10:
    # Add the patches and annotations at the new coordinates
    ax[1].add_patch(pat.Rectangle((x_start-0.25, y_start), 6.7, 1.8, facecolor="white", edgecolor="grey", linewidth=0.5, zorder=9))
    ax[1].add_patch(pat.Rectangle((x_start-0.25 + 0.5, y_start + 0.4), 1, 1, color=c[0], alpha=0.3, zorder=9))
    ax[1].add_patch(pat.Rectangle((x_start-0.25 + 1.5, y_start + 0.4), 1, 1, color=c[1], alpha=0.3, zorder=9))
    ax[1].add_patch(pat.Rectangle((x_start-0.25 + 2.5, y_start + 0.4), 1, 1, color=c[2], alpha=0.3, zorder=9))
    
    ax[1].plot([x_start-0.25 + 0.5, x_start-0.25 + 0.5 + 1], [y_start + 0.4 + 0.5, y_start + 0.4 + 0.5], color=c[0], linestyle='-', linewidth=1, zorder=10)
    ax[1].plot([x_start-0.25 + 1.5, x_start-0.25 + 1.5 + 1], [y_start + 0.4 + 0.5, y_start + 0.4 + 0.5], color=c[1], linestyle='-', linewidth=1, zorder=10)
    ax[1].plot([x_start-0.25 + 2.5, x_start-0.25 + 2.5 + 1], [y_start + 0.4 + 0.5, y_start + 0.4 + 0.5], color=c[2], linestyle='-', linewidth=1, zorder=10)
    
    plt.annotate(xy=(x_start-0.25 + 4, y_start + 0.9), text="Stat. error", verticalalignment="center", zorder=9, fontsize=font_size_tot_res)

# ax[1].add_patch(pat.Rectangle((0.5,75.5),11,3,facecolor="white",edgecolor="grey",linewidth=0.5,zorder=9))
# ax[1].add_patch(pat.Rectangle((1,76),1,2,color=c[0],alpha=0.3,zorder=9))
# ax[1].add_patch(pat.Rectangle((2,76),1,2,color=c[1],alpha=0.3,zorder=9))
# ax[1].add_patch(pat.Rectangle((3,76),1,2,color=c[2],alpha=0.3,zorder=9))
# plt.annotate(xy=(4.5,77), text="Stat. error", verticalalignment="center",zorder=9)
asp = np.diff(ax[1].get_xlim())[0] / np.diff(ax[1].get_ylim())[0]
ax[1].set_aspect(asp*0.95)

CHIP_SETTINGS = '\n'.join([
    params["CHIP_SETTINGS"]
])

add_beam_info(ax[0],y=0.14)

ax[1].text(1.03, 1.0,
                   CHIP_SETTINGS,
                   fontsize=font_size_plot_text,
                   linespacing=1.7,
                   ha='left', va='top',
                   transform=ax[1].transAxes
                   )

# plotting_date = str(date.today().year)+"-"+str(date.today().month)+"-"+str(date.today().day)

# Get the current date
current_date = datetime.now()
# Format the date as "YYYY-MM-DD"
formatted_date = current_date.strftime("%Y-%m-%d")

plt.savefig("plots/ALICE-ITS3_"+formatted_date+"_APTS-SF_inpix_res_"+CHIP+"_"+str(int(thr))+"e.pdf")
plt.savefig("plots/ALICE-ITS3_"+formatted_date+"_APTS-SF_inpix_res_"+CHIP+"_"+str(int(thr))+"e.png")
# plt.show()

