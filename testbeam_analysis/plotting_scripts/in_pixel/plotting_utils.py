from matplotlib import pyplot as plt
import datetime

font_size = 22

def plot_parameters(pars, x=0.75, y=0.6, axes=None):
    p = {k: '?' for k in ['wafer','chip','version','split', 'id', 'thresh',
                          'pwell','sub','vcasn','vcasb', 'idb',
                          'ireset', 'ibias', 'ibiasn','vbb','vh','ibiasf']}
    p.update(pars)

    if 'Diff' in p['id']:
        p['wafer'] = None
        p['chip'] = None
        p['version'] = None
    if p['sub'] is None or p['pwell'] is None or p['pwell']=="?": p['vbb'] = ""
    else: p['vbb'] = "=%s\,\\mathrm{V}"%p['sub']

    if p['vcasb']!="variable": p['vcasb'] = "%s\,\\mathrm{mV}"%p['vcasb']
    if p['vcasn']!="variable": p['vcasn'] = "%s\,\\mathrm{mV}"%p['vcasn']
    if p['ireset']!="variable": p['ireset'] = "%s\,\\mathrm{pA}"%p['ireset']
    if p['idb']!="variable": p['idb'] = "%s\,\\mathrm{nA}"%p['idb']
    if p['ibias']!="variable": p['ibias'] = "%s\,\\mathrm{nA}"%p['ibias']
    if p['ibiasn']=="Ibias/10": p['ibiasn'] = "I_{bias}/10"
    elif p['ibiasn']!="variable": p['ibiasn'] = "%s\,\\mathrm{nA}"%p['ibiasn']
    else: p['ibiasn']="variable"

    if p['vh']!="variable": p['vh'] = "%s\,\\mathrm{mV}"%p['vh']
    else: p['vh']="variable"

    info = [
        '$\\bf{%s}$'%p['id'],
        'wafer: %s'%p['wafer'],
        'chip: %s'%p['chip'],
        'version: %s'%p['version'],
        'split:  %s'%p['split'],
        '$I_{reset}=%s$' %p['ireset'],
        '$I_{bias}=%s$' %p['ibias'],
        '$I_{biasn}=%s$' %p['ibiasn'],
        '$I_{db}=%s$'   %p['idb'],
        '$V_{casn}=%s$' %p['vcasn'],
        '$V_{casb}=%s$' %p['vcasb'],
        '$V_{pwell}=V_{sub}%s$' %p['vbb'],
        '$V_{h}=%s$' %p['vh'],
        '$I_{biasf}=%s\,\\mathrm{mA}$' %p['ibiasf'],
        'Threshold$=%s\,e^{-}$' %p['thresh']
    ]

    if axes is None:
        plt.text(x,y,
            '\n'.join([i for i in info if ("None" not in i) and ("?" not in i)]),
            fontsize=8,
            ha='left', va='top',
            transform=plt.gca().transAxes
        )
    else:
        axes.text(x,y,
            '\n'.join([i for i in info if ("None" not in i) and ("?" not in i)]),
            fontsize=8,
            ha='left', va='top',
            transform=axes.transAxes
        )


def add_beam_info(ax,x=0.01,y=0.98,
        beam_info='@SPS April 2024, 120 GeV/$\it{c}$ hadrons',
        association_window=(480,480,1.5)):

    ax.text(
        x,y,
        '$\\bf{ALICE\;ITS3}$ beam test $\\it{work\;in\;progress}$',
        fontsize=font_size, color='white',
        ha='left', va='top',
        transform=ax.transAxes
    )
    ax.text(
        x,y-0.06,
        beam_info,
        fontsize=font_size-3, color='white',
        ha='left', va='top',
        transform=ax.transAxes
    )
    ax.text(
        x,y-0.105,
        datetime.datetime.now().strftime("Plotted on %d %b %Y"),
        fontsize=font_size-6, color='white',
        ha='left', va='top',
        transform=ax.transAxes
    )
    # ax.text(0.02,0.015,
    #     "Association window: %s \u03BCm $\\times$ %s \u03BCm $\\times$ %s \u03BCs"%association_window +\
    #         ", no pixel masking.",
    #     fontsize=7, color='white',
    #     ha='left', va='center',
    #     transform=ax.transAxes
    # )