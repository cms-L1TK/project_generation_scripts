def writeTopPreamble():
    string_preamble = "`timescale 1ns / 1ps\n\n"
    return string_preamble

def writeTBPreamble():
    string_preamble = "`timescale 1ns / 1ps\n\n"
    return string_preamble

def writeTopModuleOpener(topmodule_name):
    string_topmod_opener = "module "+topmodule_name+"(\n"
    return string_topmod_opener

def writeTBOpener(topfunc):
    string_tb_opener = "module " + topfunc + "_test();\n\n"
    return string_tb_opener

def writeTopModuleEntityCloser(topfunc):
    return ""

def writeTopModuleCloser(topmodule_name):
    string_closer = "\n\nendmodule\n"
    return string_closer

def writeTBModuleCloser(topmodule_name):
    string_closer = "\n\nendmodule\n"
    return string_closer

def writeTBMemoryStimulusInstance(memModule):
    # this will have to change, once Robert has a more sensible method for
    # stimulating the initial memories. But this does work for now

    wirelist = ""
    parameterlist = ""
    portlist = ""
    mem_str = ""
    # Write wires
    wirelist += "reg["+str(6+memModule.bxbitwidth)+":0] "
    wirelist += memModule.inst+"_dataarray_data_V_readaddr = 8'b00000000;\n"
    wirelist += "reg["+str(6+memModule.bxbitwidth)+":0] "
    wirelist += memModule.inst+"_dataarray_data_V_writeaddr = "
    wirelist += memModule.inst+"_dataarray_data_V_readaddr - 2;\n"
    wirelist += "wire["+str(memModule.bitwidth-1)+":0] "
    wirelist += memModule.inst+"_dataarray_data_V_dout;\n"
    for i in range(0,2**memModule.bxbitwidth):
        wirelist += "reg[6:0] "+memModule.inst+"_nentries_"
        wirelist += str(i)+"_V_dout = 7'b1101100;\n"
    wirelist += "always @(posedge clk) begin\n  "
    wirelist += memModule.inst+"_dataarray_data_V_readaddr <= "
    wirelist += memModule.inst+"_dataarray_data_V_readaddr + 1;\n"
    wirelist += memModule.inst+"_dataarray_data_V_writeaddr <= "
    wirelist += memModule.inst+"_dataarray_data_V_writeaddr + 1;\n"
    wirelist += "end\n\n"

    # Write parameters
    parameterlist += "  .RAM_WIDTH("+str(memModule.bitwidth)+"),\n"
    parameterlist += "  .RAM_DEPTH("+str(128*2**memModule.bxbitwidth)+"),\n"
    parameterlist += "  .RAM_PERFORMANCE(\"HIGH_PERFORMANCE\"),\n"
    parameterlist += "  .HEX(1),\n"
    parameterlist += "  .INIT_FILE(\"\"),\n"

    # Write ports
    portlist += "  .clka(clk),\n"
    portlist += "  .clkb(clk),\n"
    portlist += "  .enb(1'b1),\n"
    portlist += "  .addrb("+memModule.inst+"_dataarray_data_V_readaddr),\n"
    portlist += "  .doutb("+memModule.inst+"_dataarray_data_V_dout),\n"
    portlist += "  .regceb(1'b1),\n"

    mem_str += wirelist + "\nMemory #(\n"+parameterlist.rstrip("\n,")+"\n) "
    mem_str += memModule.inst+" (\n"+portlist.rstrip(",\n")+"\n);\n\n"

    return mem_str

def writeTBMemoryReadInstance(memModule):
    # this will have to change, once Robert has a more sensible method for
    # stimulating the initial memories. But this does work for now

    wirelist = ""
    # Write wires
    wirelist += "wire "+memModule.inst+"_dataarray_data_V_enb;\n"
    wirelist += "wire["+str(6+memModule.bxbitwidth)+":0] "
    wirelist += memModule.inst+"_dataarray_data_V_readaddr;\n"
    wirelist += "wire["+str(memModule.bitwidth-1)+":0] "
    wirelist += memModule.inst+"_dataarray_data_V_dout;\n"
    for i in range(0,2**memModule.bxbitwidth):
        wirelist += "wire[6:0] "+memModule.inst+"_nentries_"+str(i)+"_V_dout;\n"
    return wirelist

def writeFunctionsAndComponents():
    string_component = ""
    return string_component

def writeTopLevelMemoryInstance(memModule):
    wirelist = ""
    parameterlist = ""
    portlist = ""
    mem_str = ""

    # Write wires
    if interface != -1:
        wirelist += "wire "+memModule.inst+"_dataarray_data_V_wea;\n"
        wirelist += "wire["+str(6+memModule.bxbitwidth)+":0] "
        wirelist += memModule.inst+"_dataarray_data_V_writeaddr;\n"
        wirelist += "wire["+str(memModule.bitwidth-1)+":0] "
        wirelist += memModule.inst+"_dataarray_data_V_din;\n"
        for i in range(0,2**memModule.bxbitwidth):
            wirelist += "wire "+memModule.inst+"_nentries_"+str(i)+"_V_we;\n"
            wirelist += "wire[6:0] "+memModule.inst+"_nentries_"+str(i)+"_V_din;\n"
    if interface != 1:
        wirelist += "wire "+memModule.inst+"_dataarray_data_V_enb;\n"
        wirelist += "wire["+str(6+memModule.bxbitwidth)+":0] "
        wirelist += memModule.inst+"_dataarray_data_V_readaddr;\n"
        wirelist += "wire["+str(memModule.bitwidth-1)+":0] "
        wirelist += memModule.inst+"_dataarray_data_V_dout;\n"
        for i in range(0,2**memModule.bxbitwidth):
            wirelist += "wire[6:0] "+memModule.inst+"_nentries_"+str(i)+"_V_dout;\n"

    # Write parameters
    parameterlist += "  .RAM_WIDTH("+str(memModule.bitwidth)+"),\n"
    parameterlist += "  .RAM_DEPTH("+str(128*2**memModule.bxbitwidth)+"),\n"
    parameterlist += "  .RAM_PERFORMANCE(\"HIGH_PERFORMANCE\"),\n"
    parameterlist += "  .HEX(1),\n"
    parameterlist += "  .INIT_FILE(\"\"),\n"

    # Write ports
    portlist += "  .clka(clk),\n"
    portlist += "  .clkb(clk),\n"
    portlist += "  .wea("+memModule.inst+"_dataarray_data_V_wea),\n"
    portlist += "  .addra("+memModule.inst+"_dataarray_data_V_writeaddr),\n"
    portlist += "  .dina("+memModule.inst+"_dataarray_data_V_din),\n"
    for i in range(0,2**memModule.bxbitwidth):
        portlist += "  .nent_we"+str(i)+"("+memModule.inst+"_nentries_"+str(i)+"_V_we),\n"
        portlist += "  .nent_i"+str(i)+"("+memModule.inst+"_nentries_"+str(i)+"_V_din),\n"
    portlist += "  .enb("+memModule.inst+"_dataarray_data_V_enb),\n"
    portlist += "  .addrb("+memModule.inst+"_dataarray_data_V_readaddr),\n"
    portlist += "  .doutb("+memModule.inst+"_dataarray_data_V_dout),\n"
    for i in range(0,2**memModule.bxbitwidth):
        portlist += "  .nent_o"+str(i)+"("+memModule.inst
        portlist += "_nentries_"+str(i)+"_V_dout),\n"
    portlist += "  .regceb(1'b1),\n"

    mem_str += "\nMemory #(\n"+parameterlist.rstrip("\n,")+"\n) "
    mem_str += memModule.inst+" (\n"+portlist.rstrip(",\n")+"\n);\n\n"

    return wirelist,mem_str

def writeControlSignals_interface(initial_proc, final_proc):
    string_ctrl_signals = ""
    string_ctrl_signals += "  input clk,\n"
    string_ctrl_signals += "  input reset,\n"
    string_ctrl_signals += "  input en_proc,\n"
    string_ctrl_signals += "  input [2:0] bx_in_"+initial_proc+",\n"
    string_ctrl_signals += "  output [2:0] bx_out_"+final_proc+",\n"
    string_ctrl_signals += "  output "+final_proc+"_done,\n"
    # Add bx-out-valid signal
    return string_ctrl_signals

def writeMemoryLHSPorts_interface(memModule):
    string_input_mems = ""
    string_input_mems += "  input "+memModule.inst+"_dataarray_data_V_wea,\n"
    string_input_mems += "  input ["+str(6+memModule.bxbitwidth)+":0] "
    string_input_mems += memModule.inst+"_dataarray_data_V_writeaddr,\n"
    string_input_mems += "  input ["+str(memModule.bitwidth-1)+":0] "
    string_input_mems += memModule.inst+"_dataarray_data_V_din,\n"
    for i in range(0,2**memModule.bxbitwidth):
        string_input_mems += "  input "+memModule.inst+"_nentries_"+str(i)+"_V_we,\n"
        string_input_mems += "  input [6:0] "+memModule.inst
        string_input_mems += "_nentries_"+str(i)+"_V_din,\n"
    return string_input_mems

def writeMemoryRHSPorts_interface(memModule):
    string_output_mems = ""
    string_output_mems += "  input "+memModule.inst+"_dataarray_data_V_enb,\n"
    string_output_mems += "  input ["+str(6+memModule.bxbitwidth)+":0] "
    string_output_mems += memModule.inst+"_dataarray_data_V_readaddr,\n"
    string_output_mems += "  output ["+str(memModule.bitwidth-1)+":0] "
    string_output_mems += memModule.inst+"_dataarray_data_V_dout,\n"
    for i in range(0,2**memModule.bxbitwidth):
        string_output_mems += "  output [6:0] "+memModule.inst
        string_output_mems += "_nentries_"+str(i)+"_V_dout,\n"
    return string_output_mems

def writeTBControlSignals(topfunc, first_proc, last_proc):
    string_header = ""
    string_header += "reg clk;\n"
    string_header += "reg reset;\n\n"

    string_header += "initial begin\n"
    string_header += "  reset = 1'b1;\n"
    string_header += "  clk   = 1'b1;\n"
    string_header += "end\n\n"

    string_header += "initial begin\n"
    string_header += "  #5400\n"
    string_header += "  reset = 1'b0;\n"
    string_header += "end\n\n"

    string_header += "reg en_proc = 1'b0;\n"
    string_header += "always @(posedge clk) begin\n"
    string_header += "  if (reset) en_proc = 1'b0;\n"
    string_header += "  else       en_proc = 1'b1;\n"
    string_header += "end\n\n"

    string_header += "always begin\n"
    string_header += "  #2.5 clk = ~clk;\n"
    string_header += "end\n\n"

    string_header += "reg[2:0] bx_in_"+first_proc+";\n"
    string_header += "initial bx_in_"+first_proc+" = 3'b110;\n"
    string_header += "always begin\n"
    string_header += "  #540 bx_in_"+first_proc+" <= bx_in_"
    string_header += first_proc+" + 1'b1;\n"
    string_header += "end\n"
    string_header += "wire[2:0] bx_out_"+last_proc+";\n\n"
    return string_header

def writeFWBlockControlSignalPorts(first_proc, last_proc):
    string_fwblock_ctrl = ""
    string_fwblock_ctrl += "  .clk(clk),\n"
    string_fwblock_ctrl += "  .reset(reset),\n"
    string_fwblock_ctrl += "  .en_proc(en_proc),\n"
    string_fwblock_ctrl += "  .bx_in_"+first_proc
    string_fwblock_ctrl += "(bx_in_"+first_proc+"),\n"
    string_fwblock_ctrl += "  .bx_out_"+last_proc
    string_fwblock_ctrl += "(bx_out_"+last_proc+"),\n"
    return string_fwblock_ctrl

def writeFWBlockMemoryLHSPorts(memModule):
    string_input_mems = ""
    string_input_mems += "  ."+memModule.inst+"_dataarray_data_V_wea(1'b1),\n"
    string_input_mems += "  ."+memModule.inst+"_dataarray_data_V_writeaddr("
    string_input_mems += memModule.inst+"_dataarray_data_V_writeaddr),\n"
    string_input_mems += "  ."+memModule.inst+"_dataarray_data_V_din("
    string_input_mems += memModule.inst+"_dataarray_data_V_dout),\n"
    for i in range(0,2**memModule.bxbitwidth):
        string_input_mems += "  ."+memModule.inst+"_nentries_"+str(i)+"_V_we(1'b1),\n"
        string_input_mems += "  ."+memModule.inst+"_nentries_"+str(i)+"_V_din("
        string_input_mems += memModule.inst+"_nentries_"+str(i)+"_V_dout),\n"
    return string_input_mems

def writeFWBlockMemoryRHSPorts(memModule):
    string_output_mems = ""
    string_output_mems += "  ."+memModule.inst+"_dataarray_data_V_enb("
    string_output_mems += memModule.inst+"_dataarray_data_V_enb),\n"
    string_output_mems += "  ."+memModule.inst+"_dataarray_data_V_readaddr("
    string_output_mems += memModule.inst+"_dataarray_data_V_readaddr),\n"
    string_output_mems += "  ."+memModule.inst+"_dataarray_data_V_dout("
    string_output_mems += memModule.inst+"_dataarray_data_V_dout),\n"
    for i in range(0,2**memModule.bxbitwidth):
        string_output_mems += "  ."+memModule.inst+"_nentries_"+str(i)+"_V_dout("
        string_output_mems += memModule.inst+"_nentries_"+str(i)+"_V_dout),\n"
    return string_output_mems

def writeProcCombination(module, str_ctrl_func, special_TC, templpars_str, str_ports):
    module_str = ""
    module_str += str_ctrl_func
    module_str += module.mtype
    module_str += special_TC
    module_str += "_"+templpars_str
    module_str += " "+module.inst+ "(\n"
    module_str += str_ports+"\n);\n"

    return module_str

def writeStartSwitchAndInternalBX(module,mem):
    int_ctrl_wire = ""
    int_ctrl_wire += "wire "+module.mtype+"_done;\n"
    int_ctrl_wire += "reg "+mem.downstreams[0].mtype+"_start;\n"
    int_ctrl_wire += "initial "+mem.downstreams[0].mtype+"_start = 1'b0;\n\n"

    int_ctrl_func = ""
    int_ctrl_func += "always @("+module.mtype+"_done) begin\n"
    int_ctrl_func += "  if ("+module.mtype+"_done) "
    int_ctrl_func += mem.downstreams[0].mtype+"_start = 1'b1;\nend\n\n"

    return int_ctrl_wire,int_ctrl_func

def writeProcControlSignalPorts(module,first_of_type):
    startport = ""
    if module.is_first:
        startport += "en_proc"
    else:
        startport += module.mtype+"_start"
    string_ctrl_ports = ""
    string_ctrl_ports += "  .ap_clk(clk),\n"
    string_ctrl_ports += "  .ap_rst(reset),\n"
    string_ctrl_ports += "  .ap_start("+startport+"),\n"
    if first_of_type:
        string_ctrl_ports += "  .ap_done("+module.mtype+"_done),\n"
    return string_ctrl_ports

def writeProcBXPort(modName,isInput,isInitial):
    bx_str = ""
    if isInput and isInitial:
        bx_str += "  .bx_V(bx_in_"+modName+"),\n"
    elif isInput and not isInitial:
        bx_str += "  .bx_V(bx_out_"+modName+"),\n"
    elif not isInput:
        bx_str += "  .bx_o_V(bx_out_"+modName+"),\n"
    return bx_str

def writeProcMemoryLHSPorts(argname,memory):
    string_mem_ports = ""
    string_mem_ports += "  ."+argname+"_dataarray_data_V_we0("
    string_mem_ports += memory.inst+"_dataarray_data_V_wea),\n"
    string_mem_ports += "  ."+argname+"_dataarray_data_V_address0("
    string_mem_ports += memory.inst+"_dataarray_data_V_writeaddr),\n"
    string_mem_ports += "  ."+argname+"_dataarray_data_V_d0("
    string_mem_ports += memory.inst+"_dataarray_data_V_din),\n"
    for i in range(0,2**memory.bxbitwidth):
        string_mem_ports += "  ."+argname+"_nentries_"+str(i)+"_V_ap_vld("
        string_mem_ports += memory.inst+"_nentries_"+str(i)+"_V_we),\n"
        string_mem_ports += "  ."+argname+"_nentries_"+str(i)+"_V("
        string_mem_ports += memory.inst+"_nentries_"+str(i)+"_V_din),\n"
    return string_mem_ports

def writeProcMemoryRHSPorts(argname,memory):
    string_mem_ports = ""
    string_mem_ports += "  ."+argname+"_dataarray_data_V_ce0("
    string_mem_ports += memory.inst+"_dataarray_data_V_enb),\n"
    string_mem_ports += "  ."+argname+"_dataarray_data_V_address0("
    string_mem_ports += memory.inst+"_dataarray_data_V_readaddr),\n"
    string_mem_ports += "  ."+argname+"_dataarray_data_V_q0("
    string_mem_ports += memory.inst+"_dataarray_data_V_dout),\n"
    for i in range(0,2**memory.bxbitwidth):
        string_mem_ports += "  ."+argname+"_nentries_"+str(i)+"_V("
        string_mem_ports += memory.inst+"_nentries_"+str(i)+"_V_dout),\n"
    return string_mem_ports



