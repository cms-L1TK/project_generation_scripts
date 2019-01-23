#!/usr/bin/env python

from TrackletGraph import MemModule, ProcModule, TrackletGraph
from collections import deque
import os

########################################
# Functions to write strings
########################################
#########
# Memories
def getMemoryClassName_InputStub(instance_name):
    # Two examples of instance name: IL_L1PHIB_neg_PS10G_1_A, IL_L1PHIH_PS10G_2_B
    position = instance_name.split('_')[1][:2] # layer/disk
    ptmodule = instance_name.replace('_neg','').split('_')[2][:2] # PS or 2S

    bitformat = ''
    if 'L' in position:
        bitformat += 'BARREL'
    else:
        assert('D' in position)
        bitformat += 'DISK'

    assert(ptmodule in ['PS', '2S'])
    bitformat += ptmodule

    return 'InputStubMemory<'+bitformat+'>'
    
def getMemoryClassName_VMStubsTE(instance_name):
    # An example of instance name: VMSTE_L6PHIB15n3
    position = instance_name.split('_')[1][:2] # layer/disk
    philabel = instance_name.split('_')[1][5] # PHI

    memoryclass = ''
    bitformat = ''
    
    if position == 'L1':
        memoryclass = 'VMStubTEInnerMemory'  
        if philabel in ['Q','R','S','T','W','X','Y','Z']: # L1D1 seeding
            bitformat = 'BARRELOL'
        elif philabel in ['A','B','C','D','E','F','G','H']: # L1L2 seeding
            bitformat = 'BARRELPS'
        else:
            raise ValueError("Unknown PHI label "+philabel)
        
    elif position == 'L2':
        if philabel in ['I','J','K','L','W','X','Y','Z']: # L2L3 or L2D1 seeding
            memoryclass = 'VMStubTEInnerMemory'
            bitformat = 'BARRELOL'
        elif philabel in ['A','B','C','D']: # L1L2 seeding
            memoryclass = 'VMStubTEOuterMemory'
            bitformat = 'BARRELPS'
        else:
            raise ValueError("Unknown PHI label "+philabel)
        
    elif position == 'L3':
        if philabel in ['A','B','C','D']: # L3L4
            memoryclass = 'VMStubTEInnerMemory'
            bitformat = 'BARRELPS'
        elif philabel in ['I','J','K','L']: # L2L3
            memoryclass = 'VMStubTEOuterMemory'
            bitformat = 'BARRELPS'
        else:
            raise ValueError("Unknown PHI label "+philabel)
        
    elif position == 'L4' or position == 'L6':
        assert(philabel in ['A','B','C','D']) # L3L4, L5L6 seeding
        memoryclass = 'VMStubTEOuterMemory'
        bitformat = 'BARREL2S'
        
    elif position == 'L5':
        assert(philabel in ['A','B','C','D']) # L5L6 seeding
        memoryclass = 'VMStubTEInnerMemory'
        bitformat = 'BARREL2S'
        
    elif position == 'D1':
        if philabel in ['A','B','C','D']: # D1D2 seeding
            memoryclass = 'VMStubTEInnerMemory'
            bitformat = 'DISK'
        elif philabel in ['W','X','Y','Z']: # L1D1 or L2D1 seeding
            memoryclass = 'VMStubTEOuterMemory'
            bitformat = 'DISK'
        else:
            raise ValueError("Unknown PHI label "+philabel)
            
    elif position == 'D2' or position == 'D4': 
        assert(philabel in ['A','B','C','D']) # D1D2 or D3D4 seeding
        memoryclass = 'VMStubTEOuterMemory'
        bitformat = 'DISK'

    elif position == 'D3':
        assert(philabel in ['A','B','C','D']) # D3D4 seeding
        memoryclass = 'VMStubTEInnerMemory'
        bitformat = 'DISK'
        
    assert(bitformat != '')
    return memoryclass+'<'+bitformat+'>'

def getMemoryClassName_VMStubsME(instance_name):
    # An example of instance name: VMSME_D3PHIB8n1
    position = instance_name.split('_')[1][:2] # layer/disk
    bitformat = ''
    
    if position in ['L1','L2','L3']:
        bitformat = 'BARRELPS'
    elif position in ['L4','L5','L6']:
        bitformat = 'BARREL2S'
    else: # Disk
        assert(bitformat in ['D1','D2','D3','D4','D5'])
        bitformat = 'DISK'

    return 'VMStubMEMemory<'+bitformat+'>'

def getMemoryClassName_AllStubs(instance_name):
    ######################
    # FIXME: mix 2S and PS disk allstubs?
    ######################
    
    # An example of instance name: AS_D1PHIAn5
    position = instance_name.split('_')[1][:2]
    if position in ['L1','L2','L3']:
        return 'AllStubMemory<BARRELPS>'
    elif position in ['L4','L5','L6']:
        return 'AllStubMemory<BARREL2S>'
    elif position in ['D1','D2','D3','D4','D5']:
        return 'AllStubMemory<DISK>'
    else:
        raise ValueError("Unknown Layer/Disk "+position)
    
def getMemoryClassName_StubPairs(instance_name):
    # e.g. SP_L1PHIA2_L2PHIA3
    assert('SP_' in instance_name)
    return 'StubPairMemory'

def getMemoryClassName_TrackletParameters(instance_name):
    # e.g. TPAR_L1L2L
    assert('TPAR_' in instance_name)
    return 'TrackletParameterMemory'

def getMemoryClassName_TrackletProjections(instance_name):
    # e.g. TPROJ_L5L6A_L1PHIB
    position = instance_name.split('_')[2][:2] # layer/disk
    bitformat = ''

    if position in ['L1','L2','L3']:
        bitformat = 'INNER'
    elif position in ['L4','L5','L6']:
        bitformat = 'OUTER'
    else: # Disk
        assert(bitformat in ['D1','D2','D3','D4','D5'])
        bitformat = 'DISK'

    return 'TrackletProjectionMemory<'+bitformat+'>'

def getMemoryClassName_AllProj(instance_name):
    # e.g. AP_L4PHIB
    position = instance_name.split('_')[1][:2] # layer/disk
    bitformat = ''

    if position in ['L1','L2','L3']:
        bitformat = 'BARRELPS' # INNER
    elif position in ['L4','L5','L6']:
        bitformat = 'BARREL2S' # OUTER
    else: # Disk
        assert(bitformat in ['D1','D2','D3','D4','D5'])
        bitformat = 'DISK'

    return 'AllProjectionMemory<'+bitformat+'>'

def getMemoryClassName_VMProjections(instance_name):
    # e.g. VMPROJ_D3PHIA2
    position = instance_name.split('_')[1][:2] # layer/disk
    if position in ['L1','L2','L3','L4','L5','L6']:
        return 'VMProjectionMemory<BARREL>'
    else:
        assert(positon in ['D1','D2','D3','D4','D5'])
        return 'VMProjectionMemory<DISK>'

def getMemoryClassName_CandidateMatch(instance_name):
    # e.g. CM_L2PHIA8
    assert('CM_' in instance_name)
    return 'CandidateMatchMemory'

def getMemoryClassName_FullMatch(instance_name):
    # e.g. FM_L5L6_L3PHIB
    position = instance_name.split('_')[2][:2]
    if position in ['L1','L2','L3','L4','L5','L6']:
        return 'FullMatchMemory<BARREL>'
    else:
        assert(positon in ['D1','D2','D3','D4','D5'])
        return 'FullMatchMemory<DISK>'

def getMemoryClassName_TrackFit(instance_name):
    # e.g. TF_L3L4
    assert('TF_' in instance_name)
    return 'TrackFitMemory'

def getMemoryClassName_CleanTrack(instance_name):
    # e.g. CT_L5L6
    assert('CT_' in instance_name)
    return 'CleanTrackMemory'


def getHLSClassName(module):

    if module.mtype == 'InputLink':
        return getMemoryClassName_InputStub(module.inst)
    elif module.mtype == 'VMStubsTE':
        return getMemoryClassName_VMStubsTE(module.inst)
    elif module.mtype == 'VMStubsME':
        return getMemoryClassName_VMStubsME(module.inst)
    elif module.mtype == 'AllStubs':
        return getMemoryClassName_AllStubs(module.inst)
    elif module.mtype == 'StubPairs':
        return getMemoryClassName_StubPairs(module.inst)
    elif module.mtype == 'TrackletParameters':
        return getMemoryClassName_TrackletParameters(module.inst)
    elif module.mtype == 'TrackletProjections':
        return getMemoryClassName_TrackletProjections(module.inst)
    elif module.mtype == 'AllProj':
        return getMemoryClassName_AllProj(module.inst)
    elif module.mtype == 'VMProjections':
        return getMemoryClassName_VMProjections(module.inst)
    elif module.mtype == 'CandidateMatch':
        return getMemoryClassName_CandidateMatch(module.inst)
    elif module.mtype == 'FullMatch':
        return getMemoryClassName_FullMatch(module.inst)
    elif module.mtype == 'TrackFit':
        return getMemoryClassName_TrackFit(module.inst)
    elif module.mtype == 'CleanTrack':
        return getMemoryClassName_CleanTrack(module.inst)
    else:
        raise ValueError(module.mtype + " is unknown.")
    
    
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

def getProcFunctionArgs(proc_name, hls_source_dir):
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

def writeProcArguments(aProcModule, hls_src_dir, indentation, mem_classes=[]):
    string_args = ''
    
    args_list = getProcFunctionArgs(aProcModule.mtype, hls_src_dir)

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
            if not (mem.is_initial or mem.is_final):
                string_args += "&"
            string_args += mem.inst+", "
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

def writeProcModules(proc_list, hls_src_dir, indentation):
    # FIXME:
    # (2) how to label functions with instance name?
    # (3) how to propagate BXs?
    
    string_proc = ""

    # Sort the processing module list
    proc_list.sort(key=lambda x: x.index)

    for aProcMod in proc_list:
        
        string_proc += indentation + aProcMod.mtype

        mem_class_list = []
        
        # function arguments
        string_arguments = writeProcArguments(aProcMod, hls_src_dir, indentation,
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
    string_topfunc += indentation+"BXType bx,\n"
    
    # Input ports
    string_topfunc += string_inputs
    
    # BX output
    string_topfunc += indentation+"BXType& bx_o,\n"
    
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

    # TODO: include all available/working processing functions
    header += "#include \"Constants.hh\"\n"
    header += "#include \"ProjectionRouter.hh\"\n"
    header += "#include \"MatchEngine.h\"\n"
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
def writeTBMemories(mem_list, isInput, trackletgraph, emData_dir, sector="04"):
    inout = "input" if isInput else "output"
    
    string_mem = "///////////////////////////\n// "+inout+" memories\n"
    string_file = "///////////////////////////\n// open "+inout+" files\n"
    string_loop = ""

    for (meminst, memclass) in mem_list:
        string_mem += "static "+memclass+" "+meminst+";\n"
        validflag = "valid_"+meminst
        flabel = "f"+inout+"_"+meminst
        memtype = trackletgraph.get_mem_module(meminst).mtype
        # special cases for VMStubsTE, VMStubsME and CandidateMatch
        memtype = memtype.rstrip("TE")
        memtype = memtype.rstrip("ME")
        memtype = memtype.replace("CandidateMatch","CandidateMatches")
        if emData_dir:
            emData_dir = emData_dir.rstrip('/')+'/'
        fname = emData_dir+memtype+"_"+meminst+"_"+sector+".dat"
        string_file += "ifstream "+flabel+";\n"
        string_file += "bool "+validflag+" = openDataFile("+flabel+", \""+fname+"\");\n"
        string_file += "if (not "+validflag+") return -1;\n\n"

        if isInput:
            string_loop += "writeMemFromFile<"+memclass+">("
            string_loop += meminst+", "+flabel+", ievt);\n"
        else:
            string_loop += "err += compareMemWithFile<"+memclass+">("
            string_loop += meminst+", "+flabel+", ievt, \""+meminst+"\", "
            string_loop += "truncation);\n"

    string_mem += "\n"
            
    return string_mem, string_file, string_loop

def writeTestBench(topfunc, string_inmem, string_outmem, trackletgraph,
                   emData_dir, sector="04"):

    string_tb = "// Test bench generated by generator_vhls.py\n"
    # headers
    string_tb += "#include <algorithm>\n"+"#include <iterator>\n\n"
    string_tb += "#include \"FileReadUtility.hh\"\n"
    string_tb += "#include \"Constants.hh\"\n"
    string_tb += "#include \""+topfunc+".h\"\n\n"

    string_tb += "const int nevents = 100;  // number of events to run\n\n"
    string_tb += "using namespace std;\n\n"
    #
    string_tb += "int main() {\n\n"
    string_tb += "// error counts\n int err = 0;\n\n"

    # Lists of input memories (mem_inst, mem_class)
    inmem_list = [(x.strip().split(' ')[-1], x.strip().split('const')[-2].strip().rstrip('*')) for x in string_inmem.split(",\n") if x]
    
    # Lists of output memories (mem_inst, mem_class)
    outmem_list = [(x.strip().split(' ')[-1], x.strip().split('const')[-2].strip().rstrip('*')) for x in string_outmem.split(",\n") if x]

    # Input memories
    string_inmem, string_infile, string_writemem = writeTBMemories(
        inmem_list, True, trackletgraph, emData_dir, sector)
    # Output memories
    string_outmem, string_outfile, string_compmem = writeTBMemories(
        outmem_list, False, trackletgraph, emData_dir, sector)
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
    for imem in inmem_list:
        string_tb += "&"+imem[0]+",\n"
    string_tb += "bx_out,\n"
    for omem in outmem_list:
        string_tb += "&"+omem[0]+",\n"
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
    string_tcl += "add_files ../TrackletAlgorithm/MatchEngine.cpp -cflags \"-std=c++11\"\n"
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
    string_processing = writeProcModules(process_list, args.hls_src_dir,
                                         args.indent)
    
    # Top function interface
    string_topfunction = writeTopFunction(args.topfunc, string_topin,
                                          string_topout, args.indent)

    # Header
    string_header = writeHeaderFile(args.topfunc, string_topfunction)
    
    # Source
    string_main = writeSourceFile(args.topfunc, string_topfunction,
                                  string_memories, string_processing)

    # Test bench
    string_testbench = writeTestBench(args.topfunc, string_topin, string_topout,
                                      tracklet, args.emData_dir)

    # tcl
    string_tcl = writeTcl(args.projname, args.topfunc, args.emData_dir)
    
    # Write to disk
    fname_src = args.topfunc+".cpp"
    fname_header = args.topfunc+".h"
    fname_tb = args.topfunc+"_test.cpp"
    fname_tcl = "script_"+args.projname+".tcl"
    
    fout_source = open(fname_src,"w")
    fout_source.write(string_main)
    
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
    
