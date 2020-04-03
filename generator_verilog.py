#!/usr/bin/env python

from TrackletGraph import MemModule, ProcModule, TrackletGraph
from WriteHDLUtils import getHLSMemoryClassName, groupAllConnectedMemories, writeMemoryInstance, writeTBMemoryInstance, writeModuleInst
import os, subprocess

########################################
# Functions to write strings
########################################

########################################
# Memories
########################################

def writeMemoryModules(mem_list, interface=0):
    # mem_list: a list memory module(s)
    # the element cound be a list if the memories are grouped in an array

    string_mem = ""

    # Loop over memories in the list
    for memModule in sorted(mem_list,key=lambda x: x.index):
        amem_str,_ = writeMemoryInstance(memModule,interface)
        string_mem += amem_str
        
    return string_mem

########################################
# Processing modules
########################################
def writeProcModules(proc_list, hls_src_dir):
    # FIXME:
    # (1) how to label functions with instance name?
    # (2) how to propagate BXs?
    
    string_proc = ""
    proc_type_list = []

    # Sort the processing module list
    proc_list.sort(key=lambda x: x.index)

    for aProcMod in proc_list:
        if not aProcMod.mtype in proc_type_list:
            string_proc += writeModuleInst(aProcMod, hls_src_dir, True)+"\n"
            proc_type_list.append(aProcMod.mtype)
        else:
            string_proc += writeModuleInst(aProcMod, hls_src_dir, False)+"\n"
        
    return string_proc

#########
# Top function interface
def writeTopModule_interface(topmodule_name, process_list, memories_topin, memories_topout,
                     streamIO=False):
    # memories_topin, memories_topout: list of memory module(s)
    # topmodule_name: name of the top module

    # TODO: Top function uses hls::stream as input/output arguments
    # Need the configuration file to map the input link to memories
    # All memories are instantiated in the top function
    # Input and output arguments of the top function are hls::stream
    if streamIO:
        raise ValueError("hls::stream IO is not supported yet.")

    string_topmod_interface = "module "+topmodule_name+"(\n"

    # Find names of first & last processing modules in project
    initial_proc = ""
    final_proc = ""
    for proc in process_list:
        if proc.is_first: initial_proc = proc.mtype
        if proc.is_last: final_proc = proc.mtype
    
    # clk, reset, en_proc
    string_topmod_interface += "  input clk,\n"
    string_topmod_interface += "  input reset,\n"
    string_topmod_interface += "  input en_proc,\n"
    # BX
    string_topmod_interface += "  input [2:0] bx_in_"+initial_proc+",\n"

    # Input arguments
    for memModule in memories_topin:
        if isinstance(memModule, list): # memories in an array
            assert(len(memModule)>0)
#            memclass = getHLSMemoryClassName(memModule[0])
            #TODO Need to add functionality for arrays of memory classes here
            string_topmod_interface += "  input "+memModule.inst+"_dataarray_data_V_wea,\n"
            string_topmod_interface += "  input ["+str(6+memModule.bxbitwidth)+":0] "
            string_topmod_interface += memModule.inst+"_dataarray_data_V_writeaddr,\n"
            string_topmod_interface += "  input ["+str(memModule.bitwidth-1)+":0] "
            string_topmod_interface += memModule.inst+"_dataarray_data_V_din,\n"
            for i in range(0,2**memModule.bxbitwidth):
                string_topmod_interface += "  input "+memModule.inst+"_nentries_"+str(i)+"_V_we,\n"
                string_topmod_interface += "  input [6:0] "+memModule.inst
                string_topmod_interface += "_nentries_"+str(i)+"_V_din,\n"
        else:
#            memclass = getHLSMemoryClassName(memModule)
            string_topmod_interface += "  input "+memModule.inst+"_dataarray_data_V_wea,\n"
            string_topmod_interface += "  input ["+str(6+memModule.bxbitwidth)+":0] "
            string_topmod_interface += memModule.inst+"_dataarray_data_V_writeaddr,\n"
            string_topmod_interface += "  input ["+str(memModule.bitwidth-1)+":0] "
            string_topmod_interface += memModule.inst+"_dataarray_data_V_din,\n"
            for i in range(0,2**memModule.bxbitwidth):
                string_topmod_interface += "  input "+memModule.inst+"_nentries_"+str(i)+"_V_we,\n"
                string_topmod_interface += "  input [6:0] "+memModule.inst
                string_topmod_interface += "_nentries_"+str(i)+"_V_din,\n"

    # Output arguments
    for memModule in memories_topout:
        if isinstance(memModule, list): # memories in an array
            assert(len(memModule)>0)
#            memclass = getHLSMemoryClassName(memModule[0])
            #TODO Need to add functionality for arrays of memory classes here
            string_topmod_interface += "  input "+memModule.inst+"_dataarray_data_V_enb,\n"
            string_topmod_interface += "  input ["+str(6+memModule.bxbitwidth)+":0] "
            string_topmod_interface += memModule.inst+"_dataarray_data_V_readaddr,\n"
            string_topmod_interface += "  output ["+str(memModule.bitwidth-1)+":0] "
            string_topmod_interface += memModule.inst+"_dataarray_data_V_dout,\n"
            for i in range(0,2**memModule.bxbitwidth):
                string_topmod_interface += "  output [6:0] "+memModule.inst
                string_topmod_interface += "_nentries_"+str(i)+"_V_dout,\n"
        else:
#            memclass = getHLSMemoryClassName(memModule)
            string_topmod_interface += "  input "+memModule.inst+"_dataarray_data_V_enb,\n"
            string_topmod_interface += "  input ["+str(6+memModule.bxbitwidth)+":0] "
            string_topmod_interface += memModule.inst+"_dataarray_data_V_readaddr,\n"
            string_topmod_interface += "  output ["+str(memModule.bitwidth-1)+":0] "
            string_topmod_interface += memModule.inst+"_dataarray_data_V_dout,\n"
            for i in range(0,2**memModule.bxbitwidth):
                string_topmod_interface += "  output [6:0] "+memModule.inst
                string_topmod_interface += "_nentries_"+str(i)+"_V_dout,\n"

    # BX output
    string_topmod_interface += "  output[2:0] bx_out_"+final_proc+",\n"
    # Done signal
    string_topmod_interface += "  output "+final_proc+"_done,\n"

    # Get rid of the last comma and close the parentheses
    string_topmod_interface = string_topmod_interface.rstrip(",\n")+"\n);\n\n"

    return string_topmod_interface

#########
# Main source
def writeTopFile(string_finterface, string_mem, string_proc):
    string_src = "`timescale 1ns / 1ps\n\n"
    string_src += string_finterface
    string_src += string_mem
    string_src += string_proc
    string_src += "endmodule"

    return string_src

#########
# Test bench
def writeTBMemories(memories_list, isInput, emData_dir="", sector="04",
                    memprint_list=[]):
    # memories_list: list of memModule(s)
    inout = "input" if isInput else "output"

#    string_mem = "///////////////////////////\n// "+inout+" memories\n"
#    string_file = "///////////////////////////\n// open "+inout+" files\n"
    string_mem = ""
    string_file = ""
    string_loop = ""

    for memModule in memories_list:
        amem_str = writeTBMemoryInstance(memModule,isInput)
        string_mem += amem_str

        # Emulation files
        # If memories are in an array, open file for each of the memory object in the array
        isMemArray = isinstance(memModule, list)

        mems = memModule if isMemArray else [memModule]   
        for im, mem in enumerate(mems):
            meminst = mem.inst
            validflag = "valid_"+meminst
            flabel = "f"+inout+"_"+meminst

            memtype = mem.mtype
            # special cases for VMStubsTE, VMStubsME and CandidateMatch
            memtype = memtype.rstrip("TE")
            memtype = memtype.rstrip("ME")
            memtype = memtype.replace("CandidateMatch","CandidateMatches")
            memtype = memtype.replace("FullMatch","FullMatches")
            fname = memtype+"_"+meminst+"_"+sector+".dat"
            memprint_list.append(fname)
            if emData_dir:
                emData_dir = emData_dir.rstrip('/').split('/')[-1]+'/'
            fname = emData_dir + fname
            string_file += "ifstream "+flabel+";\n"
            string_file += "bool "+validflag+" = openDataFile("+flabel+", \""+fname+"\");\n"
            string_file += "if (not "+validflag+") return -1;\n\n"

            memname = mem.userlabel+"["+str(im)+"]" if isMemArray else meminst
            
#            if isInput:
#                string_loop += "writeMemFromFile<"+memclass+">("
#                string_loop += memname+", "+flabel+", ievt);\n"
#            else:
#                string_loop += "err += compareMemWithFile<"+memclass+">("
#                string_loop += memname+", "+flabel+", ievt, \""+memname+"\", "
#                string_loop += "truncation);\n"

    string_mem += "\n"

#    return string_mem, string_file, string_loop
    return string_mem, "", ""

def writeTestBench(topfunc, memories_in, memories_out, emData_dir, sector="04"):
    # memories_in, memories_out: list of (memModule(s), portname)

    fnames_memprint = []

    string_inmem, string_infile, string_writemem = writeTBMemories(
        memories_in, True, emData_dir, sector, fnames_memprint)
    string_outmem, string_outfile, string_compmem = writeTBMemories(
        memories_out, False, emData_dir, sector, fnames_memprint)

    for memModule in memories_in:
        if memModule.downstreams[0].is_first:
            string_first_proc = memModule.downstreams[0].mtype
            break    
    
    for memModule in memories_out:
        if memModule.upstreams[0].is_last:
            string_last_proc = memModule.upstreams[0].mtype
            break    

    string_tb = "// Test bench generated by generator_verilog.py\n\n"
    string_tb += "`timescale 1ns / 1ps\n\n"

    string_tb += "module " + topfunc + "_test();\n\n"

    string_tb += "reg clk;\n"
    string_tb += "reg reset;\n\n"

    string_tb += "initial begin\n"
    string_tb += "  reset = 1'b1;\n"
    string_tb += "  clk   = 1'b1;\n"
    string_tb += "end\n\n"

    string_tb += "initial begin\n"
    string_tb += "  #5400\n"
    string_tb += "  reset = 1'b0;\n"
    string_tb += "end\n\n"

    string_tb += "reg en_proc = 1'b0;\n"
    string_tb += "always @(posedge clk) begin\n"
    string_tb += "  if (reset) en_proc = 1'b0;\n"
    string_tb += "  else       en_proc = 1'b1;\n"
    string_tb += "end\n\n"

    string_tb += "always begin\n"
    string_tb += "  #2.5 clk = ~clk;\n"
    string_tb += "end\n\n"

    string_tb += "reg[2:0] bx_in_"+string_first_proc+";\n"
    string_tb += "initial bx_in_"+string_first_proc+" = 3'b110;\n"
    string_tb += "always begin\n"
    string_tb += "  #540 bx_in_"+string_first_proc+" <= bx_in_"
    string_tb += string_first_proc+" + 1'b1;\n"
    string_tb += "end\n"
    string_tb += "wire[2:0] bx_out_"+string_last_proc+";\n\n"

    string_tb += string_inmem
    string_tb += string_outmem
    string_tb += string_infile
    string_tb += string_outfile
    string_tb += "\n"

    string_tb += topfunc+" "+topfunc+"_inst (\n"
    string_tb += "  .clk(clk),\n"
    string_tb += "  .reset(reset),\n"
    string_tb += "  .en_proc(en_proc),\n"
    
    string_tb += "  .bx_in_"+string_first_proc
    string_tb += "(bx_in_"+string_first_proc+"),\n"

    for memModule in memories_in:
        string_tb += "  ."+memModule.inst+"_dataarray_data_V_wea(1'b1),\n"
        string_tb += "  ."+memModule.inst+"_dataarray_data_V_writeaddr("
        string_tb += memModule.inst+"_dataarray_data_V_writeaddr),\n"
        string_tb += "  ."+memModule.inst+"_dataarray_data_V_din("
        string_tb += memModule.inst+"_dataarray_data_V_dout),\n"
        for i in range(0,2**memModule.bxbitwidth):
            string_tb += "  ."+memModule.inst+"_nentries_"+str(i)+"_V_we(1'b1),\n"
            string_tb += "  ."+memModule.inst+"_nentries_"+str(i)+"_V_din("
            string_tb += memModule.inst+"_nentries_"+str(i)+"_V_dout),\n"

    string_tb += "  .bx_out_"+string_last_proc
    string_tb += "(bx_out_"+string_last_proc+"),\n"

    for memModule in memories_out:
        string_tb += "  ."+memModule.inst+"_dataarray_data_V_enb("
        string_tb += memModule.inst+"_dataarray_data_V_enb),\n"
        string_tb += "  ."+memModule.inst+"_dataarray_data_V_readaddr("
        string_tb += memModule.inst+"_dataarray_data_V_readaddr),\n"
        string_tb += "  ."+memModule.inst+"_dataarray_data_V_dout("
        string_tb += memModule.inst+"_dataarray_data_V_dout),\n"
        for i in range(0,2**memModule.bxbitwidth):
            string_tb += "  ."+memModule.inst+"_nentries_"+str(i)+"_V_dout("
            string_tb += memModule.inst+"_nentries_"+str(i)+"_V_dout),\n"
    string_tb = string_tb.rstrip(",\n")
    string_tb += "\n);\n\nendmodule"
    
    return string_tb, fnames_memprint

def writeTcl(projname, topfunc, emData_dir):
    string_tcl = "open_project -reset "+projname+"\n"
    string_tcl += "set_top "+topfunc+"\n"
    string_tcl += "add_files ../TrackletAlgorithm/"+topfunc+".cpp -cflags \"-std=c++11\"\n"
    
    # for now
    # need to add source files specific to TrackletCalculator
    string_tcl += "add_files ../TrackletAlgorithm/TrackletCalculator.cpp -cflags \"-std=c++11\"\n"
    string_tcl += "add_files ../TrackletAlgorithm/TC_L1L2.cpp -cflags \"-std=c++11\"\n"
    # and other seeding pairs if available.
    
    string_tcl += "add_files -tb ../TestBenches/"+topfunc+"_test.cpp -cflags \"-I../TrackletAlgorithm -std=c++11\"\n"
    string_tcl += "add_files -tb ../emData/"+emData_dir+"\n"
    string_tcl += "open_solution -reset \"solution1\"\n"
    #string_tcl += "set_part {xcku115-flvb2104-2-e} -tool vivado\n"
    string_tcl += "set_part {xcvu7p-flvb2104-2-e} -tool vivado\n"
    string_tcl += "create_clock -period 4 -name default\n"
    string_tcl += "#csim_design\n"
    string_tcl += "#csynth_design\n"
    string_tcl += "#cosim_design\n"
    string_tcl += "#export_design -rtl verilog -format ip_catalog\n"
    string_tcl += "\n"
    string_tcl += "#exit"

    return string_tcl

def getMemPrintDirectory(fname):
    # return directory name under fpga_emulation_longVM/MemPrints/
    # for a given memory printout file
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
    parser.add_argument('-u', '--nupstream', type=int, default=0,
                        help="Number of upstream processing steps to include")
    parser.add_argument('-d', '--ndownstream', type=int, default=0,
                        help="Number of downstream processing steps to include")

    parser.add_argument('--emData_dir', type=str, default="SectorProcessorTest",
                        help="Directory where emulation printouts are stored")
    parser.add_argument('--memprint_dir', type=str,
                        default="../fpga_emulation_longVM/MemPrints/",
                        help="Directory of emulation memory printouts")
    #parser.add_argument('-d','--debug', action='store_true',
    #                    help="Turn on for debugging")
    
    args = parser.parse_args()

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

    if args.uut is None:
        # Get all modules in the configurations
        process_list = tracklet.get_all_proc_modules()
        memory_list = tracklet.get_all_memory_modules()
    else:
        # if only want a slice of the project around the module args.uut
        uutProcModule = tracklet.get_proc_module(args.uut)
        process_list, memory_list = TrackletGraph.get_slice_around_proc(
            uutProcModule, args.nupstream, args.ndownstream) 

    # Get widths of all needed memories
    for mem in memory_list:
        TrackletGraph.populate_bitwidths(mem,args.hls_dir)
    # Get whether processing modules are first or last in chain
    for proc in process_list:
        TrackletGraph.populate_firstlast(proc)

    ########################################
    #  Plot graph
    ########################################
    width, height, dy, textsize = tracklet.draw_graph(process_list)
    os.system("root -b <<EOF \"DrawTrackletProject.C+("+str(width)+","+str(height)+","+str(dy)+","+str(textsize)+")\"")
        
    ########################################
    #  Write HLS top function
    ########################################

    # List of (memory module(s), portname)
    # memories inside the top function, input memories at top function interface,
    # output memories at top function interface
    memList_inside, memList_topin, memList_topout = groupAllConnectedMemories(
        process_list, memory_list)

    # Write memories
    string_memModules = writeMemoryModules(memList_topin,-1)
    string_memModules += writeMemoryModules(memList_inside,0)
    string_memModules += writeMemoryModules(memList_topout,1)

    # Write processing modules
    # First check if the HLS project directory exists
    if not os.path.exists(args.hls_dir):
        raise ValueError("Cannot find HLS project directory: "+args.hls_dir)
    # HLS source code directory
    source_dir = args.hls_dir.rstrip('/')+'/TrackletAlgorithm'
    string_procModules = writeProcModules(process_list, source_dir)

    # Top function interface
    string_topmod_interface = writeTopModule_interface(args.topfunc, process_list, memList_topin,
                                          memList_topout)

    # Source
    string_topfile = writeTopFile(string_topmod_interface,
                                 string_memModules, string_procModules)

    ###############
    # Test bench
    string_testbench, list_memprints = writeTestBench(
        args.topfunc, memList_topin, memList_topout, args.emData_dir)
        #,args.sector)
                                      
    ###############
    # tcl
    string_tcl = writeTcl(args.projname, args.topfunc, args.emData_dir)
    
    # Write to disk
    fname_top = args.topfunc+".v"
    fname_tb = args.topfunc+"_test.v"
    fname_tcl = "script_"+args.projname+".tcl"
    
    fout_top = open(fname_top,"w")
    fout_top.write(string_topfile)

    fout_testbench = open(fname_tb, "w")
    fout_testbench.write(string_testbench)

    fout_tcl = open(fname_tcl, "w")
    fout_tcl.write(string_tcl)

    ###############
    print "Output top file:", fname_top
    print "Output test bench file:", fname_tb
    print "Output tcl script:", fname_tcl
    
    ###############
    # Copy the necessary emulation memory printouts for test bench
    # make a local directory first
    if os.path.exists(args.memprint_dir):
        print "Creating a directory:", args.emData_dir
        subprocess.call(['mkdir','-p',args.emData_dir])

        print "Start to copy emulation printouts locally"
        for filename in list_memprints:
            memdir = getMemPrintDirectory(filename)+'/'
            fullname = args.memprint_dir.rstrip('/')+'/'+memdir+filename
            subprocess.call(['cp', fullname, args.emData_dir+'/.'])
        print "Done copying emulation printouts"
    else:
        print "Cannot find directory", args.memprint_dir
        print "No memory prinout files are copied."
    
