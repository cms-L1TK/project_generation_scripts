import os,sys
import re

def topOfList(l,string):
    l1 = [x for x in l if string not in x]
    l2 = [x for x in l if string in x]
    for x in l2:
        l1.insert(0,x)
    return l1
def endOfList(l,string):
    l1 = [x for x in l if string not in x]
    l2 = [x for x in l if string in x]
    print '1',l1
    print '2',l2
    for x in l1:
        l2.append(x)
    return l2

# Define the module class with all the properties
class Module:
    def __init__(self):
        self.module = None # Module name
        self.name = None # Instance name
        self.coname = None # Instance name with copy number ('n1','n2','n3'...) in the end stripped
        self.inputs = None # In and out from master wires file
        self.outputs = None
        self.in_names = None # In and out names should be consistent with Verilog modules
        self.out_names = None
        self.common = None
        self.parameters = '' # Each module has unique parameters
        self.size = 0 # Memory sizes for connecting wires
        self.depth = 0 # For Memory depth ( number of bits for address - 1)
        self.start = '' 
        self.done = ''
        self.reset = ''
        self.resetdone=''

# Read the processing modules
#if len(sys.argv) > 1:
#    region = sys.argv[1]
#else:
#    print 'Region to process needed. Try "D3" and run again'
#    sys.exit()
# Run the other scripts from here
#os.system('python SubProject.py '+region)
#os.system('python Wires.py wires.'+region)

# generate only full project for now
region = 'new'

f = open('processingmodules_'+region+'.dat')
modules = []
for line in f:
    signals = [] # Pair with nice name and specific instance name
    signals.append(line.split(':')[0])
    signals.append(line.split(':')[1].strip())
    modules.append(signals) # Add to the list of pairs

# Read the memory modules
g = open('memorymodules_'+region+'.dat')
memories = []
for line in g:
    signals = [] # Nice name, instance name, memory size
    signals.append(line.split(':')[0])
    signals.append(line.split(':')[1].split(' ')[1].strip())
    if len(line.split(':')[1].split(' '))>2:
        signals.append(int(line.split(':')[1].split(' ')[-1].replace('[','').replace(']','').strip()))
    memories.append(signals) # Add to the list of triplets

# Common signals for every module # IPBus might go away
#Common = '.clk(clk),\n.reset(reset),\n.en_proc(en_proc)'
Common = '.clk(clk)'

# Read initial lines of Tracklet_processing
# Define inputs, outputs and start/done signals
p = open('prologue_longvm.txt')
prologue = []
for line in p:
    prologue.append(line)
# Read final lines for IPbus and possible reader
ep  = open('epilogue.txt')
epilogue = []
for line in ep:
    epilogue.append(line)

string_prologue = ''
string_starts = ''
string_memories = ''
string_processing = ''
string_epilogue = ''
####################################################
####################################################

il = 0

# Always write the initial lines
print 'write prologue'
for p in prologue:
    string_prologue += '\n' +  p.strip()
print 'start memory loop'
# Start looping over the memories first
for x in memories:
    h = open('wires_'+region+'.dat') # Open the wire connections file
    m = Module() # Create a module
    i = [] # List of inputs
    i_n = [] # List of input names
    o = [] # List of outputs
    o_n = [] # List of output names
    m.module = x[0] # Module nice name from memory list
    m.name = x[1]  # Module instance name from memory list
    m.coname = re.sub('n[0-9]+','',x[1]) # strip 'n1','n2',... at the end
    if len(x)>2: # If triplet, get the memory size
        m.size = x[2]  # FIXME
        
    for line in h: # Loop over connections
        if line.split(' ')[0] == m.name:  # If instance corresponds to current memory
            if len(line.split(' ')[2].split('.')) > 1: # Memory has inputs
                i.append(line.split(' ')[2].split('.')[0]+'_'+m.name) # Add input to module's list
                i.append(line.split(' ')[2].split('.')[0]+'_'+m.name+'_wr_en') # Memory inputs usually have a write enable
                i_n.append('data_in') # Names defined in Verilog memory module
                i_n.append('enable')
            if len(line.split(' ')[-1].split('.')) > 1: # Memory has outputs
                o.append(m.name+'_'+line.split(' ')[-1].split('.')[0]+'_number') # Number of items in memory that goes to processing module
                o.append(m.name+'_'+line.split(' ')[-1].split('.')[0]+'_read_add')
                o.append(m.name+'_'+line.split(' ')[-1].split('.')[0])
                o_n.append('number_out') # Names defined in Verilog memory module
                o_n.append('read_add')
                o_n.append('data_out')
    # Define the properties of the module
    m.inputs = i
    m.outputs = o
    m.in_names = i_n
    m.out_names = o_n
    m.common = Common
    if len(m.inputs) > 0:
        m.start = m.inputs[0].replace(m.name,'')+'start'
        m.reset = m.inputs[0].replace(m.name,'')+'reset'
    m.done = m.name+'_start'
    m.resetdone = m.name+'_reset'
    ####################################################
    # Specific properties of the memories
    # Any new memories added here
    ####################################################
    #if m.module == 'InputLink':
    #    il +=  1
    #    m.outputs = [m.outputs[-1]] # This memory has been gutted and is now a passthrough
    #    m.in_names.append('data_in1') # Two inputs from the links stiched together
    #    m.in_names.append('data_in2')
    #    m.inputs.append('input_link%d_reg1'%il)
    #    m.inputs.append('input_link%d_reg2'%il)
    #    m.inputs.append(m.outputs[-1]+'_read_en')
    #    m.out_names = [m.out_names[-1]]
    #    m.in_names.append('read_en')
    #    m.out_names.append('empty')
    #    m.outputs.append(m.outputs[-1]+'_empty')
    #    #m.common = m.common.replace('//.reset(','.reset(')
    if m.module == 'InputLink':
        il += 1
        m.module = 'InputLinkStubs'
        m.in_names.append('data_in')
        m.in_names.append('enable')
        m.inputs.append('input_link%d'%il) # FIXME
        m.inputs.append('input_link%d_wr_en'%il) # FIXME
        m.start = 'en_proc'  # FIXME
        m.reset = 'reset'  # FIXME
        m.size = '`NBITS_STUB'
        m.depth = '`MEM_SIZE'
        
    if m.module == 'AllStubs':
        m.out_names = m.out_names[1:] # These memories don't have to send number out
        m.outputs = m.outputs[1:] # They are accessed directly by TC and MC
        m.done = ''
        m.resetdone = ''
        if 'MC' in m.outputs[0]:
            m.parameters = "#(.IsMC(1'b1))"
        else:
            m.parameters = "#(.IsMC(1'b0))"
        m.size = '`NBITS_STUB'
        m.depth = '4+`MEM_SIZE'
            
    if 'VMStubs' in m.module:  # VMStubsTE or VMStubsME
        inputs_new = []
        for i in m.inputs:
            inputs_new.append(i.replace(m.name, m.coname))
        m.inputs = inputs_new
        if 'TE' in m.module: # VMStubsTE
            if m.name.split('_')[1][0:2] in ['L1','L3','L5','D1','D3']:
                m.parameters = "#(.ISODD(1'b1))"
            else:
                m.parameters = "#(.ISODD(1'b0))"
            # special cases
            if m.name.split('_')[1][0:6] in ['L1PHIX','L1PHIY']:
                m.parameters = "#(.IDODD(1'b0))"
            m.size = '`NBITS_VMSTE'
            m.depth = '`MEM_SIZE+`NLONGVMZBITS+2'
        elif 'ME' in m.module: # VMStubsME
            m.size = '`NBITS_VMSME'
            m.depth = '`MEM_SIZE+4'
            
    if m.module == 'StubPairs':
        m.size = '`NBITS_SP'
        m.depth = '`MEM_SIZE'
        
    if m.module == 'TrackletParameters':
        m.out_names = m.out_names[1:] # These memories don't have to send number out
        m.outputs = m.outputs[1:]
        m.done = ''
        m.resetdone = ''
        m.size = '`NBITS_TPar'
        m.depth = '`MEM_SIZE+4'
        
    if m.module == 'TrackletProjections':
        #print m.name
        m.start = m.inputs[0].replace(m.name,'')+'proj_start'
        m.reset = m.inputs[0].replace(m.name,'')+'proj_reset'
        if 'From' in m.name:
            m.start = m.start.replace('proj_','')
            m.reset = m.reset.replace('proj_','')
            m.parameters = "#(1'b1)"
        if 'To' in m.name:
            m.parameters = "#(1'b1)"
        m.size = '`NBITS_TProj'
        m.depth = '`MEM_SIZE+3'
            
    if m.module == 'AllProj':
        if m.name.split('_')[2][0:2] in ['L4','L5','L6']:
            m.parameters = "#(1'b0,1'b0)"   #inner,disk
        if m.name.split('_')[2][0:2] in ['D1','D2','D3','D4','D5']:
            m.parameters = "#(1'b0,1'b1)"   #inner,disk
        m.out_names = m.out_names[1:] # These memories don't have to send number out
        m.outputs = m.outputs[1:]
        m.done = ''
        m.resetdone = ''
        m.size = '`NBITS_AP'
        m.depth = '`MEM_SIZE+2'
  
    if m.module == 'VMProjections':
        m.size = '`NBITS_VMP'
        m.depth = '`MEM_SIZE'
        
    if m.module == 'CandidateMatch':
        m.size = '`NBITS_CM'
        m.depth = '`MEM_SIZE'

    if m.module == 'FullMatch':
        m.out_names.append('read_en')
        m.outputs.append(m.outputs[-1]+'_read_en')
        if 'From' in m.name or 'To' in m.name:
            m.parameters = "#(.NEIGHBOR(1'b1))"
        else:
            m.parameters = "#(.NEIGHBOR(1'b0))"
        m.size = '`NBITS_FM'
        m.depth = '`MEM_SIZE+3'
            
    if m.module == 'TrackFit':
        #m.out_names = m.out_names[1:] # These memories don't have to send number out
        #m.outputs = m.outputs[1:]
        m.out_names.append('index_out')
        m.outputs.append(m.outputs[-1]+'_index')
        m.size = '`NBITS_TF'
        m.depth = '`MEM_SIZE+2'

    if m.module == 'CleanTrack':
        m.outputs.append(m.name+'_DataStream') # Final track out
        m.out_names.append('data_out')
        m.size = '`NBITS_TF'
        
    ####################################################
    # Declare wires to be used in the memory
    string_memories += '\n'
    for i in m.inputs:
        if 'input_link' in i:  # FIXME
            continue
        
        if ('VMS' in m.name) and not m.name.lstrip(m.coname) in ['','n1']:
            continue
            # This VMS memory module is not the first copy
            # Use the same input wires defined earlier for the first copy"
            
        if '_en' in i:
            string_memories += '\n' + 'wire '+i+';'
        else:
            string_memories += '\n' + 'wire ['+m.size+'-1:0] ' + i+';'

    for o in m.outputs:
        if 'empty' in o or 'CT_' in o: # No wires needed
            string_memories += '\n' + '//wire '+o+';'
        elif 'number' in o: # Number of objects in memory
            if m.module == 'VMStubsTE' and "ISODD(1'b0)" in m.parameters:
                    string_memories += '\n' + 'wire [(`MEM_SIZE+1)*(1<<`NLONGVMZBITS)-1:0] '+o+';'    
            else:
                string_memories += '\n' + 'wire [`MEM_SIZE:0] '+o+';'
        elif '_index' in o: # Matrix of stub indices for PD
            string_memories += '\n' + 'wire [53:0] '+o+' [`NCLKPROC-1:0];'
        elif 'read' in o:
            if '_en' in o: # read enable
                string_memories += '\n' + 'wire '+o+';'
            else:
                string_memories += '\n' + 'wire ['+m.depth+':0] '+o+';'
        elif "1'b1" in o:
            continue
        else:
            string_memories += '\n' + 'wire ['+m.size+'-1:0] ' + o+';'+'\n'

    string_memories += '\n' +  m.module + ' ' + m.parameters +  ' ' + m.name + '(' # Parameters here
    for n,i in zip(m.in_names,m.inputs): # Loop over signals and names
        string_memories += '\n' +  '.'+n+'('+i+'),'
    for n,o in zip(m.out_names,m.outputs):
        string_memories += '\n' +  '.'+n+'('+o+'),'
    string_memories += '\n' + '.start('+m.start+'),'
    string_memories += '\n' + '.done('+m.done+'),'
    string_memories += '\n' + '.reset('+m.reset+'),'
    string_memories += '\n' + '.resetdone('+m.resetdone+'),'
    string_memories += '\n' +  m.common
    string_memories += '\n' +  ');'
    string_memories += '\n'

####################################################
####################################################
# Done is only needed for 1 module
# If seen once, don't add it anymore
seen_done1_0 = False
seen_done2_0 = False
seen_done3_0 = False
seen_done4_0 = False
seen_done_proj = False
seen_done5_0 = False
seen_done6_0 = False
seen_done7_0 = False
seen_done8_0 = False
seen_done9_0 = False
seen_done10_0 = False

print 'start processing module loop'
# Start looping over the processing modules
for x in modules:
    h = open('wires_'+region+'.dat') # Open the wire connections file
    m = Module() # Create a module
    i = [] # List of inputs
    i_n = [] # List of input names
    o = [] # List of outputs
    o_n = [] # List of output names
    m.module = x[0] # Module nice name from processing list
    m.name = x[1]  # Module instance name from processing list

    for line in h: # Loop over connections
        if line.split(' ')[-1].strip().split('.')[0] == x[1]: # If instance corresponds to current processing
            i.append(line.split(' ')[0]+'_'+x[1]) # Add input to module's list
            i_n.append(line.split(' ')[-1].strip().split('.')[1])
        if line.split(' ')[2].strip().split('.')[0] == x[1]:
            o.append(x[1]+'_'+line.split(' ')[0]) # Add output to module's list
            o_n.append(line.split(' ')[2].strip().split('.')[1])
    # Define the properties of the module
    m.inputs = i
    m.outputs = o
    m.in_names = i_n
    m.out_names = o_n
    m.common = Common
    ####################################################
    # Specific properties of the processing modules
    # Any new processing added here
    ####################################################
    if 'VMRouter' in m.module: # VMRouterTE or VMRouterME
        # inputs
        si = 1
        in_names_new = []
        for i_n in m.in_names:
            if i_n == 'stubin':
                in_names_new.append(i_n+'%d'%si)
                si+=1
        m.in_names = in_names_new
        # outputs
        # rename outputs to match firmware
        out_names_new = []
        outputs_new = []
        for o_n, o in zip(m.out_names, m.outputs):
            if 'vmstubout' in o_n:
                # temporary fix for VMRTE to have the same output format as VMRME
                # modify WiresLongVM.py to get rid of the following lines
                o_n = o_n.replace('A','PHI')
                o_n = o_n.replace('B','PHI')
                o_n = o_n.replace('C','PHI')
                o_n = o_n.replace('D','PHI')
                
                # drop n1, n2, n3... at the end of string
                o_n = re.sub('n[0-9]+','',o_n)
                if o_n not in out_names_new:
                    out_names_new.append(o_n)
                    outputs_new.append(re.sub('n[0-9]+','',o)) # drop the 'n1' at the end
            else:
                out_names_new.append(o_n)
                outputs_new.append(o)
        m.out_names = out_names_new
        m.outputs = outputs_new

        enables = []
        enables_2 = []
        for o in m.out_names: 
            if 'vmstubout' in o:
                enables.append(o+'_wr_en') # For every output name create a write enable name
                
        for o in m.outputs:
            if 'VMR' in o and 'VMS' in o: # Output going to VMStub memory
                enables_2.append(o+'_wr_en') # For every output create a write enable
        m.out_names = m.out_names + enables
        m.outputs = m.outputs + enables_2
        
        # parameters
        if 'VMRTE' in m.name: # VMRouterTE
            overlap = "1'b0"
            if m.name[-1] in ['Q','W','X','Y']:
                overlap = "1'b1"          
            inner = "1'b0"
            if m.name.split('_')[1][0:2] in ['L1','L2','L3']:
                inner = "1'b1"     
            odd = "1'b0"
            if m.name.split('_')[1][1] in ['1','3','5']:
                odd = "1'b1"
            # special cases
            if m.name.split('_')[1][0:6] in ['L1PHIX','L1PHIY']:
                odd = "1'b1"
            # todo: disk

            # zbin LUTs
            table = ""
            if m.name.split('_')[1][0:2]=='L1':
                table = "TEBinTableLayer1ToLayer2.txt"
            elif m.name.split('_')[1][0:2]=='L3':
                table = "TEBinTableLayer3ToLayer4.txt"
                # TEBinTableLayer3ToLayer2.txt ?
            elif m.name.split('_')[1][0:2]=='L5':
                table = "TEBinTableLayer5ToLayer6.txt"
            elif m.name.split('_')[1][0:2]=='D1':
                if m.name[-1] in ['A','B','C','D']:
                    table = "TEBinTableDisk1ToDisk2.txt"
                elif m.name[-1] in ['X','Y']:
                    table = "TEBinTableDisk1ToLayer1.txt"
                elif m.name[-1] in ['Q','W']:
                    table = "TEBinTableDisk1ToLayer2.txt"
            elif m.name.split('_')[1][0:2]=='D3':
                table = "TEBinTableDisk3ToDisk4.txt"
            
            m.parameters = "#(.ISODD("+odd+"),.ISINNER("+inner+"),.ISOVERLAP("+overlap+"),.TEBINTABLE("+table+"))"

        m.start = m.inputs[0].replace(m.name,'')+'start'
        m.reset = m.inputs[0].replace(m.name,'')+'reset'
        m.done = m.name+'_start'
        m.resetdone = m.name+'_reset'
        seen_done2_0 = True
        vs = 0
        valids = []
        valids2 = []
        for o in m.outputs:
            if 'VMR' in o and '_AS_' in o: # Output going to AllStub memory
                vs += 1
                valids.append(o+'_wr_en')
                valids2.append('valid_out%d'%vs)
        m.outputs = m.outputs + valids
        m.out_names = m.out_names + valids2
        
    if m.module == 'TrackletEngine':
        m.out_names.append('valid_data')
        m.outputs.append(m.outputs[0]+'_wr_en')
        m.start = m.inputs[0].replace(m.name,'')+'start'
        m.reset = m.inputs[0].replace(m.name,'')+'reset'
        m.done = m.name+'_start'
        m.resetdone = m.name+'_reset'
        seen_done3_0 = True
        
        #if 'TE_F' in m.name or 'TE_B' in m.name:
        #    m.parameters = '#("TETable_%s_phi.txt","TETable_%s_z.txt",'"1'b0"')'%(m.name,m.name) # TE Tables names have to be in this format. CHECK EMULATION
        #else:
        #    m.parameters = '#("TETable_%s_phi.txt","TETable_%s_z.txt")'%(m.name,m.name) # TE Tables names have to be in this format. CHECK EMULATION

    if m.module == 'TrackletCalculator':
        for i,n in enumerate(m.in_names): # Count the inputs
            if 'stubin' in n:
                m.in_names.insert(len(m.in_names),m.in_names.pop(i)) # Move the AllProjections to the back
        for i,n in enumerate(m.inputs): # Count the inputs
            if 'AS_' in n:
                m.inputs.insert(len(m.inputs),m.inputs.pop(i)) # Move the AllProjections to the back
        ons = []
        for o in m.out_names:
            ons.append('valid_'+o)
        m.out_names = m.out_names + ons
        m.out_names = m.out_names + ['done_proj'] # Done signal for projections
        seen_done_proj = True
        outs = []
        for o in m.outputs:
            outs.append(o+'_wr_en')
        m.outputs = m.outputs+outs
        m.outputs = m.outputs+[m.name+'_proj_start'] # Hardcoded signal name

        # assign TC_index and module parameters
        iseed = m.name[-5:-1] # L1L2, L3L4, L5L6, D1D2, D3D4, D1L1, D1L2
        itc = m.name[-1]  # A, B, C, D, E, F, G, H
        iSeeds = {'L1L2':'000', 'L3L4':'001', 'L5L6':'010', 'D1D2':'011',
                 'D3D4':'100', 'D1L1':'101', 'D1L2':'110'}
        iTCs = {'A':'000', 'B':'001', 'C':'010', 'D':'011', 'E':'100',
               'F':'101', 'G':'110', 'H':'111'}
        TC_index = "6'b"+iSeeds[iseed]+iTCs[itc]
        
        if 'L1L2' in m.name:
            m.parameters = "#(.BARREL(1'b1),"+'.InvR_FILE("InvRTable_'+m.name+'.dat"),'+".R1MEAN(`TC_L1L2_krA),.R2MEAN(`TC_L1L2_krB),.TC_index("+TC_index+"),.IsInner1(1'b1),.IsInner2(1'b1))"
        elif 'L3L4' in m.name:
            m.parameters = "#(.BARREL(1'b1),"+'.InvR_FILE("InvRTable_'+m.name+'.dat"),'+".R1MEAN(`TC_L3L4_krA),.R2MEAN(`TC_L3L4_krB),.TC_index("+TC_index+"),.IsInner1(1'b1),.IsInner2(1'b0))"
        elif 'L5L6' in m.name:
            m.parameters = "#(.BARREL(1'b1),"+'.InvR_FILE("InvRTable_'+m.name+'.dat"),'+".R1MEAN(`TC_L5L6_krA),.R2MEAN(`TC_L5L6_krB),.TC_index("+TC_index+"),.IsInner1(1'b0),.IsInner2(1'b0))"
        elif 'D1D2' in m.name:
            m.parameters = '#(.BARREL(0),.InvR_FILE("InvRTable_'+m.name+'.dat"),.InvT_FILE("InvTTable_'+m.name+'.dat"),.TC_index('+TC_index+"),.Z1MEAN(14'sd981),.Z2MEAN(14'sd1515))"  # FIXME: parameterize ZMEAN
        elif 'D3D4' in m.name:
            m.parameters = '#(.BARREL(0),.InvR_FILE("InvRTable_'+m.name+'.dat"),.InvT_FILE("InvTTable_'+m.name+'.dat"),.TC_index('+TC_index+"),.Z1MEAN(14'sd3294),.Z2MEAN(14'sd3917))" # FIXME: parameterize ZMEAN
        elif 'D1L1' in m.name:
            m.parameters = '#(.BARREL(0),.InvR_FILE("InvRTable_'+m.name+'.dat"),.InvT_FILE("InvTTable_'+m.name+'.dat"),.TC_index('+TC_index+"))" # RMEAN ZMEAN?
        elif 'D1L2' in m.name:
            m.parameters = '#(.BARREL(0),.InvR_FILE("InvRTable_'+m.name+'.dat"),.InvT_FILE("InvTTable_'+m.name+'.dat"),.TC_index('+TC_index+"))" # RMEAN ZMEAN?
        m.start = m.inputs[0].replace(m.name,'')+'start'
        m.reset = m.inputs[0].replace(m.name,'')+'reset'
        m.done = m.name+'_start'
        m.resetdone = m.name+'_reset'
        seen_done4_0 = True
    if m.module == 'ProjectionTransceiver':
        m.start = m.inputs[0].replace(m.name,'')+'start'
        m.reset = m.inputs[0].replace(m.name,'')+'reset'
        m.done = m.name+'_start'
        m.resetdone = m.name+'_reset'
        # depend on the actual instantiation of the module
        # for now
        if 'L1' in m.name:
            m.parameters = '#("L1")'
        elif 'L2' in m.name:
            m.parameters = '#("L2")'
        elif 'L3D4' in m.name:
            m.parameters = '#("L3D4")'
        elif 'L4D3' in m.name:
            m.parameters = '#("L4D3")'
        elif 'L5D2' in m.name:
            m.parameters = '#("L5D2")'
        elif 'L6D1' in m.name:
            m.parameters = '#("L6D1")'
        elif 'D5' in m.name:
            m.parameters = '#("D5")'
        # current longvm config assumes the same bit assignment for barrel
        # and disk projections
        # so do not separate projin_disk and projin_layer for now.
        # This won't work with current ProjTransceiver out of box. [TODO]
        m.in_names = ['projin_'+str(x) for x in range(1,14)]
        # ground the empty input ports
        while len(m.inputs) < len(m.in_names):
            m.inputs.append("1'b0")
        outs = []
        outnames = []
        for o in m.outputs:
            outs.append(o)
            outs.append(o+'_wr_en')
        for on in m.out_names:
            outnames.append(on)
            outnames.append(on.replace('projout','valid_'))
        m.outputs = outs
        m.out_names = outnames
        m.out_names = m.out_names+['valid_proj_data_stream','proj_data_stream'] # Outputs to links
        m.in_names = m.in_names+['incomming_proj_data_stream'] # Input from links
        m.outputs = m.outputs+[m.name+'_To_DataStream_en',m.name+'_To_DataStream']
        m.inputs = m.inputs+[m.name+'_From_DataStream']
                
    if m.module == 'ProjectionRouter':
        m.outputs.append(m.outputs[-1]+'_wr_en') # Write enable signal to AllProjection memory
        m.out_names.append('valid_data')
        m.outputs = m.outputs + [x+'_wr_en' for x in m.outputs[:-2]] # Write enable to VMProjection memory
        m.out_names = m.out_names + [x+'_wr_en' for x in m.out_names[:-2]]
        # determine module parameters #(isOdd, isInner, isBarrel)  
        if 'L1PHI' in m.name or 'L3PHI' in m.name:
            m.parameters = "#(1'b1,1'b1,1'b1)"
        elif 'L2PHI' in m.name:
            m.parameters = "#(1'b0,1'b1,1'b1)"
        elif 'L4PHI' in m.name or 'L6PHI' in m.name:
            m.parameters = "#(1'b0,1'b0,1'b1)"
        elif 'L5PHI' in m.name:
            m.parameters = "#(1'b1,1'b0,1'b1)"
        # disk projection bit assignment is the same for PS and 2S module
        elif 'D1PHI' in m.name or 'D3PHI' in m.name or 'D5PHI' in m.name:
            m.parameters = "#(1'b1,1'b1,1'b0)"
        elif 'D2PHI' in m.name or 'D4PHI' in m.name:
            m.parameters = "#(1'b0,1'b1,1'b0)"
        m.start = m.inputs[0].replace(m.name,'')+'start'
        m.reset = m.inputs[0].replace(m.name,'')+'reset'
        m.done = m.name+'_start'
        m.resetdone = m.name+'_reset'
        seen_done6_0 = True
    if m.module == 'MatchEngine':
        m.outputs.append(m.outputs[0]+'_wr_en') 
        m.out_names.append('valid_data')
	if ('_D1PHI' in m.name or '_D2PHI' in m.name or '_D3PHI' in m.name or '_D4PHI' in m.name or '_D5PHI' in m.name):
	    m.parameters += "#(.DISK(1'b1))"
	if 'VMPROJ' in m.inputs[1]: #default
          m.start = m.inputs[1].replace(m.name,'')+'start'
          m.reset = m.inputs[1].replace(m.name,'')+'reset'
          m.done = m.name+'_start'
          m.resetdone = m.name+'_reset'
	elif 'VMPROJ' in m.inputs[0]: # don't think this is needed any more
          m.start = m.inputs[0].replace(m.name,'')+'start'
          m.reset = m.inputs[0].replace(m.name,'')+'reset'
          m.done = m.name+'_start'
          m.resetdone = m.name+'_reset'
        seen_done7_0 = True
    if m.module == 'MatchCalculator':
        for i,n in enumerate(m.in_names): # Count the inputs
            if 'allprojin' in n:
                m.in_names.insert(len(m.in_names),m.in_names.pop(i)) # Move the AllProjections to the back
        for i,n in enumerate(m.inputs): # Count the inputs
            if 'AP_' in n:
                m.inputs.insert(len(m.inputs),m.inputs.pop(i)) # Move the AllProjections to the back

        for i,n in enumerate(m.in_names): # Count the inputs
            if 'allstubin' in n:
                m.in_names.insert(len(m.in_names),m.in_names.pop(i)) # Move the AllStubs and AllProjections to the back
        for i,n in enumerate(m.inputs): # Count the inputs
            if 'AS_' in n:
                m.inputs.insert(len(m.inputs),m.inputs.pop(i)) # Move the AllProjections to the back

        outs = []
        outnames = []
        for o in m.outputs:
            outs.append(o)
            outs.append(o+'_wr_en')
        for on in m.out_names:
            outnames.append(on)
            outnames.append('valid_'+on)
        m.outputs = outs
        m.out_names = outnames
            
        phiregion = '00'
        if 'PHI1' in m.name:
            phiregion = '00'
        elif 'PHI2' in m.name:
            phiregion = '01'
        elif 'PHI3' in m.name:
            phiregion = '10'

        if 'MC_L1L2_L3' in m.name: # Parameter for constants # Will be moved to header file
            m.parameters = "#(2'b"+phiregion+",1'b1,`PHI_L3,`Z_L3,`R_L3,`PHID_L3,`ZD_L3,`MC_k1ABC_INNER,`MC_k2ABC_INNER,`MC_phi_L1L2_L3,`MC_z_L1L2_L3,`MC_zfactor_INNER)"
        if 'MC_L1L2_L4' in m.name:
            m.parameters = "#(2'b"+phiregion+",1'b0,`PHI_L4,`Z_L4,`R_L4,`PHID_L4,`ZD_L4,`MC_k1ABC_OUTER,`MC_k2ABC_OUTER,`MC_phi_L1L2_L4,`MC_z_L1L2_L4,`MC_zfactor_OUTER)"
        if 'MC_L1L2_L5' in m.name:
            m.parameters = "#(2'b"+phiregion+",1'b0,`PHI_L5,`Z_L5,`R_L5,`PHID_L5,`ZD_L5,`MC_k1ABC_OUTER,`MC_k2ABC_OUTER,`MC_phi_L1L2_L5,`MC_z_L1L2_L5,`MC_zfactor_OUTER)"
        if 'MC_L1L2_L6' in m.name:
            m.parameters = "#(2'b"+phiregion+",1'b0,`PHI_L6,`Z_L6,`R_L6,`PHID_L6,`ZD_L6,`MC_k1ABC_OUTER,`MC_k2ABC_OUTER,`MC_phi_L1L2_L6,`MC_z_L1L2_L6,`MC_zfactor_OUTER)"
        if 'MC_L3L4_L1' in m.name:
            m.parameters = "#(2'b"+phiregion+",1'b1,`PHI_L1,`Z_L1,`R_L1,`PHID_L1,`ZD_L1,`MC_k1ABC_INNER,`MC_k2ABC_INNER,`MC_phi_L3L4_L1,`MC_z_L3L4_L1,`MC_zfactor_INNER)"
        if 'MC_L3L4_L2' in m.name:
            m.parameters = "#(2'b"+phiregion+",1'b1,`PHI_L2,`Z_L2,`R_L2,`PHID_L2,`ZD_L2,`MC_k1ABC_INNER,`MC_k2ABC_INNER,`MC_phi_L3L4_L2,`MC_z_L3L4_L2,`MC_zfactor_INNER)"
        if 'MC_L3L4_L5' in m.name:
            m.parameters = "#(2'b"+phiregion+",1'b0,`PHI_L5,`Z_L5,`R_L5,`PHID_L5,`ZD_L5,`MC_k1ABC_OUTER,`MC_k2ABC_OUTER,`MC_phi_L3L4_L5,`MC_z_L3L4_L5,`MC_zfactor_OUTER)"
        if 'MC_L3L4_L6' in m.name:
            m.parameters = "#(2'b"+phiregion+",1'b0,`PHI_L6,`Z_L6,`R_L6,`PHID_L6,`ZD_L6,`MC_k1ABC_OUTER,`MC_k2ABC_OUTER,`MC_phi_L3L4_L6,`MC_z_L3L4_L6,`MC_zfactor_OUTER)"
        if 'MC_L5L6_L1' in m.name:
            m.parameters = "#(2'b"+phiregion+",1'b1,`PHI_L1,`Z_L1,`R_L1,`PHID_L1,`ZD_L1,`MC_k1ABC_INNER,`MC_k2ABC_INNER,`MC_phi_L5L6_L1,`MC_z_L5L6_L1,`MC_zfactor_INNER)"
        if 'MC_L5L6_L2' in m.name:
            m.parameters = "#(2'b"+phiregion+",1'b1,`PHI_L2,`Z_L2,`R_L2,`PHID_L2,`ZD_L2,`MC_k1ABC_INNER,`MC_k2ABC_INNER,`MC_phi_L5L6_L2,`MC_z_L5L6_L2,`MC_zfactor_INNER)"
        if 'MC_L5L6_L3' in m.name:
            m.parameters = "#(2'b"+phiregion+",1'b1,`PHI_L3,`Z_L3,`R_L3,`PHID_L3,`ZD_L3,`MC_k1ABC_INNER,`MC_k2ABC_INNER,`MC_phi_L5L6_L3,`MC_z_L5L6_L3,`MC_zfactor_INNER)"
        if 'MC_L5L6_L4' in m.name:
            m.parameters = "#(2'b"+phiregion+",1'b0,`PHI_L4,`Z_L4,`R_L4,`PHID_L4,`ZD_L4,`MC_k1ABC_OUTER,`MC_k2ABC_OUTER,`MC_phi_L5L6_L4,`MC_z_L5L6_L4,`MC_zfactor_OUTER)"
        m.start = m.inputs[0].replace(m.name,'')+'start'
        m.reset = m.inputs[0].replace(m.name,'')+'reset'
        m.done = m.name+'_start'
        m.resetdone = m.name+'_reset'
        seen_done8_0 = True
        
    if m.module == 'DiskMatchCalculator':
        # Current longvm config uses the same MatchCalculator for barrel and disk
        phiregion = '00'
        if 'PHI1' in m.name:
            phiregion = '00'
        elif 'PHI2' in m.name:
            phiregion = '01'
        elif 'PHI3' in m.name:
            phiregion = '10'
            
        # NEED TO CHECK PARAMETER SETTINGS
        # MC_D1D2 do not separate PS and 2S hits
        m.parameters = "#(.DTC_INDEX(2'b"+phiregion+")"
        m.parameters += ")"
    
        #if inner:
        #    m.parameters += ",.INNER(1'b1)"
        #else:
        #    m.parameters += ",.INNER(1'b0),.PHICUT(32'sd700921),.RCUT(32'sd128)"
        #if 'F3F4' in m.name and 'F5' not in m.name:
        #    m.parameters += ",.F1F2SEED(1'b0)"  
        #m.parameters += ")"
        
        for i,n in enumerate(m.in_names): # Count the inputs
            if 'allprojin' in n:
                m.in_names.insert(len(m.in_names),m.in_names.pop(i)) # Move the AllProjections to the back
        for i,n in enumerate(m.inputs): # Count the inputs
            if 'AP_' in n:
                m.inputs.insert(len(m.inputs),m.inputs.pop(i)) # Move the AllProjections to the back
        for i,n in enumerate(m.in_names): # Count the inputs
            if 'allstubin' in n:
                m.in_names.insert(len(m.in_names),m.in_names.pop(i)) # Move the AllStubs and AllProjections to the back
        for i,n in enumerate(m.inputs): # Count the inputs
            if 'AS_' in n:
                m.inputs.insert(len(m.inputs),m.inputs.pop(i)) # Move the AllProjections to the back
                
        # ?
        m.outputs = topOfList(m.outputs,'FM_'+m.name.split('_')[1]) # Put at the top of the list
        
        m.outputs = topOfList(m.outputs,'FM_FL3FL4') # Put at the top of the list	
        m.outputs = topOfList(m.outputs,'FM_L1') # Put at the top of the list
        m.outputs = topOfList(m.outputs,'FM_L4') # Put at the top of the list
        if ('MC_F1F2' in m.name):
            m.outputs = topOfList(m.outputs,'FM_F1L1') # Put at the top of the list
        m.outputs = topOfList(m.outputs,'FM_F1F') # Put at the top of the list
        m.outputs = topOfList(m.outputs,'FM_F3F') # Put at the top of the list
        
        m.outputs = topOfList(m.outputs,'ToMinus') # Put at the top of the list
        m.out_names = topOfList(m.out_names,'minus') # Put at the top of the list
        m.outputs = topOfList(m.outputs,'ToPlus') # Put at the top of the list
        m.out_names = topOfList(m.out_names,'plus') # Put at the top of the list
        #
        #os = []        
        #for o in m.outputs:
        #    os.append(o+'_wr_en')
        #m.outputs = m.outputs + os        
        #ons = []
        #p = 1
        #n = 1
        #for on in m.out_names:
        #    if 'plus' in on:
        #        ons.append('matchoutplus'+str(p))
        #        p = p+1            
        #    elif 'minus' in on:
        #        ons.append('matchoutminus'+str(n))
        #        n = n+1
        #    else:
        #        ons.append(on)
        #m.out_names = ons
        #os = []
        #ons = []
        #for o in m.out_names:
        #    ons.append('valid_'+o)
        #for o in outputs:
        #    os.append(o+'_wr_en')    
        #m.out_names = m.out_names + ons
        #m.outputs = m.outputs + os
        outs = []
        outnames = []
        for o in m.outputs:
            outs.append(o)
            outs.append(o+'_wr_en')
        for on in m.out_names:
            outnames.append(on)
            outnames.append('valid_'+on)
        m.outputs = outs
        m.out_names = outnames
      
        m.start = m.inputs[0].replace(m.name,'')+'start'
        m.reset = m.inputs[0].replace(m.name,'')+'reset'
        m.done = m.name+'_start'
        m.resetdone = m.name+'_reset'
        seen_done8_0 = True
        
    if m.module == 'MatchTransceiver':      
        ons = []
        #m.parameters = '#("Layer")'
        for i,o in enumerate(m.out_names): # Count the outputs
            ons.append(o)
        for i,o in enumerate(m.out_names):
            ons.append('valid_matchout%d'%(i+1))
        m.out_names = ons
        valids = []
        for o in m.outputs:
            valids.append(o+'_wr_en')
        m.outputs = m.outputs + valids
        m.start = m.inputs[0].replace(m.name,'')+'start'
        m.reset = m.inputs[0].replace(m.name,'')+'reset'
        m.done = m.name+'_start'
        m.resetdone = m.name+'_reset'
             
        m.out_names = m.out_names+['valid_match_data_stream','match_data_stream'] # Output signals to links
        m.in_names = m.in_names+['incomming_match_data_stream'] # Input signals from links
        m.outputs = m.outputs+[m.name+'_To_DataStream_en',m.name+'_To_DataStream']
        m.inputs = m.inputs+[m.name+'_From_DataStream']

    if m.module == 'FitTrack':        
        if 'L1L2' in m.name:
            m.parameters = '#("L1L2")'
        elif 'L3L4' in m.name:
            m.parameters = '#("L3L4")'
        elif 'L5L6' in m.name:
            m.parameters = '#("L5L6")'
        elif 'D1D2' in m.name:
            m.parameters = '#("D1D2")'
        elif 'D3D4' in m.name:
            m.parameters = '#("D3D4")'
        elif 'D1L1' in m.name:
            m.parameters = '#("D1L1")'
        elif 'D1L2' in m.name:
            m.parameters = '#("D1L2")'
                
        m.out_names.append('valid_fit')
        m.outputs.append(m.outputs[0]+'_wr_en')
        for i in m.inputs:
            if 'From' in i:
                m.start = i.replace(m.name,'')+'start'
                m.reset = i.replace(m.name,'')+'reset'
        m.done = m.name+'_start'
        m.resetdone = m.name+'_reset'
        seen_done10_0 = True
    
    if m.module == 'PurgeDuplicate':
	if region=='D3D6':
	    m.parameters = '#(.SCOPE("D3D6"))'
	if region=='D4D6':
	    m.parameters = '#(.SCOPE("D4D6"))'
	if region=='D3':
	    m.parameters = '#(.SCOPE("D3"))'
	if region=='D3D4':
	    m.parameters = '#(.SCOPE("D3D4"))'
	if region=='D5':
	    m.parameters = '#(.SCOPE("D5"))'
	if region=='D5D6':
	    m.parameters = '#(.SCOPE("D5D6"))'
        for x in range(1,len(m.outputs)+1):
            m.out_names.append('valid_out_'+str(x))
        os = []
        for o in m.outputs:
            os.append(o+'_wr_en')
        m.outputs += os
        m.start = m.inputs[0].replace(m.name,'')+'start'
        m.reset = m.inputs[0].replace(m.name,'')+'reset'
        m.done = m.name+'_start'
        m.resetdone = m.name+'_reset'
        m.in_names.append('')
        
    ####################################################
    if('mod' not in sys.argv): # If you don't want processing modules in the print out
        #string_processing += '\n'
        string_processing += '\n' +  m.module + ' ' +m.parameters + ' ' +m.name + '('
        k = 1
        #if m.module == 'ProjectionRouter':
        #    #print m.inputs
        #    while len(m.inputs) < 7:
        #        m.inputs.append("1'b0")
        #        m.in_names.append('proj'+str(len(m.inputs))+'in')
        #        
        #if m.module == 'MatchTransceiver':
        #    ins = [x for x in m.inputs if 'Stream' not in x]
        #    while len(ins) < 24:
        #        m.inputs.append("1'b0")
        #        ins.append("1'b0")
        #        m.in_names.append('matchin'+str(len(ins)))

        for n,i in zip(m.in_names,m.inputs): # Loop over inputs and input names
            if m.module != 'LayerRouter' and m.module != 'DiskRouter': # Special cases for signals without normal read_add
                if n == 'tpar1in':
                    string_processing += '\n' +  '.read_add_pars1('+i+'_read_add),'
                elif n == 'tpar2in':
                    string_processing += '\n' +  '.read_add_pars2('+i+'_read_add),'
                elif n == 'tpar3in':
                    string_processing += '\n' +  '.read_add_pars3('+i+'_read_add),'
                elif n == 'incomming_proj_data_stream':
                    string_processing += '\n' +  '.valid_incomming_proj_data_stream('+i+'_en),'
                elif n == 'incomming_match_data_stream':
                    string_processing += '\n' +  '.valid_incomming_match_data_stream('+i+'_en),'
                elif 'fullmatch' in n:
                    string_processing += '\n' +  '.number'+n.split('match')[-1]+'('+i+'_number),'
                    string_processing += '\n' +  '.read_add'+n.split('match')[-1]+'('+i+'_read_add),'
                    string_processing += '\n' +  '.read_en'+n.split('match')[-1]+'('+i+'_read_en),'
                elif 'allstubin' in n:
                    string_processing += '\n' +  '.read_add_'+n+'('+i+'_read_add),'
                elif 'allprojin' in n:
                    string_processing += '\n' +  '.read_add_'+n+'('+i+'_read_add),'
                elif 'trackin' in n:
                    string_processing += '\n' +  '.numberin'+n[-1]+'('+i+'_number),'
                    string_processing += '\n' +  '.read_add_'+n+'('+i+'_read_add),'
                    string_processing += '\n' +  '.index_in'+n[-1]+'('+i+'_index),'
                elif "1'b0" in i:
		    if 'matchin' in n:
                    	string_processing += '\n' +  '.number_in'+n.split('matchin')[-1]+"(6'b0),"
		    else:
                    	string_processing += '\n' +  '.number_in_'+n+"(6'b0),"
                elif "1'bX" in i:
                    string_processing += '\n' +  '.number_in'+n.split('matchin')[-1]+"(6'b0),"
                elif 'matchin' in n:
                    string_processing += '\n' +  '.number_in'+n.split('matchin')[-1]+'('+i+'_number),'
                    string_processing += '\n' +  '.read_add'+n.split('matchin')[-1]+'('+i+'_read_add),'
                    string_processing += '\n' +  '.read_en'+n.split('matchin')[-1]+'('+i+'_read_en),'
                else:
                    string_processing += '\n' +  '.number_in_'+n+'('+i+'_number),'
                    string_processing += '\n' +  '.read_add_'+n+'('+i+'_read_add),'
            if "1'b0" not in i and "1'bX" not in i:
                string_processing += '\n' +  '.'+n+'('+i+'),' # Write the signal name
            k = k + 1

            
        for n,o in zip(m.out_names,m.outputs): # Loop over outputs and output names 
            string_processing += '\n' +  '.'+n+'('+o+'),'
        string_processing += '\n' +  '.start('+m.start+'),'
        string_processing += '\n' +  '.done('+m.done+'),'
        string_processing += '\n' +  '.reset('+m.reset+'),'
        string_processing += '\n' +  '.resetdone('+m.resetdone+'),'
        string_processing += '\n' +  m.common
        string_processing += '\n' +  ');'
        string_processing += '\n'
        
# Write the final lines

for ep in epilogue:
    string_epilogue += ep.strip()
    
#starts = [x.split('),')[0] for x in (string_memories+string_processing).split('.start(')]

#for x in set(starts[1:]):
#    if len(x)>1 and 'IL' not in x:
#        string_starts += '\n' +  'wire [1:0] '+ x +';'

if region == 'D3':
    print 'Processing D3'
    print 'Memories implemented=',len(memories)
    print 'Processing modules implemented=',len(modules)
    string_prologue = string_prologue.replace('Tracklet_processing','Tracklet_processingD3')
if region == 'D5':
    print 'Processing D5'
    print 'Memories implemented=',len(memories)
    print 'Processing modules implemented=',len(modules)
    string_prologue = string_prologue.replace('Tracklet_processing','Tracklet_processingD5')
if region == 'D3D4':
    print 'Processing D3D4'
    print 'Memories implemented =',len(memories)
    print 'Processing modules implemented =',len(modules)
    string_prologue = string_prologue.replace('module Tracklet_processing','module Tracklet_processingD3D4')
if region == 'D3D6':
    print 'Processing D3D6'
    print 'Memories implemented =',len(memories)
    print 'Processing modules implemented =',len(modules)
    string_prologue = string_prologue.replace('module Tracklet_processing','module Tracklet_processingD3D6')
if region == 'D5D6':
    print 'Processing D5D6'
    print 'Memories implemented =',len(memories)
    print 'Processing modules implemented =',len(modules)
    string_prologue = string_prologue.replace('module Tracklet_processing','module Tracklet_processingD5D6')
if region == 'D4D5':
    print 'Processing D4D5'
    print 'Memories implemented =',len(memories)
    print 'Processing modules implemented =',len(modules)
    string_prologue = string_prologue.replace('module Tracklet_processing','module Tracklet_processingD4D5')
if region == 'D4D6':
    print 'Processing D4D6'
    print 'Memories implemented =',len(memories)
    print 'Processing modules implemented =',len(modules)
    string_prologue = string_prologue.replace('module Tracklet_processing','module Tracklet_processingD4D6')
    
g = open('test.txt','w')
g.write(string_prologue)
g.write(string_starts)
g.write(string_memories)
g.write(string_processing)
g.write(string_epilogue)
