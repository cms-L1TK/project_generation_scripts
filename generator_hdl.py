#!/usr/bin/env python3

################################################
# Scripts to write top-level VHDL
#
# N.B. Check hard-wired constants in TrackletGraph::populate_bitwidths()
################################################

from collections import OrderedDict

try:
    from rich.traceback import install
    install()
except:
    pass
from TrackletGraph import MemModule, ProcModule, MemTypeInfoByKey, TrackletGraph
from WriteHDLUtils import arrangeMemoriesByKey, \
                            writeModuleInstance
from WriteVHDLSyntax import writeTopModuleOpener, writeTBOpener, writeTopModuleCloser, writeTopModuleEntityCloser, writeTBEntityBegin, writeTBModuleCloser, \
                            writeTopPreamble, writeModulesPreamble, writeTBPreamble, writeTBMemoryStimulusProcess, writeTBMemoryReadInstance, writeTBMemoryWriteInstance, writeTBMemoryWriteRAMInstance, writeTBMemoryWriteFIFOInstance, \
                            writeMemoryUtil, writeTopLevelMemoryType, writeControlSignals_interface, \
                            writeMemoryLHSPorts_interface, writeDTCLinkLHSPorts_interface, writeMemoryRHSPorts_interface, writeTBConstants, writeTBControlSignals, \
                            writeFWBlockInstance, writeTrackStreamRHSPorts_interface
import os, subprocess

########################################
# Functions to write strings
########################################

########################################
# Memories
########################################

def writeMemoryModules(memDict, memInfoDict, extraports , delay, split = 0, MPARdict = 0):
    """
    # Inputs:
    #   memDict = dictionary of memories organised by type 
    #             & no. of bits (TPROJ_58 etc.)
    #   memInfoDict = dictionary of info (MemTypeInfoByKey) about each memory type.
    """
    string_wires = ""
    string_mem = ""
    # Loop over memory type
    for mtypeB in memDict:
        memList = memDict[mtypeB]
        if split == 1 and "AS" in mtypeB:
            tempList = []
            for mem in memList:
                if "n2" not in mem.inst:
                    tempList.append(mem)
            memList = tempList
        memInfo = memInfoDict[mtypeB]
        # FIFO memories are not instantiated in top-level (at end of chain?)
        if memInfo.isFIFO:
            continue
        if (("VMSME" in mtypeB and split == 1) or ("TPROJ" in mtypeB and split == 1)):
            continue

        string_wires_inst, string_mem_inst = writeTopLevelMemoryType(mtypeB, memList, memInfo, extraports, delay = delay, split = split, MPARdict = MPARdict)
        string_wires += string_wires_inst
        string_mem += string_mem_inst
    
    return string_wires, string_mem

########################################
# Processing modules
########################################
def writeProcModules(proc_list, hls_src_dir, extraports, delay, split = 0):
    """
    # proc_list:   a list of processing modules
    # hls_src_dir: string pointing to the HLS directory, used to extract constants
    #              from HLS constants files, and reading/writing bit widths by accessing HLS
    #              <MemoryType>Memory.h files (Not yet implemented)
    # extraports: Top-level outputting debug info via ports to test-bench.
    """

    string_proc_func = ""
    string_proc_wire = ""
    # List to keep track of whether current instance of modules is first of its type
    # (needed for things like routing bx ports, done signals, etc.)
    proc_type_list = []

    for aProcMod in proc_list:
        if ("PC" in aProcMod.mtype or "VMSMER" in aProcMod.mtype) and split == 1:
            continue
        if not aProcMod.mtype in proc_type_list: # Is this aProcMod the first of its type
            proc_wire_inst,proc_func_inst = writeModuleInstance(aProcMod, hls_src_dir, True, extraports, delay, split)
            proc_type_list.append(aProcMod.mtype)
        else:
            proc_wire_inst,proc_func_inst = writeModuleInstance(aProcMod, hls_src_dir, False, extraports, delay, split)
        string_proc_wire += proc_wire_inst
        string_proc_func += proc_func_inst
        
    return string_proc_wire,string_proc_func

########################################
# Top function interface
########################################
def writeTopModule_interface(topmodule_name, process_list, memDict, memInfoDict,  extraports, delay, split, streamIO=False, MPARdict = 0):
    """
    # topmodule_name:  name of the top module
    # process_list:    list of all processing functions in the block (in this function, this list is
    #                  only used to get the first and last processes in the block in order to
    #                  generate the bx signals. Seems a bit wasteful to pass the whole list)
    # memDict:         dictionary of memories organised by type 
    #                  & no. of bits (TPROJ_58 etc.)
    # memInfoDict:     dictionary of info (MemTypeInfoByKey) about each memory type.
    # streamIO:        controls whether the input to this firmware block is an hls::stream, rather
    #                  than a BRAM interface. This will be needed when the first processing block in the
    #                  chain is input router, and might be needed for the KF. Not yet implemented.
    """
    
    if streamIO:
        raise ValueError("hls::stream IO is not supported yet.")

    # Find names of first & last processing modules in project
    initial_proc = ""
    final_procs = []
    notfinal_procs_tmp = OrderedDict() # OrderedSet() doesn't exist ...

    for proc in process_list:
        if proc.is_first: initial_proc = proc.mtype_short()
        if proc.is_last: final_procs.append(proc.inst)
        if extraports and (not proc.is_last):
            notfinal_procs_tmp[proc.mtype_short()] = None # Use dictionary as set
    notfinal_procs = notfinal_procs_tmp.keys()
    final_procs.sort()
    string_topmod_interface = writeTopModuleOpener(topmodule_name)

    # Write control signals
    string_ctrl_signals = writeControlSignals_interface(initial_proc, final_procs, notfinal_procs, delay = delay, split = split)
    
    string_input_mems = ""
    string_output_mems = ""
    for mtypeB in memDict:
        memList = memDict[mtypeB]
        memInfo = memInfoDict[mtypeB]
        if memInfo.is_initial:
            # Input arguments
            if "DL" in mtypeB: # DTCLink
                string_input_mems += writeDTCLinkLHSPorts_interface(mtypeB, memDict)
            else:
                string_input_mems += writeMemoryLHSPorts_interface(memList, mtypeB, split = split)
        elif memInfo.is_final:
            # Output arguments
            if memInfo.isFIFO:
                string_output_mems += writeTrackStreamRHSPorts_interface(mtypeB, memDict)
            else:
                if not (("TPROJ" in mtypeB or "VMSME" in mtypeB) and args.split == 1):
                    string_output_mems += writeMemoryRHSPorts_interface(mtypeB, memInfo,memDict, split, MPARdict = MPARdict)
        elif extraports:
            # Debug ports corresponding to BRAM inputs.
            string_input_mems += writeMemoryLHSPorts_interface(memList, mtypeB, extraports, split = split)

        if (memInfo.mtype_long == "AllStubs" and args.split == 1): #for split fpga we want AS sent to second device
          ASmemDict = {mtypeB : []}
          for mem in memList:
              if "n1" in mem.inst:
                  ASmemDict[mtypeB].append(mem)
          string_input_mems += writeMemoryRHSPorts_interface(mtypeB, memInfo,  ASmemDict, split, MPARdict = MPARdict)
        
    string_topmod_interface += string_ctrl_signals
    string_topmod_interface += string_input_mems
    string_topmod_interface += string_output_mems
    string_topmod_interface = string_topmod_interface.rstrip(";\n")+"\n  );\n"
    
    return string_topmod_interface

########################################
# Top file
########################################
def writeTopFile(topfunc, process_list, memDict, memInfoDict, hls_dir, extraports, delay, split = False, MPARdict = 0):
    """
    # Inputs:
    #   memDict = dictionary of memories organised by type 
    #             & no. of bits (TPROJ_58 etc.)
    #   memInfoDict = dictionary of info (MemTypeInfoByKey) about each memory type.
    """
    
    # Write memories
    string_memWires = ""
    string_memModules = ""
    memWires_inst,memModules_inst = writeMemoryModules(memDict, memInfoDict, extraports, delay, split, MPARdict)
    string_memWires   += memWires_inst
    string_memModules += memModules_inst

    # Write processing modules
    # First check if the HLS project directory exists
    if not os.path.exists(hls_dir):
        raise ValueError("Cannot find HLS project directory: "+hls_dir)

    # HLS source code directory
    source_dir = hls_dir.rstrip('/')+'/TrackletAlgorithm'

    string_procWires, string_procModules = writeProcModules(process_list, source_dir, extraports, delay, split)

    # Top function interface
    string_topmod_interface = writeTopModule_interface(topfunc, process_list,
                                                       memDict, memInfoDict, extraports, delay, split, MPARdict=MPARdict)

    string_src = ""
    string_src += writeTopPreamble()
    string_src += string_topmod_interface
    string_src += writeTopModuleEntityCloser(topfunc)
    string_src += string_memWires
    string_src += string_procWires
    string_src += writeModulesPreamble()
    string_src += string_memModules
    string_src += string_procModules
    string_src += writeTopModuleCloser()

    return string_src

########################################
# Test bench
########################################
def writeTBMemoryReads(memDict, memInfoDict, initial_proc, split):
    """
    #   memDict:      dictionary of memories organised by type 
    #                 & no. of bits (TPROJ_58 etc.)
    #   memInfoDict:  dictionary of info (MemTypeInfoByKey) about each memory type.
    #   initial_proc: name of the first processing module of the chain
    """

    found_first_mem = False # Found (one of) the first memory of the chain 
    string_read = "  -- Get signals from input .txt files\n\n"

    for mtypeB in memDict:
        memInfo = memInfoDict[mtypeB]
        memList = memDict[mtypeB]
        if split == 1 and ("VMSME" in mtypeB or "TPROJ" in mtypeB):
          continue
        if memInfo.is_initial:
            first_mem = True if initial_proc in memInfo.downstream_mtype_short and not found_first_mem else False # first memory of the chain
            string_read += writeTBMemoryReadInstance(mtypeB, memDict, memInfo.bxbitwidth, first_mem, memInfo.is_binned, split)

            if first_mem: # Write start signal for the first memory in the chain
                string_read += "  -- As all " + memInfo.mtype_short + " signals start together, take first one, to determine when\n"
                if "DL" in memInfo.mtype_short: 
                    string_read += "  -- first event starts being read from the first link in the chain.\n"
                    string_read += "  START_FIRST_LINK <= START_" + memList[0].inst+";\n\n"
                else:
                    string_read += "  -- first event starts being written to first memory in chain.\n"
                    string_read += "  START_FIRST_WRITE <= START_" + memList[0].inst+";\n\n" 
                found_first_mem = True

    # string_read += "\n"
    return string_read

def writeFWBlockInstantiation(topfunc, memDict, memInfoDict, initial_proc, final_procs, notfinal_procs,split,MPARdict):
    """
    #   topfunc:        name of the top module
    #   memDict:        dictionary of memories organised by type 
    #                   & no. of bits (TPROJ_58 etc.)
    #   memInfoDict:    dictionary of info (MemTypeInfoByKey) about each memory type.
    #   initial_proc:   name of the first processing module of the chain
    #   final_procs:     names of the last processing module of the chain
    #   notfinal_procs: a set of the names of processing modules not at the end of the chain
    """

    string_instantiaion = "  -- ########################### Instantiation ###########################\n"
    string_instantiaion += "  -- Instantiate the Unit Under Test (UUT)\n\n"

    # Instantiate both the "normal" and the "Full"
    topfunc = topfunc[:-4] if topfunc[-4:] == "Full" else topfunc
    if initial_proc not in final_procs[0].mtype_short(): # For a single module the normal and the full are the same
        string_instantiaion += writeFWBlockInstance(topfunc, memDict, memInfoDict, initial_proc, final_procs,split=split,MPARdict=MPARdict)
    string_instantiaion += writeFWBlockInstance(topfunc+"Full", memDict, memInfoDict, initial_proc, final_procs, notfinal_procs,split=split,MPARdict=MPARdict)

    return string_instantiaion

def writeTBMemoryWrites(memDict, memInfoDict, notfinal_procs,split, MPARdict):
    """
    #   memDict:      dictionary of memories organised by type 
    #                 & no. of bits (TPROJ_58 etc.)
    #   memInfoDict:  dictionary of info (MemTypeInfoByKey) about each memory type.
    #   notfinal_procs: a set of the names of processing modules not at the end of the chain
    """

    string_intermediate = ""
    string_final = ""
    
    for mtypeB in memDict:
        if split == 1 and ("VMSME" in mtypeB or "TPROJ" in mtypeB):
          continue
        memList = memDict[mtypeB]
        memInfo = memInfoDict[mtypeB]
        proc = memInfo.upstream_mtype_short # Processing module that writes to mtypeB
        up_proc = notfinal_procs[notfinal_procs.index(proc)-1] if notfinal_procs and proc != notfinal_procs[0] and proc in notfinal_procs else "" # The previous processing module

        if memInfo.isFIFO:
            string_tmp = writeTBMemoryWriteFIFOInstance(mtypeB, memDict, proc)
            # Code for TrackBuilder to write TF concatenated track+stub data.
            # (Needed to compare with emData/).
            if mtypeB.startswith('TW_'):
                for m in memDict[mtypeB]:
                    memName = m.inst
                    seed = memName[-4:]
                    bw_keys = [key for key in memDict if key.startswith('BW_')]
                    bw_width = memDict[bw_keys[0]][0].bitwidth if len(bw_keys) > 0 else 0
                    n_bw = len(memDict[bw_keys[0]]) if len(bw_keys) > 0 else 0
                    dw_keys = [key for key in memDict if key.startswith('DW_')]
                    dw_width = memDict[dw_keys[0]][0].bitwidth if len(dw_keys) > 0 else 0
                    n_dw = len(memDict[dw_keys[0]]) if len(dw_keys) > 0 else 0
                    # Calculate total width of track word plus stub words
                    total_width = str(m.bitwidth + n_bw * bw_width + n_dw * dw_width)

                    string_tmp += "-- Code for TrackBuilder to write TF concatenated track+stub data.\n";
                    string_tmp += "-- (Needed to compare with emData/).\n";
                    string_tmp += "writeTF_"+seed+"_" + total_width + " : entity work.FileWriterFIFO\n";
                    string_tmp += "generic map (\n";
                    string_tmp += "  FILE_NAME  => FILE_OUT_TF&\""+seed+"\"&outputFileNameEnding,\n";
                    string_tmp += "  FIFO_WIDTH  => " + total_width + "\n";
                    string_tmp += ")\n";
                    string_tmp += "port map (\n";
                    string_tmp += "  CLK => CLK,\n"
                    string_tmp += "  DONE => TB_DONE,\n";
                    string_tmp += "  WRITE_EN => (TW_"+seed+"_stream_A_write and TW_"+seed+"_stream_AV_din("+str(m.bitwidth-1)+")),\n";
                    string_tmp += "  FULL_NEG => TW_"+seed+"_stream_A_full_neg,\n";
                    string_tmp += "  DATA => TW_"+seed+"_stream_AV_din&BW_"+seed+"_L1_stream_AV_din&BW_"+seed+"_L2_stream_AV_din&BW_"+seed+"_L3_stream_AV_din&BW_"+seed+"_L4_stream_AV_din&BW_"+seed+"_L5_stream_AV_din&BW_"+seed+"_L6_stream_AV_din&DW_"+seed+"_D1_stream_AV_din&DW_"+seed+"_D2_stream_AV_din&DW_"+seed+"_D3_stream_AV_din&DW_"+seed+"_D4_stream_AV_din&DW_"+seed+"_D5_stream_AV_din\n";
                    string_tmp += ");\n";
                    
        if memInfo.is_final:
            if memInfo.isFIFO:
              string_final += string_tmp
            else:
              string_final += writeTBMemoryWriteRAMInstance(mtypeB, memDict, proc, memInfo.bxbitwidth, memInfo.is_binned, split, MPARdict = MPARdict)
        elif not memInfo.is_initial: # intermediate memories
            if memInfo.isFIFO:
              string_intermediate += string_tmp
            else:
              is_cm = memInfo.downstream_mtype_short in ("TP", "MP")
              string_intermediate += writeTBMemoryWriteInstance(mtypeB, memList, proc, up_proc, memInfo.bxbitwidth, memInfo.is_binned, is_cm, split)

    string_write = "  -- Write signals to output .txt files\n\n"
    string_write += "  writeIntermediateRAMs : if INST_TOP_TF = 1 generate\n"
    string_write += "  begin\n\n"
    string_write += "    -- This writes signals going to intermediate memories in chain.\n\n"
    string_write += string_intermediate
    string_write += "  end generate writeIntermediateRAMs;\n\n\n"
    string_write += "  -- Write memories from end of chain.\n\n"
    string_write += string_final

    return string_write

def writeTestBench(tbfunc, topfunc, process_list, memDict, memInfoDict, memPrintsDir, sector="04", split = False, MPARdict = 0):
    """
    # Inputs:
    #   tbfunc:       name of the testbench
    #   topfunc:      name of the top module
    #   process_list: list of all processing functions in the block (in this function, this list is
    #                 only used to get the first and last processes in the block in order to
    #                 generate the bx signals. Seems a bit wasteful to pass the whole list)
    #   memDict:      dictionary of memories organised by type 
    #                 & no. of bits (TPROJ_58 etc.)
    #   memInfoDict:  dictionary of info (MemTypeInfoByKey) about each memory type.
    #   memPrintsDir:   directory where data for input memories is stored
    #   sector:       which sector nonant the emData is taken from
    """

    # Find names of first & last processing modules in project
    initial_proc = ""
    final_procs = []
    notfinal_procs = []
    sorted(process_list, key=lambda p: p.order) # Sort processing modules in the order they are in the chain
    for proc in process_list:
        if proc.is_first: initial_proc = proc.mtype_short()
        if proc.is_last: final_procs.append(proc)
        if not proc.is_last and proc.mtype_short() not in notfinal_procs:
            notfinal_procs.append(proc.mtype_short())

    # Write test bench header
    string_header = ""
    string_header += writeTBPreamble()
    string_header += writeTBOpener(tbfunc)

    string_constants = writeTBConstants(memDict, memInfoDict, notfinal_procs+[final_procs[-1].mtype_short()], memPrintsDir, sector, split)
    if len([key for key in memInfoDict if key.startswith('TW_')]) > 0:
        string_constants += 'constant FILE_OUT_TF          : string := dataOutDir&"TF_";';
        
    string_ctrl_signals = writeTBControlSignals(memDict, memInfoDict, initial_proc, final_procs, notfinal_procs,split, MPARdict)

    string_begin = writeTBEntityBegin()
    string_mem_read = writeTBMemoryReads(memDict, memInfoDict, initial_proc,split)
    string_mem_stim = writeTBMemoryStimulusProcess(initial_proc)

    string_fwblock_inst = writeFWBlockInstantiation(topfunc, memDict, memInfoDict, initial_proc, final_procs, notfinal_procs,split=split,MPARdict=MPARdict)

    string_mem_write = writeTBMemoryWrites(memDict, memInfoDict, notfinal_procs,split,MPARdict)

    string_tb = ""
    string_tb += string_header
    string_tb += string_constants
    string_tb += string_ctrl_signals
    string_tb += string_begin
    string_tb += string_mem_read
    string_tb += string_mem_stim
    string_tb += string_fwblock_inst
    string_tb += string_mem_write
    string_tb += writeTBModuleCloser()
    
    return string_tb

########################################
# Tcl
########################################
def writeTcl(projname, topfunc, memPrintsDir):
    string_tcl = "Not yet implemented!\n"
    return string_tcl

def getMemPrintDirectory(fname):
    """
    # return directory name under fpga_emulation_longVM/MemPrints/
    # for a given memory printout file
    """
    if "InputStubs" in fname:
        return "InputStubs"
    elif "StubPairs" in fname:
        return "StubPairs"
    elif "AllStubs" in fname:
        return "Stubs"
    elif "VMStubs_VMSME" in fname:
        return "VMStubsME"
    elif "VMStubs_VMSTE" in fname:
        return "VMStubsTE"
    elif "TrackletParameters" in fname:
        return "TrackletParameters"
    elif "AllProj" in fname or "TrackletProjections" in fname:
        return "TrackletProjections"
    elif "VMProjections" in fname:
        return "VMProjections"
    elif "CandidateMatches" in fname or "FullMatches" in fname:
        return "Matches"
    elif "TrackFit" in fname:
        return "FitTrack"
    elif "CleanTrack" in fname:
        return "CleanTrack"
    else:
        raise ValueError("Unmatched file name: "+fname)

    
###############################

if __name__ == "__main__":
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Script to generate HLS top function for Tracklet project", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('hls_dir', type=str, nargs='?',
                        default="../firmware-hls/",
                        help="HLS firmware project directory")
    parser.add_argument('-f', '--topfunc', type=str, default="SectorProcessor",
                        help="Top-level FW entity name")
    parser.add_argument('-n', '--projname', type=str, default="sectproc",
                        help="Project name")
    
    parser.add_argument('-s','--stream', action='store_true', help="True if want hls::stream objects on the interface, otherwise top function arguments are memory pointers")
    
    parser.add_argument('-p','--procconfig', type=str, default="processingmodules.dat",
                        help="Name of the configuration file for processing modules")
    parser.add_argument('-m','--memconfig', type=str, default="memorymodules.dat",
                        help="Name of the configuration file for memory modules")
    parser.add_argument('-w','--wireconfig', type=str, default="wires.dat",
                        help="Name of the configuration file for wiring")
    parser.add_argument('-r','--region', choices=['A','L','D'], default='A',
                        help="Detector region. A: all, L: barrel, D: disk")
    
    parser.add_argument('--uut', type=str, default=None, help="Unit Under Test")
    parser.add_argument('--mut', type=str, choices=["IR","VMR", "TE", "TC", "PR","TP", "PC", "ME", "MC", "FT"], default=None, help="Module Under Test")
    parser.add_argument('-u', '--nupstream', type=int, default=0,
                        help="Number of upstream processing steps to include")
    parser.add_argument('-d', '--ndownstream', type=int, default=0,
                        help="Number of downstream processing steps to include")
    parser.add_argument('-x', '--extraports', action='store_true', 
                        help="Add debug ports corresponding to all BRAM inputs")
    parser.add_argument('-de', '--delay', type=int, default=0,
                        help="Number of pipeline stages in between processing and memory modules to include, setting 0 does not include pipeline modules")
    parser.add_argument('-sp', '--split', type =int, default=0,
                        help="enables split-fpga project, a value of 1 for first-fpga project, 2 for second-fpga, 0 for single fpga projects")

    parser.add_argument('--memprints_dir', type=str, default="../../../../../MemPrints/",
                        help="Directory where emulation printouts are stored")
    parser.add_argument('-ng','--no_graph', action='store_true',
                        help="Don't make TrackletProject.pdf, so ROOT not required")
    args = parser.parse_args()

    if args.extraports:
        topfunc = args.topfunc + "Full"
    else:
        topfunc = args.topfunc

    ########################################
    # Read configuration files and setup TrackletGraph
    ########################################

    tracklet = TrackletGraph.from_configs(args.procconfig, args.memconfig,
                                          args.wireconfig, args.region)

    ########################################
    # Get processing and memory module lists
    ########################################
    process_list = []
    memory_list = []

    if args.mut is not None:

        # Get all module units of a given type
        mutModules = tracklet.get_all_module_units(args.mut,args.split)
        # Get the slices around each of the modules
        process_list = []
        memory_list = []
        for mutModule in mutModules.values():
            process, memory = TrackletGraph.get_slice_around_proc(
                mutModule, args.nupstream, args.ndownstream)
            process_list.extend(process)
            memory_list.extend(memory)

        if args.split == 1 :
            MPARdict = tracklet.get_MPAR_dict()
        else:
            MPARdict = None
        # Remove duplicates from the process and module list
        process_list = list(set(process_list))
        memory_list = list(set(memory_list))
        # Correct mem.is_initial & mem.is_final, as loop over mutModules overwrites them incorrectly. 
        for mem in memory_list:
            if mem.is_initial:
                for proc in mem.upstreams:
                    if proc is None:
                        continue
                    for p in process_list:
                        if proc.inst == p.inst:
                            mem.is_initial = False
                            break
            if mem.is_final:
                for proc in mem.downstreams:
                    if proc is None:
                        continue
                    for p in process_list:
                        if proc.inst == p.inst:
                            mem.is_final = False
                            break
        
    elif args.uut is None:
        # Get all modules in the configurations
        process_list = tracklet.get_all_proc_modules()
        memory_list = tracklet.get_all_memory_modules()
    else:
        # if only want a slice of the project around the module args.uut
        uutProcModule = tracklet.get_proc_module(args.uut)
        process_list, memory_list = TrackletGraph.get_slice_around_proc(
            uutProcModule, args.nupstream, args.ndownstream) 

    # Sort the module lists by order in which they appear in chain.
    process_list.sort(key=lambda x: x.index)
    memory_list.sort(key=lambda x: x.index)

    for mem in memory_list:
        # Get widths of all needed memories
        TrackletGraph.populate_bitwidths(mem,args.hls_dir)
        TrackletGraph.populate_is_binned(mem,args.hls_dir)

        # Determine which memories need numEntries output ports
        TrackletGraph.populate_has_numEntries_out(mem,args.hls_dir)

    # Get whether processing modules are first or last in chain
    for proc in process_list:
        TrackletGraph.populate_firstlast(proc)
        TrackletGraph.populate_IPname(proc)

    # Arrange memories in dictionaries by key (TPROJ_60 etc.)
    memDict, memInfoDict = arrangeMemoriesByKey(memory_list)

    ###############
    # File of memory utilities specific to this chain.
    string_memUtilFile = writeMemoryUtil(memDict, memInfoDict)

    ########################################
    #  Plot graph
    ########################################
    if ( args.no_graph == False ) :
        import ROOT
        pageWidth, pageHeight, dyBox, textSize = tracklet.draw_graph(process_list)
        ROOT.gROOT.SetBatch(True)
        ROOT.gROOT.LoadMacro('DrawTrackletProject.C')
        ROOT.DrawTrackletProject(pageWidth, pageHeight, dyBox, textSize);


    ###############
    #  Top File
    string_topfile = writeTopFile(topfunc, process_list,
                                  memDict, memInfoDict, args.hls_dir, args.extraports, args.delay, args.split, MPARdict = MPARdict)

    ###############
    # Test bench
    tb_name = "tb_tf_top"
    string_testbench = writeTestBench(
        tb_name, topfunc, process_list, memDict, memInfoDict, args.memprints_dir, split = args.split, MPARdict = MPARdict)
    ###############
    # tcl
    string_tcl = writeTcl(args.projname, topfunc, args.memprints_dir)
    
    # Write to disk
    fname_memUtil = "memUtil_pkg.vhd"
    fname_top = topfunc+".vhd"
    fname_tb = tb_name+".vhd"
    fname_tcl = "script_"+args.projname+".tcl"

    fout_memUtil = open(fname_memUtil,"w")
    fout_memUtil.write(string_memUtilFile)
    
    fout_top = open(fname_top,"w")
    fout_top.write(string_topfile)

    fout_testbench = open(fname_tb, "w")
    fout_testbench.write(string_testbench)

    fout_tcl = open(fname_tcl, "w")
    fout_tcl.write(string_tcl)

    ###############
    print("Output top file:", fname_top)
    print("Output test bench file:", fname_tb)
    print("Output HDL package:", fname_memUtil)
    print("Output tcl script:", fname_tcl)
    
    ###############
    # Copy the necessary emulation memory printouts for test bench
    # make a local directory first
#    if os.path.exists(args.memprints_dir):
#        print("Creating a directory:", args.emData_dir)
#        subprocess.call(['mkdir','-p',args.emData_dir])
#
#        print("Start to copy emulation printouts locally")
#        for filename in list_memprints:
#            memdir = getMemPrintDirectory(filename)+'/'
#            fullname = args.memprints_dir.rstrip('/')+'/'+memdir+filename
#            subprocess.call(['cp', fullname, args.emData_dir+'/.'])
#        print("Done copying emulation printouts")
#    else:
#        print("Cannot find directory", args.memprints_dir)
#        print("No memory prinout files are copied.")
    
