#!/usr/bin/env python

################################################
# Scripts to write top-level VHDL
#
# N.B. Check hard-wired constants in TrackletGraph::populate_bitwidths()
################################################
from TrackletGraph import MemModule, ProcModule, MemTypeInfoByKey, TrackletGraph
from WriteHDLUtils import arrangeMemoriesByKey, \
                            writeModuleInstance
from WriteVHDLSyntax import writeTopModuleOpener, writeTBOpener, writeTopModuleCloser, writeTopModuleEntityCloser, writeTBModuleCloser, \
                            writeTopPreamble, writeModulesPreamble, writeTBPreamble, writeTBMemoryStimulusInstance, writeTBMemoryReadInstance, \
                            writeMemoryUtil, writeTopLevelMemoryType, writeControlSignals_interface, \
                            writeMemoryLHSPorts_interface, writeDTCLinkLHSPorts_interface, writeMemoryRHSPorts_interface, writeTBControlSignals, \
                            writeFWBlockControlSignalPorts, writeFWBlockMemoryLHSPorts, writeFWBlockMemoryRHSPorts, writeProcDTCLinkRHSPorts
import ROOT
import os, subprocess

########################################
# Functions to write strings
########################################

########################################
# Memories
########################################

def writeMemoryModules(memDict, memInfoDict, extraports):
    """
    # Inputs:
    #   memDict = dictionary of memories organised by type 
    #             & no. of bits (TPROJ_58b etc.)
    #   memInfoDict = dictionary of info (MemTypeInfoByKey) about each memory type.
    """
    string_wires = ""
    string_mem = ""
    # Loop over memory type
    for mtypeB in memDict:
        if "DL" in mtypeB: # DTCLink
            continue
        memList = memDict[mtypeB]
        memInfo = memInfoDict[mtypeB]
        string_wires_inst, string_mem_inst = writeTopLevelMemoryType(mtypeB, memList, memInfo, extraports)
        string_wires += string_wires_inst
        string_mem += string_mem_inst
    
    return string_wires, string_mem

########################################
# Processing modules
########################################
def writeProcModules(proc_list, hls_src_dir, extraports):
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
        if not aProcMod.mtype in proc_type_list: # Is this aProcMod the first of its type
            proc_wire_inst,proc_func_inst = writeModuleInstance(aProcMod, hls_src_dir, True, extraports)
            proc_type_list.append(aProcMod.mtype)
        else:
            proc_wire_inst,proc_func_inst = writeModuleInstance(aProcMod, hls_src_dir, False, extraports)
        string_proc_wire += proc_wire_inst
        string_proc_func += proc_func_inst
        
    return string_proc_wire,string_proc_func

########################################
# Top function interface
########################################
def writeTopModule_interface(topmodule_name, process_list, memDict, memInfoDict,  extraports, streamIO=False):
    """
    # topmodule_name:  name of the top module
    # process_list:    list of all processing functions in the block (in this function, this list is
    #                  only used to get the first and last processes in the block in order to
    #                  generate the bx signals. Seems a bit wasteful to pass the whole list)
    # memDict:         dictionary of memories organised by type 
    #                  & no. of bits (TPROJ_58b etc.)
    # memInfoDict:     dictionary of info (MemTypeInfoByKey) about each memory type.
    # streamIO:        controls whether the input to this firmware block is an hls::stream, rather
    #                  than a BRAM interface. This will be needed when the first processing block in the
    #                  chain is input router, and might be needed for the KF. Not yet implemented.
    """
    
    if streamIO:
        raise ValueError("hls::stream IO is not supported yet.")

    # Find names of first & last processing modules in project
    initial_proc = ""
    final_proc = ""
    notfinal_procs = set()
    for proc in process_list:
        if proc.is_first: initial_proc = proc.mtype_short()
        if proc.is_last: final_proc = proc.mtype_short()
        if extraports and (not proc.is_last):
            notfinal_procs.add(proc.mtype_short())

    string_topmod_interface = writeTopModuleOpener(topmodule_name)

    # Write control signals
    string_ctrl_signals = writeControlSignals_interface(initial_proc, final_proc, notfinal_procs)
    
    string_input_mems = ""
    string_output_mems = ""
    for mtypeB in memDict:
        memList = memDict[mtypeB]
        memInfo = memInfoDict[mtypeB]
        if memInfo.is_initial:
            # Input arguments
            if "DL" in mtypeB: # DTCLink
                string_input_mems += writeDTCLinkLHSPorts_interface(mtypeB)
            else:
                string_input_mems += writeMemoryLHSPorts_interface(mtypeB)
        elif memInfo.is_final:
            # Output arguments
            string_output_mems += writeMemoryRHSPorts_interface(mtypeB, memInfo)
        elif extraports:
            # Debug ports corresponding to BRAM inputs.
            string_input_mems += writeMemoryLHSPorts_interface(mtypeB, extraports)            
        
    string_topmod_interface += string_ctrl_signals
    string_topmod_interface += string_input_mems
    string_topmod_interface += string_output_mems
    string_topmod_interface = string_topmod_interface.rstrip(";\n")+"\n  );\n"
    
    return string_topmod_interface

########################################
# Top file
########################################
def writeTopFile(topfunc, process_list, memDict, memInfoDict, hls_dir, extraports):
    """
    # Inputs:
    #   memDict = dictionary of memories organised by type 
    #             & no. of bits (TPROJ_58b etc.)
    #   memInfoDict = dictionary of info (MemTypeInfoByKey) about each memory type.
    """
    
    # Write memories
    string_memWires = ""
    string_memModules = ""
    memWires_inst,memModules_inst = writeMemoryModules(memDict, memInfoDict, extraports)
    string_memWires   += memWires_inst
    string_memModules += memModules_inst

    # Write processing modules
    # First check if the HLS project directory exists
    if not os.path.exists(hls_dir):
        raise ValueError("Cannot find HLS project directory: "+hls_dir)

    # HLS source code directory
    source_dir = hls_dir.rstrip('/')+'/TrackletAlgorithm'

    string_procWires, string_procModules = writeProcModules(process_list, source_dir, extraports)

    # Top function interface
    string_topmod_interface = writeTopModule_interface(topfunc, process_list,
                                                       memDict, memInfoDict, extraports)

    string_src = ""
    string_src += writeTopPreamble()
    string_src += string_topmod_interface
    string_src += writeTopModuleEntityCloser(topfunc)
    string_src += string_memWires
    string_src += string_procWires
    string_src += writeModulesPreamble()
    string_src += string_memModules
    string_src += string_procModules
    string_src += writeTopModuleCloser(topfunc)

    return string_src

########################################
# Test bench
########################################
def writeTBMemoryStimuli(memories_list, emData_dir="", sector="04"):
    """
    # memories_list: list of input memories that the test bench has to initialize
    # emData_dir:    directory where data for input memories is stored
    # sector:        which sector nonant the emData is taken from
    """

    string_mem = ""
    for memModule in memories_list:
        amem_str=""
        amem_str = writeTBMemoryStimulusInstance(memModule)
        string_mem += amem_str
    string_mem += "\n"
    return string_mem

def writeTBMemoryReads(memories_list, emData_dir="", sector="04"):
    # memories_list: list of output memories that the test bench will have to read
    # emData_dir:    directory where data for input memories is stored
    # sector:        which sector nonant the emData is taken from

    string_mem = ""
    for memModule in memories_list:
        amem_str = writeTBMemoryReadInstance(memModule)
        string_mem += amem_str
    string_mem += "\n"
    return string_mem

def writeFWBlockInstance(topfunc, memories_in, memories_out, first_proc, last_proc):
    string_inmems_ports = ""

    string_fwblock_ctrl = writeFWBlockControlSignalPorts(first_proc, last_proc)

    for memModule in memories_in:
        string_inmems_ports += writeFWBlockMemoryLHSPorts(memModule)

    string_outmems_ports = ""
    for memModule in memories_out:
        string_outmems_ports += writeFWBlockMemoryRHSPorts(memModule)

    string_fwblock_inst = ""
    string_fwblock_inst += topfunc+" "+topfunc+"_inst (\n"
    string_fwblock_inst += string_fwblock_ctrl
    string_fwblock_inst += string_inmems_ports
    string_fwblock_inst += "\n"
    string_fwblock_inst += string_outmems_ports
    string_fwblock_inst = string_fwblock_inst.rstrip(",")
    string_fwblock_inst += "\n);"
    return string_fwblock_inst

def writeTestBench(topfunc, memDict, memInfoDict, emData_dir, sector="04"):
    """
    # Inputs:
    #   memDict = dictionary of memories organised by type 
    #             & no. of bits (TPROJ_58b etc.)
    #   memInfoDict = dictionary of info (MemTypeInfoByKey) about each memory type.
    #   emData_dir =   directory where data for input memories is stored
    #   sector =       which sector nonant the emData is taken from
    """

    """
    # THIS WAS THE OLD VERILOG CODE

    # Find the first and last processing block in firmware chain
    for memModule in memories_in:
        if isinstance(memModule, list):
            for module in memModule:
                if module.downstreams[0].is_first:
                    first_proc = module.downstreams[0].mtype_short()
                    break
        elif memModule.downstreams[0].is_first:
            first_proc = memModule.downstreams[0].mtype_short()
            break
    
    for memModule in memories_out:
        if isinstance(memModule, list):
            for module in memModule:
                if module.downstreams[0].is_last:
                    last_proc = module.upstreams[0].mtype_short()
                    break
        elif memModule.upstreams[0].is_last:
            last_proc = memModule.upstreams[0].mtype_short()
            break

    # Write test bench header
    string_header = ""
    string_header += writeTBPreamble()
    string_header += writeTBOpener(topfunc)

    string_ctrl_signals = writeTBControlSignals(topfunc, first_proc, last_proc)

    string_memin = writeTBMemoryStimuli(memories_in, emData_dir, sector)
    string_memout = writeTBMemoryReads(memories_out, emData_dir, sector)

    string_fwblock_inst = writeFWBlockInstance(topfunc, memories_in, memories_out, first_proc, last_proc)

    string_tb = ""
    string_tb += string_header
    string_tb += string_ctrl_signals
    string_tb += string_memin
    string_tb += string_memout
    string_tb += string_fwblock_inst
    string_tb += writeTBModuleCloser(topfunc)
    
    return string_tb,""
    """
    return "NOT IMPLEMENTED\n",""

########################################
# Tcl
########################################
def writeTcl(projname, topfunc, emData_dir):
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
    
    parser = argparse.ArgumentParser(description="Script to generate HLS top function for Tracklet project")
    parser.add_argument('hls_dir', type=str, nargs='?',
                        default="../firmware-hls/",
                        help="HLS firmware project directory")
    parser.add_argument('-f', '--topfunc', type=str, default="SectorProcessor",
                        help="HLS top function name")
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
    parser.add_argument('--mut', type=str, choices=["IR","VMR", "TE", "TC", "PR", "ME", "MC"], default=None, help="Module Under Test")
    parser.add_argument('-u', '--nupstream', type=int, default=0,
                        help="Number of upstream processing steps to include")
    parser.add_argument('-d', '--ndownstream', type=int, default=0,
                        help="Number of downstream processing steps to include")
    parser.add_argument('-x', '--extraports', action='store_true', 
                        help="Add debug ports corresponding to all BRAM inputs")

    parser.add_argument('--emData_dir', type=str, default="SectorProcessorTest",
                        help="Directory where emulation printouts are stored")
    parser.add_argument('--memprint_dir', type=str,
                        default="../fpga_emulation_longVM/MemPrints/",
                        help="Directory of emulation memory printouts")
    
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
        print("WARNING: This feature \"--mut\" has only been tested extensively with the PRMEMC chain.")

        # Get all module units of a given type
        mutModules = tracklet.get_all_module_units(args.mut)

        # Get the slices around each of the modules
        process_list = []
        memory_list = []
        for mutModule in mutModules.values():
            process, memory = TrackletGraph.get_slice_around_proc(
                mutModule, args.nupstream, args.ndownstream)
            process_list.extend(process)
            memory_list.extend(memory)

        # Remove duplicates from the process and module list
        process_list = list(set(process_list))
        memory_list = list(set(memory_list))
        
        # Correct mem.is_initial & mem.is_final, as loop over mutModules overwrites them incorrectly. 
        for mem in memory_list:
            if mem.is_initial:
                for proc in mem.upstreams:
                    for p in process_list:
                        if proc.inst == p.inst:
                            mem.is_initial = False
                            break
            if mem.is_final:
                for proc in mem.downstreams:
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
    pageWidth, pageHeight, dyBox, textSize = tracklet.draw_graph(process_list)
    ROOT.gROOT.SetBatch(True)
    ROOT.gROOT.LoadMacro('DrawTrackletProject.C')
    ROOT.DrawTrackletProject(pageWidth, pageHeight, dyBox, textSize);


    ###############
    #  Top File
    string_topfile = writeTopFile(topfunc, process_list,
                                  memDict, memInfoDict, args.hls_dir, args.extraports)

    ###############
    # Test bench
    string_testbench, list_memprints = writeTestBench(
        topfunc, memDict, memInfoDict, args.emData_dir)
                                      
    ###############
    # tcl
    string_tcl = writeTcl(args.projname, topfunc, args.emData_dir)
    
    # Write to disk
    fname_memUtil = "memUtil_pkg.vhd"
    fname_top = topfunc+".vhd"
    fname_tb = topfunc+"_test.vhd"
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
    print "Output top file:", fname_top
    print "Output test bench file:", fname_tb
    print "Output HDL package:", fname_memUtil
    print "Output tcl script:", fname_tcl
    
    ###############
    # Copy the necessary emulation memory printouts for test bench
    # make a local directory first
#    if os.path.exists(args.memprint_dir):
#        print "Creating a directory:", args.emData_dir
#        subprocess.call(['mkdir','-p',args.emData_dir])
#
#        print "Start to copy emulation printouts locally"
#        for filename in list_memprints:
#            memdir = getMemPrintDirectory(filename)+'/'
#            fullname = args.memprint_dir.rstrip('/')+'/'+memdir+filename
#            subprocess.call(['cp', fullname, args.emData_dir+'/.'])
#        print "Done copying emulation printouts"
#    else:
#        print "Cannot find directory", args.memprint_dir
#        print "No memory prinout files are copied."
    
