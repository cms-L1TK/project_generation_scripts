#!/usr/bin/env python

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

ProcOrder_dict = {
    'VMRouter':1,
    'TrackletEngine':2,
    'TrackletCalculator':3,
    'ProjectionRouter':4,
    'MatchEngine':5,
    'MatchCalculator':6,
    'DiskMatchCalculator':6,
    'FitTrack':7,
    'PurgeDuplicate':8
}

########################################
# Define processing and memory module classes
########################################
class Node:
    def __init__(self, module_type, instance_name):
        self.mtype = module_type
        self.inst = instance_name
        self.upstreams = [] # list of pointers to upstream Nodes
        self.downstreams = [] # list of pointers to downstream Nodes

class MemModule(Node):
    def __init__(self, module_type, instance_name):
        Node.__init__(self, module_type, instance_name)
        self.size = None

class ProcModule(Node):
    def __init__(self, module_type, instance_name):
        Node.__init__(self, module_type, instance_name)
        self.parameters = {} # dictionary of parameters
        self.order = ProcOrder_dict[module_type]
        
########################################
# Functions to read the configuration file
########################################
#########
# Memory
def getMemDictFromConfig(fname_mconfig):
    # Output dictionary for memory modules:
    # Key: instance name; Value: memory MemModule object
    mem_dict = {}
    
    # Open and read memory configuration file
    file_mem = open(fname_mconfig, 'r')

    for line_mem in file_mem:
        # Memory type
        mem_type = line_mem.split(':')[0].strip()
        mem_class_hls = HLSNames_dict[mem_type]
        # Instance name
        mem_inst = line_mem.split(':')[1].strip().split(' ')[0]
        # Construct MemModule object
        aMemMod = MemModule(mem_class_hls, mem_inst)
        # Add to dictionary
        mem_dict[mem_inst] = aMemMod

    # Close file
    file_mem.close()

    return mem_dict

#########
# Processing module
def getProcDictFromConfig(fname_pconfig):
    # Output dictionary for processing modules:
    # Key: instance name; Value: ProcModule object
    proc_dict = {}

    # Open and read processing module configuration file
    file_proc = open(fname_pconfig, 'r')

    for line_proc in file_proc:
        # Processing module type
        proc_type = line_proc.split(':')[0].strip()
        # Instance name
        proc_inst = line_proc.split(':')[1].strip()
        # Construct ProcModule object
        aProcMod = ProcModule(proc_type, proc_inst)
        # TODO: determine parameters here?
        
        # Add to dictionary
        proc_dict[proc_inst] = aProcMod

    # Close file
    file_proc.close()
    
    return proc_dict

#########
# Wiring
def wireModulesFromConfig(fname_wconfig, p_dict, m_dict):

    # Read wiring config and add input and output memories to objects in p_dict  
    # p_dict: processing module dictionary generated earlier
    # m_dict: memory module dictionary generated earlier
    assert(len(p_dict)>0 and len(m_dict)>0)
    
    # Open and read the wiring configuration file
    file_wires = open(fname_wconfig, 'r')

    for line_wire in file_wires:
        ######
        # memory instance in wiring config
        wmem_inst = line_wire.split('input=>')[0].strip()
        iMem = m_dict[wmem_inst]

        ######
        # processing module that writes to this memory
        upstr = line_wire.split('input=>')[1].split('output=>')[0].strip()
        iproc_write = upstr.split('.')[0].strip()

        if iproc_write != '': # if it has an upstream module
            # Get the processing module and make the connections
            iMem.upstreams.append(p_dict[iproc_write])
            p_dict[iproc_write].downstreams.append(iMem)

        ######
        # processing module that reads from this memory
        downstr = line_wire.split('input=>')[1].split('output=>')[1].strip()
        iproc_read = downstr.split('.')[0].strip()

        if iproc_read != '': # if it has a downstream module
            # Get the downstream processing module and make the connections
            iMem.downstreams.append(p_dict[iproc_read])
            p_dict[iproc_read].upstreams.append(iMem)

    # Close file
    file_wires.close()

########################################
# Functions to write strings
########################################
#########
# Memories
def writeMemories(mem_dict, streaminput=False, indentation="  "):
    # mem_dict: the memory dictionary
    
    string_mem = "" 
    string_tin = "" # for inputs in the top function interface
    string_tout = "" # for outputs in the top function interface

    memclass_pre = ""
    # Loop over all memories
    for imem in mem_dict:
        aMemMod = mem_dict[imem]
        memclass = aMemMod.mtype
        if memclass != memclass_pre:
            # We have a new type of memories. Insert an empty line.
            string_mem += "\n"

        memclass_pre = memclass

        if not streaminput:
            # Top function arguments are pointers to memory objects
            if len(aMemMod.upstreams)==0: # Memory in the first step
                string_tin += indentation+"const "+memclass+"* const "+imem+",\n"
            elif len(aMemMod.downstreams)==0: # Memory in the last step
                string_tout += indentation+memclass+"* const "+imem+",\n"
            else:
                string_mem += indentation+"static "+memclass+" "+imem+";\n"
        else:
            # Top function uses hls::stream as input/output arguments
            print "Stream mode currently is not supported. Coming soon."
            # Need the configuration file to map the input link to memories
            assert(0)
            # All memories are instantiated in the top function
            #string_mem += indentation+"static "+memclass+" "+imem+"\n"
            # Input and output arguments of the top function are hls::stream
            #string_tin +=
            #string_tout +=

    return string_mem, string_tin, string_tout

#########
# Processing modules
def writeProcModules(proc_dict, indentation):
    # FIXME:
    # (1) add template paramters
    # (2) how to label functions with instance name?
    # (3) how to propagate BXs?
    
    string_proc = ""

    # Sort the dictionary keys based on their values
    pkeys_sorted = sorted(proc_dict, key=lambda x: proc_dict[x].order)

    for pkey in pkeys_sorted:
        # Get the processing module
        aProcMod = proc_dict[pkey]
        
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
    string_src = "#include \""+args.topfunc+".h\"\n\n"
    string_src += string_finterface
    string_src += "{\n"
    string_src += string_mem
    string_src += "\n"
    string_src += string_proc
    string_src += "}\n"

    return string_src
    
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
    parser.add_argument('-u', '--unstream', type=int, default=1,
                        help="Number of upstream processing steps to include")
    parser.add_argument('-d', '--downstream', type=int, default=1,
                        help="Number of downstream processing steps to include")
    
    parser.add_argument('--indent', type=str, default="  ",
                        help="Indentation")
    #parser.add_argument('-d','--debug', action='store_true',
    #                    help="Turn on for debugging")
    
    args = parser.parse_args()

    ########################################
    # Read configuration files
    # Setup module dictionaries and connections
    ########################################
    # Memory modules
    #
    # Get a dictionary for memories from the configuration file
    # Key: instance name; Value: MemModule object
    memory_dict = getMemDictFromConfig(args.memconfig)
    
    #  Processing modules
    #
    # Get a dictionary for processing modules from the configuration file
    # Key: instance name; Value: ProcModule object
    process_dict = getProcDictFromConfig(args.procconfig)
    
    #  Wiring
    #
    # Connect the modules
    wireModulesFromConfig(args.wireconfig, process_dict, memory_dict)
    
    ########################################
    # Skimming 
    ########################################
    #if args.uut is not None:
    #    process_dict_skim = {}
    #    memory_dict_skim = {}
    #
    #    if args.uut in process_dict:
    #        aproc = process_dict[args.uut]    
    #        process_dict_skim[args.uut] = aproc
    #        
    #        # get all its input memories
    #        for imemtype in aproc.inputs
    
    ########################################
    #  Write HLS top function
    ########################################
    # Memories
    string_memories, string_topin, string_topout = writeMemories(
        memory_dict, args.stream, args.indent)
    
    # Processing modules
    string_processing = writeProcModules(process_dict, args.indent)
    
    # Top function interface
    string_topfunction = writeTopFunction(args.topfunc, string_topin,
                                          string_topout, args.indent)

    # Header
    string_header = writeHeaderFile(args.topfunc, string_topfunction)
    
    # Source
    string_main = writeSourceFile(args.topfunc, string_topfunction,
                                  string_memories, string_processing)

    # Write to disk
    fname_src = args.topfunc+".cpp"
    fname_header = args.topfunc+".h"
    
    fout_source = open(fname_src,"w")
    fout_source.write(string_main)
    
    fout_header = open(fname_header,"w")
    fout_header.write(string_header)

    print "Output source file:", fname_src
    print "Output header file:", fname_header
