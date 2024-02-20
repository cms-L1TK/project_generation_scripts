"""
########################################
# Utilities for writing Verilog code from Vivado HLS blocks
"""

#from collections import deque
from TrackletGraph import MemModule, ProcModule, MemTypeInfoByKey

from WriteVHDLSyntax import writeStartSwitchAndInternalBX, writeProcControlSignalPorts, writeProcBXPort, writeProcMemoryLHSPorts, writeProcMemoryRHSPorts, writeProcCombination, writeProcDTCLinkRHSPorts, writeProcTrackStreamLHSPorts, writeInputLinkWordPort, writeInputLinkPhiBinsPort, writeLastTrackPorts, writeLUTPorts, writeLUTParameters, writeLUTCombination, writeLUTWires, writeLUTMemPorts
import re
# This dictionary preserves key order. 
# (Requires python >= 2.7. And can be replace with normal dict for >= 3.7)
from collections import OrderedDict

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
        if philabel in ['W','X','Y','Z']: # L2D1 seeding
            memoryclass = 'VMStubTEInnerMemory'
            bitformat = 'BARRELOL'
        elif philabel in ['I','J','K','L']: # L2L3 seeding
            memoryclass = 'VMStubTEInnerMemory'
            bitformat = 'BARRELPS'
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

def getListsOfGroupedMemories(aProcModule):
    """
    # Get a list of memories and a list of ports for a given processing module

    """
    memList = list(aProcModule.upstreams + aProcModule.downstreams)
    portList = list(aProcModule.input_port_names + aProcModule.output_port_names)

    # Sort the VMSME and VMSTE using portList, first by the phi region number (e.g. 2 in "vmstuboutPHIA2"), then alphabetically
    zipped_list = list(zip(memList, portList))
    zipped_list.sort(key=lambda m_p: 0 if 'vmstubout' else int("".join([i for i in m_p[1] if i.isdigit()]))) # sort by number
    zipped_list.sort(key=lambda m_p1: 0 if 'vmstubout' else m_p1[1][:m_p1[1].index('PHI')]) # sort alphabetically
    memList, portList = list(zip(*zipped_list)) # unzip
    memList, portList = list(memList), list(portList)

    return memList, portList

def arrangeMemoriesByKey(memory_list):
    """
    # Put memories in a dictionary organised by their keyName(),
    # corresponding to their type + bit width (TPROJ_60 etc.).
    # Also return dictionary with properties of each key name.
    """
    memDict = OrderedDict()
    for mem in memory_list:
        keyName = mem.keyName()
        if not keyName in memDict:
            memDict[keyName] = []
        memDict[keyName].append(mem)

    memTypeDict = OrderedDict()
    for keyN in memDict:
        memList = memDict[keyN]
        memTypeDict[keyN] = MemTypeInfoByKey(memList)

    return memDict, memTypeDict
 
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
# InputRouter
################################
def writeTemplatePars_IR(anIRModule):
    #InputRouter template parameters are not implemented. Add if necessary.
    return ""

def matchArgPortNames_IR(argname, portname, memoryname):
    if 'hInputStubs' in argname:
        return 'stubin' in portname
    elif 'hOutputStubs' in argname:
        return 'stubout' in portname
    elif 'hPhBnWord' in argname or 'hLinkWord' in argname:
        return False
    else:
        print("matchArgPortNames_IR: Unknown argument", argname)
        return False

# Dictionary with the memories used per layer/disk. 
# Maximum 8 memories/phi regions/bins per layer, each memory used is represented by a "1". 
# Phi region "A" is the first bit and so forth. Needed for the InputRouter.
def dictOfMemoriesPerLayer(module):
    numMemories = OrderedDict() # Dictionary that keeps track of number of memories per layer
    # Count memories per layer/disk
    for memory in list(module.downstreams):
        layerID = memory.inst.split('_')[1][0:2] # L1, L2, etc.
        phiID = ord(memory.inst.split('PHI')[1][0]) - ord("A") # Turn the phi regions into integers, A = 0 etc.
        if layerID in numMemories:
            tmpPhiBinWord = list(numMemories[layerID]) # Convert string to temporary list
        else: 
            tmpPhiBinWord = ["0"] * 8 # Temporary list with 8 zeros, each bit represents a phi region
        tmpPhiBinWord[len(tmpPhiBinWord) - phiID - 1] = "1" # Memory corresponding to phiID is being used  
        numMemories[layerID] = "".join(tmpPhiBinWord) # Convert back to string
    return numMemories

################################
# VMRouter
################################
def writeTemplatePars_VMR(aVMRModule):
    #VMRouter template parameters are not implemented. Add if necessary.
    return ""

def matchArgPortNames_VMR(argname, portname, memoryname):
    # argname and portname does not contain enough information to determine matches
    phi_region = memoryname.split("PHI")[1][0]
    position = memoryname.split("_")[1][0:2]
    overlap_phi_regions = ['Q','R','S','T','W','X','Y','Z']

    # DISK2S memories has a seperate array
    if 'inputStubsDisk2S' in argname:
        return ('stubin' in portname) and ('D' in position) and ('2S' in memoryname)
    # Non-DISK2S inputs
    elif 'inputStubs' in argname:
        if ('L' in position):
            return 'stubin' in portname
        else:
            return ('stubin' in portname) and ('PS' in memoryname)
    # Allstub memories
    elif 'memoriesAS' in argname:
        return 'allstubout' in portname
    # ME and TE memories use the same portnames, thereof an extra check
    elif 'memoriesME'  in argname:
        return 'vmstuboutME' in portname
    # TE inner/outer/overlap use the same portnames, thereof extra checks
    elif 'memoriesTEI' in argname:
        return ('vmstuboutTEI' in portname) and (phi_region not in overlap_phi_regions)
    # TE outer
    elif 'memoriesTEO' in argname:
        return 'vmstuboutTEO' in portname
    # TE overlap
    elif 'memoriesOL' in argname:
        return ('vmstuboutTEI' in portname) and (phi_region in overlap_phi_regions)
    # Known arguments that should not be matched to any ports
    elif 'mask' in argname or 'Table' in argname:
        return False
    else:
        print("matchArgPortNames_VMR: Unknown argument", argname)
        return False


################################                                                                                                                                      
# VMRouterCM                                                                                                                                                          
################################                                                                                                                                      
def writeTemplatePars_VMRCM(aVMRModule):
    #VMRouterCM template parameters are not implemented. Add if necessary.                                                                                            
    return ""

def matchArgPortNames_VMRCM(argname, portname, memoryname):
    # argname and portname does not contain enough information to determine matches                                                                                   
    phi_region = memoryname.split("PHI")[1][0]
    position = memoryname.split("_")[1][0:2]
    overlap_phi_regions = ['Q','R','S','T','W','X','Y','Z']

    # DISK2S memories has a seperate array                                                                                                                            
    if 'inputStubsDisk2S' in argname:
        return ('stubin' in portname) and ('D' in position) and ('2S' in memoryname)
    # Non-DISK2S inputs                                                                                                                                               
    elif 'inputStubs' in argname:
        if ('L' in position):
            return 'stubin' in portname
        else:
            return ('stubin' in portname) and ('PS' in memoryname)
    # AllInnerStub memories                                                                                                                                           
    elif 'memoriesASInner' in argname:
        return 'allinnerstubout' in portname
    # Allstub memories                                                                                                                                                
    elif 'memoriesAS' in argname:
        return 'allstubout' in portname
    # ME and TE memories use the same portnames, thereof an extra check                                                                                               
    elif 'memoryME'  in argname:
        return 'vmstuboutPHI' in portname
    # TE outer                                                                                                                                                        
    elif 'memoriesTEO' in argname:
        return 'vmstubout_seed' in portname
    # Known arguments that should not be matched to any ports                                                                                                         
    elif 'mask' in argname or 'Table' in argname:
        return False
    else:
        print("matchArgPortNames_VMRCM: Unknown argument", argname)
        return False



################################
# TrackletEngine
################################
def writeTemplatePars_TE(aTEModule):
    return ""

def matchArgPortNames_TE(argname, portname, memoryname):
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
        print("matchArgPortNames_TE: Unknown argument name", argname)
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
    for inmem, portname in list(zip(aTCModule.upstreams, aTCModule.input_port_names)):
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

    #assert(NASMemInner<=2)
    #assert(NASMemOuter<=2)

    # Count StubPair memories
    NSPMem = [[0,0],[0,0]]

    for inmem, portname in list(zip(aTCModule.upstreams, aTCModule.input_port_names)):
        if 'stubpair' in portname:
            sp_instance = inmem.inst
            # stubpair memory instance name example: SP_L1PHIB8_L2PHIA7
            innerphilabel = sp_instance.split('_')[1][0:6]
            outerphilabel = sp_instance.split('_')[2][0:6]

            # PHII-PHIL corresponds to AS memories PHIA-PHID
            # (only used for L2L3 seed)
            innerphilabel = innerphilabel.replace("PHII", "PHIA")
            innerphilabel = innerphilabel.replace("PHIJ", "PHIB")
            innerphilabel = innerphilabel.replace("PHIK", "PHIC")
            innerphilabel = innerphilabel.replace("PHIL", "PHID")
            outerphilabel = outerphilabel.replace("PHII", "PHIA")
            outerphilabel = outerphilabel.replace("PHIJ", "PHIB")
            outerphilabel = outerphilabel.replace("PHIK", "PHIC")
            outerphilabel = outerphilabel.replace("PHIL", "PHID")

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
    
    for outmem, portname in list(zip(aTCModule.downstreams, aTCModule.output_port_names)):
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
            assert(mask > 0)

            TPROJMask += mask << (index * 4)
            
    template_str += hex(TPROJMask)+','
    
    # truncation parameter
    template_str += 'kMaxProc'

    return template_str

def matchArgPortNames_TC(argname, portname, memoryname):
    if 'innerStubs' in argname:
        return 'innerallstub' in portname
    elif 'outerStubs' in argname:
        return 'outerallstub' in portname
    elif 'stubPairs' in argname:
        return 'stubpair' in portname
    elif 'trackletParameters' in argname:
        return 'trackpar' in portname
    elif 'projout' in argname:
        # e.g. "projout_disk[TC::N_PROJOUT_DISK]"
        destination = argname.strip().split('_')[-1][:-2]
        if 'projout' not in portname:
            return False
        if destination == "disk":
            return "projoutD" in portname
        elif destination == "ps":
            return portname[7:9] in ["L1", "L2", "L3"]
        elif destination == "2s":
            return portname[7:9] in ["L4", "L5", "L6"]
    else:
        print("matchArgPortNames_TC: Unknown argument", argname)
        return False

def decodeSeedIndex_TC(memoryname):
    if ('L1PHIA' in memoryname) or ('L4PHIA' in memoryname) or ('D1PHIA' in memoryname):
        return 0
    elif ('L1PHIB' in memoryname) or ('L4PHIB' in memoryname) or ('D1PHIB' in memoryname):
        return 1
    elif ('L1PHIC' in memoryname) or ('L4PHIC' in memoryname) or ('D1PHIC' in memoryname):
        return 2
    elif ('L1PHID' in memoryname) or ('L4PHID' in memoryname) or ('D1PHID' in memoryname):
        return 3
    elif ('L1PHIE' in memoryname) or ('L5PHIA' in memoryname) or ('D2PHIA' in memoryname):
        return 4
    elif ('L1PHIF' in memoryname) or ('L5PHIB' in memoryname) or ('D2PHIB'  in memoryname):
        return 5
    elif ('L1PHIG' in memoryname) or ('L5PHIC' in memoryname) or ('D2PHIC' in memoryname):
        return 6
    elif ('L1PHIH' in memoryname) or ('L5PHID' in memoryname) or ('D2PHID' in memoryname):
        return 7
    elif ('L2PHIA' in memoryname) or ('L6PHIA' in memoryname) or ('D3PHIA' in memoryname):
        return 8
    elif ('L2PHIB' in memoryname) or ('L6PHIB' in memoryname) or ('D3PHIB'  in memoryname):
        return 9
    elif ('L2PHIC' in memoryname) or ('L6PHIC' in memoryname) or ('D3PHIC' in memoryname):
        return 10
    elif ('L2PHID' in memoryname) or ('L6PHID' in memoryname) or ('D3PHID' in memoryname):
        return 11
    elif ('L3PHIA' in memoryname) or ('D4PHIA' in memoryname):
        return 12
    elif ('L3PHIB' in memoryname) or ('D4PHIB' in memoryname):
        return 13
    elif ('L3PHIC' in memoryname) or ('D4PHIC' in memoryname):
        return 14
    elif ('L3PHID' in memoryname) or ('D4PHID' in memoryname):
        return 15
    elif ('D5PHIA' in memoryname):
        return 16
    elif ('D5PHIB' in memoryname):
        return 17
    elif ('D5PHIC' in memoryname):
        return 18
    elif ('D5PHID' in memoryname):
        return 19
    else:
        print("decodeSeedIndex_TC: Unknown memory name", memoryname)
        return False


################################                                                                                                                                      
# TrackletProcessor                                                                                                                                                   
################################                                                                                                                                      
def writeTemplatePars_TP(aTCModule):
    instance_name = aTCModule.inst
    # e.g. TC_L3L4C                                                                                                                                                   
    iTC = 'TC::'+instance_name[-1]

    # Count AllStub memories                                                                                                                                          
    NASMemInner = 0  # number of inner allstub memories                                                                                                               
    NASMemOuter = 0  # number of outer allstub memories                                                                                                               
    PhiLabelASInner = []
    PhiLabelASOuter = []
    for inmem, portname in list(zip(aTCModule.upstreams, aTCModule.input_port_names)):
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

    #assert(NASMemInner<=2)                                                                                                                                           
    #assert(NASMemOuter<=2)                                                                                                                                           

    # Count StubPair memories                                                                                                                                         
    NSPMem = [[0,0],[0,0]]

    for inmem, portname in list(zip(aTCModule.upstreams, aTCModule.input_port_names)):
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

    for outmem, portname in list(zip(aTCModule.downstreams, aTCModule.output_port_names)):
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
            assert(mask > 0)

            TPROJMask += mask << (index * 4)

    template_str += hex(TPROJMask)+','

    # truncation parameter                                                                                                                                            
    template_str += 'kMaxProc'

    return template_str


def matchArgPortNames_TP(argname, portname, memoryname):
    if 'innerStubs' in argname:
        return 'innerallstub' in portname
    elif 'outerStubs' in argname:
        return 'outerallstub' in portname
    elif 'outerVMStubs' in argname:
        return 'outervmstubin' in portname
    elif 'trackletParameters' in argname:
        return 'trackpar' in portname
    elif 'projout' in argname:
        # e.g. "projout_disk[TC::N_PROJOUT_DISK]"                                                                                                                     
        destination = argname.strip().split('_')[-1][:-2]
        if 'projout' not in portname:
            return False
        if "projout_disk" in argname:
            return "projoutD" in portname
        elif "projout_barrel_ps" in argname:
            return portname[7:9] in ["L1", "L2", "L3"]
        elif "projout_barrel_2s" in argname:
            return portname[7:9] in ["L4", "L5", "L6"]
    elif 'lut' in argname:
        return False
    else:
        print("matchArgPortNames_TP: Unknown argument", argname)
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

def matchArgPortNames_PR(argname, portname, memoryname):
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
        print("matchArgPortNames_PR: Unknown argument", argname)
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

def matchArgPortNames_ME(argname, portname, memoryname):
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
        print("matchArgPortNames_ME: Unknown argument name", argname)
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

def matchArgPortNames_MC(argname, portname, memoryname):
    if argname in ['allstub','allproj']:
        return portname == argname+'in'
    elif 'fullmatch' in argname:
        return 'matchout' in portname
    elif 'match' in argname:
        return 'match' in portname and 'out' not in portname
    else:
        print("matchArgPortNames_MC: Unknown argument name", argname)
        return False


################################                                                                                                                                      
# MatchProcessor                                                                                                                                                      
################################                                                                                                                                      

def writeTemplatePars_MP(aMPModule):
    instance_name = aMPModule.inst
    # e.g. MP_L2PHID                                                                                                                                                  
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


def matchArgPortNames_MP(argname, portname, memoryname):
    if argname in ['allstub','allproj']:
        return portname == argname+'in'
    elif 'fullmatch' in argname:
        return 'matchout' in portname
    elif 'projin' in argname:
        return 'projin' in portname
    elif 'instubdata' in argname:
        return 'vmstubin' in portname
    else:
        print("matchArgPortNames_MP: Unknown argument name", argname)
        return False





################################
# FitTrack
################################

def writeTemplatePars_FT(aFTModule):
    raise ValueError("FitTrack is not implemented yet!")
    return ""

def matchArgPortNames_FT(argname, portname, memoryname):
    raise ValueError("FitTrack is not implemented yet!")
    return False

################################
# TrackBuilder
################################

def writeTemplatePars_TB(aTBModule):
    return ""

def matchArgPortNames_TB(argname, portname, memoryname):
    fm_layer_or_disk = None
    if memoryname.startswith("FM_"):
        fm_layer_or_disk = memoryname.split("_")[2][0]

    if argname.startswith("trackletParameters"):
        return portname.startswith("tpar")
    if argname.startswith("barrelFullMatches"):
        return (fm_layer_or_disk == "L" and portname.startswith("fullmatch"))
    if argname.startswith("diskFullMatches"):
        return (fm_layer_or_disk == "D" and portname.startswith("fullmatch"))
    if argname.startswith("trackWord"):
        return portname.startswith("trackword")
    if argname.startswith("barrelStubWords"):
        return portname.startswith("barrelstub")
    if argname.startswith("diskStubWords"):
        return portname.startswith("diskstub")
    print("matchArgPortNames_TB: Unknown argument name", argname)
    return False

################################
# PurgeDuplicate
################################

def writeTemplatePars_PD(aPDModule):
    raise ValueError("DuplicateRemoval is not implemented yet!")
    return ""

def matchArgPortNames_PD(argname, portname, memoryname):
    raise ValueError("DuplicateRemoval is not implemented yet!")
    return False

################################
# Parse HLS code
################################

def splitByComma(aString):
    """
    # Splits a string by comma delimiter into a list,
    # but ignores commas that are between balanced angular brackets "<...,...>".
    """
    ignore = 0
    aList = ['']
    for x in aString:
        split = False
        if x == '<':
            ignore += 1;
        elif x == '>':
            ignore -= 1;
        elif x == ',' and ignore == 0:
            split = True

        if split:
          aList.append('')  
        elif x != ' ' or len(aList[-1]) > 0: # Skip spaces after commas
         aList[-1] += x
    return aList


def parseProcFunction(proc_name, fname_def):
    """
    # Parse the definition of the processing function in the HLS header file
    # Assume all processing functions are templatized
    # Typical inputs: (MatchCalculator, somepath/MatchCalculator.h)
    # Return: a list of function argument types, argument names,
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
                if nextline.find(")") != -1 and nextline.find("()") == -1:
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
        print("Cannot find processing function", proc_name, "in", fname_def)
        return arg_types_list, arg_names_list, templ_pars_list
    
    # get the argument lists
    arguments_str = procfunc_str.partition("(")[2].rpartition(")")[0].strip()

    # Split by comma, ignoring commas inside template brackets <...>.
    args_list = splitByComma(arguments_str)

    for args in args_list:
        # get rid of 'const' 
        args = args.replace("const","").strip()
        # get rid of '*'
        args = args.replace("*","").strip()

        # get rid of '[...]' in case it is an array
        #args = args.split('[')[0]

        # argument type
        atype = ' '.join(args.split()[:-1]) # combine all strings except the last

        # get rid of '&' and append it to the type
        if "&" in args:
            args = args.replace("&","").strip()
            if "&" not in atype:
                atype += "&"

        arg_types_list.append(atype)
        # argument name
        aname = args.split()[-1] # the last entry in the list
        arg_names_list.append(aname)

    # get the template parameter list
    if template_buffer == "":
        print("No template parameters are found.")
        print("Please make sure the processing function", proc_name, "is templatized in", fname_def)
        return arg_types_list, arg_names_list, templ_pars_list
    
    templPars_str = template_buffer.split("<")[1].split(">")[0]
    
    for par in templPars_str.split(","):
        par = par.strip()
        templ_pars_list.append(par.split()[-1]) # the last entry in the list

    return arg_types_list, arg_names_list, templ_pars_list

def writeModuleInst_generic(module, hls_src_dir, f_writeTemplatePars,
                              f_matchArgPortNames, first_of_type, extraports,delay,split=False):
    ####
    # function name
    assert(module.mtype in ['InputRouter', 'VMRouterCM', 'TrackletProcessor',
                            'MatchProcessor', 'FitTrack', 'TrackBuilder', 'PurgeDuplicate'])

    # Add internal BX wire and start registers
    str_ctrl_wire = ""
    str_ctrl_func = ""
    if first_of_type and not module.is_last:
        for mem in module.downstreams:
            if mem.bxbitwidth != 1: continue
            oneProcDownMem = mem
            break
        ctrl_wire_inst,ctrl_func_inst = writeStartSwitchAndInternalBX(module,oneProcDownMem,extraports,delay)
        str_ctrl_wire += ctrl_wire_inst
        str_ctrl_func += ctrl_func_inst
        
    # Update here if the function name is not exactly the same as the module type

    ####
    # Header file when the processing function is defined
    fname_def = module.mtype + '.h'
    fname_def = hls_src_dir.rstrip('/')+'/'+fname_def

    ####
    # Get the list of argument types, names, and template parameters
    # WARNING, MAY NOT WORK FOR TC
    argtypes,argnames,templpars = parseProcFunction(module.mtype,fname_def)

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
    # last track ports
    string_last_track_ports = ""
    # module string
    module_str = ""

    # Dictionary of array names and the number of elements (minus one)
    array_dict = {}

    # loop over the list of argument names from parsing the header file
    for argtype, argname in list(zip(argtypes, argnames)):
        # bunch crossing
        if argtype == "BXType":
            for mem in module.upstreams:
                if mem.bxbitwidth != 1: continue
                if mem.is_initial:
                    string_bx_in += writeProcBXPort(module.mtype_short(),True,True,delay)
                    break
                else:
                    string_bx_in += writeProcBXPort(mem.upstreams[0].mtype_short(),True,False,delay)
                    break
        elif argtype == "BXType&" or argtype == "BXType &": # Could change this in the HLS instead
            if first_of_type:
                string_bx_out += writeProcBXPort(module.mtype_short(),False,False,delay) # output bx
        elif "table" in argname: # For TE
            innerPS = ("_L1" in module.inst and "_L2" in module.inst) \
                   or ("_L2" in module.inst and "_L3" in module.inst) \
                   or ("_L3" in module.inst and "_L4" in module.inst)
            outerPS = ("_L1" in module.inst and "_L2" in module.inst) \
                   or ("_L2" in module.inst and "_L3" in module.inst)
            string_ports = writeLUTPorts(argname, module)
            string_parameters = writeLUTParameters(argname, module, innerPS, outerPS)
            module_str += writeLUTCombination(module, argname, string_ports, string_parameters)
            str_ctrl_wire += writeLUTWires(argname, module, innerPS, outerPS)
            string_mem_ports += writeLUTMemPorts(argname, module)
        elif argtype.startswith("bool") and argtype.endswith("&") and argname == "done":
            string_last_track_ports = writeLastTrackPorts(ftName = module.inst, is_open = not module.is_last)
        else:
            # Given argument name, search for the matched port name in the mem lists
            foundMatch = False
            for memory, portname in list(zip(memModuleList, portNameList)):
                # Check if the portname matches the argument name from function def
                if f_matchArgPortNames is None:
                    # No matching rule provided, just check if the names are the same
                    foundMatch = (argname==portname)
                else:
                    # Use the provided matching rules
                    foundMatch = f_matchArgPortNames(argname, portname, memory.inst)

                if foundMatch:
                    # Create temporary argument name as argname can be an array and have several matches
                    tmp_argname = argname
                    argname_is_array = (tmp_argname.find('[') != -1) # Check if array

                    # TrackWords are treated differently because they are
                    # currently streams
                    if "TW" in memory.inst:
                        argname_is_array = False
                        tmp_argname = tmp_argname.split('[')[0] # Remove "[...]"

                    # Special case if argname is an array
                    # Note: it assumes the arrays are partitioned
                    if argname_is_array:
                        #  no more than two dimensions
                        argname_is_2d_array = (tmp_argname.find('][') != -1) # Check if two-dimensional array

                        # FIFO (streams) such as BarrelWords & DiskWords are treated differently
                        if memory.isFIFO():
                            argname_is_2d_array = False

                        tmp_argname = tmp_argname.split('[')[0] # Remove "[...]"

                        # For one-dimensional arrays
                        if not argname_is_2d_array:
                            # Keep track of the array names and the number of array elements
                            if tmp_argname in array_dict:
                                array_dict[tmp_argname] += 1
                            else:
                                array_dict[tmp_argname] = 0
                            # Add array index to the name as HLS implements one port for each array element
                            # Temporary bodge to account for encoded index in projection memories
                            if tmp_argname == 'projout_barrel_ps' or tmp_argname == 'projout_barrel_2s' or tmp_argname == 'projout_disk':
                                tmp_argname += "_" + str(decodeSeedIndex_TC(memory.inst))
                            else:
                                tmp_argname += "_" + str(array_dict[tmp_argname])
                        # For two-dimensional arrays
                        else:
                            # Keep track of the array names and the number of array elements
                            # array_dict[tmp_argname] keeps track of the first dimension
                            # array_dict[portname] keeps track of the second dimension
                            if tmp_argname not in array_dict:
                                array_dict[tmp_argname] = 0
                                array_dict[portname] = 0
                            elif portname not in array_dict:
                                array_dict[tmp_argname] += 1
                                array_dict[portname] = 0
                            else:
                                array_dict[portname] += 1
                            # Add array index to the name as HLS implements one port for each array element
                            tmp_argname += "_" + str(array_dict[tmp_argname]) + "_" + str(array_dict[portname])

                    # Add the memory instance to the port string
                    # Assumes a sorted memModuleList due to arrays
                    if portname.replace("inner","").find("in") != -1:
                        if "DL" in memory.inst and "AS" not in memory.inst: # DTCLink
                            string_mem_ports += writeProcDTCLinkRHSPorts(tmp_argname,memory)
                        else:
                            string_mem_ports += writeProcMemoryRHSPorts(tmp_argname,memory)

                    if portname.replace("outer","").find("out") != -1:
                        if memory.isFIFO():
                            string_mem_ports += writeProcTrackStreamLHSPorts(tmp_argname,memory)
                        else:
                            string_mem_ports += writeProcMemoryLHSPorts(tmp_argname,memory,split)
                    if portname.find("trackpar") != -1 and (module.mtype == "TrackletCalculator" or module.mtype == "TrackletProcessor"):
                        string_mem_ports += writeProcMemoryLHSPorts(tmp_argname,memory,split)
                    elif portname.find("trackpar") != -1 and module.mtype == "PurgeDuplicates":
                        string_mem_ports += writeProcMemoryRHSPorts(tmp_argname,memory)

                    # Remove the already added module and name from the lists
                    portNameList.remove(portname)
                    memModuleList.remove(memory)

                    if not argname_is_array: break # We only need one match for non-arrays
    # end of loop

    # Check that all the ports/memories have been matched
    if (memModuleList or portNameList):
        raise ValueError("There are unmatched memories: "+" ,".join([m.inst for m in memModuleList]))

    # External LUTs
    string_luts = ""
    if module.mtype == "InputRouter": # Might be temporary
        string_luts += writeInputLinkWordPort(module.inst, dictOfMemoriesPerLayer(module))
        string_luts += writeInputLinkPhiBinsPort(dictOfMemoriesPerLayer(module))

    # Add all ports together
    string_ports = ""
    string_ports += string_ctrl_ports
    string_ports += string_bx_in
    string_ports += string_bx_out
    string_ports += string_mem_ports
    string_ports += string_last_track_ports
    string_ports += string_luts
    string_ports.rstrip(",\n")

    ####
    # Put ingredients togther
    module_str += writeProcCombination(module, str_ctrl_func, string_ports)
    return str_ctrl_wire,module_str

################################
def writeModuleInstance(module, hls_src_dir, first_of_type, extraports, delay, split = False):
    if module.mtype == 'InputRouter':
        return writeModuleInst_generic(module, hls_src_dir,
                                         writeTemplatePars_IR,
                                         matchArgPortNames_IR,
                                         first_of_type, extraports, delay)
    elif module.mtype == 'VMRouter':
        return writeModuleInst_generic(module, hls_src_dir,
                                         writeTemplatePars_VMR,
                                         matchArgPortNames_VMR,
                                         first_of_type, extraports, delay)
    elif module.mtype == 'VMRouterCM':
        return writeModuleInst_generic(module, hls_src_dir,
                                         writeTemplatePars_VMRCM,
                                         matchArgPortNames_VMRCM,
                                         first_of_type, extraports, delay, split)
    elif module.mtype == 'TrackletEngine':
        return writeModuleInst_generic(module, hls_src_dir,
                                         writeTemplatePars_TE,
                                         matchArgPortNames_TE,
                                         first_of_type, extraports, delay)
    elif module.mtype == 'TrackletProcessor':
        return writeModuleInst_generic(module, hls_src_dir,
                                         writeTemplatePars_TP,
                                         matchArgPortNames_TP,
                                         first_of_type, extraports, delay, split)
    elif module.mtype == 'TrackletCalculator':
        return writeModuleInst_generic(module, hls_src_dir,
                                         writeTemplatePars_TC,
                                         matchArgPortNames_TC,
                                         first_of_type, extraports, delay)
    elif module.mtype == 'ProjectionRouter':
        return writeModuleInst_generic(module, hls_src_dir,
                                         writeTemplatePars_PR,
                                         matchArgPortNames_PR,
                                         first_of_type, extraports, delay)
    elif module.mtype == 'MatchEngine':
        return writeModuleInst_generic(module, hls_src_dir,
                                         writeTemplatePars_ME,
                                         matchArgPortNames_ME,
                                         first_of_type, extraports, delay)
    elif module.mtype == 'MatchCalculator':
        return writeModuleInst_generic(module, hls_src_dir,
                                         writeTemplatePars_MC,
                                         matchArgPortNames_MC,
                                         first_of_type, extraports, delay)
    elif module.mtype == 'MatchProcessor':
        return writeModuleInst_generic(module, hls_src_dir,
                                         writeTemplatePars_MP,
                                         matchArgPortNames_MP,
                                         first_of_type, extraports, delay)
    elif module.mtype == 'FitTrack':
        return writeModuleInst_generic(module, hls_src_dir,
                                         writeTemplatePars_FT,
                                         matchArgPortNames_FT,
                                         first_of_type, extraports, delay)
    elif module.mtype == 'TrackBuilder':
        return writeModuleInst_generic(module, hls_src_dir,
                                         writeTemplatePars_TB,
                                         matchArgPortNames_TB,
                                         first_of_type, extraports, delay)
    elif module.mtype == 'PurgeDuplicate':
        return writeModuleInst_generic(module, hls_src_dir,
                                         writeTemplatePars_PD,
                                         matchArgPortNames_PD,
                                         first_of_type, extraports, delay)
    else:
        raise ValueError(module.mtype + " is unknown.")
