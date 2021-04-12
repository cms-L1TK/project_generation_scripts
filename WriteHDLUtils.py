"""
# Utilities for writing Verilog code from Vivado HLS blocks
"""

#from collections import deque
from TrackletGraph import MemModule, ProcModule
from WriteVHDLSyntax import writeStartSwitchAndInternalBX, writeProcControlSignalPorts, writeProcBXPort, writeProcMemoryLHSPorts, writeProcMemoryRHSPorts, writeProcCombination
import re

def getMemoryClassName_InputStub(instance_name):
    """
    # Memory objects
    # Two examples of instance name: IL_L1PHIB_neg_PS10G_1_A, IL_L1PHIH_PS10G_2_B
    """
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
    """
    # An example of instance name: VMSTE_L6PHIB15n3
    """
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
    """
    # An example of instance name: VMSME_D3PHIB8n1
    """
    position = instance_name.split('_')[1][:2] # layer/disk
    bitformat = ''
    
    if position in ['L1','L2','L3']:
        bitformat = 'BARRELPS'
    elif position in ['L4','L5','L6']:
        bitformat = 'BARREL2S'
    else: # Disk
        assert(position in ['D1','D2','D3','D4','D5'])
        bitformat = 'DISK'

    return 'VMStubMEMemory<'+bitformat+'>'

def getMemoryClassName_AllStubs(instance_name):
    """
    # FIXME: separate Disk PS and 2S AllStub memories for MatchCalculator
    # when config files are updated
    """
    
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
    """
    # e.g. SP_L1PHIA2_L2PHIA3
    """
    assert('SP_' in instance_name)
    return 'StubPairMemory'

def getMemoryClassName_TrackletParameters(instance_name):
    """
    # e.g. TPAR_L1L2L
    """
    assert('TPAR_' in instance_name)
    return 'TrackletParameterMemory'

def getMemoryClassName_TrackletProjections(instance_name):
    """
    # e.g. TPROJ_L5L6A_L1PHIB
    """
    position = instance_name.split('_')[2][:2] # layer/disk
    bitformat = ''

    if position in ['L1','L2','L3']:
        bitformat = 'BARRELPS'
    elif position in ['L4','L5','L6']:
        bitformat = 'BARREL2S'
    else: # Disk
        assert(position in ['D1','D2','D3','D4','D5'])
        bitformat = 'DISK'

    return 'TrackletProjectionMemory<'+bitformat+'>'

def getMemoryClassName_AllProj(instance_name):
    """
    # e.g. AP_L4PHIB
    """
    position = instance_name.split('_')[1][:2] # layer/disk
    bitformat = ''

    if position in ['L1','L2','L3']:
        bitformat = 'BARRELPS'
    elif position in ['L4','L5','L6']:
        bitformat = 'BARREL2S'
    else: # Disk
        assert(position in ['D1','D2','D3','D4','D5'])
        bitformat = 'DISK'

    return 'AllProjectionMemory<'+bitformat+'>'

def getMemoryClassName_VMProjections(instance_name):
    """
    # e.g. VMPROJ_D3PHIA2
    """
    position = instance_name.split('_')[1][:2] # layer/disk
    if position in ['L1','L2','L3','L4','L5','L6']:
        return 'VMProjectionMemory<BARREL>'
    else:
        assert(position in ['D1','D2','D3','D4','D5'])
        return 'VMProjectionMemory<DISK>'

def getMemoryClassName_CandidateMatch(instance_name):
    """
    # e.g. CM_L2PHIA8
    """
    assert('CM_' in instance_name)
    return 'CandidateMatchMemory'

def getMemoryClassName_FullMatch(instance_name):
    """
    # e.g. FM_L5L6_L3PHIB
    """
    position = instance_name.split('_')[2][:2]
    if position in ['L1','L2','L3','L4','L5','L6']:
        return 'FullMatchMemory<BARREL>'
    else:
        assert(position in ['D1','D2','D3','D4','D5'])
        return 'FullMatchMemory<DISK>'

def getMemoryClassName_TrackFit(instance_name):
    """
    # e.g. TF_L3L4
    """
    assert('TF_' in instance_name)
    return 'TrackFitMemory'

def getMemoryClassName_CleanTrack(instance_name):
    """
    # e.g. CT_L5L6
    """
    assert('CT_' in instance_name)
    return 'CleanTrackMemory'

def getHLSMemoryClassName(module):

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

def labelConnectedMemoryArrays(proc_list):
    """
    # label those memories that will be constructed in an array
    # (if these scripts end up generating the HLS top levels, will this function
    # be needed? That is, even if the templated HLS function has arrays on the
    # interface, the top-level could still be individual memories, although you'd
    # still have to pass those individual memories to the templated block as an array
    """
    for aProcModule in proc_list:

        if aProcModule.mtype == 'TrackletCalculator':
            # stubpair and allstub memories are arrays
            # they are all inputs
            for inmem,inport in zip(aProcModule.upstreams,aProcModule.input_port_names):
                if 'stubpair' in inport:
                    inmem.userlabel = 'stubPairs_'+aProcModule.inst
                elif 'innerallstubin' in inport:
                    inmem.userlabel = 'innerStubs_'+aProcModule.inst
                elif 'outerallstubin' in inport:
                    inmem.userlabel = 'outerStubs_'+aProcModule.inst

        # add other processing steps here if they have array inputs/outputs
        #elif aProcModule.mtype == '':

def getListsOfGroupedMemories(aProcModule):
    """
    # Get a list of memories and a list of ports for a given processing module
    # The memories are further grouped in a list if they are expected to be
    # constructed and passed to the processing function as an array

    # add array name to 'userlabel' of the connected memory module
    """
    labelConnectedMemoryArrays([aProcModule])

    memList = list(aProcModule.upstreams + aProcModule.downstreams)
    portList = list(aProcModule.input_port_names + aProcModule.output_port_names)
    # sort?

    newmemList = []
    newportList = []
    arraycontainer_dict = {}

    for memory, portname in zip(memList, portList):
        if not memory.userlabel:  # default is '', i.e. no array label added
            newmemList.append(memory)
            newportList.append(portname)
        else:
            arrayname = memory.userlabel
            if arrayname not in arraycontainer_dict:
                arraycontainer_dict[arrayname] = [memory]
            else:
                arraycontainer_dict[arrayname].append(memory)
    # add back memory arrays
    for arrayname in arraycontainer_dict:
        newmemList.append(arraycontainer_dict[arrayname])
        newportList.append(arrayname)

    return newmemList, newportList

def groupAllConnectedMemories(proc_list, mem_list):
    """
    # Regroup memories into the lists called inside, topin, topout
    #   topin:  memories at the top of the fw block, stimulated by test bench
    #   inside: memories internal to the fw block
    #   topout: memories at the bottom of the fw blcok, read by test bench
    """

    memories_topin = []  # input memories at the top function interface
    memories_inside = []  # memories instantiated inside the top function
    memories_topout = []  # output memories at the top function interface

    # add array name to 'userlabel' of the connected memory module
    # if they are to be constructed and connected in an array
    labelConnectedMemoryArrays(proc_list)

    arraycontainer_dict = {}
    for memory in mem_list:
        if not memory.userlabel:  # default is '', i.e. no array label added
            if memory.is_initial:
                memories_topin.append(memory)
            elif memory.is_final:
                memories_topout.append(memory)
            else:
                memories_inside.append(memory)
        else:
            arrayname = memory.userlabel
            if arrayname not in arraycontainer_dict:
                arraycontainer_dict[arrayname] = [memory]
            else:
                arraycontainer_dict[arrayname].append(memory)
    # add memory arrays
    for arrayname in arraycontainer_dict:
        if arraycontainer_dict[arrayname][0].is_initial:
            memories_topin.append(arraycontainer_dict[arrayname])
        elif arraycontainer_dict[arrayname][0].is_final:
            memories_topout.append(arraycontainer_dict[arrayname])
        else:
            memories_inside.append(arraycontainer_dict[arrayname])

    return memories_topin, memories_inside, memories_topout
 
########################################
# Processing functions
########################################
# writeTemplatePars: Write the template parameters for the HLS top level as part of the name
#                    of the HLS IP. Once these scripts also generate the top-level HLS
#                    blocks, these functions might not be needed
# matchArgPortNames: Match the HLS argument names to the python-generated port names from
#                    the wires file. Once these scripts also generate the top-level HLS
#                    blocks, these functions might not be needed
########################################

################################
# VMRouter
################################
def writeTemplatePars_VMR(aVMRModule):
    raise ValueError("VMRouter is not implemented yet!")
    return ""

def matchArgPortNames_VMR(argname, portname):
    raise ValueError("VMRouter is not implemented yet!")
    return False

################################
# TrackletEngine
################################
def writeTemplatePars_TE(aTEModule):
    return ""

def matchArgPortNames_TE(argname, portname):
    """
    # Define rules to match the argument and the port names for MatchEngine
    """
    if argname == 'instubinnerdata':
        return portname == 'innervmstubin'
    elif argname == 'instubouterdata':
        return portname == 'outervmstubin'
    elif argname == 'outstubpair':
        return portname == 'stubpairout' or 'stubPairs_' in portname
    else:
        print "matchArgPortNames_TE: Unknown argument name", argname
        return False

################################
# TrackletCalculator
################################
def writeTemplatePars_TC(aTCModule):
    instance_name = aTCModule.inst
    # e.g. TC_L3L4C
    iTC = 'TC::'+instance_name[-1]

    # Count AllStub memories
    NASMemInner = 0  # number of inner allstub memories
    NASMemOuter = 0  # number of outer allstub memories
    PhiLabelASInner = []
    PhiLabelASOuter = []
    for inmem, portname in zip(aTCModule.upstreams, aTCModule.input_port_names):
        if 'innerallstub' in portname:
            NASMemInner += 1
            # AS memory instance name example: AS_L1PHICn3
            philabel = inmem.inst.split('_')[1][0:6]  # e.g. L1PHIC
            PhiLabelASInner.append(philabel)
        elif 'outerallstub' in portname:
            NASMemOuter += 1
            philabel = inmem.inst.split('_')[1][0:6]
            PhiLabelASOuter.append(philabel)

    # sort the phi label list alphabetically
    PhiLabelASInner.sort()
    PhiLabelASOuter.sort()

    assert(NASMemInner<=2)
    assert(NASMemOuter<=2)

    # Count StubPair memories
    NSPMem = [[0,0],[0,0]]

    for inmem, portname in zip(aTCModule.upstreams, aTCModule.input_port_names):
        if 'stubpair' in portname:
            sp_instance = inmem.inst
            # stubpair memory instance name example: SP_L1PHIB8_L2PHIA7
            innerphilabel = sp_instance.split('_')[1][0:6]
            outerphilabel = sp_instance.split('_')[2][0:6]

            assert(innerphilabel in PhiLabelASInner)
            innerindex = PhiLabelASInner.index(innerphilabel)

            assert(outerphilabel in PhiLabelASOuter)
            outerindex = PhiLabelASOuter.index(outerphilabel)

            NSPMem[innerindex][outerindex] += 1
            
    template_str = iTC+','+str(NASMemInner)+','+str(NASMemOuter)+','+str(NSPMem[0][0])+','+str(NSPMem[0][1])+','+str(NSPMem[1][0])+','+str(NSPMem[1][1])+','

    # Count connected TProj memories and compute the TPROJMask parameter

    # list of layers/disks the seeds projecting to for a given seeding
    ProjLayers_List = ['L1','L2','L3','L4','L5','L6','D1','D2','D3','D4','D5']
    # remove the ones if they are seeding layers/disks
    TCSeed = instance_name.split('_')[-1][0:4]
    seed1 = TCSeed[0:2]
    seed2 = TCSeed[2:4]
    ProjLayers_List.remove(seed1)
    ProjLayers_List.remove(seed2)

    TPROJMask = 0
    
    for outmem, portname in zip(aTCModule.downstreams, aTCModule.output_port_names):
        if 'projout' in portname: # portname example: projoutL6PHID
            layer = portname[7:9] # L6
            phi = portname[-1] # D

            assert(layer in ProjLayers_List)
            index = ProjLayers_List.index(layer)

            mask = 0
            if phi == 'A':
                mask = 1
            elif phi == 'B':
                mask = 2
            elif phi == 'C':
                mask = 4
            elif phi == 'D':
                mask = 8
            #assert(mask > 0)

            TPROJMask += mask << (index * 4)
            
    template_str += hex(TPROJMask)+','
    
    # truncation parameter
    template_str += 'kMaxProc'

    return template_str

def matchArgPortNames_TC(argname, portname):
    if 'innerStubs' in argname:
        return 'innerStubs' in portname
    elif 'outerStubs' in argname:
        return 'outerStubs' in portname
    elif 'stubPairs' in argname:
        return 'stubPairs' in portname
    elif 'trackletParameters' in argname:
        return 'trackpar' in portname
    elif 'projout' in argname:
        # e.g. "projout_disk[TC::N_PROJOUT_DISK]"
        destination = argname.strip().split('_')[-1][:-1]
        if 'projout' not in portname:
            return False
        if destination == "DISK":
            return "projoutD" in portname
        elif destination == "BARREL2S":
            return portname[7:9] in ["L1", "L2", "L3"]
        elif destination == "BARRELPS":
            return portname[7:9] in ["L4", "L5", "L6"]
    else:
        print "matchArgPortNames_TC: Unknown argument", argname
        return False

################################
# ProjectionRouter
################################

def writeTemplatePars_PR(aPRModule):
    """
    # Write ProjectionRouter template parameters
    """
    instance_name = aPRModule.inst
    # e.g. PR_L3PHIC
    pos = instance_name.split('_')[1][0:2]
    PROJTYPE = ''
    VMPTYPE = ''
    LAYER = '0'
    DISK = '0'
    if pos in ['L1','L2','L3','L4','L5','L6']:
        VMPTYPE = 'BARREL'
        LAYER = pos[1]
        if int(LAYER) > 3:
            PROJTYPE = 'BARREL2S'
        else:
            PROJTYPE = 'BARRELPS'
    else:
        VMPTYPE = 'DISK'
        PROJTYPE = 'DISK'
        DISK = pos[1]

    nInMemory = len(aPRModule.upstreams)

    templpars_str = PROJTYPE+','+VMPTYPE+','+str(nInMemory)+','+LAYER+','+DISK
    return templpars_str

def matchArgPortNames_PR(argname, portname):
    """
    # Define rules to match the argument and the port names for ProjectionRouter
    """
    if 'projin' in argname:
        # projXXin for input TrackletProjection memories
        return 'proj' in portname and 'in' in portname
    elif 'allprojout' in argname:
        # output AllProjection memory
        return argname==portname
    elif 'vmprojout' in argname:
        return 'vmprojout' in portname
    else:
        print "matchArgPortNames_PR: Unknown argument", argname
        return False

################################
# MatchEngine
################################

def writeTemplatePars_ME(aMEModule):
    """
    # Write MatchEngine template parameters
    """
    instance_name = aMEModule.inst
    # e.g. ME_L4PHIC20
    pos = instance_name.split('_')[1][0:2]
    VMSTYPE = ''
    LAYER = '0'
    DISK = '0'
    if pos in ['L1','L2','L3','L4','L5','L6']:
        LAYER = pos[1]
        if int(LAYER) > 3:
            VMSTYPE = 'BARREL2S'
        else:
            VMSTYPE = 'BARRELPS'
    else:  # Disk
        DISK = pos[1]
        VMSTYPE = 'DISK'

    templpars_str = LAYER+','+VMSTYPE
    return templpars_str

def matchArgPortNames_ME(argname, portname):
    """
    # Define rules to match the argument and the port names for MatchEngine
    """
    if argname == 'inputStubData':
        return portname == 'vmstubin'
    elif argname == 'inputProjectionData':
        return portname == 'vmprojin'
    elif argname == 'outputCandidateMatch':
        return portname == 'matchout'
    else:
        print "matchArgPortNames_ME: Unknown argument name", argname
        return False

################################
# MatchCalculator
################################

def writeTemplatePars_MC(aMCModule):
    instance_name = aMCModule.inst
    # e.g. MC_L2PHID
    pos = instance_name.split('_')[1][0:2]
    ASTYPE = ''
    APTYPE = ''
    FMTYPE = ''
    LAYER = '0'
    DISK = '0'
    if pos in ['L1','L2','L3']:
        LAYER = pos[1]
        FMTYPE = 'BARREL'
        APTYPE = 'BARRELPS'
        ASTYPE = 'BARRELPS'
    elif pos in ['L4','L5','L6']:
        LAYER = pos[1]
        FMTYPE = 'BARREL'
        APTYPE = 'BARREL2S'
        ASTYPE = 'BARREL2S'
    else: # Disk
        DISK = pos[1]
        FMTYPE = 'DISK'
        APTYPE = 'DISK'
        # FIXME here after the allstubs are seperated for disk ps and 2s in the configs
        ASTYPE = 'DISKPS' # all ps for now

    # FIXME 
    PHISEC = '2'  # PHISEC??
        
    templpars_str = ASTYPE+','+APTYPE+','+FMTYPE+','+LAYER+','+DISK+','+PHISEC
        
    return templpars_str

def matchArgPortNames_MC(argname, portname):
    if argname in ['allstub','allproj']:
        return portname == argname+'in'
    elif 'fullmatch' in argname:
        return 'matchout' in portname
    elif 'match' in argname:
        return 'match' in portname and 'out' not in portname
    else:
        print "matchArgPortNames_MC: Unknown argument name", argname
        return False

# Temporary bodge to get the correct argname index for the fullmatch memories
def decodeSeedIndex_MC(memoryname):
    if 'L1L2' in memoryname:
        return 0
    elif 'L2L3' in memoryname:
        return 1
    elif 'L3L4' in memoryname:
        return 2
    elif 'L5L6' in memoryname:
        return 3
    elif 'D1D2' in memoryname:
        return 4
    elif 'D3D4' in memoryname:
        return 5
    elif 'L1D1' in memoryname:
        return 6
    elif 'L2D1' in memoryname:
        return 7
    else:
        print "decodeSeedIndex_MC: Unknown memory name", memoryname
        return False

################################
# FitTrack
################################

def writeTemplatePars_FT(aFTModule):
    raise ValueError("FitTrack is not implemented yet!")
    return ""

def matchArgPortNames_FT(argname, portname):
    raise ValueError("FitTrack is not implemented yet!")
    return False

################################
# PurgeDuplicate
################################

def writeTemplatePars_PD(aPDModule):
    raise ValueError("DuplicateRemoval is not implemented yet!")
    return ""

def matchArgPortNames_PD(argname, portname):
    raise ValueError("DuplicateRemoval is not implemented yet!")
    return False

def parseProcFunction(proc_name, fname_def):
    """
    # Parse the definition of the processing function in the HLS header file
    # Assume all processing functions are templatized
    # Return a list of function argument types, argument names,
    # and template parameters
    """
    
    # Open the header file
    file_proc_hh = open(fname_def)

    # string to temporarily store the template arguments when reading the file
    template_buffer = ""
    # turn on this flag if detect template
    is_template = False

    # string to store the function arguments
    procfunc_str = ""
    
    # Read the file
    for line in file_proc_hh:
        #######
        # if detect keywork "template"
        if 'template' in line:
            is_template = True
            # empty the buffer and get ready for the new template parameters
            template_buffer = "" 
        # store the template string into the buffer
        if is_template:
            # get rid of comments and the new line character
            template_buffer += line.split("//",1)[0].strip("\n")
        # turn off the template flag if detect ">" in the end
        if '>' in line and is_template:
            is_template = False

        #######
        # Search for "proc_name("
        if proc_name+"(" in line: # found the processing function
            # get rid of comments and the new line character
            procfunc_str += line.split("//",1)[0].strip("\n") 

            # keep reading the next lines
            nextline = next(file_proc_hh)
            while nextline:
                # get rid of comments and the new line character
                procfunc_str += nextline.split("//",1)[0].strip("\n") 
                # If detect ")", we are done. Stop reading the following lines
                if ")" in nextline:
                    nextline = ""
                else:
                    nextline = next(file_proc_hh)

            # We've got what we want. Stop reading the file.
            break

    file_proc_hh.close()

    arg_types_list = []
    arg_names_list = []
    templ_pars_list = []
    
    if procfunc_str == "":
        print "Cannot find processing function", proc_name, "in", fname_def
        return arg_types_list, arg_names_list, templ_pars_list
    
    # get the argument lists
    arguments_str = procfunc_str.split("(")[1].split(")")[0].strip()

    # Split by comma, ignoring commas inside template brackets <...>.
    #args_list = arguments_str.split(",")
    args_list = re.split(', *(?![^<]*>)', arguments_str)
    for args in args_list:
        # get rid of 'const' 
        args = args.replace("const","").strip()
        # get rid of '*'
        args = args.replace("*","").strip()
        # get rid of '&' ?

        # get rid of '[...]' in case it is an array
        #args = args.split('[')[0]

        # argument type
        atype = ' '.join(args.split()[:-1]) # combine all strings except the last
        arg_types_list.append(atype)
        # argument name
        aname = args.split()[-1] # the last entry in the list
        arg_names_list.append(aname)

    # get the template parameter list
    if template_buffer == "":
        print "No template parameters are found."
        print "Please make sure the processing function", proc_name, "is templatized in", fname_def
        return arg_types_list, arg_names_list, templ_pars_list
    
    templPars_str = template_buffer.split("<")[1].split(">")[0]
    
    for par in templPars_str.split(","):
        par = par.strip()
        templ_pars_list.append(par.split()[-1]) # the last entry in the list

    return arg_types_list, arg_names_list, templ_pars_list

def writeModuleInst_generic(module, hls_src_dir, f_writeTemplatePars,
                              f_matchArgPortNames, first_of_type):
    ####
    # function name
    assert(module.mtype in ['VMRouter','TrackletEngine','TrackletCalculator',
                            'ProjectionRouter','MatchEngine','MatchCalculator',
                            'DiskMatchCalculator','FitTrack','PurgeDuplicate'])

    # Add internal BX wire and start registers
    str_ctrl_wire = ""
    str_ctrl_func = ""
    if first_of_type and not module.is_last:
        for mem in module.downstreams:
            if mem.bxbitwidth != 1: continue
            oneProcDownMem = mem
            break
        ctrl_wire_inst,ctrl_func_inst = writeStartSwitchAndInternalBX(module,oneProcDownMem)
        str_ctrl_wire += ctrl_wire_inst
        str_ctrl_func += ctrl_func_inst
        
    # Update here if the function name is not exactly the same as the module type

    # TrackletCalculator
    special_TC = ""
    if module.mtype == 'TrackletCalculator':
        # 'TrackletCalculator_<seeding>'
        # extract seeding from instance name: TC_L3L4C
        special_TC += '_'+module.inst.split('_')[1][0:4]

    ####
    # Header file when the processing function is defined
    fname_def = module.mtype + '.h'
    fname_def = hls_src_dir.rstrip('/')+'/'+fname_def

    ####
    # Get the list of argument types, names, and template parameters
    # WARNING, MAY NOT WORK FOR TC
    argtypes,argnames,templpars = parseProcFunction(module.mtype,fname_def)

    ####
    # Determine function template parameters
    templpars_str = f_writeTemplatePars(module)
    templpars_str = templpars_str.replace(",","_");

    ####
    # Write ports
    memModuleList, portNameList = getListsOfGroupedMemories(module)

    # clock, reset, start
    string_ctrl_ports = writeProcControlSignalPorts(module, first_of_type)

    # Bunch crossing
    string_bx_in = ""
    string_bx_out = ""
    # memory ports
    string_mem_ports = ""

    # Dictionary of array names and the number of elements (minus one)
    array_dict = {}
    # loop over the list of argument names from parsing the header file
    for argtype, argname in zip(argtypes, argnames):
        # bunch crossing
        if argtype == "BXType":
            for mem in module.upstreams:
                if mem.bxbitwidth != 1: continue
                if mem.is_initial:
                    string_bx_in += writeProcBXPort(module.mtype,True,True)
                    break
                else:
                    string_bx_in += writeProcBXPort(mem.upstreams[0].mtype,True,False)
                    break
        elif argtype == "BXType&":
            if first_of_type:
                string_bx_out += writeProcBXPort(module.mtype,False,False) # output bx
        else:
            # Given argument name, search for the matched port name in the mem lists
            foundMatch = False
            for memory, portname in zip(memModuleList, portNameList):
                # Check if the portname matches the argument name from function def
                if f_matchArgPortNames is None:
                    # No matching rule provided, just check if the names are the same
                    foundMatch = (argname==portname)
                else:
                    # Use the provided matching rules
                    if "table" not in argname:
                        foundMatch = f_matchArgPortNames(argname, portname)

                if foundMatch:
                    # Create temporary argument name as argname can be an array and have several matches
                    tmp_argname = argname
                    argname_is_array = (tmp_argname.find('[') != -1) # Check if array

                    # Special case if argname is an array
                    if argname_is_array:
                        tmp_argname = tmp_argname.split('[')[0] # Remove "[...]"
                        # Keep track of the array names and the number of array elements
                        if tmp_argname in array_dict:
                            array_dict[tmp_argname] += 1
                        else:
                            array_dict[tmp_argname] = 0
                        # Add array index to the name as HLS implements one port for each array element
                        # Temporary bodge to account for encoded index in fullmatch memories
                        if tmp_argname == 'fullmatch':
                            tmp_argname += "_" + str(decodeSeedIndex_MC(memory.inst))
                        else:
                            tmp_argname += "_" + str(array_dict[tmp_argname])

                    # Add the memory instance to the port string
                    # Assumes a sorted memModuleList due to arrays?
                    if portname.find("in") != -1:
                        if isinstance(memory, list):
                            for memmodule in memory:
                                string_mem_ports += writeProcMemoryRHSPorts(tmp_argname,  memmodule)
                        else:
                            string_mem_ports += writeProcMemoryRHSPorts(tmp_argname,memory)
                    if portname.find("out") != -1:
                        if isinstance(memory, list):
                            for memmodule in memory:
                                string_mem_ports += writeProcMemoryLHSPorts(tmp_argname,memmodule)
                        else:
                            string_mem_ports += writeProcMemoryLHSPorts(tmp_argname,memory)
                    if portname.find("stubPairs_") != -1 and module.mtype == "TrackletEngine":
                        if isinstance(memory, list):
                            for memmodule in memory:
                                string_mem_ports += writeProcMemoryLHSPorts(tmp_argname,memmodule)
                        else:
                            string_mem_ports += writeProcMemoryLHSPorts(tmp_argname,memory)
                    elif portname.find("stubPairs_") != -1 and module.mtype == "TrackletCalculator":
                        if isinstance(memory, list):
                            for memmodule in memory:
                                string_mem_ports += writeProcMemoryRHSPorts(tmp_argname,  memmodule)
                        else:
                            string_mem_ports += writeProcMemoryRHSPorts(tmp_argname,memory)
                    if portname.find("trackpar") != -1 and module.mtype == "TrackletCalculator":
                        if isinstance(memory, list):
                            for memmodule in memory:
                                string_mem_ports += writeProcMemoryRHSPorts(tmp_argname,  memmodule)
                        else:
                            string_mem_ports += writeProcMemoryRHSPorts(tmp_argname,memory)
                    elif portname.find("trackpar") != -1 and module.mtype == "PurgeDuplicates":
                        if isinstance(memory, list):
                            for memmodule in memory:
                                string_mem_ports += writeProcMemoryLHSPorts(tmp_argname,  memmodule)
                        else:
                            string_mem_ports += writeProcMemoryLHSPorts(tmp_argname,memory)

                    # Remove the already added module and name from the lists
                    portNameList.remove(portname)
                    memModuleList.remove(memory)

                    if not argname_is_array: break # We only need one match for non-arrays
    # end of loop
    string_ports = ""
    string_ports += string_ctrl_ports
    string_ports += string_bx_in
    string_ports += string_bx_out
    string_ports += string_mem_ports
    string_ports.rstrip(",\n")

    ####
    # Put ingredients togther
    module_str = writeProcCombination(module, str_ctrl_func, 
                                      special_TC, templpars_str, string_ports)
    return str_ctrl_wire,module_str

################################
def writeModuleInstance(module, hls_src_dir, first_of_type):
    if module.mtype == 'VMRouter':
        return writeModuleInst_generic(module, hls_src_dir,
                                         writeTemplatePars_VMR,
                                         matchArgPortNames_VMR,
                                         first_of_type)
    elif module.mtype == 'TrackletEngine':
        return writeModuleInst_generic(module, hls_src_dir,
                                         writeTemplatePars_TE,
                                         matchArgPortNames_TE,
                                         first_of_type)
    elif module.mtype == 'TrackletCalculator':
        return writeModuleInst_generic(module, hls_src_dir,
                                         writeTemplatePars_TC,
                                         matchArgPortNames_TC,
                                         first_of_type)
    elif module.mtype == 'ProjectionRouter':
        return writeModuleInst_generic(module, hls_src_dir,
                                         writeTemplatePars_PR,
                                         matchArgPortNames_PR,
                                         first_of_type)
    elif module.mtype == 'MatchEngine':
        return writeModuleInst_generic(module, hls_src_dir,
                                         writeTemplatePars_ME,
                                         matchArgPortNames_ME,
                                         first_of_type)
    elif module.mtype in ['MatchCalculator','DiskMatchCalculator']:
        return writeModuleInst_generic(module, hls_src_dir,
                                         writeTemplatePars_MC,
                                         matchArgPortNames_MC,
                                         first_of_type)
    elif module.mtype == 'FitTrack':
        return writeModuleInst_generic(module, hls_src_dir,
                                         writeTemplatePars_FT,
                                         matchArgPortNames_FT,
                                         first_of_type)
    elif module.mtype == 'PurgeDuplicate':
        return writeModuleInst_generic(module, hls_src_dir,
                                         writeTemplatePars_PD,
                                         matchArgPortNames_PD,
                                         first_of_type)
    else:
        raise ValueError(module.mtype + " is unknown.")
