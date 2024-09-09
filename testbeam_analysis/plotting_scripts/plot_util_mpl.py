import matplotlib.pyplot as plt
import datetime



################################
# Auxiliary plotting functions #
################################

def draw_chip(ax, x=1.05, y=0.95, font_size=15, spacing=0.055, process="Modified w/ Gap", pitch="22.5"):
    ax.annotate(r'Chip: $\mathbf{CE}$-$\mathbf{65v2}$ (ER1)',xy=(x, y), xycoords='axes fraction', fontsize=font_size, color='black')
    ax.annotate(fr'Process: {process}',xy=(x, y-spacing), xycoords='axes fraction', fontsize=font_size, color='black')
    ax.annotate(fr'Pitch: {pitch} $\mu$m',xy=(x, y-2*spacing), xycoords='axes fraction', fontsize=font_size, color='black')

def draw_configuration(ax, x=1.05, y=0.75, font_size=12, spacing=0.055):
    ax.annotate(r'V$_{sub}$ = V$_{pwell}$ = 0        T = 20 $^{o}$C',xy=(x, y), xycoords='axes fraction', fontsize=font_size, color='black')
    ax.annotate('I$_{mat}$ = 3 mA, I$_{col}$ = 200 $\mu$A, V$_{offset}$ = 1 V',xy=(x, y-spacing), xycoords='axes fraction', fontsize=font_size, color='black')
    ax.annotate('AC amp.: HV = 10 V, I$_{pmos}$ = 100 $\mu$A',xy=(x, y-2*spacing), xycoords='axes fraction', fontsize=font_size, color='black')

def draw_preliminary(ax, x=0.05, y=0.12, font_size=12, spacing=0.05, hspacing=0.05, beam="SPS"):
    if beam=="SPS":
        ax.annotate(r'$\mathbf{ALICE}$ $\mathbf{ITS3}$-$\mathbf{WP3}$ beam test $\mathit{preliminary}$', xy=(x, y), xycoords='axes fraction', fontsize=15, color='black')
        ax.annotate('@CERN-SPS April 2024, 120 GeV/c hadrons', xy=(x+hspacing, y-spacing), xycoords='axes fraction', fontsize=13, color='black')
    elif beam=="lab":
        ax.annotate(r'$\mathbf{ALICE}$ $\mathbf{ITS3}$-$\mathbf{WP3}$ $\mathit{preliminary}$', xy=(x, y), xycoords='axes fraction', fontsize=15, color='black')
        ax.annotate('$^{55}$Fe Source Measurement', xy=(x+hspacing, y-spacing), xycoords='axes fraction', fontsize=13, color='black')
    ax.annotate(datetime.datetime.now().strftime("Plotted on %d %b %Y"), xy=(x+2*hspacing, y-2*spacing), xycoords='axes fraction', fontsize=13, color='black')
