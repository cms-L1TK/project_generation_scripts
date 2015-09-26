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

Common = '.clk(clk),\n//.reset(reset),\n.en_proc(en_proc),\n.io_clk(io_clk),\n.io_sel(io_sel_R3_io_block),\n.io_addr(io_addr[15:0]),        \n.io_sync(io_sync),\n.io_rd_en(io_rd_en),\n.io_wr_en(io_wr_en),\n.io_wr_data(io_wr_data[31:0]),\n.io_rd_data(io_rd_data_R3_io_block),\n.io_rd_ack(io_rd_ack_R3_io_block)'

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
counter = 1
il = 0 # Input Links
sl = 0 # Stub by Layer
vms = 0 # VM Stubs
alls = 0 # All Stubs
sp = 0 # Stub Pairs
tpj = 0 # Tracklet Projections
tpj_pm = 0 # Tracklet Projections plus/minus
vmp = 0 # VM Projections
cm = 0 # Candidate Matches
allp = 0 # All Projections
fm = 0 # Full Matches
tpar = 0 # Tracklet Parameters
tf = 0 # Track Fits

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
        il = il + 1
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
        sl = sl + 1
        m.start = 'start2_0'
        m.done = 'done1_5_'+str(sl)
    if m.module == 'AllStubs':
        m.out_names = m.out_names[1:]
        m.outputs = m.outputs[1:]
        m.start = 'start3_0'
        if 'MC' in m.outputs[0]:
            m.out_names = ['read_add_MC','data_out_MC']
    if m.module == 'VMStubs':
        vms = vms + 1
        m.start = 'start3_0'
        m.done = 'done2_5_'+str(vms)
        if 'ME' in m.outputs[0]:
            m.out_names = ['number_out_ME','read_add_ME','data_out_ME']
    if m.module == 'StubPairs':
        sp = sp + 1
        m.start = 'start4_0'
        m.done = 'done3_5_'+str(sp)
    if m.module == 'TrackletParameters':
        m.out_names = m.out_names[1:]
        m.outputs = m.outputs[1:]
        m.start = 'start5_0'
    if m.module == 'TrackletProjections':
        tpj = tpj + 1
        tpj = tpj + 1
        m.parameters = "#(0,1)"
        m.start = 'start5_0'
        m.done = 'done5_5_'+str(tpj)
        if 'ToPlus' in m.name or 'ToMinus' in m.name:
            tpj_pm = tpj_pm + 1
            m.parameters = "#(0,0)"
            m.done = 'done4_5_'+str(tpj_pm)
        if 'FromPlus'in m.name or 'FromMinus' in m.name:
            m.parameters = "#(1,1)"
    if m.module == 'AllProj':
        allp = allp + 1
        m.out_names = m.out_names[1:]
        m.outputs = m.outputs[1:]
        m.start = 'start7_0'
        m.done = 'done7_5_'+str(allp)
    if m.module == 'VMProjections':
        vmp = vmp + 1
        m.start = 'start7_0'
        m.done = 'done6_5_'+str(vmp)
    if m.module == 'CandidateMatch':
        cm = cm + 1
        m.start = 'start8_0'
        m.done = 'done7_5_'+str(cm)
    if m.module == 'FullMatch':
        fm = fm + 1
        m.start = 'start9_0'
        m.done = 'done8_5_'+str(fm)
    if m.module == 'TrackFit':
        tf = tf + 1
        m.inputs.append(m.name+'_led_test')
        m.in_names.append('led_test')
        m.outputs.append(m.name+'_DataStream')
        m.out_names.append('data_out')
        m.start = 'start10_0'
        m.done = 'done9_5_'+str(tf)
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
            if 'empty' in o or 'TF_L' in o:
                print '//wire '+o+';'
            elif 'number' in o or 'read' in o:
                print 'wire [5:0] '+o+';'
            else:
                print 'wire ['+str(m.size-1)+':0] '+o+';'
        print m.module,m.parameters,m.name + '('
        for n,i in zip(m.in_names,m.inputs):
            print '.'+n+'('+i+'),'
        for n,o in zip(m.out_names,m.outputs):
            print '.'+n+'('+o+'),'
        print '.start('+m.start+'),'
        print '.done('+m.done+'),'
        counter = counter + 1
        print m.common
        print ');'

####################################################
####################################################
done_cnt = 0
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
    done_cnt = done_cnt + 1

    if m.module == 'LayerRouter':
        m.inputs.append(m.inputs[-1]+'_read_en')
        m.in_names.append('read_en')
        m.start = 'start1_5'
        if done_cnt == 1:
            m.done = 'done1_0'
        else:
            m.done = 'done1'
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
        if done_cnt == 4:
            m.done = 'done2_0'
        else:
            m.done = 'done2'
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
    if m.module == 'TrackletEngine':
        m.out_names.append('valid_data')
        m.outputs.append(m.outputs[0]+'_wr_en')
        m.start = 'start3_5'
        if done_cnt == 10:
            m.done = 'done3_0'
        else:
            m.done = 'done3'
        m.parameters = '#("/home/Jorge/work/firmware/TrackletProject/AdditionalFiles/tables/TETable_%s_phi.txt","/home/Jorge/work/firmware/TrackletProject/AdditionalFiles/tables/TETable_%s_z.txt")'%(m.name,m.name)
    if m.module == 'TrackletCalculator':
        ons = []
        for o in m.out_names:
            ons.append('valid_'+o)
        m.out_names = m.out_names + ons    
        outs = []
        for o in m.outputs:
            outs.append(o+'_wr_en')
        m.outputs = m.outputs+outs
        #if 'L1D3L2D3' in m.name: # PARAMETERS BROKEN
         #   m.parameters = "#(12'sd981,12'sd1514,14,12,9,9,1'b1,16'h86a)"
        m.start = 'start4_5'
        if done_cnt == 64:
            m.done = 'done4_0'
        else:
            m.done = 'done4'
    if m.module == 'ProjectionTransceiver':
        ons = []
        for i,o in enumerate(m.out_names):
            ons.append(o+'_%d'%(i+1))
        m.out_names = ons
        ins = []
        for i,o in enumerate(m.in_names):
            ins.append(o+'_%d'%(i+1))
        m.in_names = ins
        if done_cnt == 79:
            m.done = 'done5_0'
        else:
            m.done = 'done5'
    if m.module == 'ProjectionRouter':
        m.outputs.append(m.outputs[-1]+'_wr_en')
        m.out_names.append('valid_data')
        m.outputs = m.outputs + [x+'_wr_en' for x in m.outputs[:-2]]
        m.out_names = m.out_names + [x+'_wr_en' for x in m.out_names[:-2]]
        if 'PR_L1' in m.name or 'PR_L3' in m.name:
            m.parameters = "#(1'b1,29)"
        elif 'PR_L2' in m.name:
            m.parameters = "#(1'b0,29)"
        elif 'PR_L4' in m.name or 'PR_L6' in m.name:
            m.parameters = "#(1'b0,26)"
        elif 'PR_L5' in m.name:
            m.parameters = "#(1'b1,26)"
        m.start = 'start6_5'
        if done_cnt == 67:
            m.done = 'done6_0'
        else:
            m.done = 'done6'
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
        if done_cnt == 81:
            m.done = 'done7_0'
        else:
            m.done = 'done7'
    if m.module == 'MatchCalculator':
        m.in_names.append(m.in_names[0])
        #m.in_names.append(m.in_names[1])
        m.in_names = m.in_names[1:]
        m.inputs.append(m.inputs[0])
        #m.inputs.append(m.inputs[1])
        m.inputs = m.inputs[1:]
        m.outputs.append(m.outputs[0]+'_wr_en')
        m.outputs.append(m.outputs[1]+'_wr_en')
        m.outputs.append(m.outputs[2]+'_wr_en')
        m.out_names.append('valid_matchminus')
        m.out_names.append('valid_matchplus')
        m.out_names.append('valid_match')
        m.start = 'start8_5'
        if done_cnt == 165:
            m.done = 'done8_0'
        else:
            m.done = 'done8'
    if m.module == 'FitTrack':
        m.in_names.append(m.in_names[4])
        m.in_names = m.in_names[:4]+m.in_names[5:]
        m.inputs.append(m.inputs[4])
        m.inputs = m.inputs[:4]+m.inputs[5:]
        m.start = 'start9_5'
        if done_cnt == 183:
            m.done = 'done9_0'
        else:
            m.done = 'done9'
    
####################################################

    if('mod' in sys.argv):
        print '\n'
        print m.module,m.parameters,m.name + '('
        k = 1
        for n,i in zip(m.in_names,m.inputs):
            if m.module != 'LayerRouter':
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
