#!/bin/env python3

# Plot preliminary results for approval

import argparse
import os
import plot_util
import ROOT
from copy import deepcopy
from pprint import pprint
import datetime

# Binning: width, min, max
database = {
  'submatrix': ['AC','DC','SF'],
  'variant': ['A4', 'B4', 'C4', 'D4'],
  # 'variant': ['A4', 'B4', 'C4'],
  # 'variant': ['A4'],
  # 'variant': ['A4', 'B4', 'C4'],
  # 'variant': ['C4'],
  'A4':{
    'template': 'B4',
    'process': 'Standard',
    'pitch': '15',
    'binning_seedChargeENC':[25, 0, 3100],
    'noise':'/local/ITS3utils/PS202205/qa/A4/PS-A4_HV10-noisemap.root',
    'AC':{
    # Using CODIMD calib factors
      'calibration': 4.17,
      'result':{
        'file': 'output/analysisCE65-AC_iter1-seed_PS-A4_HV10.root',
      },
    },
    'DC':{
      'calibration': 5.56,
      'result':{
        'file': 'output/analysisCE65-DC_iter1-seed_PS-A4_HV10.root',
      },
    },
    'SF':{
      'calibration': 1.49,
      'result':{
        'file': 'output/analysisCE65-SF_iter1-seed_PS-A4_HV10.root',
      },
    },
  },
  'B4_HV1':{
    'template': 'B4',
    'noise':'qa/PS-B4_HV1-noisemap.root',
    'setup':{
      'HV': 1,
      'PWELL': 0,
      'PSUB': 0,
    },
  },
  'B4':{
    'template': 'B4',
    'PIXEL_NX': 64,
    'PIXEL_NY': 32,
    'process': 'Modified w/ Gap',
    'pitch': '15',
    'split': 4,
    'setup':{
      'HV': 10,
      'PWELL': 0,
      'PSUB': 0,
    },
    'binning_noiseENC':[1.0, 0, 100],
    'binning_chargeENC':[50, 0, 5100],
    'binning_seedChargeENC':[50, 0, 3100],
    'noise':'/local/ITS3utils/PS202205/qa/B4/PS-B4_HV10-noisemap.root',
    'AC':{
      'title': 'AC amp.',
      'edge':[0, 20],
      'binning_noise':[5, 0, 400],
      'binning_charge':[100, 0, 15000],
      'calibration': 4.35,
      'result':{
        'seed_snr': 3,
        'seed_charge': 200,
        'cluster_charge': 1000,
        'file':'output/analysisCE65-AC_iter1-seed_PS-B4_HV10.root',
      }
    },
    'DC':{
      'title': 'DC amp.',
      'edge':[21, 41],
      'calibration': 3.70,
      'binning_noise':[5, 0, 400],
      'binning_charge':[100, 0, 15000],
      'result':{
        'seed_snr': 3,
        'seed_charge': 200,
        'cluster_charge': 1000,
        'file':'output/analysisCE65-DC_iter1-seed_PS-B4_HV10.root',
      }
    },
    'SF':{
      'title': 'SF',
      'edge':[42, 63],
      'calibration': 1.20,
      'binning_noise':[1, 0, 100],
      'binning_charge':[50, 0, 5000],
      'result':{
        'seed_snr': 3,
        'seed_charge': 200,
        'cluster_charge': 1000,
        'file':'output/analysisCE65-SF_iter1-seed_PS-B4_HV10.root',
      }
    },
  },
  'C4':{
    'template': 'B4',
    'PIXEL_NX': 64,
    'PIXEL_NY': 32,
    'process': 'Modified',
    'pitch': '15',
    'split': 4,
    'setup':{
      'HV': 10,
      'PWELL': 0,
      'PSUB': 0,
    },
    'binning_noiseENC':[1.0, 0, 100],
    'binning_chargeENC':[50, 0, 5100],
    'binning_seedChargeENC':[50, 0, 3100],
    'noise':'/local/ITS3utils/PS202205/qa/C4/PS-C4_HV10-noisemap.root',
    'AC':{
      'title': 'AC amp.',
      'edge':[0, 20],
      'binning_noise':[5, 0, 400],
      'binning_charge':[100, 0, 15000],
      # quick_spectra
      'calibration': 4.34,
      # # matrix 3x3
      # 'calibration': 4.25,
      'result':{
        'seed_snr': 3,
        'seed_charge': 200,
        'cluster_charge': 1000,
        'file':'output/analysisCE65-AC_iter1-seed_PS-C4_HV10.root',
      }
    },
    'DC':{
      'title': 'DC amp.',
      'edge':[21, 41],
      # quick_spectra
      'calibration': 3.61,
      # # matrix 3x3
      # 'calibration': 3.74,
      'binning_noise':[5, 0, 400],
      'binning_charge':[100, 0, 15000],
      'result':{
        'seed_snr': 3,
        'seed_charge': 200,
        'cluster_charge': 1000,
        'file':'output/analysisCE65-DC_iter1-seed_PS-C4_HV10.root',
      }
    },
    'SF':{
      'title': 'SF',
      'edge':[42, 63],
      # quick_spectra
      'calibration': 1.18,
      # # matrix 3x3
      # 'calibration': 1.18,
      'binning_noise':[1, 0, 100],
      'binning_charge':[50, 0, 5000],
      'result':{
        'seed_snr': 3,
        'seed_charge': 200,
        'cluster_charge': 1000,
        'file':'output/analysisCE65-SF_iter1-seed_PS-C4_HV10.root',
      }
    },
  },
  'D4':{
    'template': 'B4',
    'PIXEL_NX': 48,
    'PIXEL_NY': 32,
    'process': 'Standard',
    'pitch': '25',
    'split': 4,
    'setup':{
      'HV': 10,
      'PWELL': 0,
      'PSUB': 0,
    },
    'binning_noiseENC':[1.0, 0, 100],
    'binning_chargeENC':[50, 0, 5100],
    'binning_seedChargeENC':[50, 0, 3100],
    'noise':'/local/ITS3utils/PS202205/qa/D4/PS-D4_HV10-noisemap.root',
    'AC':{
      'title': 'AC amp.',
      'edge':[0, 15],
      'binning_noise':[5, 0, 400],
      'binning_charge':[100, 0, 15000],
      # quick_spectra
      'calibration': 4.44,
      # # matrix 3x3
      # 'calibration': 4.19,
      'result':{
        'seed_snr': 3,
        'seed_charge': 200,
        'cluster_charge': 1000,
        'file':'output/analysisCE65-AC_iter1-seed_PS-D4_HV10.root',
      }
    },
    'DC':{
      'title': 'DC amp.',
      'edge':[16, 31],
      # # quick_spectra
      # 'calibration': 4.59,
      # matrix 3x3 
      # 'calibration': 5.37,
      # matrix 5x5 --> Necessary due to massive charge sharing
      'calibration': 5.88,
      'binning_noise':[5, 0, 400],
      'binning_charge':[100, 0, 15000],
      'result':{
        'seed_snr': 3,
        'seed_charge': 200,
        'cluster_charge': 1000,
        'file':'output/analysisCE65-DC_iter1-seed_PS-D4_HV10.root',
      }
    },
    'SF':{
      'title': 'SF',
      'edge':[32, 47],
      # quick_spectra
      'calibration': 1.44,
      # # matrix 3x3
      # 'calibration': 1.44,
      'binning_noise':[1, 0, 100],
      'binning_charge':[50, 0, 5000],
      'result':{
        'seed_snr': 3,
        'seed_charge': 200,
        'cluster_charge': 1000,
        'file':'output/analysisCE65-SF_iter1-seed_PS-D4_HV10.root',
      }
    },
  }
}
def dict_update(config : dict, template : dict):
  configNew = deepcopy(template)
  for k, v in config.items():
    if(type(v) is dict):
      configNew[k] = dict_update(v, template[k])
    else:
      configNew[k] = deepcopy(v)
  return configNew
for chip in database['variant']:
  chipConfig = database[chip]
  if(chip == chipConfig.get('template')): continue
  database[chip] = dict_update(chipConfig, database[chipConfig['template']])

# Style
HIST_Y_SCALE = 1.4
color_vars = {}
color_fill = {}
plot_util.COLOR_SET = plot_util.COLOR_SET_ALICE
for i, sub in enumerate(database['submatrix']):
  color_vars[sub] = next(plot_util.COLOR)
marker_vars = {}
line_vars = {}
plot_util.MARKER_SET = plot_util.MARKER_SET_DEFAULT
for chips in database['variant']:
  marker_vars[chips] = next(plot_util.MARKER)
  line_vars[chips] = next(plot_util.LINE)

def plot_alice(painter : plot_util.Painter, x1 = 0.02, y1 = 0.03, x2 = 0.47, y2 = 0.17,
 size=0.04, pos='lt', test='beam'):
  """
  """
  if pos == 'rb' or pos == 'rt':
    align=32
  else:
    align=11
  if test == 'beam':
    label = painter.new_obj(plot_util.InitALICELabel(x1, y1, x2, y2, 
      align=12, type='#bf{ALICE ITS3-WP3} beam test #it{preliminary}', size=size, pos=pos))
    painter.add_text(label, '@CERN-PS May 2022, 10 GeV/#it{c} #pi^{-}', size=size*0.75, align=align)
  else:
    label = painter.new_obj(plot_util.InitALICELabel(x1, y1, x2, y2, 
      align=12, type='#bf{ALICE ITS3-WP3} #it{preliminary}', size=size, pos=pos))
  painter.add_text(label, datetime.datetime.now().strftime("Plotted on %d %b %Y"), size=size*0.75, align=align)
  label.Draw('same')
  return label

def draw_configuration(painter : plot_util.Painter, pave, sub='all', size=0.02):
  """
  """
  painter.add_text(pave, 'V_{sub} = V_{pwell} = 0 V', size=size)
  painter.add_text(pave, 'I_{mat} = 5 mA, I_{col} = 100 #muA, V_{offset} = 0.4 V', size=size)
  if(sub == 'all'):
    painter.add_text(pave, 'AC amp.: HV = 10 V, I_{pmos} = 1 #muA', size=size)
    painter.add_text(pave, 'DC amp.: I_{pmos} = 1 #muA', size=size)
    painter.add_text(pave, 'SF : I_{nmos} = 1 #muA, V_{reset} = 3.3 V', size=size)
  elif(sub == 'SF'):
    painter.add_text(pave, 'I_{nmos} = 1 #muA, V_{reset} = 3.3 V', size=size)

# Noise
def plot_noise(painter : plot_util.Painter, variant='B4'):
  """Noise distribution of each sub-matrix
  """
  painter.NextPad()
  painter.pageName = f'Noise - {variant}'
  chip_vars = database[variant]
  chip_setup = chip_vars['setup']
  noiseFile = ROOT.TFile.Open(chip_vars['noise'])
  hNoiseMap = painter.new_obj(noiseFile.Get('hnoisepl1').Clone(f'hNoiseMap_{variant}'))
  hNoiseMapENC = painter.new_obj(hNoiseMap.Clone(f'hNoiseMapENC_{variant}'))
  hNoiseMapENC.UseCurrentStyle()
  lgd = painter.new_obj(ROOT.TLegend(0.35, 0.55, 0.5, 0.7))
  histMax = 0
  for sub in database['submatrix']:
    vars = chip_vars[sub]
    hsub = painter.new_hist(f'hnoise_{chip}_{sub}','Noise distribution;Equivalent noise charge (e^{-});# Pixels',
      chip_vars['binning_noiseENC'])
    hsub.SetLineColor(color_vars[sub])
    hsub.SetLineWidth(2)
    hsub.SetMarkerStyle(marker_vars[chip])
    hsub.SetMarkerColor(color_vars[sub])
    lgd.AddEntry(hsub,vars['title'])
    for ix in range(vars['edge'][0], vars['edge'][1]+1):
      for iy in range(chip_vars['PIXEL_NY']):
        enc = hNoiseMap.GetBinContent(ix+1,iy+1) / vars['calibration']
        hsub.Fill(enc)
        hNoiseMapENC.SetBinContent(ix+1, iy+1, enc)
    if(hsub.GetMaximum() > histMax):
      histMax = hsub.GetMaximum()
    print("Noise in ADUs ->", hsub.GetMean()*vars['calibration'])
    painter.DrawHist(hsub, samePad=True)
    painter.save_obj(hsub)
  painter.primaryHist.GetYaxis().SetRangeUser(0, HIST_Y_SCALE * histMax)
  ROOT.gPad.SetLogy(False)
  # Legend
  lgd.Draw('same')
  # Text
  plot_alice(painter,test='lab')
  #ptxt = painter.draw_text(0.65, 0.65, 0.95, 0.92)
  ptxt = painter.draw_text(0.62, 0.60, 0.95, 0.93)
  painter.add_text(ptxt, f'Chip : CE65 (MLR1)')
  # painter.add_text(ptxt, f'Process : {chip_vars["process"]} (split {chip_vars["split"]})')
  painter.add_text(ptxt, f'Process : {chip_vars["process"]}')
  painter.add_text(ptxt, f'Pitch : {chip_vars["pitch"]} #mum')
  draw_configuration(painter, ptxt)
  #painter.add_text(ptxt,
    #f'HV-AC = {chip_setup["HV"]}, V_{{psub}} = {chip_setup["PSUB"]}, V_{{pwell}} = {chip_setup["PWELL"]} (V)',
    #size=0.03)
  ptxt.Draw('same')
  # Noise Map - ENC
  hNoiseMapENC.UseCurrentStyle()
  hNoiseMapENC.SetTitle('Noise map ENC;Column (pixel);Row (pixel);ENC (e^{-})')
  # New pad (overlap)
  padOverlap = painter.new_obj(ROOT.TPad(f'padOverlap_{variant}','',0.5,0.2, 0.93,0.6))
  padOverlap.SetFillStyle(4000) # will be transparent
  painter.canvas.cd()
  padOverlap.Draw()
  padOverlap.cd()
  hNoiseMapENC.Draw('colz')
  #painter.DrawHist(hNoiseMapENC, option='colz')
  ROOT.gPad.SetRightMargin(0.12)
  palette = painter.set_hist_palette(hNoiseMapENC)
  hNoiseMapENC.GetZaxis().SetRangeUser(0., 100.)
  padOverlap.Update()
  # Output
  painter.save_obj([hNoiseMap, hNoiseMapENC])
  painter.NextPage(f'NoiseDistribution_{variant}')

def plot_cluster_charge(painter : plot_util.Painter, optNorm=False, optSeed=False):
  """Cluster charge plot for all variants and sub-matrix
  """
  if(optSeed):
    painter.pageName = 'SeedCharge' + ('Norm' if optNorm else '')
    histNameSource = 'seedChargeAssociated'
    histNameCharge = 'hSeedChargeENC'
    histNameRaw = 'hSeedCharge'
    histXTitle = 'Seed charge'
    binningCharge = 'binning_seedChargeENC'
  else:
    painter.pageName = 'ClusterCharge' + ('Norm' if optNorm else '')
    histNameSource = 'clusterChargeAssociated'
    histNameCharge = 'hClusterChargeENC'
    histNameRaw = 'hClusterCharge'
    histXTitle = 'Cluster charge'
    binningCharge = 'binning_chargeENC'
  if optNorm:
    ROOT.gPad.SetTopMargin(0.05)
  histMax = 0
  snrMin = 10
  lgd = painter.new_obj(ROOT.TLegend(0.62, 0.2, 0.93, 0.45))
  qcdb = {'MPV':[]}
  for chip in database['variant']:
    chip_vars = database[chip]
    for sub in database['submatrix']:
      sub_vars = chip_vars[sub]
      corry_vars = sub_vars['result']
      resultFile = ROOT.TFile.Open(corry_vars['file'])
      dirAna = resultFile.Get('AnalysisCE65')
      dirAna = dirAna.Get('CE65_4')
      hChargeRaw = painter.new_obj(dirAna.Get(histNameSource).Clone(f'{histNameRaw}_{chip}_{sub}'))
      hChargeRaw.SetDirectory(0x0)
      histName = f'{histNameCharge}_{chip}_{sub}'
      if optNorm:
        histName = f'{histNameCharge}norm_{chip}_{sub}'
      hCharge = painter.new_hist(histName,
        f'{histXTitle};{histXTitle} '+'(e^{-});Entries;',
        chip_vars[binningCharge])
      hCharge.SetBit(ROOT.TH1.kIsNotW)
      hCharge.GetYaxis().SetMaxDigits(4)
      hCharge.SetLineColor(color_vars[sub])
      hCharge.SetLineStyle(line_vars[chip])
      hCharge.SetMarkerColor(color_vars[sub])
      hCharge.SetMarkerStyle(marker_vars[chip])
      hCharge.SetMarkerSize(1.5)
      hCharge.SetDirectory(0x0)
      # Scale with calibration
      scale = sub_vars['calibration']
      binmin = hChargeRaw.FindBin(chip_vars[binningCharge][1] * scale)
      binmax = hChargeRaw.FindBin(chip_vars[binningCharge][2] * scale)
      for ix in range(binmin, binmax):
        calibratedX = hChargeRaw.GetBinCenter(ix) / scale
        val = hChargeRaw.GetBinContent(ix)
        hCharge.Fill(calibratedX, val)
      hCharge.Sumw2()
      if(optNorm):
        hCharge.Scale(1/hCharge.Integral('width'))
        hCharge.SetYTitle(f'Entries (normalised)')
      else:
        hCharge.SetYTitle(f'Entries / {hCharge.GetBinWidth(1):.0f} ' + 'e^{-}')
      if(hCharge.GetMaximum() > histMax):
        histMax = hCharge.GetMaximum()
      if(corry_vars["seed_snr"] < snrMin):
        snrMin = corry_vars["seed_snr"]
      painter.hist_rebin(hChargeRaw, sub_vars['binning_charge'])
      # Draw
      painter.DrawHist(hCharge, samePad=True)
        # Fitting
      fit, result = painter.optimise_hist_langau(hCharge,
        color=color_vars[sub], style=line_vars[chip], notext=True)
        # Line at MPV
      mpshift = -0.22278298
      mpv = fit.GetParameter(1) - mpshift * fit.GetParameter(0)
      database[chip][sub]['result'][histNameRaw + '_MPV'] = mpv
      qcdb['MPV'].append(mpv)
      ROOT.gPad.Update()
      result.Print() # DEBUG
        # Legend
      lgd.AddEntry(hCharge, f'{chip_vars["process"]} {sub_vars["title"]}')
      resultFile.Close()
      painter.save_obj([hChargeRaw, hCharge, fit])
  # Pad style
  painter.primaryHist.GetYaxis().SetRangeUser(0, HIST_Y_SCALE * histMax)
  if(painter.showGrid): # FIXME: failed to show by painter itself
    ROOT.gPad.SetGrid(1,1)
  # Clustering
  pTxtClustering = painter.draw_text(0.62, 0.53, 0.93, 0.61)
  painter.add_text(pTxtClustering, f'Cluster window: 3#times3', size=0.03)
  painter.add_text(pTxtClustering, f'Seed charge > 100 e^{{-}}, SNR > {snrMin}', size=0.03)
  pTxtClustering.Draw('same')
  # Legend
  painter.draw_text(0.62, 0.45, 0.90, 0.48, 'Fitting by Landau-Gaussian function', size=0.03, font=42).Draw('same')
  lgd.SetTextSize(0.035)
  lgd.Draw('same')
  plot_alice(painter)
  ptxt = painter.draw_text(0.62, 0.65, 0.95, 0.92)
  painter.add_text(ptxt, f'Chip : CE65 (MLR1)')
  painter.add_text(ptxt, f'Process : std/mod_gap (split {chip_vars["split"]})')
  chip_setup = chip_vars['setup']
  draw_configuration(painter, ptxt)
  ptxt.Draw('same')
  if optSeed:
    return qcdb
  painter.NextPage(f'{painter.pageName}_' + '_'.join(database['variant']))

def plot_seed_charge(painter : plot_util.Painter, optNorm=False):
  qcdb = plot_cluster_charge(painter, optSeed=True, optNorm=optNorm)
  mpvCluster = []
  # Cluster charge MPV
  for chip in database['variant']:
    chip_vars = database[chip]
    for sub in database['submatrix']:
      sub_vars = chip_vars[sub]
      mpvCluster.append(sub_vars['result']['hClusterCharge_MPV'])
  # Band of cluster charge MPV
  xmin = min(mpvCluster)
  xmax = max(mpvCluster)
  band = painter.draw_band(xmin, xmax)
  lgd = painter.new_obj(ROOT.TLegend(0.35, 0.65, 0.55, 0.70))
  lgd.AddEntry(band, 'MPV of cluster charge')
  lgd.Draw('same')
  #
  painter.pageName = 'SeedCharge' + ('Norm' if optNorm else '')
  painter.NextPage(f'{painter.pageName}_' + '_'.join(database['variant']))
  return qcdb

def plot_cluster_shape(painter : plot_util.Painter):
  """Cluster distribution in a window around seed
  """
  sub = 'SF'
  for chip in database['variant']:
    lgd = painter.new_legend(0.62, 0.60, 0.82, 0.65)
    painter.pageName = f'ClusterShape - {chip}_{sub}'
    chip_vars = database[chip]
    chip_setup = chip_vars['setup']
    sub_vars = chip_vars[sub]
    corry_vars = sub_vars['result']
    resultFile = ROOT.TFile.Open(corry_vars['file'])
    dirAna = resultFile.Get('AnalysisCE65')
    dirAna = dirAna.Get('CE65_4')
    dirCluster = dirAna.Get('cluster')
    hRatio = painter.new_obj(dirCluster.Get("clusterShape_ChargeRatio_Accumulated").Clone(f'hClusterChargeRatio_{chip}_{sub}'))
    hRatio.UseCurrentStyle()
    hRatio.SetYTitle('#it{R}_{n} (accumulated charge ratio)')
    hRatio.SetXTitle('Number of selected pixels by decreasing charge')
    hRatio.RebinY(int(0.02 // hRatio.GetYaxis().GetBinWidth(1) ))
    hRatio.GetXaxis().SetRangeUser(0,10)
    hRatio.GetYaxis().SetRangeUser(0,1.2)
    hPx = painter.new_obj(hRatio.ProfileX())
    hPx.SetLineColor(ROOT.kBlack)
    hPx.SetLineStyle(ROOT.kDashed) # dash-dot
    hPx.SetLineWidth(4)
    hPx.SetMarkerColor(ROOT.kBlack)
    hPx.SetMarkerStyle(plot_util.kFullStar)
    hPx.SetMarkerSize(4)
    painter.normalise_profile_y(hRatio)
    painter.NextPad()
    hRatio.Draw('colz')
    #painter.DrawHist(hRatio, option='colz', optNormY=True)
    # Palette
    ROOT.gPad.SetRightMargin(0.15)
    #painter.set_hist_palette(hRatio)
    hRatio.SetZTitle('Entries (normalised)')
    hPx.Draw('same')
    # Legend
    lgd.AddEntry(hPx, '<#it{R}_{n}>')
    lgd.Draw('same')
    painter.draw_text(0.62, 0.53, 0.82, 0.58, 'Cluster window : 3#times3',size=0.03, font=42).Draw('same')
    # Label
    plot_alice(painter, 0.02, 0.03, 0.35, 0.15, size=0.03, pos='rb')
    # Line at Y/Rn=1
    painter.canvas.Update()
    line = painter.new_obj(ROOT.TLine(ROOT.gPad.GetUxmin(), 1., ROOT.gPad.GetUxmax(), 1.0))
    line.SetLineWidth(3)
    line.Draw('same')
    # Text info
    ptxt = painter.draw_text(0.62, 0.29, 0.85, 0.50)
    painter.add_text(ptxt, f'Chip : CE65 (MLR1)', size=0.03)
    painter.add_text(ptxt, f'Process : {chip_vars["process"]} (split {chip_vars["split"]})', size=0.03)
    painter.add_text(ptxt,f'Sub-matrix : {sub}', size=0.03)
    draw_configuration(painter, ptxt, sub='SF', size=0.015)
    ptxt.Draw('same')
    # Output
    painter.save_obj(hRatio)
    painter.NextPage(f'ClusterChargeRatioRn_{chip}')
  # Draw
def plot_tracking_residual(painter : plot_util.Painter, axis='X'):
  """
  """
  histMax = 0
  painter.pageName = f'Tracking residual - {axis}'
  histNameSource = f'residuals{axis}'
  if axis == 'X':
    histXTitle = '#it{x}_{track} - #it{x}_{cluster} (#mum)'
  elif axis == 'Y':
    histXTitle = '#it{y}_{track} - #it{y}_{cluster} (#mum)'
  else:
    print(f'[X] Error - UNKNOWN {axis = }')
  lgd = painter.new_obj(ROOT.TLegend(0.57, 0.28, 0.90, 0.58))
  for chip in database['variant']:
    chip_vars = database[chip]
    for sub in database['submatrix']:
      sub_vars = chip_vars[sub]
      corry_vars = sub_vars['result']
      resultFile = ROOT.TFile.Open(corry_vars['file'])
      dirAna = resultFile.Get('AnalysisCE65')
      dirAna = dirAna.Get('CE65_4')
      dirTracking = dirAna.Get('global_residuals')
      hTrack = painter.new_obj(dirTracking.Get(histNameSource).Clone(f'{histNameSource}_{chip}_{sub}'))
      hTrack.UseCurrentStyle()
      hTrack.SetDirectory(0x0)
      resultFile.Close()
      # Norm
      hTrack.Rebin(int(1. / hTrack.GetBinWidth(1)))
      hTrack.SetYTitle(f'Entriess / {hTrack.GetBinWidth(1)} #mum')
      hTrack.Scale(1/hTrack.Integral('width'))
      if(hTrack.GetMaximum() > histMax):
        histMax = hTrack.GetMaximum()
      # Style
      hTrack.SetXTitle(histXTitle)
      hTrack.SetYTitle(f'Entries (normalised)')
      hTrack.SetLineColor(color_vars[sub])
      hTrack.SetLineStyle(line_vars[chip])
      hTrack.SetMarkerColor(color_vars[sub])
      hTrack.SetMarkerStyle(marker_vars[chip])
      hTrack.SetMarkerSize(1.5)
      painter.DrawHist(hTrack, samePad=True)
      # Fitting
      fit, result = painter.optimise_hist_gaus(hTrack,
        color=color_vars[sub], style=line_vars[chip], notext=True)
      result.Print() # DEBUG
      lgd.AddEntry(hTrack, f'{chip_vars["process"]} {sub_vars["title"]}'
        f' (#sigma = {fit.GetParameter(2):.1f} #mum)')
      painter.save_obj(hTrack)
      # End - sub
    # End - chip
  painter.primaryHist.GetXaxis().SetRangeUser(-30., 60)
  painter.primaryHist.GetYaxis().SetRangeUser(0, HIST_Y_SCALE * histMax)
  # Text
  painter.draw_text(0.57, 0.59, 0.90, 0.62, 'Fitting by Gaussian function', size=0.03, font=42).Draw('same')
  lgd.SetTextSize(0.035)
  lgd.Draw('same')
  plot_alice(painter)
  ptxt = painter.draw_text(0.62, 0.65, 0.95, 0.93)
  painter.add_text(ptxt, f'Chip : CE65 (MLR1)')
  painter.add_text(ptxt, f'Process : std/mod_gap (split {chip_vars["split"]})')
  chip_setup = chip_vars['setup']
  draw_configuration(painter, ptxt)
  ptxt.Draw('same')
  painter.NextPage(f'TrackingResiduals{axis}_' + '_'.join(database['variant']))

def plot_preliminary(prefix='plots/preliminary', all=False, **kwargs):
  plot_util.ALICEStyle()
  outputDir = os.path.dirname(prefix)
  if(all):
    os.system(f'mkdir -p {outputDir}/plot')
  painter = plot_util.Painter(
    printer=f'{prefix}.pdf',
    winX=1600, winY=1000, nx=1, ny=1,
    showGrid=True, printAll=all, printDir=f'{outputDir}/plot', showPageNo=True,
    saveROOT=True)
  painter.PrintCover('CE65 Preliminary')
  # plot_noise(painter,'B4')
  plot_noise(painter,'A4')
  plot_noise(painter,'B4')
  plot_noise(painter,'C4')
  plot_noise(painter,'D4')
  # plot_cluster_charge(painter)
  # plot_cluster_charge(painter, optNorm=True)
  # plot_seed_charge(painter)
  # plot_seed_charge(painter, optNorm=True)
  # plot_cluster_shape(painter)
  # plot_tracking_residual(painter,axis='X')
  # plot_tracking_residual(painter,axis='Y')
  painter.PrintBackCover('-')

if __name__ == '__main__':
  parser = argparse.ArgumentParser('Preliminary pltos for multiple variants and sub-matrix')
  parser.add_argument('-p','--prefix',default='plots/preliminary', help='Prefix of output fils, generate files .pdf .root and plot/')
  parser.add_argument('-a','--all', default=False, action='store_true', help='Option to save all figures in .eps and .pdf individually')
  args, unknown = parser.parse_known_args()
  if unknown:
    print(f'[+] Unknown aruments : {unknown}')
  plot_preliminary(args.prefix, args.all)
  #pprint(database)
