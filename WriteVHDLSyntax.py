def writeTopPreamble():
    string_preamble = "library IEEE;\nuse IEEE.STD_LOGIC_1164.ALL;\n\n"
    return string_preamble

def writeTBPreamble():
    return ""

def writeTopModuleOpener(topmodule_name):
    string_topmod_opener = "entity "+topmodule_name+" is\n  port(\n"
    return string_topmod_opener

def writeTBOpener(topfunc):
    string_tb_opener = "module " + topfunc + "_test();\n\n"
    return string_tb_opener

def writeTopModuleEntityCloser(topmodule_name):
    string_closer = "\n\nend "+topmodule_name+";\n\n"
    string_closer += "architecture rtl of "+topmodule_name+" is\n\n"
    return string_closer

def writeTopModuleCloser(topmodule_name):
    string_closer = "\n\nend rtl;"
    return string_closer

def writeTBModuleCloser(topmodule_name):
    return ""

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
    f = open("FunctionAndComponentDefinitions.txt", "r")
    string_component += f.read()
    return string_component

def writeTopLevelMemoryInstance(memModule, interface):
    wirelist = ""
    parameterlist = ""
    portlist = ""
    mem_str = ""

    # Write wires
    if interface != -1:
        wirelist += "  signal "+memModule.inst+"_dataarray_data_V_wea       : std_logic;\n"
        wirelist += "  signal "+memModule.inst+"_dataarray_data_V_writeaddr : "
        wirelist += "std_logic_vector("+str(6+memModule.bxbitwidth)+" downto 0);\n"
        wirelist += "  signal "+memModule.inst+"_dataarray_data_V_din       : "
        wirelist += "std_logic_vector("+str(memModule.bitwidth-1)+" downto 0);\n"
        for i in range(0,2**memModule.bxbitwidth):
            if memModule.is_binned:
                for j in range(0,8):
                    wirelist += "  signal "+memModule.inst+"_nentries_"+str(i)+"_V_"+str(j)+"_we  : std_logic;\n"
                    wirelist += "  signal "+memModule.inst+"_nentries_"+str(i)+"_V_"+str(j)+"_din : "
                    wirelist += "std_logic_vector(3 downto 0);\n"
            else:
                wirelist += "  signal "+memModule.inst+"_nentries_"+str(i)+"_V_we  : std_logic;\n"
                wirelist += "  signal "+memModule.inst+"_nentries_"+str(i)+"_V_din : "
                wirelist += "std_logic_vector(7 downto 0);\n"
    if interface != 1:
        wirelist += "  signal "+memModule.inst+"_dataarray_data_V_enb      : std_logic;\n"
        wirelist += "  signal "+memModule.inst+"_dataarray_data_V_readaddr : "
        wirelist += "std_logic_vector("+str(6+memModule.bxbitwidth)+" downto 0);\n"
        wirelist += "  signal "+memModule.inst+"_dataarray_data_V_dout     : "
        wirelist += "std_logic_vector("+str(memModule.bitwidth-1)+" downto 0);\n"
        for i in range(0,2**memModule.bxbitwidth):
            if memModule.is_binned:
                for j in range(0,8):
                    wirelist += "  signal "+memModule.inst+"_nentries_"+str(i)+"_V_"+str(j)+"_dout : "
                    wirelist += "std_logic_vector(3 downto 0);\n"
            else:
                wirelist += "  signal "+memModule.inst+"_nentries_"+str(i)+"_V_dout : "
                wirelist += "std_logic_vector(7 downto 0);\n"

    # Write parameters
    parameterlist += "      RAM_WIDTH       => "+str(memModule.bitwidth)+",\n"
    parameterlist += "      RAM_DEPTH       => "+str(128*2**memModule.bxbitwidth)+",\n"
    parameterlist += "      INIT_FILE       => \"\",\n"
    parameterlist += "      RAM_PERFORMANCE => \"HIGH_PERFORMANCE\",\n"
    parameterlist += "      HEX             => 0,\n"

    # Write ports
    portlist += "      clka      => clk,\n"
    portlist += "      wea       => "+memModule.inst+"_dataarray_data_V_wea,\n"
    portlist += "      addra     => "+memModule.inst+"_dataarray_data_V_writeaddr,\n"
    portlist += "      dina      => "+memModule.inst+"_dataarray_data_V_din,\n"
    portlist += "      clkb      => clk,\n"
    portlist += "      rstb      => '0',\n"
    portlist += "      regceb    => '1',\n"
    portlist += "      enb       => "+memModule.inst+"_dataarray_data_V_enb,\n"
    portlist += "      addrb     => "+memModule.inst+"_dataarray_data_V_readaddr,\n"
    portlist += "      doutb     => "+memModule.inst+"_dataarray_data_V_dout,\n"
    for i in range(0,2**memModule.bxbitwidth):
        if memModule.is_binned:
            for j in range(0,8):
                portlist += "      nent_"+str(i)+"_we"+str(j)+" => "+memModule.inst+"_nentries_"+str(i)+"_V_"+str(j)+"_we,\n"
                portlist += "      nent_"+str(i)+"_i"+str(j)+"  => "+memModule.inst+"_nentries_"+str(i)+"_V_"+str(j)+"_din,\n"
        else:    
            portlist += "      nent_we"+str(i)+" => "+memModule.inst+"_nentries_"+str(i)+"_V_we,\n"
            portlist += "      nent_i"+str(i)+"  => "+memModule.inst+"_nentries_"+str(i)+"_V_din,\n"
    for i in range(2**memModule.bxbitwidth,8):
        if memModule.is_binned:
            for j in range(0,8):
                portlist += "      nent_"+str(i)+"_we"+str(j)+" => '0',\n"
                portlist += "      nent_"+str(i)+"_i"+str(j)+"  => (others=>'0'),\n"
        else:
            portlist += "      nent_we"+str(i)+" => '0',\n"
            portlist += "      nent_i"+str(i)+"  => (others=>'0'),\n"
    for i in range(0,2**memModule.bxbitwidth):
        if memModule.is_binned:
            for j in range(0,8):
                portlist += "      nent_"+str(i)+"_o"+str(j)+"  => "+memModule.inst+"_nentries_"+str(i)+"_V_"+str(j)+"_dout,\n"
        else:
            portlist += "      nent_o"+str(i)+"  => "+memModule.inst+"_nentries_"+str(i)+"_V_dout,\n"
    for i in range(2**memModule.bxbitwidth,8):
        if memModule.is_binned:
            for j in range(0,8):
                portlist += "      nent_"+str(i)+"_o"+str(j)+"  => open,\n"
        else:
            portlist += "      nent_o"+str(i)+"  => open,\n"

    mem_str += "\n  "+memModule.inst+" : myMemory"
    mem_str += "\n    generic map (\n"+parameterlist.rstrip(",\n")+"\n    )"
    mem_str += "\n    port map (\n"+portlist.rstrip(",\n")+"\n  );\n\n"
    return wirelist,mem_str

def writeControlSignals_interface(initial_proc, final_proc):
    string_ctrl_signals = ""
    string_ctrl_signals += "    clk        : in std_logic;\n"
    string_ctrl_signals += "    reset      : in std_logic;\n"
    string_ctrl_signals += "    en_proc    : in std_logic;\n"
    string_ctrl_signals += "    bx_in_"+initial_proc+" : in std_logic_vector(2 downto 0);\n"
    string_ctrl_signals += "    bx_out_"+final_proc+" : out std_logic_vector(2 downto 0);\n"
    string_ctrl_signals += "    bx_out_"+final_proc+"_vld : out std_logic;\n"
    string_ctrl_signals += "    "+final_proc+"_done   : out std_logic;\n"
    return string_ctrl_signals

def writeMemoryLHSPorts_interface(memModule):
    string_input_mems = ""
    string_input_mems += "    "+memModule.inst+"_dataarray_data_V_wea       : in std_logic;\n"
    string_input_mems += "    "+memModule.inst+"_dataarray_data_V_writeaddr : in std_logic_vector("
    string_input_mems += str(6+memModule.bxbitwidth)+" downto 0);\n"
    string_input_mems += "    "+memModule.inst+"_dataarray_data_V_din       : in std_logic_vector("
    string_input_mems += str(memModule.bitwidth-1)+" downto 0);\n"
    for i in range(0,2**memModule.bxbitwidth):
        if memModule.is_binned:
            for j in range(0,8):
                string_input_mems += "    "+memModule.inst+"_nentries_"+str(i)+"_V_"+str(j)+"_we  : in std_logic;\n"
                string_input_mems += "    "+memModule.inst+"_nentries_"+str(i)+"_V_"+str(j)+"_din : "
                string_input_mems += "in std_logic_vector(3 downto 0);\n"
        else:
            string_input_mems += "    "+memModule.inst+"_nentries_"+str(i)+"_V_we  : in std_logic;\n"
            string_input_mems += "    "+memModule.inst+"_nentries_"+str(i)+"_V_din : "
            string_input_mems += "in std_logic_vector(7 downto 0);\n"

    return string_input_mems

def writeMemoryRHSPorts_interface(memModule):
    string_output_mems = ""
    string_output_mems += "    "+memModule.inst+"_dataarray_data_V_enb      : in std_logic;\n"
    string_output_mems += "    "+memModule.inst+"_dataarray_data_V_readaddr : in std_logic_vector("
    string_output_mems += str(6+memModule.bxbitwidth)+" downto 0);\n"
    string_output_mems += "    "+memModule.inst+"_dataarray_data_V_dout     : out std_logic_vector("
    string_output_mems += str(memModule.bitwidth-1)+" downto 0);\n"
    for i in range(0,2**memModule.bxbitwidth):
        if memModule.is_binned:
            for j in range(0,8):
                string_output_mems += "    "+memModule.inst+"_nentries_"+str(i)+"_V_"+str(j)+"_dout : "
                string_output_mems += "out std_logic_vector(3 downto 0);\n"
        else:
            string_output_mems += "    "+memModule.inst+"_nentries_"+str(i)+"_V_dout : "
            string_output_mems += "out std_logic_vector(7 downto 0);\n"

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
        if memModule.is_binned:
            for j in range(0,8):
                string_input_mems += "  ."+memModule.inst+"_nentries_"+str(i)+"_V_"+str(j)+"_we(1'b1),\n"
                string_input_mems += "  ."+memModule.inst+"_nentries_"+str(i)+"_V_"+str(j)+"_din("
                string_input_mems += memModule.inst+"_nentries_"+str(i)+"_V_"+str(j)+"_dout),\n"
        else:
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
        if memModule.is_binned:
            for j in range(0,8):
                string_output_mems += "  ."+memModule.inst+"_nentries_"+str(i)+"_V_"+str(j)+"_dout("
                string_output_mems += memModule.inst+"_nentries_"+str(i)+"_V_"+str(j)+"_dout),\n"
        else:
            string_output_mems += "  ."+memModule.inst+"_nentries_"+str(i)+"_V_dout("
            string_output_mems += memModule.inst+"_nentries_"+str(i)+"_V_dout),\n"

    return string_output_mems

def writeProcCombination(module, str_ctrl_func, special_TC, templpars_str, str_ports):
# FIXME needs fixing to include template parameters for generic proc module writing
    module_str = ""
    module_str += str_ctrl_func
    module_str += special_TC
    module_str += "  "+module.inst+" : entity work."+module.mtype+"\n"
    module_str += "    port map (\n"
    module_str += str_ports+"\n);\n"

    return module_str

def writeStartSwitchAndInternalBX(module,mem):
    int_ctrl_wire = ""
    int_ctrl_wire += "  signal "+module.mtype+"_done : std_logic := '0';\n"
    int_ctrl_wire += "  signal "+mem.downstreams[0].mtype+"_start : std_logic := '0';\n"
    int_ctrl_wire += "  signal bx_out_"+module.mtype+" : std_logic_vector(2 downto 0);\n"
    int_ctrl_wire += "  signal bx_out_"+module.mtype+"_vld : std_logic;\n"


    int_ctrl_func = ""
    int_ctrl_func += "  process("+module.mtype+"_done)\n  begin\n"
    int_ctrl_func += "    if "+module.mtype+"_done = '1' then "
    int_ctrl_func += mem.downstreams[0].mtype+"_start <= '1'; end if;\n  end process;\n\n"

    return int_ctrl_wire,int_ctrl_func

def writeProcControlSignalPorts(module,first_of_type):
    startport = ""
    if module.is_first:
        startport += "en_proc"
    else:
        startport += module.mtype+"_start"
    string_ctrl_ports = ""
    string_ctrl_ports += "      ap_clk   => clk,\n"
    string_ctrl_ports += "      ap_rst   => reset,\n"
    string_ctrl_ports += "      ap_start => "+startport+",\n"
    string_ctrl_ports += "      ap_idle  => open,\n"
    string_ctrl_ports += "      ap_ready => open,\n"
    if first_of_type:
        string_ctrl_ports += "      ap_done  => "+module.mtype+"_done,\n"
    else:
        string_ctrl_ports += "      ap_done  => open,\n"

    return string_ctrl_ports

def writeProcBXPort(modName,isInput,isInitial):
    bx_str = ""
    if isInput and isInitial:
        bx_str += "      bx_V          => bx_in_"+modName+",\n"
    elif isInput and not isInitial:
        bx_str += "      bx_V          => bx_out_"+modName+",\n"
    elif not isInput:
        bx_str += "      bx_o_V        => bx_out_"+modName+",\n"
        bx_str += "      bx_o_V_ap_vld => bx_out_"+modName+"_vld,\n"
    return bx_str

def writeProcMemoryLHSPorts(argname,memory):
    string_mem_ports = ""
    string_mem_ports += "      "+argname+"_dataarray_data_V_ce0         => open,\n"
    string_mem_ports += "      "+argname+"_dataarray_data_V_we0         => "
    string_mem_ports += memory.inst+"_dataarray_data_V_wea,\n"
    string_mem_ports += "      "+argname+"_dataarray_data_V_address0    => "
    string_mem_ports += memory.inst+"_dataarray_data_V_writeaddr,\n"
    string_mem_ports += "      "+argname+"_dataarray_data_V_d0          => "
    string_mem_ports += memory.inst+"_dataarray_data_V_din,\n"
    for i in range(0,2**memory.bxbitwidth):
        if memory.is_binned:
            for j in range(0,8):
                string_mem_ports += "      "+argname+"_nentries_"+str(i)+"_V_"+str(j)+"_ap_vld => "
                string_mem_ports += memory.inst+"_nentries_"+str(i)+"_V_"+str(j)+"_we,\n"
                string_mem_ports += "      "+argname+"_nentries_"+str(i)+"_V_"+str(j)+"        => "
                string_mem_ports += memory.inst+"_nentries_"+str(i)+"_V_"+str(j)+"_din,\n"
        else:
            string_mem_ports += "      "+argname+"_nentries_"+str(i)+"_V_ap_vld => "
            string_mem_ports += memory.inst+"_nentries_"+str(i)+"_V_we,\n"
            string_mem_ports += "      "+argname+"_nentries_"+str(i)+"_V        => "
            string_mem_ports += memory.inst+"_nentries_"+str(i)+"_V_din,\n"

    return string_mem_ports

def writeProcMemoryRHSPorts(argname,memory):
    string_mem_ports = ""
    string_mem_ports += "      "+argname+"_dataarray_data_V_ce0         => "
    string_mem_ports += memory.inst+"_dataarray_data_V_enb,\n"
    string_mem_ports += "      "+argname+"_dataarray_data_V_address0    => "
    string_mem_ports += memory.inst+"_dataarray_data_V_readaddr,\n"
    string_mem_ports += "      "+argname+"_dataarray_data_V_q0            => "
    string_mem_ports += memory.inst+"_dataarray_data_V_dout,\n"
    for i in range(0,2**memory.bxbitwidth):
        if memory.is_binned:
            for j in range(0,8):
                string_mem_ports += "      "+argname+"_nentries_"+str(i)+"_V_"+str(j)+"        => "
                string_mem_ports += memory.inst+"_nentries_"+str(i)+"_V_"+str(j)+"_dout,\n"
        else:
            string_mem_ports += "      "+argname+"_nentries_"+str(i)+"_V        => "
            string_mem_ports += memory.inst+"_nentries_"+str(i)+"_V_dout,\n"

    return string_mem_ports
