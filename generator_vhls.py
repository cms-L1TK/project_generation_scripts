#!/usr/bin/env python

from TrackletGraph import MemModule, ProcModule, TrackletGraph
from collections import deque
import os

########################################
# A map between module names in the configuration file and HLS class name
### UPDATE ME ###
#HLSNames_dict = {
#    # memories
#    'InputLink':'InputStubMemory',
#    'VMStubsTE':'VMStubMemory',
#    'VMStubsME':'VMStubMemory',
#    'StubPairs':'StubPairMemory',
#    'AllStubs':'AllStubMemory',
#    'StubPairs':'StubPairMemory',
#    'TrackletProjections':'TrackletProjectionMemory',
#    'VMProjections':'VMProjectionMemory',
#    'CandidateMatch':'CandidateMatchMemory',
#    'AllProj':'AllProjectionMemory',
#    'FullMatch':'FullMatchMemory',
#    'TrackletParameters':'TrackletParameterMemory',
#    'TrackFit':'TrackFitMemory',
#    'CleanTrack':'CleanTrackMemory',
#    # processing module names are the same
#}
    
#########


########################################
# Functions to write strings
########################################
#########
# Memories
def getHLSClassName(module):  # UPDATE ME
    module_type = module.mtype
    instance_name = module.inst
    
    if module.mtype == 'InputLink':
        return 'InputStubMemory'
    
    elif module_type == 'VMStubsTE':
        vmste = ''
        # class based on layer/disk position and phi region
        pos = instance_name.split('_')[1][:2] # layer/disk
        phi = instance_name.split('_')[1][5:6] # PHI
        if pos in ['L4','L6']: # L4L5, L5L6
            vmste = 'VMStubMemory' # barrel outer 2S
        elif pos in ['L5']: # L5L6
            vmste = 'VMStubMemory' # barrel inner 2S
        elif pos in ['D2','D4']: # D1D2, D3D4
            vmste = 'VMStubMemory' # disk outer
        elif pos in ['D3']: # D3D4
            vmste = 'VMStubMemory' # disk inner
        elif pos == 'D1':
            if phi in ['X','Y','Z','W','Q','R']: # L1D1 or L2D1
                vmste = 'VMStubMemory' # disk outer
            else: # D1D2
                vmste = 'VMStubMemory' # disk inner
        elif pos == 'L1':
            if phi in ['X','Y','Z','W','Q','R']: # L1D1
                vmste = 'VMStubMemory' # barrel inner L1D1
            else: # L1L2
                vmste = 'VMStubMemory' # barrel inner PS
        elif pos == 'L2':
            if phi in ['X','Y','Z','W','I','J','K','L']: # L2D1 or L2L3
                vmste = 'VMStubMemory' # barrel inner L2
            else: # L1L2
                vmste = 'VMStubMemory' # barrel outer PS
        elif pos == 'L3':
            if phi in ['I','J','K','L']: # L2L3
                vmste = 'VMStubMemory' # barrel outer PS
            else: # L3L4
                vmste = 'VMStubMemory' # barrel inner PS
        return vmste
    
    elif module_type == 'VMStubsME':
        vmsme = ''
        pos = instance_name.split('_')[1][:2] # layer/disk
        if pos in ['L1','L2','L3']: # barrel PS
            vmsme = 'VMStubMemory'
        elif pos in ['L4','L5','L6']: # barrel 2S
            vmsme = 'VMStubMemory'
        elif pos in ['D1','D2','D3','D4','D5']: # disk
            vmsme = 'VMStubMemory'
        return vmsme
    
    elif module_type == 'StubPairs':
        return 'StubPairMemory'
    elif module_type == 'AllStubs':
        return 'AllStubMemory'
    
    elif module_type == 'TrackletProjections':
        tproj = ''
        pos = instance_name.split('_')[2][:2] # layer/disk
        if pos in ['L1','L2','L3']: # barrel PS
            tproj = 'TrackletProjectionMemory'
        elif pos in ['L4','L5','L6']: # barrel 2S
            tproj = 'TrackletProjectionMemory'
        elif pos in ['D1','D2','D3','D4','D5']: # disk
            tproj = 'TrackletProjectionMemory'
        return tproj
    
    elif module_type == 'VMProjections':
        return 'VMProjectionMemory'
    elif module_type == 'CandidateMatch':
        return 'CandidateMatchMemory'
    elif module_type == 'AllProj':
        return 'AllProjectionMemory'
    elif module_type == 'FullMatch':
        return 'FullMatchMemory'
    elif module_type == 'TrackletParameters':
        return 'TrackletParameterMemory'
    elif module_type == 'TrackFit':
        return 'TrackFitMemory'
    elif module_type == 'CleanTrack':
        return 'CleanTrackMemory'
    else:
        return module_type
    
#########
def writeMemories(mem_list, streaminput=False, indentation="  "):
    # mem_dict: the memory dictionary
    
    string_mem = "" 
    string_tin = "" # for inputs in the top function interface
    string_tout = "" # for outputs in the top function interface

    memclass_pre = ""
    # Loop over all memories
    for aMemMod in sorted(mem_list,key=lambda x: x.index):
        memclass = getHLSClassName(aMemMod)
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
def parseProcFunctionDef(proc_header_file_name, proc_name):
    
    proc_str = ""
    
    file_proc_h = open(proc_header_file_name)
    
    for line in file_proc_h:
        # Search for "void proc_name("
        if "void "+proc_name+"(" in line:
            #print line[:line.index("//")].strip()
            proc_str += line.split("//",1)[0] # get rid of comments

            nextline = next(file_proc_h)
            while nextline:
                proc_str += nextline.split("//",1)[0] # get rid of comments
                if ")" in nextline:
                    nextline = ""
                else:
                    nextline = next(file_proc_h)

    file_proc_h.close()

    args_str = proc_str.split("(")[1].split(")")[0]
    arguments = []
    for arg in args_str.split(","):
        arg = arg.strip()
        # get rid of const and only get the types
        arg = arg.replace("const ","").split(' ')[0]
        arguments.append(arg)
    
    return arguments

def getProcFunctionArgs(proc_name,
                        # FIXME
                        hls_source_dir = "../firmware-hls/TrackletAlgorithm/"):
    header_name = proc_name + '.hh'

    # Hack for now. Should make all header file names consistent
    if proc_name in ['MatchEngine', 'TrackletEngine']:
        header_name = proc_name + '.h'

    full_name = hls_source_dir.rstrip('/')+'/'+header_name
        
    return parseProcFunctionDef(full_name, proc_name)


# 2D dictionary for processing function template memory type lookup
ProcTemplateMemTypes_dict = {
    # FIXME
    'ProjectionRouter': {'MemTypeTProj': 'TrackletProjections',
                         'MemTypeAProj': 'AllProj',
                         'MemTypeVMProj': 'VMProjections'},
    # ADD MORE HERE if the HLS function is templatized
}

def writeProcArguments(aProcModule, indentation, mem_classes=[]):
    string_args = ''
    
    args_list = getProcFunctionArgs(aProcModule.mtype)

    pre_type = ''
    mem_q = deque([])
    for argtype in args_list:
        # bunch crossing # FIXME
        if argtype=="BXType": 
            string_args += "\n"+"bx, "
            continue
        elif argtype=="BXType&":
            string_args += "\n"+"bx_o, "  # output bx
            continue

        # memories
        argtype = argtype.rstrip("*")
        #print argtype

        # check if function template is used
        # if so, need to map the mem types to the actual ones
        usetemplate = aProcModule.mtype in ProcTemplateMemTypes_dict

        if argtype != pre_type: # start to deal with a new memory type
            string_args += "\n"
            # make a new queue of memory modules of this type 
            mem_q.clear()
            memlist_tmp = []

            for amem in aProcModule.upstreams+aProcModule.downstreams:
                if usetemplate:
                    if amem.mtype == ProcTemplateMemTypes_dict[aProcModule.mtype][argtype]:
                        memlist_tmp.append(amem)
                        # Add HLS memory class to the list
                        hlsclass = getHLSClassName(amem)
                        if hlsclass not in mem_classes:
                            mem_classes.append(hlsclass)
                else:
                    # mem type is taken literally
                    if getHLSClassName(amem) == argtype:
                        memlist_tmp.append(amem)
                        # Add HLS memory class to the list
                        if argtype not in mem_classes:
                            mem_classes.append(argtype)
                            
            # sort
            memlist_tmp.sort(key=lambda x: x.index)
            mem_q = deque(memlist_tmp)

        if len(mem_q)>0:
            mem = mem_q.popleft()
            string_args += "&"+mem.inst+", "
        else:
            # write null pointer
            string_args += "0, "
        
        pre_type = argtype

    return string_args.rstrip(", ")

def writeTemplateParameters(aProcModule, mem_classes=[]):

    string_par = ""
    
    if aProcModule.mtype == "ProjectionRouter":
        # Memory classes
        assert(len(mem_classes)==3)
        for mclass in mem_classes:
            string_par += mclass+","

        # Data types
        string_par += string_par.replace("Memory","")
        
        # Number of inputs
        string_par += str(len(aProcModule.upstreams))+","
        
        # Layer/Disk
        procname = aProcModule.inst
        pos = procname.split('_')[1][:2]
        if pos[0] == 'L':  # layer
            string_par += pos[1]+",0"
        else: # pos[0] = 'D' disk
            string_par += "0,"+pos[1]
            
        string_par = "<"+string_par+">"

    return string_par

def writeProcModules(proc_list, indentation):
    # FIXME:
    # (1) add template paramters
    # (2) how to label functions with instance name?
    # (3) how to propagate BXs?
    
    string_proc = ""

    # Sort the processing module list
    proc_list.sort(key=lambda x: x.index)

    for aProcMod in proc_list:
        
        string_proc += indentation + aProcMod.mtype

        mem_class_list = []
        
        # function arguments
        string_arguments = writeProcArguments(aProcMod, indentation,
                                              mem_class_list)
        #print string_arguments
        
        # template arguments
        string_proc += writeTemplateParameters(aProcMod,mem_class_list)

        

        string_proc += "("
        string_proc += string_arguments
        string_proc += ");\n\n"
        
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
            string_mem += "static "+getHLSClassName(mem)+" "+mem.inst+";\n"
            
            validflag = "valid_"+mem.inst
            flabel = "f"+inout+"_"+mem.inst
            fname = emData_dir+mem.mtype+"_"+mem.inst+"_"+sector+".dat"        
            string_file += "ifstream "+flabel+";\n"
            string_file += "bool "+validflag+" = openDataFile("+flabel+", \""+fname+"\");\n"
            string_file += "if (not "+validflag+") return -1;\n\n"

            if isInput:
                string_loop += "writeMemFromFile<"+getHLSClassName(mem)+">("
                string_loop += mem.inst+", "+flabel+", ievt);\n"
            else:
                string_loop += "err += compareMemWithFile<"+getHLSClassName(mem)+">("
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

    #print getProcFunctionArgs("ProjectionRouter")
    #print getProcFunctionArgs("MatchEngine")
    
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
