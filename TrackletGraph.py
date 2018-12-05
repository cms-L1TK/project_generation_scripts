#######################################
# Ordering of the processing steps
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
# TODO: Should be able to generate this from the wiring

#######################################
# Processing and memory module classes
class Node(object):
    def __init__(self, module_type, instance_name):
        self.mtype = module_type
        self.inst = instance_name
        self.upstreams = [] # list of pointers to upstream Nodes
        self.downstreams = [] # list of pointers to downstream Nodes
        
class MemModule(Node):
    def __init__(self, module_type, instance_name):
        Node.__init__(self, module_type, instance_name)
        self.upstreams = [None]
        self.downstreams = [None]
        self.size = None
        # position flags
        self.is_initial = False # True if it is the initial step
        self.is_final = False # True if it is the final step

class ProcModule(Node):
    def __init__(self, module_type, instance_name):
        Node.__init__(self, module_type, instance_name)
        self.parameters = {} # dictionary of parameters
        self.order = ProcOrder_dict[module_type]

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
    def from_configs(cls, fname_proc, fname_mem, fname_wire):
        " Initialize from the configuration .dat files "
        
        # Get processing module dictionary
        procDict = cls.get_proc_dict_from_config(fname_proc)
        
        # Get memory module dictionary
        memDict = cls.get_mem_dict_from_config(fname_mem)
        
        # Wire the modules based on the wiring configuration
        cls.wire_modules_from_config(fname_wire, procDict, memDict)
        
        return cls(procDict, memDict)      

    @staticmethod
    def get_proc_dict_from_config(fname_pconfig):
        """ Read the processing module configuration file and return a dictionary
            for processing modules.
            Key: instance name; Value: ProcModule object
        """
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
            # Add to dictionary
            proc_dict[proc_inst] = aProcMod

        # Close file
        file_proc.close()
        
        return proc_dict
    
    @staticmethod
    def get_mem_dict_from_config(fname_mconfig):
        """ Read the memory module configuration file and return a dictionary 
            for memory modules
            Key: instance name; Value: memory MemModule object
        """
        mem_dict = {}

        # Open and read memory configuration file
        file_mem = open(fname_mconfig, 'r')

        for line_mem in file_mem:
            # Memory type
            mem_type = line_mem.split(':')[0].strip()
            # Instance name
            mem_inst = line_mem.split(':')[1].strip().split(' ')[0]
            # Construct MemModule object
            aMemMod = MemModule(mem_type, mem_inst)
            # Add to dictionary
            mem_dict[mem_inst] = aMemMod
            
        # Close file
        file_mem.close()

        return mem_dict
        
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
            iMem = m_dict[wmem_inst]

            ######
            # processing module that writes to this memory
            upstr = line_wire.split('input=>')[1].split('output=>')[0].strip()
            iproc_write = upstr.split('.')[0].strip()

            if iproc_write != '': # if it has an upstream module
                # Get the processing module and make the connections
                iMem.upstreams[0] = p_dict[iproc_write]
                p_dict[iproc_write].downstreams.append(iMem)
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
            else:
                iMem.is_final = True

        # Close file
        file_wires.close()
        
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
                print "WARNING!! Cannot find module", instance_name,"!!"
            return None

    def get_mem_module(self, instance_name, verbose=True):
        " Return a MemModule object given the instance name "
        if instance_name in self.__mem_dict:
            return self.__mem_dict[instance_name]
        else:
            if verbose:
                print "Cannot find module", instance_name
            return None
    
    def get_module(self, instance_name):
        " Return a ProcModule/MemModule object given the instance name "
        # try processing modules first
        aModule = self.get_proc_module(instance_name, verbose=False)
        # if not, try memory modules
        if aModule is None:
            aModule = self.get_mem_module(instance_name, verbose=False)
        # if still no, print warning
        if aModule is None:
            print "TrackletGraph: Cannot find module", instance_name

        return aModule
    
    def reset_mem_position_flags(self):
        """ Reset all the is_initial and is_final flags of the MemModule objects 
            based on the connections
        """
        for imem in self.get_memory_modules():
            
            assert(len(imem.upstreams)==1 and len(imem.downstreams)==1)

            imem.is_initial = imem.upstreams[0] is None
            imem.is_final = imem.downstreams[0] is None

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
        mem_list = list(set(inmem_list).union(outmem_list))

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
