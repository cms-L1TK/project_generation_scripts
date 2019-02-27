#!/usr/bin/env python

from TrackletGraph import MemModule, ProcModule, TrackletGraph
from WriteHLSUtils import getHLSMemoryClassName, groupAllConnectedMemories, writeMemoryInstance, writeProcFunction
import os

########################################
# Functions to write strings
########################################

########################################
# Memories
########################################

def writeMemoryModules(mem_list):
    # mem_list: a list memory module(s)
    # the element cound be a list if the memories are grouped in an array

    string_mem = ""

    # Loop over memories in the list
    for memModule in sorted(mem_list,key=lambda x: x.index):
        amem_str,_ = writeMemoryInstance(memModule)
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

    # Sort the processing module list
    proc_list.sort(key=lambda x: x.index)

    for aProcMod in proc_list:
        string_proc += writeProcFunction(aProcMod, hls_src_dir)+"\n"
        
    return string_proc

#########
# Top function interface
def writeTopFunction(topfunc_name, memories_topin, memories_topout,
                     streamIO=False):
    # memories_topin, memories_topout: list of memory module(s)
    # topfunc_name: name of the top function

    # TODO: Top function uses hls::stream as input/output arguments
    # Need the configuration file to map the input link to memories
    # All memories are instantiated in the top function
    # Input and output arguments of the top function are hls::stream
    if streamIO:
        raise ValueError("hls::stream IO is not supported yet.")

    string_topfunc = "void "+topfunc_name+"(\n"

    # BX
    string_topfunc += "BXType bx,\n"

    # Input arguments
    for memModule in memories_topin:
        if isinstance(memModule, list): # memories in an array
            assert(len(memModule)>0)
            memclass = getHLSMemoryClassName(memModule[0])
            string_topfunc += "const "+memclass+" "+memModule[0].userlabel+"["+str(len(memModule))+"],\n"
        else:
            memclass = getHLSMemoryClassName(memModule)
            string_topfunc += "const "+memclass+"& "+memModule.inst+",\n"

    # BX output
    string_topfunc += "BXType& bx_o,\n"

    # Output arguments
    for memModule in memories_topout:
        if isinstance(memModule, list): # memories in an array
            assert(len(memModule)>0)
            memclass = getHLSMemoryClassName(memModule[0])
            string_topfunc += memclass+" "+memModule[0].userlabel+"["+str(len(memModule))+"],\n"
        else:
            memclass = getHLSMemoryClassName(memModule)
            string_topfunc += memclass+"& "+memModule.inst+",\n"

    # Get rid of the last comma and close the parentheses
    string_topfunc = string_topfunc.rstrip(",\n")+")\n"

    return string_topfunc

#########
# Header
def writeHeaderFile(topfunc, string_finterface):
    header = "#ifndef "+topfunc.upper()+"_H\n"
    header += "#define "+topfunc.upper()+"_H\n"
    header += "\n"

    # TODO: include all available/working processing functions
    header += "#include \"Constants.hh\"\n"
    header += "#include \"TrackletCalculator.hh\"\n"
    header += "#include \"ProjectionRouter.hh\"\n"
    header += "#include \"MatchEngine.h\"\n"
    header += "#include \"MatchCalculator.hh\"\n"
    header += "\n"

    header += string_finterface.rstrip("\n")
    header += ";\n\n"
    
    header += "#endif\n"

    return header

#########
# Main source
def writeSourceFile(topfunc, string_finterface, string_mem, string_proc):
    string_src = "#include \""+topfunc+".h\"\n\n"
    string_src += string_finterface
    string_src += "{\n"
    string_src += string_mem
    string_src += "\n"
    string_src += string_proc
    string_src += "}\n"

    return string_src

#########
# Test bench
def writeTBMemories(memories_list, isInput, emData_dir="", sector="04"):
    # memories_list: list of memModule(s)
    inout = "input" if isInput else "output"

    string_mem = "///////////////////////////\n// "+inout+" memories\n"
    string_file = "///////////////////////////\n// open "+inout+" files\n"
    string_loop = ""

    for memModule in memories_list:
        amem_str, memclass = writeMemoryInstance(memModule)
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
            if emData_dir:
                emData_dir = emData_dir.rstrip('/').split('/')[-1]+'/'
            fname = emData_dir+memtype+"_"+meminst+"_"+sector+".dat"
            string_file += "ifstream "+flabel+";\n"
            string_file += "bool "+validflag+" = openDataFile("+flabel+", \""+fname+"\");\n"
            string_file += "if (not "+validflag+") return -1;\n\n"

            memname = mem.userlabel+"["+str(im)+"]" if isMemArray else meminst
            
            if isInput:
                string_loop += "writeMemFromFile<"+memclass+">("
                string_loop += memname+", "+flabel+", ievt);\n"
            else:
                string_loop += "err += compareMemWithFile<"+memclass+">("
                string_loop += memname+", "+flabel+", ievt, \""+memname+"\", "
                string_loop += "truncation);\n"

    string_mem += "\n"

    return string_mem, string_file, string_loop

def writeTestBench(topfunc, memories_in, memories_out, emData_dir, sector="04"):
    # memories_in, memories_out: list of (memModule(s), portname)
    
    string_tb = "// Test bench generated by generator_vhls.py\n"
    # headers
    string_tb += "#include <algorithm>\n"+"#include <iterator>\n\n"
    string_tb += "#include \"FileReadUtility.hh\"\n"
    string_tb += "#include \"Constants.hh\"\n"
    string_tb += "#include \""+topfunc+".h\"\n\n"
    
    string_tb += "const int nevents = 5;  // number of events to run\n\n"
    string_tb += "using namespace std;\n\n"
    #
    string_tb += "int main() {\n\n"
    string_tb += "// error counts\n int err = 0;\n\n"

    string_inmem, string_infile, string_writemem = writeTBMemories(
        memories_in, True, emData_dir, sector)
    string_outmem, string_outfile, string_compmem = writeTBMemories(
        memories_out, False, emData_dir, sector)

    string_tb += string_inmem
    string_tb += string_outmem
    string_tb += string_infile
    string_tb += string_outfile
    string_tb += "\n"

    # loop over events
    string_tb += "// loop over events\n"
    string_tb += "cout << \"Start event loop ...\" << endl;\n\n"
    string_tb += "for (unsigned int ievt = 0; ievt < nevents; ++ievt) {\n"
    string_tb += "cout << \"Event: \" << dec << ievt << endl;\n\n"
    string_tb += "// read event and write to memories\n"
    string_tb += string_writemem+"\n"
    # bx
    string_tb += "// bx\n"+"BXType bx = ievt;\n"+"BXType bx_out;\n\n"
    # call top function
    string_tb += "// Unit Under Test\n"
    string_tb += topfunc+"(bx,\n"
    # input memories
    for memModule in memories_in:
        if isinstance(memModule,list):
            string_tb += memModule[0].userlabel
        else:
            string_tb += memModule.inst
        string_tb += ",\n"
    # bx_o
    string_tb += "bx_out,\n"
    # output memories
    for memModule in memories_out:
        if isinstance(memModule,list):
            string_tb += memModule[0].userlabel
        else:
            string_tb += memModule.inst
        string_tb += ",\n"
    #
    string_tb = string_tb.rstrip(",\n")+");\n\n"

    # compare outputs
    string_tb += "// compare the computed outputs with the expected ones\n"
    string_tb += "bool truncation = false;\n"
    string_tb += string_compmem
    string_tb += "\n"+"} // end of the event loop\n\n"
    string_tb += "return err;\n\n"
    string_tb += "}"
    
    return string_tb

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
    string_tcl += "set_part {xcku115-flvb2104-2-e} -tool vivado\n"
    string_tcl += "create_clock -period 4 -name default\n"
    string_tcl += "#csim_design\n"
    string_tcl += "#csynth_design\n"
    string_tcl += "#cosim_design\n"
    string_tcl += "#export_design -rtl verilog -format ip_catalog\n"
    string_tcl += "\n"
    string_tcl += "#exit"

    return string_tcl
    
###############################

if __name__ == "__main__":
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Script to generate HLS top function for Tracklet project")
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

    parser.add_argument('--uut', type=str, default=None, help="Unit Under Test")
    parser.add_argument('-u', '--nupstream', type=int, default=0,
                        help="Number of upstream processing steps to include")
    parser.add_argument('-d', '--ndownstream', type=int, default=0,
                        help="Number of downstream processing steps to include")

    parser.add_argument('--emData_dir', type=str, default="",
                        help="Directory where emulation printouts are stored")
    parser.add_argument('--hls_src_dir', type=str,
                        default="../firmware-hls/TrackletAlgorithm/",
                        help="HLS source code directory")
    #parser.add_argument('--indent', type=str, default="  ",
    #                    help="Indentation")
    #parser.add_argument('-d','--debug', action='store_true',
    #                    help="Turn on for debugging")
    
    args = parser.parse_args()

    ########################################
    # Read configuration files and setup TrackletGraph
    ########################################

    tracklet = TrackletGraph.from_configs(args.procconfig, args.memconfig,
                                          args.wireconfig)

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
    string_memories = writeMemoryModules(memList_inside)

    # Write processing modules
    string_processing = writeProcModules(process_list, args.hls_src_dir)

    # Top function interface
    string_topfunction = writeTopFunction(args.topfunc, memList_topin,
                                          memList_topout)

    # Header
    string_header = writeHeaderFile(args.topfunc, string_topfunction)
    
    # Source
    string_src = writeSourceFile(args.topfunc, string_topfunction,
                                 string_memories, string_processing)

    ###############
    # Test bench
    string_testbench = writeTestBench(args.topfunc, memList_topin,
                                      memList_topout, args.emData_dir)
                                      #,args.sector)
    ###############

    # tcl
    string_tcl = writeTcl(args.projname, args.topfunc, args.emData_dir)
    
    # Write to disk
    fname_src = args.topfunc+".cpp"
    fname_header = args.topfunc+".h"
    fname_tb = args.topfunc+"_test.cpp"
    fname_tcl = "script_"+args.projname+".tcl"
    
    fout_source = open(fname_src,"w")
    fout_source.write(string_src)
    
    fout_header = open(fname_header,"w")
    fout_header.write(string_header)

    fout_testbench = open(fname_tb, "w")
    fout_testbench.write(string_testbench)

    fout_tcl = open(fname_tcl, "w")
    fout_tcl.write(string_tcl)

    print "Output source file:", fname_src
    print "Output header file:", fname_header
    print "Output test bench file:", fname_tb
    print "Output tcl script:", fname_tcl
    
