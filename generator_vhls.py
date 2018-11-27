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

########################################
# Define processing module class
########################################
class ProcModule:
    def  __init__(self, module_type, instance_name):
        self.mtype = module_type
        self.inst = instance_name
        # Dictionaries of input and output memories.
        # key: memtype; value: list of instances
        self.inputs = {} 
        self.outputs = {}
        self.parameters = {} # dictionary of parameters

########################################
# Functions to read the configuration file
########################################
#########
# Memory
def getMemDictFromConfig(fname_mconfig):
    # Output dictionary for memory modules:
    # Key: instance name; Value: memory class name
    mem_dict = {}
    
    # Open and read memory configuration file
    file_mem = open(fname_mconfig, 'r')

    for line_mem in file_mem:
        # Memory type
        mem_type = line_mem.split(':')[0].strip()  
        # Instance name
        mem_inst = line_mem.split(':')[1].strip().split(' ')[0]
        # Add to dictionary
        mem_dict[mem_inst] = HLSNames_dict[mem_type]

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

    # Types of memories as inputs to the first processing step
    first_mtype = set()
    # Types of memories as outputs of the last processing step
    last_mtype = set()
    
    # Open and read the wiring configuration file
    file_wires = open(fname_wconfig, 'r')

    for line_wire in file_wires:
        # memory instance in wiring config
        wmem_inst = line_wire.split('input=>')[0].strip()
        wmem_type = m_dict[wmem_inst]

        # processing module that writes to this memory
        upstream = line_wire.split('input=>')[1].split('output=>')[0].strip()
        aproc_write = upstream.split('.')[0].strip()

        if aproc_write == '': # no upstream module
            first_mtype.add(wmem_type)
        else:
            # Get the upstream proc module and add the memory into its outputs

            # If the first time wmem_type is added to the proc module outputs
            if wmem_type not in p_dict[aproc_write].outputs:
                # create an empty list
                p_dict[aproc_write].outputs[wmem_type] = []

            p_dict[aproc_write].outputs[wmem_type].append(wmem_inst)

        # processing module that reads from this memory
        downstream = line_wire.split('input=>')[1].split('output=>')[1].strip()
        aproc_read = downstream.split('.')[0].strip()

        if aproc_read == '': # no downstream module
            last_mtype.add(wmem_type)
        else:
            # Get the downstream proc module and add the memory into its inputs

            # If the first time wmem_type is added to the proc module inputs
            if wmem_type not in p_dict[aproc_read].inputs:
                # create an empty list
                p_dict[aproc_read].inputs[wmem_type] = []

            p_dict[aproc_read].inputs[wmem_type].append(wmem_inst)

    # Close file
    file_wires.close()

    return first_mtype, last_mtype

########################################
# Functions to write strings
########################################
#########
# Memories
def writeMemories(mem_dict, inmem_types, outmem_types, streaminput=False,
                  indentation="  "):
    # mem_dict: the memory dictionary
    # inmem_types: a set of memory types for top function inputs
    # outmem_types: a set of memory types for top function outputs 
    
    
    string_mem = "" 
    string_tin = "" # for inputs in the top function interface
    string_tout = "" # for outputs in the top function interface

    memclass_pre = ""
    # Loop over all memories
    for imem in mem_dict:
        memclass = mem_dict[imem]
        if memclass != memclass_pre:
            # We have a new type of memories. Insert an empty line.
            string_mem += "\n"

        memclass_pre = memclass

        if not streaminput:
            # Top function arguments are pointers to memory objects
            if memclass in inmem_types:
                string_tin += indentation+"const "+memclass+"* const "+imem+",\n"
            elif memclass in outmem_types:
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
    
    for pkey, aproc in proc_dict.iteritems():
        string_proc += indentation+aproc.mtype+"(\n"
        
        # inputs
        string_proc += indentation+indentation
        for imemtype in aproc.inputs:
            imemlist = aproc.inputs[imemtype]
            for imem in imemlist:
                string_proc += "&"+imem+", "
            string_proc += "\n"

        # FIXME: fill zeros for unconnected ports
            
        # outputs
        string_proc += indentation+indentation
        for omemtype in aproc.outputs:
            omemlist = aproc.outputs[omemtype]
            for omem in omemlist:
                string_proc += "&"+omem+", "
            string_proc += "\n"

        # FIXME: fill zeros for unconnected ports

        # Get rid of the last ',' and close function
        string_proc = string_proc.rstrip(", \n")+");\n\n"
        
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
    parser.add_argument('-s','--stream', action='store_true', help="True if want hls::stream objects on the interface, otherwise top function arguments are memory pointers")
    parser.add_argument('-f', '--topfunc', type=str, default="SectorProcessor",
                        help="HLS top function name")
    parser.add_argument('-p','--procconfig', type=str, default="processingmodules.dat",
                        help="Name of the configuration file for processing modules")
    parser.add_argument('-m','--memconfig', type=str, default="memorymodules.dat",
                        help="Name of the configuration file for memory modules")
    parser.add_argument('-w','--wireconfig', type=str, default="wires.dat",
                        help="Name of the configuration file for wiring")
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
    # Key: instance name; Value: memory class name
    memory_dict = getMemDictFromConfig(args.memconfig)
    
    #  Processing modules
    #
    # Get a dictionary for processing modules from the configuration file
    # Key: instance name; Value: ProcModule object
    process_dict = getProcDictFromConfig(args.procconfig)
    
    #  Wiring
    #
    first_memtype, last_memtype = wireModulesFromConfig(args.wireconfig,
                                                        process_dict,
                                                        memory_dict)

    ########################################
    #  Write HLS top function
    ########################################
    # Memories
    string_memories, string_topin, string_topout = writeMemories(memory_dict,
                                                                 first_memtype,
                                                                 last_memtype,
                                                                 args.stream,
                                                                 args.indent)
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
