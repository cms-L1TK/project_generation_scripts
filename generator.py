import sys

# Define the module class with all the properties
class Module:
    def __init__(self):
        self.module = None
        self.name = None # Names defined in the DN
        self.inputs = None # In and out from master wires file
        self.outputs = None
        self.in_names = None # In and out names should be consistent with Verilog modules
        self.out_names = None
        self.common = None
        self.parameters = '' # Each module has unique parameters
        self.size = 0 # Memory sizes for connecting wires
        self.start = '' 
        self.done = ''

# Read the processing modules
f = open('processingmodules.dat')
modules = []
for line in f:
    signals = [] # Pair with nice name and specific instance name
    signals.append(line.split(':')[0])
    signals.append(line.split(':')[1].strip())
    modules.append(signals) # Add to the list of pairs

# Read the memory modules
g = open('memorymodules.dat')
memories = []
for line in g:
    signals = [] # Nice name, instance name, memory size
    signals.append(line.split(':')[0])
    signals.append(line.split(':')[1].split(' ')[1].strip())
    if len(line.split(':')[1].split(' '))>2:
        signals.append(int(line.split(':')[1].split(' ')[-1].replace('[','').replace(']','').strip()))
    memories.append(signals) # Add to the list of triplets

# Common signals for every module # IPBus might go away
Common = '.clk(clk),\n.reset(reset),\n.en_proc(en_proc)'

# Read initial lines of Tracklet_processing
# Define inputs, outputs and start/done signals
p  = open('prologue.txt')
prologue = []
for line in p:
    prologue.append(line)
# Read final lines for IPbus and possible reader
ep  = open('epilogue.txt')
epilogue = []
for line in ep:
    epilogue.append(line)

####################################################
####################################################
# Done is only needed for 1 module
# If seen once, don't add it anymore
seen_done1_5 = False
seen_done2_5 = False
seen_done3_5 = False
seen_done4_5 = False
seen_done5_5 = False
seen_done6_5 = False
seen_done7_5 = False
seen_done8_5 = False
seen_done9_5 = False
seen_done10_5 = False

il = 0

# Always write the initial lines
for p in prologue:
    print p.strip()

# Start looping over the memories first
for x in memories:
    h = open('wires.dat') # Open the wire connections file
    m = Module() # Create a module
    i = [] # List of inputs
    i_n = [] # List of input names
    o = [] # List of outputs
    o_n = [] # List of output names
    m.module = x[0] # Module nice name from memory list
    m.name = x[1]  # Module instance name from memory list
    if len(x)>2: # If triplet, get the memory size
        m.size = x[2]
    for line in h: # Loop over connections
        if line.split(' ')[0] == x[1]:  # If instance corresponds to current memory
            if len(line.split(' ')[2].split('.')) > 1: # Memory has inputs
                i.append(line.split(' ')[2].split('.')[0]+'_'+x[1]) # Add input to module's list
                i.append(line.split(' ')[2].split('.')[0]+'_'+x[1]+'_wr_en') # Memory inputs usually have a write enable
                i_n.append('data_in') # Names defined in Verilog memory module
                i_n.append('enable')
            if len(line.split(' ')[-1].split('.')) > 1: # Memory has outputs
                o.append(x[1]+'_'+line.split(' ')[-1].split('.')[0]+'_number') # Number of items in memory that goes to processing module
                o.append(x[1]+'_'+line.split(' ')[-1].split('.')[0]+'_read_add')
                o.append(x[1]+'_'+line.split(' ')[-1].split('.')[0])
                o_n.append('number_out') # Names defined in Verilog memory module
                o_n.append('read_add')
                o_n.append('data_out')
    # Define the properties of the module
    m.inputs = i
    m.outputs = o
    m.in_names = i_n
    m.out_names = o_n
    m.common = Common
    ####################################################
    # Specific properties of the memories
    # Any new memories added here
    ####################################################
    if m.module == 'InputLink':
        il += 1
        m.outputs = [m.outputs[-1]] # This memory has been gutted and is now a passthrough
        m.in_names.append('data_in1') # Two inputs from the links stiched together
        m.in_names.append('data_in2')
        m.inputs.append('input_link%d_reg1'%il)
        m.inputs.append('input_link%d_reg2'%il)
        m.inputs.append(m.outputs[-1]+'_read_en')
        m.out_names = [m.out_names[-1]]
        m.in_names.append('read_en')
        m.out_names.append('empty')
        m.outputs.append(m.outputs[-1]+'_empty')
        m.common = m.common.replace('//.reset(','.reset(')
    if m.module == 'StubsByLayer':
        m.start = 'start2_0'
        m.done = '' if seen_done1_5 else 'done1_5' # After 1 seen, no more dones
        seen_done1_5 = True
    if m.module == 'StubsByDisk':
        m.start = 'start2_0'
        m.done = '' if seen_done1_5 else 'done1_5'
        seen_done1_5 = True
    if m.module == 'AllStubs':
        m.out_names = m.out_names[1:] # These memories don't have to send number out
        m.outputs = m.outputs[1:] # They are accessed directly by TC and MC
        m.start = 'start3_0'
        if 'MC' in m.outputs[0]:
            m.out_names = ['read_add_MC','data_out_MC'] # If the memory is read by an MC change the output names # TODO not needed anymore
    if m.module == 'VMStubs':
        m.start = 'start3_0'
        m.done = '' if seen_done2_5 else 'done2_5'
        seen_done2_5 = True
        if 'ME' in m.outputs[0]:
            m.parameters = '#("Match")'
        else:
            m.parameters = '#("Tracklet")'
    if m.module == 'StubPairs':
        m.start = 'start4_0'
        m.done = '' if seen_done3_5 else 'done3_5'
        seen_done3_5 = True
    if m.module == 'TrackletParameters':
        m.out_names = m.out_names[1:] # These memories don't have to send number out
        m.outputs = m.outputs[1:]
        m.start = 'start5_0'
    if m.module == 'TrackletProjections':
        if 'From' not in m.name:
            m.start = 'startproj5_0' # Projections from neighbors start later
        else:
            m.start = 'start6_0'
        if 'ToPlus' in m.name or 'ToMinus' in m.name:
	    m.done = '' if seen_done4_5 else 'done4_5'
            seen_done4_5 = True
        if 'FromPlus'in m.name or 'FromMinus' in m.name:
	    m.done = '' if seen_done5_5 else 'done5_5'
            seen_done5_5 = True       
    if m.module == 'AllProj':
        m.out_names = m.out_names[1:] # These memories don't have to send number out
        m.outputs = m.outputs[1:]
        m.start = 'start7_0'
    if m.module == 'VMProjections':
        m.start = 'start7_0'
        m.done = '' if seen_done6_5 else 'done6_5'
        seen_done6_5 = True
    if m.module == 'CandidateMatch':
        m.start = 'start8_0'
        m.done = '' if seen_done7_5 else 'done7_5'
        seen_done7_5 = True
    if m.module == 'FullMatch':
        
        m.out_names.append('read_en')
        if 'From' in m.name:
            m.parameters = "#(128)"
            m.start = 'start10_0' # Matches from neighbors start later
            m.done = '' if seen_done9_5 else 'done9_5'
            seen_done9_5 = True
            m.outputs.append(m.outputs[-1]+'_read_en')
        elif 'To' in m.name:
            m.parameters = "#(128)"
            m.start = 'start9_0'
            m.outputs.append("1'b1")
        else:
            m.start = 'start9_0'
            m.done = '' if seen_done8_5 else 'done8_5'
            seen_done8_5 = True
            m.outputs.append(m.outputs[-1]+'_read_en')
    if m.module == 'TrackFit':
        m.outputs.append(m.name+'_DataStream') # Final track out, going to DTC but should go to DuplicateRemoval
        m.out_names.append('data_out')
        m.start = 'start11_0'
        m.done = '' if seen_done10_5 else 'done10_5'
        seen_done10_5 = True
    ####################################################
    if('mem' in sys.argv): # If you want memories in the print out
        print '\n'
        for i in m.inputs: # Declare the wires to be used in the memory
            if 'input_link' not in i: # Input link memory does not have an enable
                if '_en' in i:
                    print 'wire '+i+';'
                else:
                    print 'wire ['+str(m.size-1)+':0] '+i+';' # Size of the wire
        for o in m.outputs: # Declare the wires to be used in the memory
            if 'empty' in o or 'TF_' in o: # Not needed wires
                print '//wire '+o+';'
            elif 'number' in o:
                print 'wire [5:0] '+o+';' # Number of objects in memory
            elif 'read' in o:
                if m.module == 'VMStubs' or m.module == 'AllStubs' or m.module == 'TrackletParameters' : # These memories have to cross the link
                    print 'wire [10:0] '+o+';' # Deeper for latency
                elif m.module == 'TrackletProjections' or m.module == 'FullMatch': # Not as deep
                    if '_en' in o:
                        print 'wire '+o+';'
                    else:
                        print 'wire [9:0] '+o+';'
                else:
                    print 'wire [8:0] '+o+';' # Standard depth 6 bits of number plus 3 of BX
                #print 'wire [5:0] '+o+';'
            elif "1'b1" in o:
                continue
            else:
                print 'wire ['+str(m.size-1)+':0] '+o+';' # Wire size
        print m.module,m.parameters,m.name + '(' # Parameters here
        for n,i in zip(m.in_names,m.inputs): # Loop over signals and names
            print '.'+n+'('+i+'),'
        for n,o in zip(m.out_names,m.outputs):
            print '.'+n+'('+o+'),'
        print '.start('+m.start+'),'
        print '.done('+m.done+'),'
        print m.common
        print ');'

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

# Start looping over the processing modules
for x in modules:
    h = open('wires.dat') # Open the wire connections file
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
    if m.module == 'LayerRouter':
        m.inputs.append(m.inputs[-1]+'_read_en') 
        m.in_names.append('read_en')
        m.start = 'start1_5'
        m.done = 'done1' if seen_done1_0 else 'done1_0'
        seen_done1_0 = True
        out_names = []
        outputs = []
        for cnt,out in enumerate(m.outputs):
            out_names.append(str('wr_en%d' %(cnt+1))) # Write enable for every layer
            outputs.append(out+'_wr_en')
        #print out_names
        m.out_names = m.out_names + out_names
        m.outputs = m.outputs + outputs
    if m.module == 'DiskRouter':
        m.inputs.append(m.inputs[-1]+'_read_en')
        m.in_names.append('read_en')
        m.start = 'start1_5'
        m.done = 'done1' if seen_done1_0 else 'done1_0'
        seen_done1_0 = True
        out_names = []
        outputs = []
        for cnt,out in enumerate(m.outputs):
            out_names.append(str('wr_en%d' %(cnt+1))) # Write enable for every disk
            outputs.append(out+'_wr_en')
        m.out_names = m.out_names + out_names
        m.outputs = m.outputs + outputs
    if m.module == 'VMRouter':
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
        if 'L1' in m.name or 'L3' in m.name or 'L5' in m.name: # Odd layer parameters
            if 'L1' in m.name or 'L3' in m.name: # Inner layer parameter
                m.parameters = "#(1'b1,1'b1)"
            else:
                m.parameters = "#(1'b0,1'b1)"
        else:
            if 'L2' in m.name:
                m.parameters = "#(1'b1,1'b0)"
            else:
                m.parameters = "#(1'b0,1'b0)"
        m.start = 'start2_5'
        m.done = 'done2' if seen_done2_0 else 'done2_0'
        seen_done2_0 = True
        vs = 0
        valids = []
        valids2 = []
        for o in m.outputs:
            if 'VMR_L' in o and '_AS_L' in o: # Output going to AllStub memory
                vs = vs + 1
                valids.append(o+'_wr_en')
                valids2.append('valid_data%d'%vs)
        m.outputs = m.outputs + valids
        m.out_names = m.out_names + valids2
    if m.module == 'VMDRouter': # VM router for the disks. Make sure the parameters are set correctly
        enables = []
        enables_2 = []
        for o in m.out_names:
            if 'vmstubout' in o:
                enables.append(o+'_wr_en')
        for o in m.outputs:
            if 'VMRD' in o and 'VMS' in o:  # Output going to VMStub memory
                enables_2.append(o+'_wr_en')
        m.out_names = m.out_names + enables
        m.outputs = m.outputs + enables_2
        if 'L1' in m.name or 'L3' in m.name or 'L5' in m.name: # CHANGE THIS
            if 'L1' in m.name or 'L3' in m.name:
                m.parameters = "#(1'b1,1'b1)"
            else:
                m.parameters = "#(1'b0,1'b1)"
        else:
            if 'L2' in m.name:
                m.parameters = "#(1'b1,1'b0)"
            else:
                m.parameters = "#(1'b0,1'b0)"
        m.start = 'start2_5'
        m.done = 'done2' if seen_done2_0 else 'done2_0'
        seen_done2_0 = True
        vs = 0
        valids = []
        valids2 = []
        for o in m.outputs:
            if 'VMR_F' in o and '_AS_F' in o: # Output going to AllStub memory
                vs = vs + 1
                valids.append(o+'_wr_en')
                valids2.append('valid_data%d'%vs)
        m.outputs = m.outputs + valids
        m.out_names = m.out_names + valids2
    if m.module == 'TrackletEngine':
        m.out_names.append('valid_data')
        m.outputs.append(m.outputs[0]+'_wr_en')
        m.start = 'start3_5'
        m.done = 'done3' if seen_done3_0 else 'done3_0'
        seen_done3_0 = True
        m.parameters = '#("TETable_%s_phi.txt","TETable_%s_z.txt")'%(m.name,m.name) # TE Tables names have to be in this format. CHECK EMULATION
    if m.module == 'TrackletCalculator':
        ons = []
        for o in m.out_names:
            ons.append('valid_'+o)
        m.out_names = m.out_names + ons
        if not seen_done_proj:    
            m.out_names = m.out_names + ['done_proj'] # Done signal for projections
        seen_done_proj = True
        outs = []
        for o in m.outputs:
            outs.append(o+'_wr_en')
        m.outputs = m.outputs+outs
        m.outputs = m.outputs+['done_proj4_0'] # Hardcoded signal name
        #if 'L1D3L2D3' in m.name: # PARAMETERS BROKEN # Will be fixed when seeding in other layers
         #   m.parameters = "#(12'sd981,12'sd1514,14,12,9,9,1'b1,16'h86a)"
        m.start = 'start4_5'
        m.done = 'done4' if seen_done4_0 else 'done4_0'
        seen_done4_0 = True
    if m.module == 'TrackletDiskCalculator':
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
        m.out_names = m.out_names + ['done_proj']            
        outs = []
        for o in m.outputs:
            outs.append(o+'_wr_en')
        m.outputs = m.outputs+outs
        m.outputs = m.outputs+['done_proj4_0']
        m.parameters = '#(47,17,"",981,1515)' # Parameter string for possible LUT file
        m.start = 'start4_5'
        m.done = 'done4' if seen_done4_0 else 'done4_0'
        seen_done4_0 = True
    if m.module == 'ProjectionTransceiver':
        ons = []
        for i,o in enumerate(m.out_names): # Count the outputs
            ons.append(o+'_%d'%(i+1)) # Enumerate them
        for i,o in enumerate(m.out_names):
            ons.append('valid_%d'%(i+1)) # Valid outputs
        m.out_names = ons
        valids = []
        for o in m.outputs:
            valids.append(o+'_wr_en')
        m.outputs = m.outputs + valids
        ins = []
        for i,o in enumerate(m.in_names): # Count the inputs
            ins.append(o+'_%d'%(i+1)) # Enumerate them
        m.in_names = ins
        m.start = 'start5_5'
        m.done = 'done5' if seen_done5_0 else 'done5_0'
        seen_done5_0 = True
        m.out_names = m.out_names+['valid_proj_data_stream','proj_data_stream'] # Outputs to links
        m.in_names = m.in_names+['incomming_proj_data_stream'] # Input from links
        m.outputs = m.outputs+[m.name+'_To_DataStream_en',m.name+'_To_DataStream']
        m.inputs = m.inputs+[m.name+'_From_DataStream']        
    if m.module == 'ProjectionRouter':
        m.outputs.append(m.outputs[-1]+'_wr_en') # Write enable signal to AllProjection memory
        m.out_names.append('valid_data')
        m.outputs = m.outputs + [x+'_wr_en' for x in m.outputs[:-2]] # Write enable to VMProjection memory
        m.out_names = m.out_names + [x+'_wr_en' for x in m.out_names[:-2]]
        if 'PR_L1' in m.name or 'PR_L3' in m.name: # Inner odd parameters
            m.parameters = "#(1'b1,1'b1)"
        elif 'PR_L2' in m.name:
            m.parameters = "#(1'b0,1'b1)"
        elif 'PR_L4' in m.name or 'PR_L6' in m.name: # Outer even parameters
            m.parameters = "#(1'b0,1'b0)"
        elif 'PR_L5' in m.name:
            m.parameters = "#(1'b1,1'b0)"
        m.start = 'start6_5'
        m.done = 'done6' if seen_done6_0 else 'done6_0'
        seen_done6_0 = True
    if m.module == 'ProjectionDiskRouter': # Disk Router. CHECK PARAMETERS
        m.outputs.append(m.outputs[-1]+'_wr_en') # Write enable signal to AllProjection memory
        m.out_names.append('valid_data')
        m.outputs = m.outputs + [x+'_wr_en' for x in m.outputs[:-2]] # Write enable to VMProjection memory
        m.out_names = m.out_names + [x+'_wr_en' for x in m.out_names[:-2]]
        if 'PR_L1' in m.name or 'PR_L3' in m.name:
            m.parameters = "#(1'b1,1'b1)"
        elif 'PR_L2' in m.name:
            m.parameters = "#(1'b0,1'b1)"
        elif 'PR_L4' in m.name or 'PR_L6' in m.name:
            m.parameters = "#(1'b0,1'b0)"
        elif 'PR_L5' in m.name:
            m.parameters = "#(1'b1,1'b0)"
        m.start = 'start6_5'
        m.done = 'done6' if seen_done6_0 else 'done6_0'
        seen_done6_0 = True
    if m.module == 'MatchEngine':
        m.outputs.append(m.outputs[0]+'_wr_en') 
        m.out_names.append('valid_data')
        m.start = 'start7_5'
        m.done = 'done7' if seen_done7_0 else 'done7_0'
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
        m.outputs.append(m.outputs[0]+'_wr_en') # Write enable for local and neighbor matches
        m.outputs.append(m.outputs[1]+'_wr_en')
        m.outputs.append(m.outputs[2]+'_wr_en')
        m.out_names.append('valid_matchminus')
        m.out_names.append('valid_matchplus')
        m.out_names.append('valid_match')
        if 'MC_L1L2_L3' in m.name: # Parameter for constants # Will be moved to header file
            m.parameters = "#(1'b1,14,12,7,7,8,2,4,868,9,0)"
        if 'MC_L1L2_L4' in m.name:
            m.parameters = "#(1'b0,17,8,8,8,7,0,9,1793,53,4)"
        if 'MC_L1L2_L5' in m.name:
            m.parameters = "#(1'b0,17,8,8,8,7,0,9,1388,53,4)"
        if 'MC_L1L2_L6' in m.name:
            m.parameters = "#(1'b0,17,8,8,8,7,0,9,1138,53,4)"
        m.start = 'start8_5'
        m.done = 'done8' if seen_done8_0 else 'done8_0'
        seen_done8_0 = True
    if m.module == 'MatchTransceiver':
        ons = []
        for i,o in enumerate(m.out_names): # Count the outputs
            ons.append(o)
        for i,o in enumerate(m.out_names):
            ons.append('valid_matchout%d'%(i+1))
        m.out_names = ons
        valids = []
        for o in m.outputs:
            valids.append(o+'_wr_en')
        m.outputs = m.outputs + valids
        m.start = 'start9_5'
        m.done = 'done9' if seen_done9_0 else 'done9_0'
        seen_done9_0 = True
        m.out_names = m.out_names+['valid_match_data_stream','match_data_stream'] # Output signals to links
        m.in_names = m.in_names+['incomming_match_data_stream'] # Input signals from links
        m.outputs = m.outputs+[m.name+'_To_DataStream_en',m.name+'_To_DataStream']
        m.inputs = m.inputs+[m.name+'_From_DataStream']        
    if m.module == 'FitTrack':
        for i,n in enumerate(m.in_names): # Count the inputs
            if 'tpar1' in n:
                m.in_names.insert(len(m.in_names),m.in_names.pop(i)) # Move the AllStubs and AllProjections to the back
        for i,n in enumerate(m.in_names): # Count the inputs
            if 'tpar2' in n:
                m.in_names.insert(len(m.in_names),m.in_names.pop(i)) # Move the AllStubs and AllProjections to the back
        for i,n in enumerate(m.in_names): # Count the inputs
            if 'tpar3' in n:
                m.in_names.insert(len(m.in_names),m.in_names.pop(i)) # Move the AllStubs and AllProjections to the back
        for i,n in enumerate(m.inputs):
            if 'TPAR' in n:
                m.inputs.insert(len(m.inputs),m.inputs.pop(i))
        for i,n in enumerate(m.inputs):
            if 'TPAR' in n:
                m.inputs.insert(len(m.inputs),m.inputs.pop(i))

        m.out_names.append('valid_fit')
        m.outputs.append(m.outputs[0]+'_wr_en')
        m.start = 'start10_5'
        m.done = 'done10' if seen_done10_0 else 'done10_0'
        seen_done10_0 = True

    ####################################################
    if('mod' in sys.argv): # If you want processing modules in the print out
        print '\n'
        print m.module,m.parameters,m.name + '('
        k = 1
        for n,i in zip(m.in_names,m.inputs): # Loop over inputs and input names 
            if m.module != 'LayerRouter' and m.module != 'DiskRouter': # Special cases for signals without normal read_add
                if n == 'innerallstubin':
                    print '.read_add_innerall('+i+'_read_add),'
                elif n == 'outerallstubin':
                    print '.read_add_outerall('+i+'_read_add),'
                elif n == 'allstubin':
                    print '.read_add_allstub('+i+'_read_add),'
                elif n == 'allprojin':
                    print '.read_add_allproj('+i+'_read_add),'
                elif n == 'tpar1in':
                    print '.read_add_pars1('+i+'_read_add),'
                elif n == 'tpar2in':
                    print '.read_add_pars2('+i+'_read_add),'
                elif n == 'tpar3in':
                    print '.read_add_pars3('+i+'_read_add),'
                elif n == 'incomming_proj_data_stream':
                    print '.valid_incomming_proj_data_stream('+i+'_en),'
                elif n == 'incomming_match_data_stream':
                    print '.valid_incomming_match_data_stream('+i+'_en),'
                elif 'fullmatch' in n:
                    print '.number'+n.split('match')[-1]+'('+i+'_number),'
                    print '.read_add'+n.split('match')[-1]+'('+i+'_read_add),'
                    print '.read_en'+n.split('match')[-1]+'('+i+'_read_en),'
                else:
                    print '.number_in'+str(k)+'('+i+'_number),'
                    print '.read_add'+str(k)+'('+i+'_read_add),'
            print '.'+n+'('+i+'),' # Write the signal name
            k = k + 1
        for n,o in zip(m.out_names,m.outputs): # Loop over outputs and output names 
            print '.'+n+'('+o+'),'
        print '.start('+m.start+'),'
        print '.done('+m.done+'),'
        print m.common
        print ');'

# Write the final lines
for ep in epilogue:
    print ep.strip() 
