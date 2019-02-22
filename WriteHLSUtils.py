########################################
# Utilities for writing Vivado HLS code
########################################
#from collections import deque
from TrackletGraph import MemModule, ProcModule

########################################
# Memory objects
########################################
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
        assert(position in ['D1','D2','D3','D4','D5'])
        bitformat = 'DISK'

    return 'VMStubMEMemory<'+bitformat+'>'

def getMemoryClassName_AllStubs(instance_name):
    ######################
    # FIXME: separate Disk PS and 2S AllStub memories for MatchCalculator
    # when config files are updated
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
        bitformat = 'BARRELPS'
    elif position in ['L4','L5','L6']:
        bitformat = 'BARREL2S'
    else: # Disk
        assert(position in ['D1','D2','D3','D4','D5'])
        bitformat = 'DISK'

    return 'TrackletProjectionMemory<'+bitformat+'>'

def getMemoryClassName_AllProj(instance_name):
    # e.g. AP_L4PHIB
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
    # e.g. VMPROJ_D3PHIA2
    position = instance_name.split('_')[1][:2] # layer/disk
    if position in ['L1','L2','L3','L4','L5','L6']:
        return 'VMProjectionMemory<BARREL>'
    else:
        assert(position in ['D1','D2','D3','D4','D5'])
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
        assert(position in ['D1','D2','D3','D4','D5'])
        return 'FullMatchMemory<DISK>'

def getMemoryClassName_TrackFit(instance_name):
    # e.g. TF_L3L4
    assert('TF_' in instance_name)
    return 'TrackFitMemory'

def getMemoryClassName_CleanTrack(instance_name):
    # e.g. CT_L5L6
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

########################################
# Processing functions
########################################
################################
# VMRouter
################################
def writeTemplatePars_VMR(aVMRModule):
    assert(0)
    return ""

def matchArgPortNames_VMR(argname, portname):
    assert(0)
    return False

################################
# TrackletEngine
################################
def writeTemplatePars_TE(aTEModule):
    assert(0)
    return ""

def matchArgPortNames_TE(argname, portname):
    assert(0)
    return False

################################
# TrackletCalculator
################################
def writeTemplatePars_TC(aTCModule):
    assert(0)
    return ""

def matchArgPortNames_TC(argname, portname):
    assert(0)
    return False

################################
# ProjectionRouter
################################
####
# Write ProjectionRouter template parameters
def writeTemplatePars_PR(aPRModule):
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

####
# Define rules to match the argument and the port names for ProjectionRouter
def matchArgPortNames_PR(argname, portname):
    
    if 'proj' in argname and 'in' in argname:
        # projXXin for input TrackletProjection memories
        return argname==portname
    elif 'allprojout' in argname:
        # output AllProjection memory
        return argname==portname
    elif 'vmprojout' in argname:
        if 'vmprojout' not in portname:
            return False
        # output VMProjection memories
        # port name format: vmprojoutPHIA13
        # get the last digits
        vmphi_port = int(portname[13:]) # 1 - 32
        # covert allproj phi region A, B, C, D, ... to 1, 2, 3, 4, ...
        projphi_port = ord(portname[12].lower()) - 96
        # The number of vmme bins per allproj phi is either 8 or 4
        nvmme = 8 # if this is true, expect (vmphi-1)/nvmme + 1 == projphi
        # if not, try nvmme = 4
        if (vmphi_port-1)/nvmme + 1 != projphi_port:
            nvmme = 4
            assert((vmphi_port-1)/nvmme + 1 == projphi_port)
            
        # vmprojoutX for output VMProjection memories
        X_port = vmphi_port%nvmme if vmphi_port%nvmme != 0 else nvmme
        X_arg = int(argname[9:])
        return X_arg == X_port
    else:
        print "matchArgPortNames_PR: Unknown argument", argname
        return False
    
################################
# MatchEngine
################################
####
# Write MatchEngine template parameters
def writeTemplatePars_ME(aMEModule):
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
        print "WARNING! Disk MatchEngine is not supported yet!"
        DISK = pos[1]
        VMSTYPE = 'DISK'

    templpars_str = LAYER+','+VMSTYPE
    return templpars_str

####
# Define rules to match the argument and the port names for MatchEngine
def matchArgPortNames_ME(argname, portname):

    if argname == 'instubdata':
        return portname == 'vmstubin'
    elif argname == 'inprojdata':
        return portname == 'vmprojin'
    elif argname == 'outcandmatch':
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
        
    templpars_str = ASTYPE+','+APTYPE+','+FMTYPE+','+LAYER+','+DISK
    # PHISEC? Is this necessary?
        
    return templpars_str

def matchArgPortNames_MC(argname, portname):
    if argname in ['match1','match2','match3','match4',
                   'match5','match6','match7','match8',
                   'allstub','allproj']:
        return portname == argname+'in'
    elif argname == 'fullmatch1':
        return portname == 'matchout1'
    elif argname == 'fullmatch2':
        return portname == 'matchout2'
    else:
        print "matchArgPortNames_MC: Unknow argument name", argname
        return False

################################
# FitTrack
################################
def writeTemplatePars_FT(aFTModule):
    assert(0)
    return ""

def matchArgPortNames_FT(argname, portname):
    assert(0)
    return False

################################
# PurgeDuplicate
################################
def writeTemplatePars_PD(aPDModule):
    assert(0)
    return ""

def matchArgPortNames_PD(argname, portname):
    assert(0)
    return False

################################
def parseProcFunction(proc_name, fname_def):
    # Parse the definition of the processing function in the header file
    # Assume all processing functions are templatized
    # Return a list of function argument types, argument names,
    # and template parameters
    
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
    
    for args in arguments_str.split(","):
        # get rid of 'const' 
        args = args.replace("const","").strip()
        # get rid of '*'
        args = args.replace("*","").strip()
        # get rid of '&' ?

        # argument type
        atype = ' '.join(args.split()[:-1]) # combine all strings except the last
        arg_types_list.append(atype)
        # argument name
        aname = args.split()[-1] # the last entry in the list
        arg_names_list.append(aname)

    # get the template parameter list
    templPars_str = template_buffer.split("<")[1].split(">")[0]
    
    for par in templPars_str.split(","):
        par = par.strip()
        templ_pars_list.append(par.split()[-1]) # the last entry in the list

    return arg_types_list, arg_names_list, templ_pars_list

########################################
def writeProcFunction_BX(argtype):
    # FIXME
    bx_str = ""
    # bunch crossing
    if argtype == "BXType":
        bx_str += "bx,\n"
    elif argtype == "BXType&":
        bx_str += "bx_o,\n" # output bx

    return bx_str

def getProcFunctionArguments(aProcModule, argTypeList, argNameList, 
                             ArgName_Match_PortName=None):
    # Return a string of the processing function arguments
    # aProcModule: a ProcModule instance, for which we are writing the function string
    # argTypeList and argNameList: Lists of argument types and names from parsing the correspoding HLS function definitions
    # ArgName_Match_PortName: a function that defines the rules of matching argument names and the port names

    arguments_str = ""

    memModuleList = list(aProcModule.upstreams + aProcModule.downstreams)
    portNameList = list(aProcModule.input_port_names + aProcModule.output_port_names)
    
    # loop over the list of argument names from parsing the header file
    for argtype, argname in zip(argTypeList, argNameList):
        
        # Special cases e.g. bunch crossing
        if "BXType" in argtype:
            arguments_str += writeProcFunction_BX(argtype)
            continue

        # Given argument name, search for the matched port name in the mem lists
        foundMatch = False
        for memory, portname in zip(memModuleList, portNameList):
            # Check if the portname matches the argument name from function def
            if ArgName_Match_PortName is None:
                # No matching rule provided, just check if the names are the same
                foundMatch = (argname==portname)
            else:
                # Use the provided matching rules
                foundMatch = ArgName_Match_PortName(argname, portname)

            if foundMatch:
                # Add the memory instance to the arguments
                if not (memory.is_initial or memory.is_final):
                    arguments_str += "&"
                arguments_str += memory.inst+",\n"
                # Remove the already added module and name from the lists
                memModuleList.remove(memory)
                portNameList.remove(portname)
                break

        if not foundMatch:
            # no matched memory instance found, write a null pointer
            arguments_str += "0,\n"
            
    # end of loop
    
    return arguments_str.rstrip(",\n")

def writeProcFunction_generic(module, hls_src_dir, f_writeTemplatePars,
                              f_matchArgPortNames):
    ####
    # function name
    assert(module.mtype in ['VMRouter','TrackletEngine','TrackletCalculator',
                            'ProjectionRouter','MatchEngine','MatchCalculator',
                            'DiskMatchCalculator','FitTrack','PurgeDuplicate'])
    function_str = module.mtype
    # Update here if the function name is not exactly the same as the module type

    ####
    # Header file when the processing function is defined
    fname_def = module.mtype + '.hh'
    # Special cases (probably should make the naming consistent...)
    if module.mtype in ['TrackletEngine','MatchEngine']:
        fname_def = module.mtype + '.h'
    # DiskMatchCalculator?
    
    fname_def = hls_src_dir.rstrip('/')+'/'+fname_def
    
    ####
    # Get the list of argument typesm names, and template parameters
    argtypes,argnames,templpars = parseProcFunction(function_str,fname_def)

    ####
    # Determine function template parameters
    templpars_str = f_writeTemplatePars(module)

    ####
    # Determine function arguments
    arguments_str = getProcFunctionArguments(module, argtypes, argnames,
                                             f_matchArgPortNames)

    ####
    # Put ingredients togther
    function_str += "<"+templpars_str+">\n"
    function_str += "("+arguments_str+");\n"
    
    return function_str
    
def writeProcFunction(module, hls_src_dir):
    if module.mtype == 'VMRouter':
        return writeProcFunction_generic(module, hls_src_dir,
                                         writeTemplatePars_VMR,
                                         matchArgPortNames_VMR)
    elif module.mtype == 'TrackletEngine':
        return writeProcFunction_generic(module, hls_src_dir,
                                         writeTemplatePars_TE,
                                         matchArgPortNames_TE)
    elif module.mtype == 'TrackletCalculator':
        return writeProcFunction_generic(module, hls_src_dir,
                                         writeTemplatePars_TC,
                                         matchArgPortNames_TC)
    elif module.mtype == 'ProjectionRouter':
        return writeProcFunction_generic(module, hls_src_dir,
                                         writeTemplatePars_PR,
                                         matchArgPortNames_PR)
    elif module.mtype == 'MatchEngine':
        return writeProcFunction_generic(module, hls_src_dir,
                                         writeTemplatePars_ME,
                                         matchArgPortNames_ME)
    elif module.mtype in ['MatchCalculator','DiskMatchCalculator']:
        return writeProcFunction_generic(module, hls_src_dir,
                                         writeTemplatePars_MC,
                                         matchArgPortNames_MC)
    elif module.mtype == 'FitTrack':
        return writeProcFunction_generic(module, hls_src_dir,
                                         writeTemplatePars_FT,
                                         matchArgPortNames_FT)
    elif module.mtype == 'PurgeDuplicate':
        return writeProcFunction_generic(module, hls_src_dir,
                                         writeTemplatePars_PD,
                                         matchArgPortNames_PD)
    else:
        raise ValueError(module.mtype + " is unknown.")
