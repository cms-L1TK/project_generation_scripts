#!/usr/bin/env python

from TrackletGraph import MemModule, ProcModule, TrackletGraph
from ROOT import TH1I, TCanvas, gPad
import argparse

parser = argparse.ArgumentParser(description="Script to analyze the Tracklet graph")
parser.add_argument('-p','--procconfig', type=str, default="processingmodules.dat",
                    help="Name of the configuration file for processing modules")
parser.add_argument('-m','--memconfig', type=str, default="memorymodules.dat",
                    help="Name of the configuration file for memory modules")
parser.add_argument('-w','--wireconfig', type=str, default="wires.dat",
                    help="Name of the configuration file for wiring")

args = parser.parse_args()

# Instantiate a TrackletGraph object from the configuration files
tracklet = TrackletGraph.from_configs(args.procconfig, args.memconfig,
                                      args.wireconfig)

# Get processing module lists
proc_list = tracklet.get_all_proc_modules()

# Histograms to store the numbers of input and output memories
nbins_i= 45
xlow_i = 0.5
# number of inputs
h_proc_input_num = TH1I("proc_input_num","Number of input memories per processing module", nbins_i, xlow_i, xlow_i+nbins_i)
# VMRouter
h_proc_input_num_vmr = TH1I("proc_input_num_vmr","Number of input memories per VMRouter", 10, xlow_i, xlow_i+10)
# TrackletEngine
h_proc_input_num_te = TH1I("proc_input_num_te","Number of input memories per TrackletEngine", 3, xlow_i, xlow_i+3)
# TrackletCalculator
h_proc_input_num_tc = TH1I("proc_input_num_tc","Number of input memories per TrackletCalculator", 40, xlow_i, xlow_i+40)
# ProjectionRouter
h_proc_input_num_pr = TH1I("proc_input_num_pr","Number of input memories per ProjectionRouter", 25, xlow_i, xlow_i+25)
# MatchEngine
h_proc_input_num_me = TH1I("proc_input_num_me","Number of input memories per MatchEngine", 3, xlow_i, xlow_i+3)
# MatchCalculator
h_proc_input_num_mc = TH1I("proc_input_num_mc","Number of input memories per MatchCalculator", 12, xlow_i, xlow_i+12)
# FitTrack
h_proc_input_num_ft = TH1I("proc_input_num_ft","Number of input memories per FitTrack", 50, xlow_i, xlow_i+50)
# PurgeDuplicate
h_proc_input_num_pd = TH1I("proc_input_num_pd","Number of input memories per PurgeDuplicate", 8, xlow_i, xlow_i+8)

nbins_o= 50
xlow_o = 0.5
# number of outputs
h_proc_output_num = TH1I("proc_output_num","Number of output memories per processing module", nbins_o, xlow_o, xlow_o+nbins_o)
# VMRouter
h_proc_output_num_vmr = TH1I("proc_output_num_vmr","Number of output memories per VMRouter", nbins_o, xlow_o, xlow_o+nbins_o)
# TrackletEngine
h_proc_output_num_te = TH1I("proc_output_num_te","Number of output memories per TrackletEngine", 2, xlow_o, xlow_o+2)
# TrackletCalculator
h_proc_output_num_tc = TH1I("proc_output_num_tc","Number of output memories per TrackletCalculator", 30, xlow_o, xlow_o+30)
# ProjectionRouter
h_proc_output_num_pr = TH1I("proc_output_num_pr","Number of output memories per ProjectionRouter", 10, xlow_o, xlow_o+10)
# MatchEngine
h_proc_output_num_me = TH1I("proc_output_num_me","Number of output memories per MatchEngine", 2, xlow_o, xlow_o+2)
# MatchCalculator
h_proc_output_num_mc = TH1I("proc_output_num_mc","Number of output memories per MatchCalculator", 10, xlow_o, xlow_o+10)
# FitTrack
h_proc_output_num_ft = TH1I("proc_output_num_ft","Number of output memories per FitTrack", 2, xlow_o, xlow_o+2)
# PurgeDuplicate
h_proc_output_num_pd = TH1I("proc_output_num_pd","Number of output memories per PurgeDuplicate", 2, xlow_o, xlow_o+2)

# Loop over the list of processing modules
for aProcMod in proc_list:
    ninputs = len(aProcMod.upstreams)
    noutputs = len(aProcMod.downstreams)

    # Fill the histograms
    h_proc_input_num.Fill(ninputs)
    h_proc_output_num.Fill(noutputs)

    moduletype = aProcMod.mtype
    if moduletype == 'VMRouter':
        h_proc_input_num_vmr.Fill(ninputs)
        h_proc_output_num_vmr.Fill(noutputs)
    elif moduletype == 'TrackletEngine':
        h_proc_input_num_te.Fill(ninputs)
        h_proc_output_num_te.Fill(noutputs)
    elif moduletype == 'TrackletCalculator':
        h_proc_input_num_tc.Fill(ninputs)
        h_proc_output_num_tc.Fill(noutputs)
    elif moduletype == 'ProjectionRouter':
        h_proc_input_num_pr.Fill(ninputs)
        h_proc_output_num_pr.Fill(noutputs)
    elif moduletype == 'MatchEngine':
        h_proc_input_num_me.Fill(ninputs)
        h_proc_output_num_me.Fill(noutputs)
    elif moduletype in ['MatchCalculator','DiskMatchCalculator']:
        h_proc_input_num_mc.Fill(ninputs)
        h_proc_output_num_mc.Fill(noutputs)
    elif moduletype == 'FitTrack':
        h_proc_input_num_ft.Fill(ninputs)
        h_proc_output_num_ft.Fill(noutputs)
    elif moduletype == 'PurgeDuplicate':
        h_proc_input_num_pd.Fill(ninputs)
        h_proc_output_num_pd.Fill(noutputs)

# Plot the histograms
canvas = TCanvas()

h_proc_input_num_vmr.Draw("HIST")
canvas.SaveAs("proc_input_num_vmr.pdf")
h_proc_output_num_vmr.Draw("HIST")
canvas.SaveAs("proc_output_num_vmr.pdf")

h_proc_input_num_te.Draw("HIST")
canvas.SaveAs("proc_input_num_te.pdf")
h_proc_output_num_te.Draw("HIST")
canvas.SaveAs("proc_output_num_te.pdf")

h_proc_input_num_tc.Draw("HIST")
canvas.SaveAs("proc_input_num_tc.pdf")
h_proc_output_num_tc.Draw("HIST")
canvas.SaveAs("proc_output_num_tc.pdf")

h_proc_input_num_pr.Draw("HIST")
canvas.SaveAs("proc_input_num_pr.pdf")
h_proc_output_num_pr.Draw("HIST")
canvas.SaveAs("proc_output_num_pr.pdf")

h_proc_input_num_me.Draw("HIST")
canvas.SaveAs("proc_input_num_me.pdf")
h_proc_output_num_me.Draw("HIST")
canvas.SaveAs("proc_output_num_me.pdf")

h_proc_input_num_mc.Draw("HIST")
canvas.SaveAs("proc_input_num_mc.pdf")
h_proc_output_num_mc.Draw("HIST")
canvas.SaveAs("proc_output_num_mc.pdf")

h_proc_input_num_ft.Draw("HIST")
canvas.SaveAs("proc_input_num_ft.pdf")
h_proc_output_num_ft.Draw("HIST")
canvas.SaveAs("proc_output_num_ft.pdf")

h_proc_input_num_pd.Draw("HIST")
canvas.SaveAs("proc_input_num_pd.pdf")
h_proc_output_num_me.Draw("HIST")
canvas.SaveAs("proc_output_num_pd.pdf")

gPad.SetLogy()

h_proc_input_num.Draw("HIST")
canvas.SaveAs("proc_input_num.pdf")
h_proc_output_num.Draw("HIST")
canvas.SaveAs("proc_output_num.pdf")
