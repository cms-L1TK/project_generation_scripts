#!/usr/bin/env python

from TrackletGraph import MemModule, ProcModule, TrackletGraph
import os

########################################
# A map between module names in the configuration file and HLS class name
### UPDATE ME ###
HLSNames_dict = {
    # memories
    'InputLink':'InputStubMemory',
    'VMStubsTE':'VMStubMemory',
    'VMStubsME':'VMStubMemory',
    'StubPairs':'StubPairMemory',
    'AllStubs':'AllStubMemory',
    'StubPairs':'StubPairMemory',
    'TrackletProjections':'TrackletProjectionMemory',
    'VMProjections':'VMProjectionMemory',
    'CandidateMatch':'CandidateMatchMemory',
    'AllProj':'AllProjectionMemory',
    'FullMatch':'FullMatchMemory',
    'TrackletParameters':'TrackletParameterMemory',
    'TrackFit':'TrackFitMemory',
    'CleanTrack':'CleanTrackMemory',
    # processing module names are the same
}

#########


########################################
# Functions to write strings
########################################
#########
# Memories
def writeMemories(mem_list, streaminput=False, indentation="  "):
    # mem_dict: the memory dictionary
    
    string_mem = "" 
    string_tin = "" # for inputs in the top function interface
    string_tout = "" # for outputs in the top function interface

    memclass_pre = ""
    # Loop over all memories
    for aMemMod in mem_list:
        memclass = HLSNames_dict[aMemMod.mtype]
        if memclass != memclass_pre:
            # We have a new type of memories. Insert an empty line.
            string_mem += "\n"

        memclass_pre = memclass

        if not streaminput:
            # Top function arguments are pointers to memory objects
            if aMemMod.is_initial: # Memory in the initial step
                string_tin += indentation+"const "+memclass+"* const "+aMemMod.inst+",\n"
            elif aMemMod.is_final: # Memory in the last step
                string_tout += indentation+memclass+"* const "+aMemMod.inst+",\n"
            else:
                string_mem += indentation+"static "+memclass+" "+aMemMod.inst+";\n"
        else:
            # Top function uses hls::stream as input/output arguments
            print "Stream mode currently is not supported. Coming soon."
            # Need the configuration file to map the input link to memories
            assert(0)
            # All memories are instantiated in the top function
            #string_mem += indentation+"static "+memclass+" "+aMemMod.inst+"\n"
            # Input and output arguments of the top function are hls::stream
            #string_tin +=
            #string_tout +=

    return string_mem, string_tin, string_tout

#########
# Processing modules
def writeProcModules(proc_list, indentation):
    # FIXME:
    # (1) add template paramters
    # (2) how to label functions with instance name?
    # (3) how to propagate BXs?
    
    string_proc = ""

    # Sort the processing module list
    proc_list.sort(key=lambda x: x.order)

    for aProcMod in proc_list:
        
        string_proc += indentation + aProcMod.mtype+"("

        memtype_pre = ""
        # inputs
        string_proc += indentation+indentation
        for iMem in aProcMod.upstreams:
            if iMem.mtype!=memtype_pre:
                string_proc += "\n"       
            string_proc += "&"+iMem.inst+", "
            memtype_pre = iMem.mtype

        # FIXME: fill zeros for unconnected ports
            
        # outputs
        string_proc += indentation+indentation
        for oMem in aProcMod.downstreams:
            if oMem.mtype!=memtype_pre:
                string_proc += "\n"
            string_proc += "&"+oMem.inst+", "
            memtype_pre = oMem.mtype

        # FIXME: fill zeros for unconnected ports

        # Get rid of the last ',' and close parentheses
        string_proc = string_proc.rstrip(", ")+");\n\n"
        
    return string_proc

#########
# Top function interface
def writeTopFunction(topfunc, string_inputs, string_outputs,
                     indentation="  "):
    string_topfunc = "void "+topfunc+"(\n"
    
    # BX
    string_topfunc += indentation+"BXType bx\n"
    
    # Input ports
    string_topfunc += string_inputs
    
    # BX output
    string_topfunc += indentation+"BXType& bx_o\n"
    
    # Output ports
    # get rid of the last ','
    string_outputs = string_outputs.rstrip(",\n")+"\n"
    string_topfunc += string_outputs

    string_topfunc += ")\n"

    return string_topfunc

#########
# Header
def writeHeaderFile(topfunc, string_finterface):
    header = "#ifndef "+topfunc.upper()+"_H\n"
    header += "#define "+topfunc.upper()+"_H\n"
    header += "\n"

    # TODO: include
    header += "TODO: add inlcude here \n"
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
def writeTBMemories(mem_list, isInput, emData_dir, sector="04"):
    inout = "input" if isInput else "output"
    
    string_mem = "///////////////////////////\n// "+inout+" memories\n"
    string_file = "///////////////////////////\n// open "+inout+" files\n"
    string_loop = ""
    string_interface = ""
    
    mem_dict = TrackletGraph.get_input_mem_dict(mem_list) if isInput else TrackletGraph.get_output_mem_dict(mem_list)

    for memtype in mem_dict:
        memories = mem_dict[memtype]
        for mem in memories:
            string_mem += "static "+HLSNames_dict[mem.mtype]+" "+mem.inst+";\n"
            
            validflag = "valid_"+mem.inst
            flabel = "f"+inout+"_"+mem.inst
            fname = emData_dir+mem.mtype+"_"+mem.inst+"_"+sector+".dat"        
            string_file += "ifstream "+flabel+";\n"
            string_file += "bool "+validflag+" = openDataFile("+flabel+", \""+fname+"\");\n"
            string_file += "if (not "+validflag+") return -1;\n\n"

            if isInput:
                string_loop += "writeMemFromFile<"+HLSNames_dict[mem.mtype]+">("
                string_loop += mem.inst+", "+flabel+", ievt);\n"
            else:
                string_loop += "err += compareMemWithFile<"+HLSNames_dict[mem.mtype]+">("
                string_loop += mem.inst+", "+flabel+", ievt, \""+mem.inst+"\", "
                string_loop += "truncation);\n"

            string_interface += "&"+mem.inst+", "
                
        string_mem += "\n"
        string_interface += "\n"

    return string_mem, string_file, string_loop, string_interface

def writeTestBench(topfunc, mem_list, emData_dir, sector="04"):
    string_tb = "// Test bench generated by generator_vhls.py\n"
    # headers
    string_tb += "#include <algorithm>\n"+"#include <iterator>\n\n"
    string_tb += "#include \"FileReadUtility.hh\"\n"
    string_tb += "#include \"Constants.hh\"\n"
    string_tb += "#include "+topfunc+".h\n\n"

    string_tb += "const int nevents = 100;  // number of events to run\n\n"
    string_tb += "using namespace std;\n\n"
    #
    string_tb += "int main() {\n\n"
    string_tb += "// error counts\n int err = 0;\n\n"
    
    # Input memories
    string_inmem,string_infile,string_writemem,string_topin = writeTBMemories(
        mem_list, True, emData_dir, sector)
    # Output memories
    string_outmem,string_outfile,string_compmem,string_topout = writeTBMemories(
        mem_list, False, emData_dir, sector)
    string_tb += string_inmem
    string_tb += string_outmem
    string_tb += string_infile
    string_tb += string_outfile
    string_tb += "\n"
    
    # loop over events
    string_tb += "// loop over events\n"
    string_tb += "cout << \"Start event loop ...\" << endl;"
    string_tb += "for (unsigned int ievt = 0; ievt < nevents; ++ievt) {\n"
    string_tb += "cout << \"Event: \" << dec << ievt << endl;\n\n"
    string_tb += "// read event and write to memories\n"
    string_tb += string_writemem+"\n"
    # bx
    string_tb += "// bx\n"+"BXType bx = ievt;\n"+"BXType bx_out;\n\n"
    # call top function
    string_tb += "// Unit Under Test\n"
    string_tb += topfunc+"(bx,\n"
    string_tb += string_topin
    string_tb += "bx_out,\n"
    string_tb += string_topout.rstrip(", \n")+");\n\n"
    
    # compare outputs
    string_tb += "// compare the computed outputs with the expected ones\n"
    string_tb += "bool truncation = false;\n"
    string_tb += string_compmem
    string_tb += "\n"+"} // end of the event loop\n\n"
    string_tb += "return err;\n\n"
    string_tb += "}"

    return string_tb
    
###############################

if __name__ == "__main__":
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Script to generate HLS top function for Tracklet project")
    parser.add_argument('-f', '--topfunc', type=str, default="SectorProcessor",
                        help="HLS top function name")
    
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
    parser.add_argument('--indent', type=str, default="  ",
                        help="Indentation")
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
    # Memories
    string_memories, string_topin, string_topout = writeMemories(
        memory_list, args.stream, args.indent)
    
    # Processing modules
    string_processing = writeProcModules(process_list, args.indent)
    
    # Top function interface
    string_topfunction = writeTopFunction(args.topfunc, string_topin,
                                          string_topout, args.indent)

    # Header
    string_header = writeHeaderFile(args.topfunc, string_topfunction)
    
    # Source
    string_main = writeSourceFile(args.topfunc, string_topfunction,
                                  string_memories, string_processing)

    # Test bench
    string_testbench = writeTestBench(args.topfunc, memory_list, args.emData_dir)
    
    # Write to disk
    fname_src = args.topfunc+".cpp"
    fname_header = args.topfunc+".h"
    fname_tb = args.topfunc+"_test.cpp"
    
    fout_source = open(fname_src,"w")
    fout_source.write(string_main)
    
    fout_header = open(fname_header,"w")
    fout_header.write(string_header)

    fout_testbench = open(fname_tb, "w")
    fout_testbench.write(string_testbench)

    print "Output source file:", fname_src
    print "Output header file:", fname_header
    print "Output test bench file:", fname_tb
