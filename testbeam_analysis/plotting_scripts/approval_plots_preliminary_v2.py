#!/bin/env python3

# Plot preliminary results for approval
# Slightly altered for v2

import argparse
import os
import plot_util
import ROOT
from copy import deepcopy
from pprint import pprint
import datetime

# Binning: width, min, max
database = {
  'pitches': ['225', '15'],
  # 'variant': ['GAP225SQ', 'GAP15SQ', 'STD225SQ', 'STD15SQ'],
  'variant': ['GAP225SQ', 'STD225SQ'],
  'GAP225SQ':{
    'template': 'GAP225SQ',
    'PIXEL_NX': 48,
    'PIXEL_NY': 24,
    'process': 'Modified w/ Gap',
    'split': 4,
    'setup':{
      'HV': 10,
      'PWELL': 0,
      'PSUB': 0,
    },
    'binning_noiseENC':[1.0, 0, 100],
    'binning_chargeENC':[50, 0, 5100],
    'binning_seedChargeENC':[50, 0, 3100],
    '225':{
      'title': 'AC amp.',
      'pitch': '22.5',
      'edge':[0, 47],
      'binning_noise':[5, 0, 400],
      'binning_charge':[100, 0, 15000],
      'calibration': 4.29,
      'noise':'output/SPS-GAP225SQ_HV10-noisemap.root',
      'result':{
        'seed_snr': 3,
        'seed_charge': 435,
        'cluster_charge': 435,
        'file':'output/analysis_SPS-GAP225SQ_173004514_240424004519_seedthr400_nbh100_snr3_window.root',
      }
    },
    '15':{
      'title': 'AC amp.',
      'pitch': '15',
      'edge':[0, 47],
      'binning_noise':[5, 0, 400],
      'binning_charge':[100, 0, 15000],
      'calibration': 4.22,
      'noise':'output/SPS-GAP15SQ_HV10-noisemap.root',
      'result':{
        'seed_snr': 3,
        'seed_charge': 435,
        'cluster_charge': 435,
        'file':'output/analysis_SPS-GAP15SQ_164222116_240419010802_seedthr400_nbh100_snr3_window.root',
      }
    },
  },
  'STD225SQ':{
    'template': 'GAP225SQ',
    'process': 'Standard',
    'setup':{
      'HV': 10,
      'PWELL': 0,
      'PSUB': 0,
    },
    '225':{
      'title': 'AC amp.',
      'pitch': '22.5',
      'calibration': 4.25,
      'noise':'output/SPS-STD225SQ_HV10-noisemap.root',
      'result':{
        'seed_snr': 3,
        'seed_charge': 435,
        'cluster_charge': 435,
        'file':'output/analysis_SPS-STD225SQ_165100540_240419100546_seedthr400_nbh100_snr3_window.root',
      }
    },
    '15':{
      'title': 'AC amp.',
      'pitch': '15',
      'calibration': 4.15,
      'noise':'output/SPS-STD15SQ_HV10-noisemap.root',
      'result':{
        'seed_snr': 3,
        'seed_charge': 435,
        'cluster_charge': 435,
        'file':'output/analysis_SPS-STD15SQ_165232707_240419232713_seedthr400_nbh100_snr3_window.root',
      }
    },
  },
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

# # Load colors from okabe_ito file
# with open("okabe_ito.json", 'r') as file:
#     color_dict = json.load(file)

# Permute dict to use desired colours in order
# permutation_order = [
# shuffled_dict = {key: data_dict[key] for key in np.array(list(keys))[permute]}

# Choose colours for the different "pitches"
pitch_colors = {"225" : 4, "18" : 5, "15" : 6}
for i, pit in enumerate(database['pitches']):
  # color_vars[pit] = next(plot_util.COLOR)
  color_vars[pit] = plot_util.COLOR_SET_ALICE[pitch_colors[pit]]
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
    painter.add_text(label, '@CERN-SPS April 2024, 120 GeV/#it{c} #pi^{-}', size=size*0.75, align=align)
  else:
    label = painter.new_obj(plot_util.InitALICELabel(x1, y1, x2, y2, 
      align=12, type='#bf{ALICE ITS3-WP3} #it{preliminary}', size=size, pos=pos))
  painter.add_text(label, datetime.datetime.now().strftime("Plotted on %d %b %Y"), size=size*0.75, align=align)
  label.Draw('same')
  return label

def draw_configuration(painter : plot_util.Painter, pave, sub='all', size=0.03):
  """
  """
  painter.add_text(pave, 'V_{psub} = V_{pwell} = 0 V        T = 20 #circC', size=size)
  # painter.add_text(pave, 'V_{psub} = V_{pwell} = 0 V        T = 20 #scale[0.99]{#circ}C', size=size)
  painter.add_text(pave, 'I_{mat} = 3 mA, I_{col} = 200 #muA, V_{offset} = 1 V', size=size)
  if(sub == 'all'):
    painter.add_text(pave, 'AC amp.: HV = 10 V, I_{pmos} = 100 #muA', size=size)
    # painter.add_text(pave, 'DC amp.: I_{pmos} = 100 #muA', size=size)
    # painter.add_text(pave, 'SF : I_{nmos} = 1 #muA, V_{reset} = 3.3 V', size=size)
  elif(sub == 'SF'):
    # technically deprecated since not present for v2
    painter.add_text(pave, 'I_{nmos} = 1 #muA, V_{reset} = 3.3 V', size=size)

# Noise
def plot_noise(painter : plot_util.Painter, variant='GAP225SQ', pitch='225'):
  """Noise distribution of each matrix
  """
  painter.NextPad()
  painter.pageName = f'Noise - {variant}'
  chip_vars = database[variant]
  chip_setup = chip_vars['setup']
  noiseFile = ROOT.TFile.Open(chip_vars[pitch]['noise'])
  hNoiseMap = painter.new_obj(noiseFile.Get('hnoisepl1').Clone(f'hNoiseMap_{variant}'))
  hNoiseMapENC = painter.new_obj(hNoiseMap.Clone(f'hNoiseMapENC_{variant}'))
  hNoiseMapENC.UseCurrentStyle()
  # lgd = painter.new_obj(ROOT.TLegend(0.35, 0.55, 0.5, 0.7))
  lgd = painter.new_obj(ROOT.TLegend(1.35, 0.55, 1.5, 0.7))
  histMax = 0
  for pit in database['pitches']:
    # Plot only a single pitch
    if(pit!=pitch): continue 
    vars = chip_vars[pit]
    # hsub = painter.new_hist(f'hnoise_{chip}_{sub}','Noise distribution;Equivalent noise charge (e^{-});# Pixels',
    hsub = painter.new_hist(f'hnoise_{chip}_{pit}','Noise distribution;Equivalent noise charge (e^{-});# Pixels',
      chip_vars['binning_noiseENC'])
    hsub.SetLineColor(color_vars[pit])
    hsub.SetLineWidth(2)
    hsub.SetMarkerStyle(marker_vars[chip])
    hsub.SetMarkerColor(color_vars[pit])
    lgd.AddEntry(hsub,vars['title'])
    for ix in range(vars['edge'][0], vars['edge'][1]+1):
      for iy in range(chip_vars['PIXEL_NY']):
        enc = hNoiseMap.GetBinContent(ix+1,iy+1) / vars['calibration']
        hsub.Fill(enc)
        hNoiseMapENC.SetBinContent(ix+1, iy+1, enc)
    if(hsub.GetMaximum() > histMax):
      histMax = hsub.GetMaximum()
    painter.DrawHist(hsub, samePad=True)
    painter.save_obj(hsub)
  painter.primaryHist.GetYaxis().SetRangeUser(0, HIST_Y_SCALE * histMax)
  ROOT.gPad.SetLogy(False)
  # Legend
  lgd.Draw('same')
  # Text
  plot_alice(painter,test='lab')
  # ptxt = painter.draw_text(0.65, 0.65, 0.95, 0.92)

  # Text info
  ptxt = painter.draw_text(0.62, 0.65, 0.95, 0.93)
  painter.add_text(ptxt, f'Chip : CE-65v2 (ER1)')
  painter.add_text(ptxt, f'Process : {chip_vars["process"]}')
  pitch_string = eval(f'chip_vars["{pitch}"]["pitch"]')
  painter.add_text(ptxt, f'Pitch : {pitch_string} #mum')
  chip_setup = chip_vars['setup']
  draw_configuration(painter, ptxt)
  ptxt.Draw('same')

  #painter.add_text(ptxt,
    #f'HV-AC = {chip_setup["HV"]}, V_{{psub}} = {chip_setup["PSUB"]}, V_{{pwell}} = {chip_setup["PWELL"]} (V)',
    #size=0.03)
  # ptxt.Draw('same')
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
  ROOT.gPad.Update()
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
    for pit in database['pitches']:
      pit_vars = chip_vars[pit]
      corry_vars = pit_vars['result']
      resultFile = ROOT.TFile.Open(corry_vars['file'])
      dirAna = resultFile.Get('AnalysisCE65')
      dirAna = dirAna.Get('CE65_6')
      hChargeRaw = painter.new_obj(dirAna.Get(histNameSource).Clone(f'{histNameRaw}_{chip}_{pit}'))
      hChargeRaw.SetDirectory(0x0)
      histName = f'{histNameCharge}_{chip}_{pit}'
      if optNorm:
        histName = f'{histNameCharge}norm_{chip}_{pit}'
      hCharge = painter.new_hist(histName,
        f'{histXTitle};{histXTitle} '+'(e^{-});Entries;',
        chip_vars[binningCharge])
      hCharge.SetBit(ROOT.TH1.kIsNotW)
      hCharge.GetYaxis().SetMaxDigits(4)
      hCharge.SetLineColor(color_vars[pit])
      hCharge.SetLineStyle(line_vars[chip])
      hCharge.SetMarkerColor(color_vars[pit])
      hCharge.SetMarkerStyle(marker_vars[chip])
      hCharge.SetMarkerSize(1.5)
      hCharge.SetDirectory(0x0)
      # Scale with calibration
      scale = pit_vars['calibration']
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
      painter.hist_rebin(hChargeRaw, pit_vars['binning_charge'])
      # Draw
      painter.DrawHist(hCharge, samePad=True)
        # Fitting
      fit, result = painter.optimise_hist_langau(hCharge,
        color=color_vars[pit], style=line_vars[chip], notext=True)
        # Line at MPV
      mpshift = -0.22278298
      mpv = fit.GetParameter(1) - mpshift * fit.GetParameter(0)
      database[chip][pit]['result'][histNameRaw + '_MPV'] = mpv
      print("MPV = ", mpv)
      qcdb['MPV'].append(mpv)
      ROOT.gPad.Update()
      result.Print() # DEBUG
        # Legend
      lgd.AddEntry(hCharge, f'{chip_vars["process"]} ({pit_vars["pitch"]} #mum)')
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

  # ptxt = painter.draw_text(0.62, 0.65, 0.95, 0.93)
  ptxt = painter.draw_text(0.57, 0.64, 0.90, 0.91)
  painter.add_text(ptxt, f'Chip : CE-65v2 (ER1)')
  painter.add_text(ptxt, f'Process : Standard/Modified w/ Gap')
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
    for pit in database['pitches']:
      pit_vars = chip_vars[pit]
      mpvCluster.append(pit_vars['result']['hClusterCharge_MPV'])
  # Band of cluster charge MPV
  xmin = min(mpvCluster)
  xmax = max(mpvCluster)
  band = painter.draw_band(xmin, xmax)
  lgd = painter.new_obj(ROOT.TLegend(0.35, 0.65, 0.55, 0.70))
  # lgd = painter.new_obj(ROOT.TLegend(1.35, 0.65, 1.55, 0.70))
  lgd.AddEntry(band, 'MPV of cluster charge')
  lgd.Draw('same')
  #
  painter.pageName = 'SeedCharge' + ('Norm' if optNorm else '')
  painter.NextPage(f'{painter.pageName}_' + '_'.join(database['variant']))
  return qcdb

def plot_cluster_shape(painter : plot_util.Painter, pitch='225'):
  """Cluster distribution in a window around seed
  """
  pit = pitch
  for chip in database['variant']:
    lgd = painter.new_legend(0.55, 0.38, 0.82, 0.43)
    # lgd = painter.new_legend(1.62, 0.60, 1.82, 0.65)
    painter.pageName = f'ClusterShape - {chip}_{pit}'
    chip_vars = database[chip]
    chip_setup = chip_vars['setup']
    pit_vars = chip_vars[pit]
    corry_vars = pit_vars['result']
    resultFile = ROOT.TFile.Open(corry_vars['file'])
    dirAna = resultFile.Get('AnalysisCE65')
    dirAna = dirAna.Get('CE65_6')
    dirCluster = dirAna.Get('cluster')
    hRatio = painter.new_obj(dirCluster.Get("clusterShape_ChargeRatio_Accumulated").Clone(f'hClusterChargeRatio_{chip}_{pit}'))
    hRatio.UseCurrentStyle()
    hRatio.SetYTitle('#it{R}_{n} (#bf{#scale[2.5]{#lower[0.35]{#Sigma}}} #it{q}_{n} charge ratio)')
    hRatio.SetXTitle('Number of pixels in cluster')
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
    lgd.AddEntry(hPx, '<#it{R}_{n}> (average)')
    lgd.Draw('same')
    pTxtClustering = painter.draw_text(0.55, 0.28, 0.82, 0.36)
    painter.add_text(pTxtClustering, f'Cluster window: 3#times3', size=0.03)
    painter.add_text(pTxtClustering, f'Seed charge > 100 e^{{-}}, SNR > 3', size=0.03)
    pTxtClustering.Draw('same')
    # Label
    plot_alice(painter, 0.08, 0.03, 0.40, 0.15, size=0.034, pos='rb')
    # Line at Y/Rn=1
    painter.canvas.Update()
    line = painter.new_obj(ROOT.TLine(ROOT.gPad.GetUxmin(), 1., ROOT.gPad.GetUxmax(), 1.0))
    line.SetLineWidth(3)
    line.Draw('same')

    # Text info
    ptxt = painter.draw_text(0.55, 0.45, 0.85, 0.72)
    painter.add_text(ptxt, f'Chip : CE-65v2 (ER1)')
    painter.add_text(ptxt, f'Process : {chip_vars["process"]}')
    pitch_string = eval(f'chip_vars["{pitch}"]["pitch"]')
    painter.add_text(ptxt, f'Pitch : {pitch_string} #mum')
    chip_setup = chip_vars['setup']
    draw_configuration(painter, ptxt)
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
  lgd = painter.new_obj(ROOT.TLegend(0.57, 0.18, 0.90, 0.58))
  for chip in database['variant']:
    chip_vars = database[chip]
    for pit in database['pitches']:
      pit_vars = chip_vars[pit]
      corry_vars = pit_vars['result']
      resultFile = ROOT.TFile.Open(corry_vars['file'])
      dirAna = resultFile.Get('AnalysisCE65')
      dirAna = dirAna.Get('CE65_6')
      dirTracking = dirAna.Get('global_residuals')
      hTrack = painter.new_obj(dirTracking.Get(histNameSource).Clone(f'{histNameSource}_{chip}_{pit}'))
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
      hTrack.SetLineColor(color_vars[pit])
      hTrack.SetLineStyle(line_vars[chip])
      hTrack.SetMarkerColor(color_vars[pit])
      hTrack.SetMarkerStyle(marker_vars[chip])
      hTrack.SetMarkerSize(1.5)
      painter.DrawHist(hTrack, samePad=True)
      # Fitting
      fit, result = painter.optimise_hist_gaus(hTrack,
        color=color_vars[pit], style=line_vars[chip], notext=True)
      result.Print() # DEBUG
      lgd.AddEntry(hTrack, f'{chip_vars["process"]} ({pit_vars["pitch"]} #mum)')
        # f' (#sigma = {fit.GetParameter(2):.1f} #mum)')
      pit_entry = lgd.AddEntry(0, f'#sigma = {fit.GetParameter(2):.1f} #mum', '')
      pit_entry.SetMarkerColor(0)  # Set marker color to transparent
      pit_entry.SetLineColor(0)    # Set line color to transparent
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

  # ptxt = painter.draw_text(0.62, 0.65, 0.95, 0.93)
  ptxt = painter.draw_text(0.57, 0.64, 0.90, 0.91)
  painter.add_text(ptxt, f'Chip : CE-65v2 (ER1)')
  painter.add_text(ptxt, f'Process : Standard/Modified w/ Gap')
  chip_setup = chip_vars['setup']
  draw_configuration(painter, ptxt)

  ptxt.Draw('same')
  painter.NextPage(f'TrackingResiduals{axis}_' + '_'.join(database['variant']))

def plot_preliminary(prefix='output/preliminary', all=False, **kwargs):
  plot_util.ALICEStyle()
  outputDir = os.path.dirname(prefix)
  if(all):
    os.system(f'mkdir -p {outputDir}/plot')
  painter = plot_util.Painter(
    printer=f'{prefix}.pdf',
    winX=1600, winY=1000, nx=1, ny=1,
    showGrid=True, printAll=all, printDir=f'{outputDir}/plot', showPageNo=True,
    saveROOT=True)
  painter.PrintCover('CE-65v2 Preliminary')
  plot_noise(painter,'GAP225SQ', '225')
  plot_noise(painter,'GAP225SQ', '15')
  plot_noise(painter,'STD225SQ', '225')
  plot_noise(painter,'STD225SQ', '15')
  plot_cluster_charge(painter)
  plot_cluster_charge(painter, optNorm=True)
  plot_seed_charge(painter)
  plot_seed_charge(painter, optNorm=True)
  plot_cluster_shape(painter, '225')
  plot_tracking_residual(painter,axis='X')
  plot_tracking_residual(painter,axis='Y')
  painter.PrintBackCover('-')

if __name__ == '__main__':
  parser = argparse.ArgumentParser('Preliminary pltos for multiple variants and sub-matrix')
  parser.add_argument('-p','--prefix',default='output/preliminary_v2', help='Prefix of output fils, generate files .pdf .root and plot/')
  parser.add_argument('-a','--all', default=False, action='store_true', help='Option to save all figures in .eps and .pdf individually')
  args, unknown = parser.parse_known_args()
  if unknown:
    print(f'[+] Unknown aruments : {unknown}')
  plot_preliminary(args.prefix, args.all)
  #pprint(database)
