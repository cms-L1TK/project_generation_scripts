from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
import re
import math
import copy
from builtins import range

#######################################
# Ordering of the processing steps
ProcOrder_dict = {
   'InputRouter':0,
   'VMRouter':1,
   'TrackletEngine':2,
   'TrackletCalculator':3,
   'ProjectionRouter':4,
   'MatchEngine':5,
   'MatchCalculator':6,
   'FitTrack':7,
   'PurgeDuplicate':8,
   'TrackBuilder':9
}
# TODO: Should be able to generate this from the wiring
#######################################
# Drawing parameters
ModuleDrawWidth_dict = {'DTCLink':2.0,
                        'InputLink':2.0,
                        'VMStubsTEInner':3.0,
                        'VMStubsTEOuter':3.0,
                        'VMStubsME':3.0,
                        'AllStubs':3.0,
                        'StubPairs':4.0,
                        'TrackletParameters':3.0,
                        'TrackletProjections':4.0,
                        'VMProjections':3.0,
                        'AllProj':2.5,
                        'CandidateMatch':3.0,
                        'FullMatch':3.0,
                        'TrackFit':2.5,
                        'TrackWord':2.5,
                        'BarrelStubWord':2.5,
                        'DiskStubWord':2.5,
                        'CleanTrack':2.5,
                        ###################
                        'InputRouter':2.0,
                        'VMRouter':2.0,
                        'TrackletEngine':4.0,
                        'TrackletCalculator':2.5,
                        'ProjectionRouter':2.5,
                        'MatchEngine':3.0,
                        'MatchCalculator':2.5,
                        'FitTrack':2.0,
                        'TrackBuilder':2.0,
                        'PurgeDuplicate':2.0,
                        'XGap':2.0}

#######################################
# Processing and memory module classes
class Node(object):
    def __init__(self, module_type, instance_name, i):
        self.mtype = module_type # Module type (e.g. "TrackletProjections")
        self.inst = instance_name
        # Bodge to prevent VHDL enums starting with a number, which is illegal.
        if (self.inst.startswith("DL_2S")):
            self.inst = self.inst.replace("DL_2S","DL_twoS")
        self.upstreams = [] # list of pointers to upstream Nodes
        self.downstreams = [] # list of pointers to downstream Nodes
        self.index = i  # instance index from the configuration file
        # drawing parameters
        self.width = 1.  # Width of the box
        self.xstart = 0  # Starting x coordinate
        self.ycenter = 0  # y coordinate
    def mtype_short(self):
        return self.inst.split("_",1)[0] # Short module type (e.g. "TPROJ")
    def var(self):
        return self.inst.split("_",1)[-1] # Remainder of instance name
        
class MemModule(Node):
    def __init__(self, module_type, instance_name, index):
        Node.__init__(self, module_type, instance_name, index)
        self.upstreams = [None]
        self.downstreams = [None]
        self.size = None
        # position flags
        self.is_initial = False # True if it is the initial step
        self.is_final = False # True if it is the final step
        self.bitwidth = 0
        self.bxbitwidth = 0
        self.is_binned = False
        self.has_numEntries_out = True # True if has numEntries out port.

    def keyName(self): # All mems with same keyName made in same VHDL "generate" loop.
        return self.mtype_short()+"_"+str(self.bitwidth)
    def isFIFO(self): # Is FIFO rather than BRAM memory
        mts = self.mtype_short()
        return (mts == "DL" or mts == "TW" or mts == "BW" or mts == "DW") 
    def __lt__(self, other) : # py3 needs this explicitly for ordering
        return self.inst < other.inst ### lexical sort on instance name

class ProcModule(Node):
    def __init__(self, module_type, instance_name, index):
        Node.__init__(self, module_type, instance_name, index)
        self.parameters = {} # dictionary of parameters
        self.order = ProcOrder_dict[module_type]
        self.input_port_names = []
        self.output_port_names = []
        self.is_first = False
        self.is_last = False
        self.IPname = instance_name

class MemTypeInfoByKey(object):
    """
    # Info common to all memory objects of a given keyName() (e.g. TPROJ_60)
    """
    def __init__(self, memList):        
        # Input: list of all memory objects of a given key type
        assert(len(memList) > 0)
        self.mtype_short = memList[0].mtype_short()
        self.mtype_long = memList[0].mtype
        self.bitwidth   = memList[0].bitwidth
        self.bxbitwidth = memList[0].bxbitwidth
        self.is_binned  = memList[0].is_binned
        self.has_numEntries_out = memList[0].has_numEntries_out
        self.isFIFO     = memList[0].isFIFO()
        # At least one memory of this type is initial.
        self.is_initial = any(m.is_initial for m in memList)
        # All memories of this type is final.
        self.is_final   = all(m.is_final for m in memList)
        assert(not (self.is_initial and self.is_final))
        # Short type name of any upstream/downstream processing module.
        self.upstream_mtype_short   = ""
        self.downstream_mtype_short = ""
        # Indicates if some modules of this type take have upstream/downstream
        # connections and others do not.
        self.mixedIO = False; 
        keySet = set()
        for m in memList:
            keySet.add(m.keyName())
            if m.upstreams[0] is not None:
                self.upstream_mtype_short = m.upstreams[0].mtype_short()
            if m.downstreams[0] is not None:
                self.downstream_mtype_short = m.downstreams[0].mtype_short()
            if (self.is_initial and not m.is_initial) or (self.is_final and not m.is_final):
                self.mixedIO = True
        assert(len(keySet) == 1) # Ensure only one key name is input memory list.
        if self.mixedIO and self.is_initial:
            print("ERROR: Memories of type ",self.mtype_short," in chain have mixed I/O: some inputs connected to chain & some to external ports. NOT YET SUPPORTED BY SCRIPT")
            exit(1)


#######################################
# Tracklet Graph
class TrackletGraph(object):
    # Constructors
    def __init__(self, procDict=None, memDict=None):
        """ Initialize from a processing modules dictionary: procDict 
            and from a memory module dictionary: memDict
            key: module instance name; value: ProcModule/MemModule object
        """
        
        self.__proc_dict = procDict if procDict is not None else {}
        self.__mem_dict = memDict if memDict is not None else {}

    @classmethod
    def from_configs(cls, fname_proc, fname_mem, fname_wire, region='-'):
        " Initialize from the configuration .dat files "
        
        # Get processing module dictionary
        procDict = cls.get_proc_dict_from_config(fname_proc)
        
        # Get memory module dictionary
        memDict = cls.get_mem_dict_from_config(fname_mem, region)
        
        # Wire the modules based on the wiring configuration
        cls.wire_modules_from_config(fname_wire, procDict, memDict)

        # Convert the TrackFit memory into separate streams for the track and
        # stub words
        cls.split_track_fit_streams(procDict, memDict)
        
        return cls(procDict, memDict)      

    @staticmethod
    def populate_bitwidths(mem,hls_dir): # FIXME this information should be parsed from the <memorytype>Memory.h HLS files, not hard-coded here
        # Populate data bit width
        barrelPSList = ["L1P","L2P","L3P"]
        barrelPS = -1
        for item in barrelPSList:
            barrelPS = max(barrelPS,mem.inst.find(item))
        barrel2SList = ["L4P","L5P","L6P"]
        barrel2S = -1
        for item in barrel2SList:
            barrel2S = max(barrel2S,mem.inst.find(item))
        diskList = ["D1P","D2P","D3P","D4P","D5P"]
        disk = -1
        for item in diskList:
            disk = max(disk,mem.inst.find(item))
        if mem.mtype == "VMStubsTEInner":
            if mem.inst.find("L5")>-1: mem.bitwidth = 23 
            else: mem.bitwidth = 22
        elif mem.mtype == "VMStubsTEOuter":
            if (mem.inst.find("L4")>-1 or mem.inst.find("L6")>-1): mem.bitwidth = 17
            else: mem.bitwidth = 16
        elif mem.mtype == "AllStubs" or mem.mtype == "InputLink":
            mem.bitwidth = 36
        elif mem.mtype == "DTCLink":
            mem.bitwidth = 39
        elif mem.mtype == "StubPairs":
            mem.bitwidth = 14
        elif mem.mtype == "TrackletParameters":
            mem.bitwidth = 70
        elif mem.mtype == "TrackletProjections" or mem.mtype == "AllProj":
            if barrelPS>-1: mem.bitwidth = 60
            if barrel2S>-1: mem.bitwidth = 58
            if disk>-1: mem.bitwidth = 59
        elif mem.mtype == "VMProjections":
            if barrelPS>-1 or barrel2S>-1: mem.bitwidth = 24
            if disk>-1: mem.bitwidth = 24
        elif mem.mtype == "VMStubsME":
            if barrelPS>-1: mem.bitwidth = 16
            if barrel2S>-1 or disk>-1: mem.bitwidth = 17
        elif mem.mtype == "CandidateMatch":
            mem.bitwidth = 14
        elif mem.mtype == "FullMatch":
            if barrelPS>-1 or barrel2S>-1: mem.bitwidth = 52
            if disk>-1: mem.bitwidth = 55
        elif mem.mtype == "TrackWord":
            mem.bitwidth = 84
        elif mem.mtype == "BarrelStubWord":
            mem.bitwidth = 46
        elif mem.mtype == "DiskStubWord":
            mem.bitwidth = 49
        else:
            raise ValueError("Bitwidth undefined for "+mem.mtype)

        # Populate BX bit width
        if (      mem.mtype == "TrackletProjections" or mem.mtype == "VMProjections"
               or mem.mtype == "CandidateMatch" or mem.mtype == "FullMatch"
               or mem.mtype == "StubPairs" or mem.mtype == "VMStubsTEInner" or mem.mtype == "VMStubsTEOuter"
               or mem.mtype == "InputLink" or mem.mtype == "DTCLink"):
            mem.bxbitwidth = 1
        elif (    mem.mtype == "AllProj" or mem.mtype == "VMStubsME"
               or mem.mtype == "AllStubs" or mem.mtype == "TrackletParameters"):
            mem.bxbitwidth = 3
        elif (    mem.mtype == "TrackWord"
               or mem.mtype == "BarrelStubWord" or mem.mtype == "DiskStubWord"):
            mem.bxbitwidth = 0 # FIFO memories
        else:
            raise ValueError("Bxbitwidth undefined for "+mem.mtype)

    @staticmethod
    def populate_is_binned(mem,hls_dir):
        # Populate fields saying whether mem module is binned
        if (mem.mtype == "VMStubsTEOuter" or mem.mtype == "VMStubsME"):
            mem.is_binned = True

    @staticmethod
    def populate_has_numEntries_out(mem,hls_dir):
        # Some memories need no numEntries out port, as no processing module wants to read it.
        # (Check which by searching for GetEntries() in HLS code).
        # If those memories are at the of the chain, add numEntries port anyway for VHDL chain debugging purposes.
        if mem.mtype == "AllStubs" and not mem.is_final:
            mem.has_numEntries_out = False
        elif mem.mtype == "AllProj" and not mem.is_final:
            mem.has_numEntries_out = False
        elif mem.mtype == "TrackletParameters" and not mem.is_final:
            mem.has_numEntries_out = False
        else:
            mem.has_numEntries_out = True

    @staticmethod
    def populate_firstlast(proc):
        # Populate fields saying whether proc module is first or last in slice
        is_first = True
        is_last = True
        for mem in proc.upstreams:
            if not mem.is_initial: is_first = False
        for mem in proc.downstreams:
            if not mem.is_final: is_last = False
        proc.is_first = is_first
        proc.is_last = is_last

    @staticmethod
    def populate_IPname(proc):
    # Set name of HLS IP core.
    # (If several instance names assigned to same IP core name, then
    #  they share a single IP core).

        if proc.mtype == 'MatchEngine':
            # Final number and phi region unimportant in typical name,
            # e.g., "ME_D5PHIC11"
            proc.IPname = proc.inst[:5]
        elif proc.mtype == 'TrackletEngine':
            innerPS = ("_L1" in proc.inst and "_L2" in proc.inst) \
                   or ("_L2" in proc.inst and "_L3" in proc.inst) \
                   or ("_L3" in proc.inst and "_L4" in proc.inst)
            outerPS = ("_L1" in proc.inst and "_L2" in proc.inst) \
                   or ("_L2" in proc.inst and "_L3" in proc.inst)
            proc.IPname = "TE_"
            proc.IPname += "PS_" if innerPS else "2S_"
            proc.IPname += "PS" if outerPS else "2S"
        else:
            # FIX: check for other processing modules steps.
            proc.IPname = proc.inst

    @staticmethod
    def get_proc_dict_from_config(fname_pconfig):
        """ Read the processing module configuration file and return a dictionary
            for processing modules.
            Key: instance name; Value: ProcModule object
        """
        proc_dict = {}
        
        # Open and read processing module configuration file
        file_proc = open(fname_pconfig, 'r')
        
        for i,line_proc in enumerate(file_proc):
            # Processing module type
            proc_type = line_proc.split(':')[0].strip()
            # temporary hack: FitTrack-->TrackBuilder
            if proc_type == "FitTrack":
                proc_type = "TrackBuilder"
            # Instance name
            proc_inst = line_proc.split(':')[1].strip()
            # Construct ProcModule object
            aProcMod = ProcModule(proc_type, proc_inst, i) 
            # Add to dictionary
            proc_dict[proc_inst] = aProcMod

        # Close file
        file_proc.close()
        
        return proc_dict
    
    @staticmethod
    def get_mem_dict_from_config(fname_mconfig, region='-'):
        """ Read the memory module configuration file and return a dictionary 
            for memory modules
            Key: instance name; Value: memory MemModule object
            region: 'L' for barrel layers only; 'D' for disks only
        """
        mem_dict = {}

        barrelstr = re.compile('L[1-6]PHI')
        diskstr = re.compile('D[1-5]PHI')
        barrelseed = re.compile('L[1235]L[2346]')
        diskseed = re.compile('D[13]D[24]')
        hybridseed = re.compile('L[12]D1')
        
        # Open and read memory configuration file
        file_mem = open(fname_mconfig, 'r')

        for i,line_mem in enumerate(file_mem):
            # Memory type
            mem_type = line_mem.split(':')[0].strip()
            # Instance name
            mem_inst = line_mem.split(':')[1].strip().split(' ')[0]
            
            # Check which detector region the memory belongs to
            isbarrel = False
            isdisk = False

            if mem_type in ['InputLink','VMStubsTE','VMStubsME','StubPairs',
                            'AllStubs','VMProjections','CandidateMatch','AllProj']:
                if barrelstr.search(mem_inst):
                    isbarrel = True
                if diskstr.search(mem_inst):
                    isdisk = True
            elif mem_type in ['TrackletProjections','FullMatch']:
                if barrelseed.search(mem_inst) and barrelstr.search(mem_inst):
                    isbarrel = True
                if diskseed.search(mem_inst) and diskstr.search(mem_inst):
                    isdisk = True
            elif mem_type in ['TrackletParameters','TrackFit','CleanTrack']:
                if barrelseed.search(mem_inst):
                    isbarrel = True
                if diskseed.search(mem_inst):
                    isdisk = True
            elif mem_type in ['DTCLink']: # Dont try to assign DTC to barrel/disk
                isbarrel = True
                isdisk = True
            else:
                raise ValueError("Unknown memory type: "+mem_type)

            #assert(isbarrel or isdisk)
            
            if region == 'L': # barrel project
                if not isbarrel:
                    continue
            elif region == 'D': # disk project
                if not isdisk:
                    continue

            if mem_type == 'VMStubsTE':
                """
                # An example of instance name: VMSTE_L6PHIB15n3
                """
                position = mem_inst.split('_')[1][:2] # layer/disk
                philabel = mem_inst.split('_')[1][5] # PHI
                mem_type_new = ""
                if position == 'L1':
                    mem_type_new = 'VMStubsTEInner'
                elif position == 'L2':
                    if philabel in ['I','J','K','L','W','X','Y','Z']: # L2L3 or L2D1 seeding
                        mem_type_new = 'VMStubsTEInner'
                    elif philabel in ['A','B','C','D']: # L1L2 seeding
                        mem_type_new = 'VMStubsTEOuter'
                    else:
                        raise ValueError("Unknown PHI label "+philabel)
                elif position == 'L3':
                    if philabel in ['A','B','C','D']: # L3L4
                        mem_type_new = 'VMStubsTEInner'
                    elif philabel in ['I','J','K','L']: # L2L3
                        mem_type_new = 'VMStubsTEOuter'
                    else:
                        raise ValueError("Unknown PHI label "+philabel)
                elif position == 'L4' or position == 'L6':
                    mem_type_new = 'VMStubsTEOuter'
                elif position == 'L5':
                    mem_type_new = 'VMStubsTEInner'
                elif position == 'D1':
                    if philabel in ['A','B','C','D']: # D1D2 seeding
                        mem_type_new = 'VMStubsTEInner'
                    elif philabel in ['W','X','Y','Z']: # L1D1 or L2D1 seeding
                        mem_type_new = 'VMStubsTEOuter'
                    else:
                        raise ValueError("Unknown PHI label "+philabel)
                elif position == 'D2' or position == 'D4':
                    mem_type_new = 'VMStubsTEOuter'
                elif position == 'D3':
                    mem_type_new = 'VMStubsTEInner'
                mem_type= mem_type_new
            # Construct MemModule object
            aMemMod = MemModule(mem_type, mem_inst, i)
            # Add to dictionary
            mem_dict[mem_inst] = aMemMod
            
        # Close file
        file_mem.close()

        return mem_dict

    @staticmethod
    def split_track_fit_streams(p_dict, m_dict):
        """ Convert any TrackFit memories into separate streams for the track
            and stub words
            p_dict: processing module dictionary
            m_dict: memory module dictionary
        """
        for m in list(m_dict.keys()): # py3 doesn't make a copy of list of keys, like py2
            if not m.startswith("TF_"):
                continue
            seed = m.split("_")[1]

            # Remove the TF memory from m_dict and from the downstreams and
            # upstreams of the upstream and downstream module, respectively.
            old_mem = m_dict.pop(m)
            up_p = None
            down_p = None
            if len(old_mem.upstreams) > 0:
                up_p = old_mem.upstreams[0]
                if up_p is not None:
                    i = up_p.downstreams.index(old_mem)
                    up_p.downstreams.remove(old_mem)
                    up_p.output_port_names.pop(i)
            if len(old_mem.downstreams) > 0:
                down_p = old_mem.downstreams[0]
                if down_p is not None:
                    i = down_p.upstreams.index(old_mem)
                    down_p.upstreams.remove(old_mem)
                    down_p.input_port_names.pop(i)

            # Replace the old memory with a track word.
            new_mem = copy.copy(old_mem)
            new_mem.mtype = "TrackWord"
            new_mem.inst = "TW_" + seed
            m_dict[new_mem.inst] = new_mem
            if up_p is not None:
                up_p.downstreams.append(new_mem)
                up_p.output_port_names.append("trackwordout")
            if down_p is not None:
                down_p.upstreams.append(new_mem)
                down_p.input_port_names.append("trackwordin")

            # Determine the layers/disks from the associated full match
            # memories.
            layers = set()
            if up_p is not None:
                for up_m in up_p.upstreams:
                    if up_m.mtype != "FullMatch":
                        continue
                    layer = up_m.inst.split("_")[-1][0:2]
                    assert(layer.startswith("L") or layer.startswith("D"))
                    layers.add(layer)

            # Replace the old memory with a stub word for each of the
            # layers/disks that can have matches.
            barrelIndex = 0
            diskIndex = 0
            for layer in sorted(layers):
                new_mem = copy.copy(old_mem)
                portname = None
                index = None
                if layer.startswith("L"):
                    new_mem.mtype = "BarrelStubWord"
                    new_mem.inst = "BW_" + seed + "_" + layer
                    portname = "barrelstub"
                    index = barrelIndex
                    barrelIndex += 1
                elif layer.startswith("D"):
                    new_mem.mtype = "DiskStubWord"
                    new_mem.inst = "DW_" + seed + "_" + layer
                    portname = "diskstub"
                    index = diskIndex
                    diskIndex += 1
                # Avoid all SW having same index, as sorted by them later.
                new_mem.index += 0.01*barrelIndex + 0.1*diskIndex;

                m_dict[new_mem.inst] = new_mem
                if up_p is not None:
                    up_p.downstreams.append(new_mem)
                    up_p.output_port_names.append(portname + str(index) + "out")
                if down_p is not None:
                    down_p.upstreams.append(new_mem)
                    down_p.input_port_names.append(portname + str(index) + "in")

    @staticmethod
    def wire_modules_from_config(fname_wconfig, p_dict, m_dict):
        """ Read wiring configuration file and connect the modules
            p_dict: processing module dictionary
            m_dict: memory module dictionary
        """
        assert(len(p_dict)>0 and len(m_dict)>0)

        # Open and read the wiring configuration file
        file_wires = open(fname_wconfig, 'r')

        for line_wire in file_wires:
            ######
            # memory instance in wiring config
            wmem_inst = line_wire.split('input=>')[0].strip()
            # check if the memory is in the dictionary
            if not wmem_inst in m_dict:
                continue
            
            iMem = m_dict[wmem_inst]

            ######
            # processing module that writes to this memory
            upstr = line_wire.split('input=>')[1].split('output=>')[0].strip()
            iproc_write = upstr.split('.')[0].strip()

            if iproc_write != '': # if it has an upstream module
                # Get the processing module and make the connections
                iMem.upstreams[0] = p_dict[iproc_write]
                p_dict[iproc_write].downstreams.append(iMem)
                iproc_write_port = upstr.split('.')[1].strip()
                p_dict[iproc_write].output_port_names.append(iproc_write_port)
            else:
                iMem.is_initial = True

            ######
            # processing module that reads from this memory
            downstr = line_wire.split('input=>')[1].split('output=>')[1].strip()
            iproc_read = downstr.split('.')[0].strip()
            
            if iproc_read != '': # if it has a downstream module
                # Get the downstream processing module and make the connections
                iMem.downstreams[0] = p_dict[iproc_read]
                p_dict[iproc_read].upstreams.append(iMem)
                iproc_read_port = downstr.split('.')[1].strip()
                p_dict[iproc_read].input_port_names.append(iproc_read_port)
            else:
                iMem.is_final = True

        # Close file
        file_wires.close()

        # Remove processing modules if they do not have input/output memories
        for name, proc in p_dict.items():
            nInputs = len(proc.upstreams)
            nOutputs = len(proc.downstreams)
            
            if nInputs == 0 or nOutputs == 0:
                del p_dict[name]
        
    ########################################       
    # Accessors
    def get_all_memory_names(self):
        " Return a list of memory instance names "
        return list(self.__mem_dict.keys())

    def get_all_memory_modules(self):
        " Return a list of MemModule objects "
        return list(self.__mem_dict.values())

    def get_all_proc_names(self):
        " Return a list of processing module instance names "
        return list(self.__proc_dict.keys())

    def get_all_proc_modules(self):
        " Return a list of ProcModule objects "
        return list(self.__proc_dict.values())

    def get_proc_module(self, instance_name, verbose=True):
        " Return a ProcModule object given the instance name "
        if instance_name in self.__proc_dict:
            return self.__proc_dict[instance_name]
        else:
            if verbose:
                print("WARNING!! Cannot find module", instance_name,"!!")
            return None

    def get_all_module_units(self, module):
        "Return all the ProcModule objects of a given type"
        modules = {}
        for instance_name in self.__proc_dict:
            if instance_name.startswith(module+"_"):
                modules[instance_name]=self.__proc_dict[instance_name]
        if not modules:
            print("WARNING!! Cannot find any modules with name starting with", module,"!!")
        else:
            return modules

    def get_mem_module(self, instance_name, verbose=True):
        " Return a MemModule object given the instance name "
        if instance_name in self.__mem_dict:
            return self.__mem_dict[instance_name]
        else:
            if verbose:
                print("Cannot find module", instance_name)
            return None
    
    def get_module(self, instance_name):
        " Return a ProcModule/MemModule object given the instance name "
        # try processing modules first
        aModule = self.get_proc_module(instance_name, verbose=False)
        # if not, try memory modules
        if aModule is None:
            aModule = self.get_mem_module(instance_name, verbose=False)
        # if still no, print(warning)
        if aModule is None:
            print("TrackletGraph: Cannot find module", instance_name)

        return aModule
    
    def reset_mem_position_flags(self):
        """ Reset all the is_initial and is_final flags of the MemModule objects 
            based on the connections
        """
        for imem in self.get_memory_modules():
            
            assert(len(imem.upstreams)==1 and len(imem.downstreams)==1)

            imem.is_initial = imem.upstreams[0] is None
            imem.is_final = imem.downstreams[0] is None

    @staticmethod
    def get_input_mem_dict(MemList):
        """ Return a dictionary for input memories.
            Key: memory type; Value: list of instance
        """
        inmem_dict = {}
        for mem in MemList:
            if mem.is_initial:
                if mem.mtype not in inmem_dict:
                    inmem_dict[mem.mtype] = list()
                inmem_dict[mem.mtype].append(mem)

        return inmem_dict

    @staticmethod
    def get_output_mem_dict(MemList):
        """ Return a dictionary for output memories.
            Key: memory type; Value: list of instance
        """
        outmem_dict = {}
        for mem in MemList:
            if mem.is_final:
                if mem.mtype not in outmem_dict:
                    outmem_dict[mem.mtype] = list()
                outmem_dict[mem.mtype].append(mem)

        return outmem_dict
    
    ########################################
    # Graph methods
    @staticmethod
    def add_input_mem_modules(aProcModule, ProcList=[], MemList=[]):
        """ Add a given ProcModule object and all its input memories into the 
            ProcList and MemList respectively
        """
        if aProcModule is None:
            return ProcList, MemList

        if aProcModule not in ProcList:
            ProcList.append(aProcModule)

        # Loop over all its input memories
        for inmem in aProcModule.upstreams:
            inmem.is_final = False

            if inmem not in MemList:
                inmem.is_initial = True
                MemList.append(inmem)

        return ProcList, MemList
        
    @staticmethod
    def add_output_mem_modules(aProcModule, ProcList=[], MemList=[]):
        """ Add a given ProcModule object and all its output memories into the
            ProcList and MemList respectively
        """
        if aProcModule is None:
            return ProcList, MemList

        if aProcModule not in ProcList:
            ProcList.append(aProcModule)

        # Loop over all its output memories
        for outmem in aProcModule.downstreams:
            outmem.is_initial = False

            if outmem not in MemList:
                outmem.is_final = True
                MemList.append(outmem)

        return ProcList, MemList
        
    @staticmethod
    def add_connected_mem_modules(aProcModule, ProcList=[], MemList=[]):
        """ Add a given ProcModule object and all the connected MemModule 
            objects into the ProcList and MemList respectively
        """
        TrackletGraph.add_input_mem_modules(aProcModule, ProcList, MemList)
        TrackletGraph.add_output_mem_modules(aProcModule, ProcList, MemList)

        return ProcList, MemList

    @staticmethod
    def add_upstream_proc_modules(aMemModule, ProcList=[], MemList=[]):
        """ Add a given MemModule object and its upstream ProcModule object into
            the ProcList and MemList respectively
            Also add all the MemModule objects connected to the upstream 
            ProcModule object into the MemList
        """
        if aMemModule is None:
            return ProcList, MemList

        # A few special cases: stop further expanding them upstream
        if aMemModule.mtype in ['VMStubsME','AllStubs','TrackletParameters','AllProj']:
            aMemModule.is_initial = True
            return ProcList, MemList

        assert(len(aMemModule.upstreams)==1)
        prevProcModule = aMemModule.upstreams[0]

        if prevProcModule is not None:
            aMemModule.is_initial = False

        if aMemModule not in MemList:
            aMemModule.is_final = True
            MemList.append(aMemModule)
        
        TrackletGraph.add_connected_mem_modules(prevProcModule, ProcList, MemList)

        return ProcList, MemList

    @staticmethod
    def add_downstream_proc_modules(aMemModule, ProcList=[], MemList=[]):
        """ Add a given MemModule object and its downstream ProcModule object 
            into the ProcList and MemList respectively
            Also add all the MemModule objects connected to the downstream 
            ProcModule object into the MemList
        """
        if aMemModule is None:
            return ProcList, MemList
        
        # A few special cases: stop further expanding them downstream
        if aMemModule.mtype in ['VMStubsME','AllStubs','TrackletParameters','AllProj']:
            aMemModule.is_final = True
            return ProcList, MemList

        assert(len(aMemModule.downstreams)==1)
        nextProcModule = aMemModule.downstreams[0]

        if nextProcModule is not None:
            aMemModule.is_final = False

        if aMemModule not in MemList:
            aMemModule.is_initial = True
            MemList.append(aMemModule)

        TrackletGraph.add_connected_mem_modules(nextProcModule, ProcList, MemList)

        return ProcList, MemList  

    @staticmethod
    def add_connected_proc_modules(aMemModule, ProcList=[], MemList=[]):
        """ Add a given MemModule object and both its upstream and downstream 
            ProcModule objects into the ProcList and MemList respectively
            Also add all the MemModule objects connected to either of the 
            ProcModule object into the MemList
        """
        TrackletGraph.add_upstream_proc_modules(aMemModule, ProcList, MemList)
        TrackletGraph.add_downstream_proc_modules(aMemModule, ProcList, MemList)

        return ProcList, MemList

    #@staticmethod
    #def collect_proc_steps_downstream(aProcModule, ProcList=[]):
    #    """
    #    """
    #    for omem in aProcModule.downstreams:
    #        assert(len(omem.downstreams)==1)
    #        if not omem.is_final:
    #            nextProcModule = mem.downstreams[0]
    
    #@staticmethod
    #def count_proc_steps_upstream(aProcModule):
        
        
    #@staticmethod
    #def count_proc_steps_downstream(aProcModule, ProcList=[]):

    
    @staticmethod
    def get_slice_around_proc(aProcModule, nStepsUp=0, nStepsDown=0):
        """ Get a slice of the tracklet project that centers around the 
            processing module <aProcModule> and expands <nStepsUp> upstream  
            and <nStepsDown> downstreams
            Return a list of ProcModule objects and a list of MemModule objects
        """
        proc_list = []
        
        # Seperate memory lists into upstream and downstream memories
        # This is because we don't want to expand the secondary memory modules
        # toward an opposite direction further
        # E.g. we are not interested in the processing module that writes to 
        # the downstream memory that is a input memory of a downstream processing
        # module in our list. We fill these kind of memories directly from the
        # test bench.
        inmem_list = []
        outmem_list = []

        # Grow from the central processing module
        TrackletGraph.add_input_mem_modules(aProcModule, proc_list, inmem_list)
        TrackletGraph.add_output_mem_modules(aProcModule, proc_list, outmem_list)

        # Grow upstream
        for istepup in range(nStepsUp,0,-1):
            # Get the latest list of the initial memories
            initmem_list = []
            for mem in inmem_list:
                if mem.is_initial:
                    initmem_list.append(mem)

            # Expand upstream further from the current initial memories
            for imem in initmem_list:
                TrackletGraph.add_upstream_proc_modules(imem, proc_list, inmem_list)
            
        # Grow downstream
        for istepdown in range(nStepsDown,0,-1):
            # Get the latest list of the final memories
            finalmem_list = []
            for mem in outmem_list:
                if mem.is_final:
                    finalmem_list.append(mem)

            # Expand downstream further from the current final memories
            for fmem in finalmem_list:
                TrackletGraph.add_downstream_proc_modules(fmem, proc_list, outmem_list)

        # Merge inmem_list and outmem_list
        # There could be loops in the tracklet graph(?), so inmem_list and
        # outmem_list can potentially have duplicated modules
        mem_list = sorted(list(set(inmem_list).union(outmem_list)))

        # The duplicated memory modules should have both is_initial and is_final
        # flags set to True during the growing process. Correct them now.
        for mem in mem_list:
            if mem.is_initial and mem.is_final:
                mem.is_initial = False
                mem.is_final = False

        return proc_list, mem_list

    # TODO
    #@staticmethod
    #def get_slice_between(startProcModule, endProcModule):

    #@stateicmethod
    #def get_best_slice_between(startProcStep, endProcStep):

    ########################################
    # Draw
    @staticmethod
    def draw_graph(ProcList):
        """
        """
        # First check how many types of modules to draw
        ProcTypes = set()
        for proc in ProcList:
            ProcTypes.add(proc.mtype)

        # total number of processing module types
        num_proc_types = len(ProcTypes)
        # total number of columns to draw
        num_columns = 2 * num_proc_types + 1

        # A container for modules in each column to draw
        columns_module = [[] for c in range(num_columns)]
        
        # Sort the ProcList based on the module types
        ProcList_sorted = sorted(ProcList, key=lambda x: x.index)
        
        i_proc_type = 0
        current_mtype = ""       
        for proc in ProcList_sorted:
            
            if proc.mtype != current_mtype:
                i_proc_type += 1
                current_mtype = proc.mtype
            
            assert(i_proc_type <= num_proc_types and i_proc_type >= 1)
                
            inmem_list = []
            for inmem in proc.upstreams:
                if inmem.is_initial:
                    inmem_list.append(inmem)

            outmem_list = proc.downstreams
            
            # Add to column_modules
            columns_module[2*i_proc_type-2] += inmem_list
            columns_module[2*i_proc_type-1].append(proc)
            columns_module[2*i_proc_type] += outmem_list
            
        # Do some floor planning and determine the module coordinates
        columns_width = [0.] * num_columns
        for icol, column in enumerate(columns_module):
            for module in column:
                mwidth = ModuleDrawWidth_dict[module.mtype]
                if mwidth > columns_width[icol]:
                    columns_width[icol] = mwidth

        # Starting x coordinate 
        columns_xstart = []
        xtotal = 0.
        for icol, width in enumerate(columns_width):
            xgap = ModuleDrawWidth_dict['XGap']
            xtotal += xgap if icol>=1 else xgap/4.
            columns_xstart.append(xtotal)
            xtotal += width
        xtotal += xgap/4.
            
        # Normalize
        columns_xstart = [float(x)/xtotal for x in columns_xstart]
            
        # Number of modules per column
        columns_num = [len(modules) for modules in columns_module]
        maxnum = max(columns_num)

        # Set coordinates
        for icol, column in enumerate(columns_module):
            nmodules = columns_num[icol]
            ytotal = 0.
            for imod, module in enumerate(column):
                module.width = ModuleDrawWidth_dict[module.mtype]/xtotal
                module.xstart = columns_xstart[icol]
                module.ycenter = (0.5+imod)/nmodules
        
        # Write to the output file
        fo = open("diagram.dat","w")

        for proc in ProcList:
            # Process Module
            fo.write("Process "+proc.inst+" ")
            fo.write(str(proc.xstart)+" "+str(proc.ycenter)+" ")
            fo.write(str(proc.xstart+proc.width)+" "+str(proc.ycenter)+"\n")

            # Memory Module
            for imem in proc.upstreams:
                fo.write("Memory "+imem.inst+" ")
                fo.write(str(imem.xstart)+" "+str(imem.ycenter)+" ")
                fo.write(str(imem.xstart+imem.width)+" "+str(imem.ycenter)+"\n")
                # Draw lines
                fo.write("Line "+str(imem.xstart+imem.width)+" "+str(imem.ycenter))
                fo.write(" "+str(proc.xstart)+" "+str(proc.ycenter)+"\n")
                
            for omem in proc.downstreams:
                fo.write("Memory "+omem.inst+" ")
                fo.write(str(omem.xstart)+" "+str(omem.ycenter)+" ")
                fo.write(str(omem.xstart+omem.width)+" "+str(omem.ycenter)+"\n")
                # Draw lines
                fo.write("Line "+str(proc.xstart+proc.width)+" "+str(proc.ycenter))
                fo.write(" "+str(omem.xstart)+" "+str(omem.ycenter)+"\n")
                
        fo.close()

        # FIXME
        # Work In Progress - adjusts sizes in TrackletProject.pdf
        # Return canvas size in pixels along X and Y
        pageWidth = 10000
        pageHeight = 5000
        dyBox = 0.5/(math.log(maxnum)*10)
        textSize = 0.5/(math.log(maxnum)*10+1)

        # print( pageWidth, pageHeight, dyBox, textSize, maxnum)
        return int(pageWidth), int(pageHeight), dyBox, textSize
