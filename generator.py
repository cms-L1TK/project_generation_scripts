import sys

class Module:
    def __init__(self):
        self.module = None
        self.name = None
        self.inputs = None
        self.outputs = None
        self.in_names = None
        self.out_names = None
        self.common = None
        self.parameters = ''
        self.size = 0
        self.start = ''
        self.done = ''

f = open('processingmodules.dat')
modules = []
for line in f:
    signals = []
    signals.append(line.split(':')[0])
    signals.append(line.split(':')[1].strip())
    modules.append(signals)

g = open('memorymodules.dat')
memories = []
for line in g:
    signals = []
    signals.append(line.split(':')[0])
    signals.append(line.split(':')[1].split(' ')[1].strip())
    if len(line.split(':')[1].split(' '))>2:
        signals.append(int(line.split(':')[1].split(' ')[-1].replace('[','').replace(']','').strip()))
    memories.append(signals)

Common = '.clk(clk),\n.reset(reset),\n.en_proc(en_proc),\n.io_clk(io_clk),\n.io_sel(io_sel_R3_io_block),\n.io_addr(io_addr[15:0]),        \n.io_sync(io_sync),\n.io_rd_en(io_rd_en),\n.io_wr_en(io_wr_en),\n.io_wr_data(io_wr_data[31:0]),\n.io_rd_data(io_rd_data_R3_io_block),\n.io_rd_ack(io_rd_ack_R3_io_block)'

p  = open('prologue.txt')
prologue = []
for line in p:
    prologue.append(line)
ep  = open('epilogue.txt')
epilogue = []
for line in ep:
    epilogue.append(line)

####################################################
####################################################
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

for p in prologue:
    print p.strip()
for x in memories:    
    #if x[0] == 'TrackPars':
    #   break
    h = open('wires.dat')
    m = Module()
    i = []
    i_n = []
    o = []
    o_n = []
    m.module = x[0]    
    m.name = x[1]
    if len(x)>2:
        m.size = x[2]
    for line in h:
        if line.split(' ')[0] == x[1]:
            if len(line.split(' ')[2].split('.')) > 1:
                i.append(line.split(' ')[2].split('.')[0]+'_'+x[1])
                i.append(line.split(' ')[2].split('.')[0]+'_'+x[1]+'_wr_en')
                i_n.append('data_in')
                i_n.append('enable')
            if len(line.split(' ')[-1].split('.')) > 1:
                o.append(x[1]+'_'+line.split(' ')[-1].split('.')[0]+'_number')
                o.append(x[1]+'_'+line.split(' ')[-1].split('.')[0]+'_read_add')
                o.append(x[1]+'_'+line.split(' ')[-1].split('.')[0])
                o_n.append('number_out')
                o_n.append('read_add')
                o_n.append('data_out')
    m.inputs = i
    m.outputs = o
    m.in_names = i_n
    m.out_names = o_n
    m.common = Common
    if m.module == 'InputLink':
        il += 1
        m.outputs = [m.outputs[-1]]
        m.in_names.append('data_in1')
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
        m.done = '' if seen_done1_5 else 'done1_5_1'
        seen_done1_5 = True
    if m.module == 'StubsByDisk':
        m.start = 'start2_0'
        m.done = '' if seen_done1_5 else 'done1_5_1'
        seen_done1_5 = True
    if m.module == 'AllStubs':
        m.out_names = m.out_names[1:]
        m.outputs = m.outputs[1:]
        m.start = 'start3_0'
        if 'MC' in m.outputs[0]:
            m.out_names = ['read_add_MC','data_out_MC']
    if m.module == 'VMStubs':
        m.start = 'start3_0'
        m.done = '' if seen_done2_5 else 'done2_5_1'
        seen_done2_5 = True
        if 'ME' in m.outputs[0]:
            m.out_names = ['number_out_ME','read_add_ME','data_out_ME']
    if m.module == 'StubPairs':
        m.start = 'start4_0'
        m.done = '' if seen_done3_5 else 'done3_5_1'
        seen_done3_5 = True
    if m.module == 'TrackletParameters':
        m.out_names = m.out_names[1:]
        m.outputs = m.outputs[1:]
        m.start = 'start5_0'
    if m.module == 'TrackletProjections':
        m.parameters = "#(0,1)"
        if 'From' not in m.name:
            m.start = 'startproj5_0'
        else:
            m.start = 'start6_0'        
        if 'ToPlus' in m.name or 'ToMinus' in m.name:
            m.parameters = "#(0,0)"
            m.done = '' if seen_done4_5 else 'done4_5_1'
            seen_done4_5 = True
        if 'FromPlus'in m.name or 'FromMinus' in m.name:
            m.parameters = "#(1,1)"
            m.done = '' if seen_done5_5 else 'done5_5_1'
            seen_done5_5 = True       
    if m.module == 'AllProj':
        m.out_names = m.out_names[1:]
        m.outputs = m.outputs[1:]
        m.start = 'start7_0'
    if m.module == 'VMProjections':
        m.start = 'start7_0'
        m.done = '' if seen_done6_5 else 'done6_5_1'
        seen_done6_5 = True
    if m.module == 'CandidateMatch':
        m.start = 'start8_0'
        m.done = '' if seen_done7_5 else 'done7_5_1'
        seen_done7_5 = True
    if m.module == 'FullMatch':
        if 'From' in m.name:
            m.start = 'start10_0'
            m.done = '' if seen_done9_5 else 'done9_5_1'
            seen_done9_5 = True
        else:
            m.start = 'start9_0'
            m.done = '' if seen_done8_5 else 'done8_5_1'
            seen_done8_5 = True
    if m.module == 'TrackFit':
        m.inputs.append(m.name+'_led_test')
        m.in_names.append('led_test')
        m.outputs.append(m.name+'_DataStream')
        m.out_names.append('data_out')
        m.start = 'start11_0'
        m.done = '' if seen_done10_5 else 'done10_5_1'
        seen_done10_5 = True
####################################################
    if('mem' in sys.argv):
        print '\n'
        for i in m.inputs:
            if 'input_link' not in i:
                if '_en' in i:
                    print 'wire '+i+';'
                else:
                    print 'wire ['+str(m.size-1)+':0] '+i+';'
        for o in m.outputs:
            if 'empty' in o or 'TF_' in o:
                print '//wire '+o+';'
            elif 'number' in o:
                print 'wire [5:0] '+o+';'
            elif 'read' in o:
                if m.module == 'VMStubs' or m.module == 'AllStubs' or m.module == 'TrackletParameters' :
                    print 'wire [10:0] '+o+';'
                elif m.module == 'TrackletProjections' or m.module == 'FullMatch':
                    print 'wire [9:0] '+o+';'
                else:
                    print 'wire [8:0] '+o+';'
                #print 'wire [5:0] '+o+';'
            else:
                print 'wire ['+str(m.size-1)+':0] '+o+';'
        print m.module,m.parameters,m.name + '('
        for n,i in zip(m.in_names,m.inputs):
            print '.'+n+'('+i+'),'
        for n,o in zip(m.out_names,m.outputs):
            print '.'+n+'('+o+'),'
        print '.start('+m.start+'),'
        print '.done('+m.done+'),'
        print m.common
        print ');'

####################################################
####################################################
seen_done1_0 = False
seen_done2_0 = False
seen_done3_0 = False
seen_done4_0 = False
seen_done5_0 = False
seen_done6_0 = False
seen_done7_0 = False
seen_done8_0 = False
seen_done9_0 = False
seen_done10_0 = False

for x in modules:
    #if x[0] == 'ProjRouter':
    #break
    h = open('wires.dat')
    m = Module()
    i = []
    i_n = []
    o = []
    o_n = []
    m.module = x[0]
    m.name = x[1]
    for line in h:
        if line.split(' ')[-1].strip().split('.')[0] == x[1]:
            i.append(line.split(' ')[0]+'_'+x[1])
            i_n.append(line.split(' ')[-1].strip().split('.')[1])
        if line.split(' ')[2].strip().split('.')[0] == x[1]:
            o.append(x[1]+'_'+line.split(' ')[0])
            o_n.append(line.split(' ')[2].strip().split('.')[1])
    m.inputs = i
    m.outputs = o
    m.in_names = i_n
    m.out_names = o_n
    m.common = Common
    if m.module == 'LayerRouter':
        m.inputs.append(m.inputs[-1]+'_read_en')
        m.in_names.append('read_en')
        m.start = 'start1_5'
        m.done = 'done1' if seen_done1_0 else 'done1_0'
        seen_done1_0 = True
        out_names = []
        outputs = []
        for cnt,out in enumerate(m.outputs):
            out_names.append(str('wr_en%d' %(cnt+1)))
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
            out_names.append(str('wr_en%d' %(cnt+1)))
            outputs.append(out+'_wr_en')
        #print out_names
        m.out_names = m.out_names + out_names
        m.outputs = m.outputs + outputs
    if m.module == 'VMRouter':
        enables = []
        enables_2 = []
        for o in m.out_names:
            if 'vmstubout' in o:
                enables.append(o+'_wr_en')
        for o in m.outputs:
            if 'VMR' in o and 'VMS' in o:
                enables_2.append(o+'_wr_en')
        m.out_names = m.out_names + enables
        m.outputs = m.outputs + enables_2
        if 'L1' in m.name or 'L3' in m.name or 'L5' in m.name:
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
            if 'VMR_L' in o and '_AS_L' in o:
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
            if 'VMR' in o and 'VMS' in o:
                enables_2.append(o+'_wr_en')
        m.out_names = m.out_names + enables
        m.outputs = m.outputs + enables_2
        if 'L1' in m.name or 'L3' in m.name or 'L5' in m.name:
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
            if 'VMR_F' in o and '_AS_F' in o:
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
        m.parameters = '#("TETable_%s_phi.txt","TETable_%s_z.txt")'%(m.name,m.name)
    if m.module == 'TrackletCalculator':
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
        #if 'L1D3L2D3' in m.name: # PARAMETERS BROKEN
         #   m.parameters = "#(12'sd981,12'sd1514,14,12,9,9,1'b1,16'h86a)"
        m.start = 'start4_5'
        m.done = 'done4' if seen_done4_0 else 'done4_0'
        seen_done4_0 = True
    if m.module == 'TrackletDiskCalculator':
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
        m.parameters = '#(47,17,"",981,1515)'
        #if 'L1D3L2D3' in m.name: # PARAMETERS BROKEN
         #   m.parameters = "#(12'sd981,12'sd1514,14,12,9,9,1'b1,16'h86a)"
        m.start = 'start4_5'
        m.done = 'done4' if seen_done4_0 else 'done4_0'
        seen_done4_0 = True
    if m.module == 'ProjectionTransceiver':
        ons = []
        for i,o in enumerate(m.out_names):
            ons.append(o+'_%d'%(i+1))
        for i,o in enumerate(m.out_names):
            ons.append('valid_%d'%(i+1))
        m.out_names = ons
        valids = []
        for o in m.outputs:
            valids.append(o+'_wr_en')
        m.outputs = m.outputs + valids
        ins = []
        for i,o in enumerate(m.in_names):
            ins.append(o+'_%d'%(i+1))
        m.in_names = ins
        m.start = 'start5_5'
        m.done = 'done5' if seen_done5_0 else 'done5_0'
        seen_done5_0 = True
        m.out_names = m.out_names+['valid_proj_data_stream','proj_data_stream']
        m.in_names = m.in_names+['incomming_proj_data_stream']
        m.outputs = m.outputs+[m.name+'_To_DataStream_en',m.name+'_To_DataStream']
        m.inputs = m.inputs+[m.name+'_From_DataStream']        
    if m.module == 'ProjectionRouter':
        m.outputs.append(m.outputs[-1]+'_wr_en')
        m.out_names.append('valid_data')
        m.outputs = m.outputs + [x+'_wr_en' for x in m.outputs[:-2]]
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
    if m.module == 'ProjectionDiskRouter': # Disk Router. Check parameters
        m.outputs.append(m.outputs[-1]+'_wr_en')
        m.out_names.append('valid_data')
        m.outputs = m.outputs + [x+'_wr_en' for x in m.outputs[:-2]]
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
        m.in_names.append(m.in_names[0])
        m.in_names.append(m.in_names[1])
        m.in_names = m.in_names[2:]
        m.inputs.append(m.inputs[0])
        m.inputs.append(m.inputs[1])
        m.inputs = m.inputs[2:]
        m.outputs.append(m.outputs[0]+'_wr_en')
        m.out_names.append('valid_data')
        m.start = 'start7_5'
        m.done = 'done7' if seen_done7_0 else 'done7_0'
        seen_done7_0 = True
    if m.module == 'MatchCalculator':
        for i,n in enumerate(m.in_names):
            if 'all' in n:
                m.in_names.insert(-1,m.in_names.pop(i))
        m.outputs.append(m.outputs[0]+'_wr_en')
        m.outputs.append(m.outputs[1]+'_wr_en')
        m.outputs.append(m.outputs[2]+'_wr_en')
        m.out_names.append('valid_matchminus')
        m.out_names.append('valid_matchplus')
        m.out_names.append('valid_match')
        if '_L1D' in m.name or '_L2D' in m.name or '_L3D' in m.name:
            m.parameters = "#(1'b1,14,12,7,7,8,2,4)"
        elif '_L4D' in m.name or '_L5D' in m.name or '_L6D' in m.name:
            m.parameters = "#(1'b0,17,8,8,8,7,0,9)"
        if 'MC_L1L2_L3' in m.name:
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
        for i,o in enumerate(m.out_names):
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
        m.out_names = m.out_names+['valid_match_data_stream','match_data_stream']
        m.in_names = m.in_names+['incomming_match_data_stream']
        m.outputs = m.outputs+[m.name+'_To_DataStream_en',m.name+'_To_DataStream']
        m.inputs = m.inputs+[m.name+'_From_DataStream']        
    if m.module == 'FitTrack':
        m.in_names.append(m.in_names[4])
        m.in_names = m.in_names[:4]+m.in_names[5:]
        m.inputs.append(m.inputs[4])
        m.inputs = m.inputs[:4]+m.inputs[5:]
        m.out_names.append('valid_fit')
        m.outputs.append(m.outputs[0]+'_wr_en')
        m.start = 'start10_5'
        m.done = 'done10' if seen_done10_0 else 'done10_0'
        seen_done10_0 = True

####################################################

    if('mod' in sys.argv):
        print '\n'
        print m.module,m.parameters,m.name + '('
        k = 1
        for n,i in zip(m.in_names,m.inputs):
            if m.module != 'LayerRouter' and m.module != 'DiskRouter':
                if n == 'innerallstubin':
                    print '.read_add_innerall('+i+'_read_add),'
                elif n == 'outerallstubin':
                    print '.read_add_outerall('+i+'_read_add),'
                elif n == 'allstubin':
                    print '.read_add_allstub('+i+'_read_add),'
                elif n == 'allprojin':
                    print '.read_add_allproj('+i+'_read_add),'
                elif n == 'tpar1in':
                    print '.read_add_pars('+i+'_read_add),'
                elif n == 'incomming_proj_data_stream':
                    print '.valid_incomming_proj_data_stream('+i+'_en),'
                elif n == 'incomming_match_data_stream':
                    print '.valid_incomming_match_data_stream('+i+'_en),'                    
                else:
                    print '.number_in'+str(k)+'('+i+'_number),'
                    print '.read_add'+str(k)+'('+i+'_read_add),'
            print '.'+n+'('+i+'),'
            k = k + 1
        for n,o in zip(m.out_names,m.outputs):
            print '.'+n+'('+o+'),'
        print '.start('+m.start+'),'
        print '.done('+m.done+'),'
        print m.common
        print ');'

for ep in epilogue:
    print ep.strip() 
