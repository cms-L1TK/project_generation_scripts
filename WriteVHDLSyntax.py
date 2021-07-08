from __future__ import absolute_import
from builtins import range
from TrackletGraph import MemModule, ProcModule, MemTypeInfoByKey

def writeTopPreamble(all=True):
    string_preamble = "--! Standard libraries\n"
    string_preamble += "library IEEE;\n"+"use IEEE.STD_LOGIC_1164.ALL;\n"
    string_preamble += "--! User packages\n"
    string_preamble += "use work.tf_pkg.all;\n"
    if all:
        string_preamble += "use work.memUtil_pkg.all;\n"
    string_preamble += "\n"
    return string_preamble

def writeModulesPreamble():
    string_preamble = "\n"
    string_preamble = "\nbegin\n\n"
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
    string_closer = "end "+topmodule_name+";\n\n"
    string_closer += "architecture rtl of "+topmodule_name+" is\n\n"
    return string_closer

def writeTopModuleCloser(topmodule_name):
    string_closer = "\n\nend rtl;\n"
    return string_closer

def writeTBModuleCloser(topmodule_name):
    return "\n"

def writeTBMemoryStimulusInstance(memModule):
    """
    # Verilog test-bench
    # this will have to change, once Robert has a more sensible method for
    # stimulating the initial memories. But this does work for now
    """
    wirelist = ""
    parameterlist = ""
    portlist = ""
    mem_str = ""
    # Write wires
    wirelist += "reg["+str(6+memModule.bxbitwidth)+":0] "
    wirelist += memModule.inst+"_mem_V_readaddr = 8'b00000000;\n"
    wirelist += "reg["+str(6+memModule.bxbitwidth)+":0] "
    wirelist += memModule.inst+"_mem_V_writeaddr = "
    wirelist += memModule.inst+"_mem_V_readaddr - 2;\n"
    wirelist += "wire["+str(memModule.bitwidth-1)+":0] "
    wirelist += memModule.inst+"_mem_V_dout;\n"
    for i in range(0,2**memModule.bxbitwidth):
        wirelist += "reg[6:0] "+memModule.inst+"_nentries_"
        wirelist += str(i)+"_V_dout = 7'b1101100;\n"
    wirelist += "always @(posedge clk) begin\n  "
    wirelist += memModule.inst+"_mem_V_readaddr <= "
    wirelist += memModule.inst+"_mem_V_readaddr + 1;\n"
    wirelist += memModule.inst+"_mem_V_writeaddr <= "
    wirelist += memModule.inst+"_mem_V_writeaddr + 1;\n"
    wirelist += "end\n\n"

    # Write parameters
    parameterlist += "  .RAM_WIDTH("+str(memModule.bitwidth)+"),\n"
    parameterlist += "  .NUM_PAGES("+str(2**memModule.bxbitwidth)+"),\n"
    parameterlist += "  .INIT_FILE(\"\"),\n"
    parameterlist += "  .INIT_HEX(1),\n"
    parameterlist += "  .RAM_PERFORMANCE(\"HIGH_PERFORMANCE\"),\n"
 
    # Write ports
    portlist += "  .clka(clk),\n"
    portlist += "  .clkb(clk),\n"
    portlist += "  .enb(1'b1),\n"
    portlist += "  .regceb(1'b1),\n"  
    portlist += "  .addrb("+memModule.inst+"_mem_V_readaddr),\n"
    portlist += "  .doutb("+memModule.inst+"_mem_V_dout),\n"
    portlist += "  .sync_nent(1'b0),\n"
  
    mem_str += wirelist + "\n"+"tf_mem (\n"+parameterlist.rstrip(",\n")+"\n) "
    mem_str += memModule.inst+" (\n"+portlist.rstrip(",\n")+"\n);\n\n"

    return mem_str

def writeTBMemoryReadInstance(memModule):
    """
    # Verilog test-bench
    # this will have to change, once Robert has a more sensible method for
    # stimulating the initial memories. But this does work for now
    """
    wirelist = ""
    # Write wires
    wirelist += "wire "+memModule.inst+"_mem_V_enb;\n"
    wirelist += "wire["+str(6+memModule.bxbitwidth)+":0] "
    wirelist += memModule.inst+"_mem_V_readaddr;\n"
    wirelist += "wire["+str(memModule.bitwidth-1)+":0] "
    wirelist += memModule.inst+"_mem_V_dout;\n"
    for i in range(0,2**memModule.bxbitwidth):
        wirelist += "wire[6:0] "+memModule.inst+"_nentries_"+str(i)+"_V_dout;\n"
    return wirelist

def writeMemoryUtil(memDict, memInfoDict):
    """
    # Produce VHDL package with utilities for memories that are specific
    # to current chain.
    # Inputs:
    #   memDict = dictionary of memories organised by type 
    #             & no. of bits (TPROJ_58b etc.)
    #   memInfoDict = dictionary of info about each memory type.
    """
    ss = writeTopPreamble(False)
    ss += "package memUtil_pkg is\n\n"
    ss += "  -- ########################### Types ###########################\n\n"

    for mtypeB in memDict:
        memInfo = memInfoDict[mtypeB]

        memList = memDict[mtypeB]
        # Sort with memories connected to top-level interface first.
        # (This required only for special case, where only a subset of
        # memories of given type are interfaced to top-level function. 
        # It allows a VHDL enum of this subset to be a VHDL subtype of the 
        # enum of all memories of this type).
        memList.sort(key=lambda m: int(m.is_initial or m.is_final), reverse=True)

        # Define enum type listing all memory instances of this type.
        enumName = "enum_"+mtypeB
        ss += "  type "+enumName+" is ("
        for mem in memList:
            ss += mem.var()+","
        ss = ss.rstrip(",")
        ss += ");\n\n"
        
        """
        # FIX IF NEEDED: 
        # Needed only for special case where only a subset of memories of
        # given type are interfaced to top-level function. 
        # Define enum subtype for them.
        if memInfo.mixedIO:
            varListExt = []
            for mem in memList:
                if mem.is_initial or mem.is_final:
                    varListExt.append(mem.var())
            assert(len(varListExt()) > 0)
            enumName = "enumPartial_"+mtypeB
            ss += "  subtype "+enumName+" is enum_"+mtypeB
            ss += " range "+varList[0]
            ss += " to "   +varList[-1]+";\n\n"        
        """

    # Define array types indexed by enums above used for signals connecting to memories.
    for mtypeB in memInfoDict:
        memInfo = memInfoDict[mtypeB]
        enumName = "enum_"+mtypeB
        mtype = mtypeB.split("_")[0]
        bitwidth = int(mtypeB.split("_")[1]);
        num_pages = 2**memInfo.bxbitwidth

        # address and nentries types not needed for DTC links or output track
        # streams
        if "DL" in mtypeB \
           or "TW" in mtypeB or "BW" in mtypeB or "DW" in mtypeB:
            arrName = "t_arr_"+mtypeB+"_1b"
            ss += "  type "+arrName+" is array("+enumName+") of std_logic;\n"

            arrName = "t_arr_"+mtypeB+"_DATA"
            ss += "  type "+arrName+" is array("+enumName+") of std_logic_vector("+str(bitwidth-1)+" downto 0);\n" 
        else:
            arrName = "t_arr_"+mtypeB+"_1b"
            ss += "  type "+arrName+" is array("+enumName+") of std_logic;\n" 

            arrName = "t_arr_"+mtypeB+"_ADDR"
            ss += "  type "+arrName+" is array("+enumName+") of std_logic_vector("+str(6+memInfo.bxbitwidth)+" downto 0);\n" 

            arrName = "t_arr_"+mtypeB+"_DATA"
            ss += "  type "+arrName+" is array("+enumName+") of std_logic_vector("+str(bitwidth-1)+" downto 0);\n" 

            if memInfo.is_binned:
                varStr = "_8_5b"
            else:
                varStr = "_7b"
            arrName = "t_arr_"+mtypeB+"_NENT"
            ss += "  type "+arrName+" is array("+enumName+") of t_arr"+str(num_pages)+varStr+";\n"

    ss += "\n  -- ########################### Functions ###########################\n\n"
    ss += "  -- Following functions are needed because VHDL doesn't preserve case when converting an enum to a string using image\n"

    for mtypeB in memDict:
        ss += "  function memory_enum_to_string(val: enum_"+mtypeB+") return string;\n";

    ss += "\nend package memUtil_pkg;\n\n"
    ss += "package body memUtil_pkg is\n\n"
    ss += "  -- ########################### Functions ###########################\n\n"
 
    for mtypeB in memDict:
        memList = memDict[mtypeB]
        
        ss += "  function memory_enum_to_string(val: enum_"+mtypeB+") return string is\n";
        ss += "  begin\n"
        ss += "    case val is\n"
        for mem in memList:
            ss += "       when "+mem.var()+" => return \""+mem.var()+"\";\n"
        ss += "    end case;\n"
        ss += "    return \"No conversion found.\";\n"
        ss += "  end memory_enum_to_string;\n\n"

    ss += "end package body memUtil_pkg;\n"

    return ss;

def writeTopLevelMemoryType(mtypeB, memList, memInfo, extraports):
    """
    # Declaration of memories of type "mtype" (e.g. TPROJ) & associated wires
    # Inputs:
    #   mTypeB  = memory type & its bits width (TPROJ_58b etc.)
    #   memList = list of memories of given type & bit width
    #   memInfo = Info about each memory type (in MemTypeInfoByKey class)
    """
    wirelist = ""
    parameterlist = ""
    portlist = ""
    mem_str = ""

    mtype = mtypeB.split("_")[0]
    bitwidth = mtypeB.split("_")[1]

    # Assume all memories of given type have same bxbitwidth.
    bxbitwidth =  memInfo.bxbitwidth
    num_pages = 2**bxbitwidth

    interface = int(memInfo.is_final) - int(memInfo.is_initial)

    if interface == 1:
        assert memInfo.upstream_mtype_short != ""
        sync_signal = memInfo.upstream_mtype_short+"_done"
    else:
        assert memInfo.downstream_mtype_short != ""
        sync_signal = memInfo.downstream_mtype_short+"_start"

    # Write wires
    if (interface != -1 and not extraports) or (interface == 1 and extraports):
        wirelist += "  signal "+mtypeB+"_mem_A_wea          : "
        wirelist += "t_arr_"+mtypeB+"_1b;\n"
        wirelist += "  signal "+mtypeB+"_mem_AV_writeaddr   : "
        wirelist += "t_arr_"+mtypeB+"_ADDR;\n"
        wirelist += "  signal "+mtypeB+"_mem_AV_din         : "
        wirelist += "t_arr_"+mtypeB+"_DATA;\n"
    if interface != 1:
        wirelist += "  signal "+mtypeB+"_mem_A_enb          : "
        wirelist += "t_arr_"+mtypeB+"_1b;\n"
        wirelist += "  signal "+mtypeB+"_mem_AV_readaddr    : "
        wirelist += "t_arr_"+mtypeB+"_ADDR;\n"
        wirelist += "  signal "+mtypeB+"_mem_AV_dout        : "
        wirelist += "t_arr_"+mtypeB+"_DATA;\n" 

        if memInfo.has_numEntries_out:
            if memInfo.is_binned:
                wirelist += "  signal "+mtypeB+"_mem_AAAV_dout_nent : "
                wirelist += "t_arr_"+mtypeB+"_NENT; -- (#page)(#bin)\n"
            else:
                wirelist += "  signal "+mtypeB+"_mem_AAV_dout_nent  : "
                wirelist += "t_arr_"+mtypeB+"_NENT; -- (#page)\n"

    # Write parameters
    parameterlist += "        RAM_WIDTH       => "+bitwidth+",\n"
    parameterlist += "        NUM_PAGES       => "+str(num_pages)+",\n"
    parameterlist += "        INIT_FILE       => \"\",\n"
    parameterlist += "        INIT_HEX        => true,\n"
    parameterlist += "        RAM_PERFORMANCE => \"HIGH_PERFORMANCE\",\n"

    if "VMSME_D" in memList[0].inst: # VMSME memories have 16 bins in the disks
        parameterlist += "        NUM_MEM_BINS    => 16,\n"
        parameterlist += "        NUM_ENTRIES_PER_MEM_BINS => 8,\n"

    # Write ports
    portlist += "        clka      => clk,\n"
    portlist += "        wea       => "+mtypeB+"_mem_A_wea(var),\n"
    portlist += "        addra     => "+mtypeB+"_mem_AV_writeaddr(var),\n"
    portlist += "        dina      => "+mtypeB+"_mem_AV_din(var),\n"
    portlist += "        clkb      => clk,\n"
    portlist += "        enb       => "+mtypeB+"_mem_A_enb(var),\n"
    portlist += "        rstb      => '0',\n"
    portlist += "        regceb    => '1',\n"
    portlist += "        addrb     => "+mtypeB+"_mem_AV_readaddr(var),\n"
    portlist += "        doutb     => "+mtypeB+"_mem_AV_dout(var),\n"
    portlist += "        sync_nent => "+sync_signal+",\n"

    if memList[0].has_numEntries_out:
        if memList[0].is_binned:
            portlist += "        nent_o    => "+mtypeB+"_mem_AAAV_dout_nent(var),\n"
        else:
            portlist += "        nent_o    => "+mtypeB+"_mem_AAV_dout_nent(var),\n"
    else:
        portlist += "        nent_o    => open,\n"

    enum_type = "enum_"+mtypeB
    genName = mtypeB+"_loop"
    mem_str += "  "+genName+" : for var in "+enum_type+" generate\n"
    mem_str += "  begin\n\n"
    if memList[0].is_binned:
        mem_str += "    "+mtypeB+" : entity work.tf_mem_bin\n"
    else:
        mem_str += "    "+mtypeB+" : entity work.tf_mem\n"        
    mem_str += "      generic map (\n"+parameterlist.rstrip(",\n")+"\n      )\n"
    mem_str += "      port map (\n"+portlist.rstrip(",\n")+"\n      );\n\n"
    mem_str += "  end generate "+genName+";\n\n\n"

    return wirelist,mem_str

def writeControlSignals_interface(initial_proc, final_proc, notfinal_procs):
    """
    # Top-level interface: control signals
    """
    string_ctrl_signals = ""
    string_ctrl_signals += "    clk        : in std_logic;\n"
    string_ctrl_signals += "    reset      : in std_logic;\n"
    string_ctrl_signals += "    "+initial_proc+"_start  : in std_logic;\n"
    string_ctrl_signals += "    "+initial_proc+"_bx_in : in std_logic_vector(2 downto 0);\n"
    string_ctrl_signals += "    "+final_proc+"_bx_out : out std_logic_vector(2 downto 0);\n"
    string_ctrl_signals += "    "+final_proc+"_bx_out_vld : out std_logic;\n"
    string_ctrl_signals += "    "+final_proc+"_done   : out std_logic;\n"
    # Extra output ports if debug info must be sent to test-bench.
    for mid_proc in notfinal_procs:
        string_ctrl_signals += "    "+mid_proc+"_bx_out : out std_logic_vector(2 downto 0);\n"
        string_ctrl_signals += "    "+mid_proc+"_bx_out_vld : out std_logic;\n"
        string_ctrl_signals += "    "+mid_proc+"_done   : out std_logic;\n"

    return string_ctrl_signals

def writeMemoryLHSPorts_interface(mtypeB, extraports=False):
    """
    # Top-level interface: input memories' ports.
    """

    if (extraports):
        direction = "out" # carry debug info to test-bench
    else:
        direction = "in"

    string_input_mems = ""
    string_input_mems += "    "+mtypeB+"_mem_A_wea        : "+direction+" t_arr_"+mtypeB+"_1b;\n"
    string_input_mems += "    "+mtypeB+"_mem_AV_writeaddr : "+direction+" t_arr_"+mtypeB+"_ADDR;\n"
    string_input_mems += "    "+mtypeB+"_mem_AV_din       : "+direction+" t_arr_"+mtypeB+"_DATA;\n"

    return string_input_mems

def writeDTCLinkLHSPorts_interface(mtypeB):
    """
    # Top-level interface: input DTC link ports.
    """

    string_input_mems = ""
    string_input_mems += "    "+mtypeB+"_link_AV_dout       : in t_arr_"+mtypeB+"_DATA;\n"
    string_input_mems += "    "+mtypeB+"_link_empty_neg     : in t_arr_"+mtypeB+"_1b;\n"
    string_input_mems += "    "+mtypeB+"_link_read          : out t_arr_"+mtypeB+"_1b;\n"

    return string_input_mems

def writeMemoryRHSPorts_interface(mtypeB, memInfo):
    """
    # Top-level interface: output memories' ports.
    # Inputs:
    #   mTypeB  = memory type & its bits width (TPROJ_58b etc.)
    #   memInfo = Info about each memory type (in MemTypeInfoByKey class)
    """

    # Assume all memories of given type have same bxbitwidth.
    bxbitwidth =  memInfo.bxbitwidth

    string_output_mems = ""
    string_output_mems += "    "+mtypeB+"_mem_A_enb          : in t_arr_"+mtypeB+"_1b;\n"
    string_output_mems += "    "+mtypeB+"_mem_AV_readaddr    : in t_arr_"+mtypeB+"_ADDR;\n"
    string_output_mems += "    "+mtypeB+"_mem_AV_dout        : out t_arr_"+mtypeB+"_DATA;\n"

    if memInfo.has_numEntries_out:
        num_pages = 2**bxbitwidth
        if memInfo.is_binned:
            string_output_mems += "    "+mtypeB+"_mem_AAAV_dout_nent : "
            string_output_mems += "out t_arr_"+mtypeB+"_NENT;\n"
        else:
            string_output_mems += "    "+mtypeB+"_mem_AAV_dout_nent  : "
            string_output_mems += "out t_arr_"+mtypeB+"_NENT;\n" 

    return string_output_mems

def writeTrackStreamRHSPorts_interface(mtypeB):
    """
    # Top-level interface: output track stream ports.
    # Inputs:
    #   mTypeB  = memory type & its bits width (TPROJ_58b etc.)
    """
    string_output_mems = ""
    string_output_mems += "    "+mtypeB+"_stream_AV_din       : out t_arr_"+mtypeB+"_DATA;\n"
    string_output_mems += "    "+mtypeB+"_stream_A_full_neg   : in t_arr_"+mtypeB+"_1b;\n"
    string_output_mems += "    "+mtypeB+"_stream_A_write      : out t_arr_"+mtypeB+"_1b;\n"

    return string_output_mems

def writeTBControlSignals(topfunc, first_proc, last_proc):
    """
    # Verilog test bench: control signals
    """
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

    string_header += "reg "+first_proc+"_start = 1'b0;\n"
    string_header += "always @(posedge clk) begin\n"
    string_header += "  if (reset) "+first_proc+"_start = 1'b0;\n"
    string_header += "  else       "+first_proc+"_start = 1'b1;\n"
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
    """
    # Verilog test bench: send control signals to top-level
    """
    string_fwblock_ctrl = ""
    string_fwblock_ctrl += "  .clk(clk),\n"
    string_fwblock_ctrl += "  .reset(reset),\n"
    string_fwblock_ctrl += "  ."+first_proc+"_start("+first_proc+"_start),\n"
    string_fwblock_ctrl += "  .bx_in_"+first_proc
    string_fwblock_ctrl += "(bx_in_"+first_proc+"),\n"
    string_fwblock_ctrl += "  .bx_out_"+last_proc
    string_fwblock_ctrl += "(bx_out_"+last_proc+"),\n"

    return string_fwblock_ctrl

def writeFWBlockMemoryLHSPorts(memModule):
    """
    # Verilog test bench: send memories to top-level.
    """
    string_input_mems = ""
    string_input_mems += "  ."+memModule.inst+"_mem_A_wea(1'b1),\n"
    string_input_mems += "  ."+memModule.inst+"_mem_AV_writeaddr("
    string_input_mems += memModule.inst+"_mem_V_writeaddr),\n"
    string_input_mems += "  ."+memModule.inst+"_mem_AV_din("
    string_input_mems += memModule.inst+"_mem_V_dout),\n"

    return string_input_mems

def writeFWBlockMemoryRHSPorts(memModule):
    """
    # Verilog test bench: returned memories from top-level.
    """
    string_output_mems = ""
    string_output_mems += "  ."+memModule.inst+"_mem_A_enb("
    string_output_mems += memModule.inst+"_mem_A_enb),\n"
    string_output_mems += "  ."+memModule.inst+"_mem_AV_readaddr("
    string_output_mems += memModule.inst+"_mem_AV_readaddr),\n"
    string_output_mems += "  ."+memModule.inst+"_mem_AV_dout("
    string_output_mems += memModule.inst+"_mem_AV_dout),\n"
    if memModule.has_numEntries_out:
        for i in range(0,2**memModule.bxbitwidth):
            if memModule.is_binned:
                string_output_mems += "  ."+memModule.inst+"_mem_"+str(i)+"_AAAV_dout_nent("
                string_output_mems += memModule.inst+"_mem_"+str(i)+"_AAAV_dout_nent),\n"
            else:
                string_output_mems += "  ."+memModule.inst+"_mem_"+str(i)+"_AAV_dout_nent("
                string_output_mems += memModule.inst+"_mem_"+str(i)+"_AAV_dout_nent),\n"

    return string_output_mems

def writeProcCombination(module, str_ctrl_func, templpars_str, str_ports):
    """
    # Instantiation of processing module within top-level.
    # FIXME needs fixing to include template parameters for generic proc module writing
    """
    module_str = ""
    module_str += str_ctrl_func
    module_str += "  "+module.inst+" : entity work."+module.IPname+"\n"
    module_str += "    port map (\n"+str_ports.rstrip(",\n")+"\n  );\n\n"

    return module_str

def writeLUTCombination(lut, argname, portlist, parameterlist):
    argname = argname.split("[")[0]
    lut_str = ""
    lut_str += "\n  "+lut.inst+"_"+argname+" : entity work.tf_lut"
    lut_str += "\n    generic map (\n"+parameterlist.rstrip(",\n")+"\n    )"
    lut_str += "\n    port map (\n"+portlist.rstrip(",\n")+"\n  );\n\n"

    return lut_str

def writeStartSwitchAndInternalBX(module,mem,extraports=False):
    """
    # Top-level: control (start/done) & Bx signals for use by given module
    # Inputs: processing module & memory that is downstream of it.
    """
    mtype = module.mtype_short()
    mtype_down = mem.downstreams[0].mtype_short()

    int_ctrl_wire = ""
    if not extraports: 
        int_ctrl_wire += "  signal "+mtype+"_done : std_logic := '0';\n"
        int_ctrl_wire += "  signal "+mtype+"_bx_out : std_logic_vector(2 downto 0);\n"
        int_ctrl_wire += "  signal "+mtype+"_bx_out_vld : std_logic;\n"
    int_ctrl_wire += "  signal "+mtype_down+"_start : std_logic := '0';\n"

    int_ctrl_func = "  "+mtype_down+"_start <= '1' when "+mtype+"_done = '1';\n\n"

    return int_ctrl_wire,int_ctrl_func

def writeProcControlSignalPorts(module,first_of_type):
    """
    # Processing module port assignment: control signals
    """
    string_ctrl_ports = ""
    string_ctrl_ports += "      ap_clk   => clk,\n"
    string_ctrl_ports += "      ap_rst   => reset,\n"
    string_ctrl_ports += "      ap_start => "+module.mtype_short()+"_start,\n"
    string_ctrl_ports += "      ap_idle  => open,\n"
    string_ctrl_ports += "      ap_ready => open,\n"
    if first_of_type:
        string_ctrl_ports += "      ap_done  => "+module.mtype_short()+"_done,\n"
    else:
        string_ctrl_ports += "      ap_done  => open,\n"

    return string_ctrl_ports

def writeProcBXPort(modName,isInput,isInitial):
    """
    # Processing module port assignment: BX ports
    """
    bx_str = ""
    if isInput and isInitial:
        bx_str += "      bx_V          => "+modName+"_bx_in,\n"
    elif isInput and not isInitial:
        bx_str += "      bx_V          => "+modName+"_bx_out,\n"
    elif not isInput:
        bx_str += "      bx_o_V        => "+modName+"_bx_out,\n"
        bx_str += "      bx_o_V_ap_vld => "+modName+"_bx_out_vld,\n"
    return bx_str

def writeProcMemoryLHSPorts(argname,mem):
    """
    # Processing module port assignment: outputs to memories
    """
    string_mem_ports = ""
    string_mem_ports += "      "+argname+"_dataarray_data_V_ce0       => open,\n"
    string_mem_ports += "      "+argname+"_dataarray_data_V_we0       => "
    string_mem_ports += mem.keyName()+"_mem_A_wea("+mem.var()+"),\n"
    string_mem_ports += "      "+argname+"_dataarray_data_V_address0  => "
    string_mem_ports += mem.keyName()+"_mem_AV_writeaddr("+mem.var()+"),\n"
    string_mem_ports += "      "+argname+"_dataarray_data_V_d0        => "
    string_mem_ports += mem.keyName()+"_mem_AV_din("+mem.var()+"),\n"

    return string_mem_ports

def writeProcMemoryRHSPorts(argname,mem,portindex=0):
    """
    # Processing module port assignment: inputs from memories
    """
    string_mem_ports = ""
    string_mem_ports += "      "+argname+"_dataarray_data_V_ce"+str(portindex)+"       => "
    string_mem_ports += mem.keyName()+"_mem_A_enb("+mem.var()+"),\n"
    string_mem_ports += "      "+argname+"_dataarray_data_V_address"+str(portindex)+"  => "
    string_mem_ports += mem.keyName()+"_mem_AV_readaddr("+mem.var()+"),\n"
    string_mem_ports += "      "+argname+"_dataarray_data_V_q"+str(portindex)+"        => "
    string_mem_ports += mem.keyName()+"_mem_AV_dout("+mem.var()+"),\n"

    if mem.has_numEntries_out and portindex == 0:
        for i in range(0,2**mem.bxbitwidth):
            if mem.is_binned:
                for j in range(0,8):
                    string_mem_ports += "      "+argname+"_nentries_"+str(i)+"_V_"+str(j)+"     => "
                    string_mem_ports += mem.keyName()+"_mem_AAAV_dout_nent("+mem.var()+")("+str(i)+")("+str(j)+"),\n"
            else:
                string_mem_ports += "      "+argname+"_nentries_"+str(i)+"_V               => "
                string_mem_ports += mem.keyName()+"_mem_AAV_dout_nent("+mem.var()+")("+str(i)+"),\n"

    return string_mem_ports

def writeLUTPorts(argname,lut):
    string_lut_ports = ""
    argname = argname.split("[")[0]
    string_lut_ports += "      clk       => clk,\n"
    string_lut_ports += "      addr      => "+lut.inst+"_"+argname+"_addr,\n"
    string_lut_ports += "      ce        => "+lut.inst+"_"+argname+"_ce,\n"
    string_lut_ports += "      dout      => "+lut.inst+"_"+argname+"_dout\n"

    return string_lut_ports

def writeLUTParameters(argname, lut):
    parameterlist = ""
    width = 0
    if "in" in argname:
        width = 1
        depth = 8
        parameterlist += "      lut_file  => "+"getDirEMDATA & \"LUTs/"+lut.inst+"_stubptinnercut.tab\",\n"
    elif "out" in argname:
        width = 1
        depth = 8
        parameterlist += "      lut_file  => "+"getDirEMDATA & \"LUTs/"+lut.inst+"_stubptoutercut.tab\",\n"
    parameterlist += "      lut_width => "+str(width)+",\n"
    parameterlist += "      lut_depth => "+str(2**depth)+"\n"
    
    return parameterlist

def writeLUTWires(argname, lut):
    wirelist = ""
    argname = argname.split("[")[0]
    depth = 0
    width = 0
    if "in" in argname:
        depth = 8
        width = 1
    elif "out" in argname:
        depth = 8
        width = 1
    wirelist += "  signal "+lut.inst+"_"+argname+"_addr       : "
    wirelist += "std_logic_vector("+str(depth-1)+" downto 0);\n"
    wirelist += "  signal "+lut.inst+"_"+argname+"_ce       : std_logic;\n"
    wirelist += "  signal "+lut.inst+"_"+argname+"_dout : "
    wirelist += "std_logic_vector("+str(width-1)+" downto 0);\n"
    return wirelist

def writeLUTMemPorts(argname, module):
    argname = argname.split("[")[0]
    string_mem_ports = ""
    string_mem_ports += "      "+argname+"_V_address0                  => " 
    string_mem_ports += module.inst+"_"+argname+"_addr,\n"
    string_mem_ports += "      "+argname+"_V_ce0                       => "
    string_mem_ports += module.inst+"_"+argname+"_ce,\n"
    string_mem_ports += "      "+argname+"_V_q0                        => "
    string_mem_ports += module.inst+"_"+argname+"_dout,\n"
    return string_mem_ports

def writeProcDTCLinkRHSPorts(argname,mem):
    """
    # Processing module port assignment: inputs from DTCLink FIFOs
    """
    string_mem_ports = ""
    string_mem_ports += "      "+argname+"_V_dout     => "
    string_mem_ports += mem.keyName()+"_link_AV_dout("+mem.var()+"),\n"
    string_mem_ports += "      "+argname+"_V_empty_n  => "
    string_mem_ports += mem.keyName()+"_link_empty_neg("+mem.var()+"),\n"
    string_mem_ports += "      "+argname+"_V_read     => "
    string_mem_ports += mem.keyName()+"_link_read("+mem.var()+"),\n"
    return string_mem_ports

def writeProcTrackStreamLHSPorts(argname,mem):
    """
    # Processing module port assignment: output track streams
    """
    string_mem_ports = ""
    string_mem_ports += "      "+argname+"_V_din       => "
    string_mem_ports += mem.keyName()+"_stream_AV_din("+mem.var()+"),\n"
    string_mem_ports += "      "+argname+"_V_full_n    => "
    string_mem_ports += mem.keyName()+"_stream_A_full_neg("+mem.var()+"),\n"
    string_mem_ports += "      "+argname+"_V_write     => "
    string_mem_ports += mem.keyName()+"_stream_A_write("+mem.var()+"),\n"
    return string_mem_ports

def writeInputLinkWordPort(module_instance, memoriesPerLayer):
    """
    # Processing module port assignment: InputRouter kInputLink port
    """
    inputLinkWord = ""

    # Loop over each layer/disk the module instance writes to. Repeat up to four times.
    for layer in memoriesPerLayer:
        isBarrelBit = "1" if "L" in layer else "0" # Is barrel bit
        inputLinkWord = '{0:03b}'.format(int(layer[1])) + isBarrelBit + inputLinkWord # Add the layer number (3 bits) and the barrelbit

    inputLinkWord = inputLinkWord.zfill(16) # Pad with zeros so it contains 16 bits
    inputLinkWord = ("1" if "2S" in module_instance else "0") + inputLinkWord # Is 2S bit
    inputLinkWord = '{0:03b}'.format(len(memoriesPerLayer)) + inputLinkWord # Number of layers

    string_ilword_port = "      hLinkWord_V => \""+inputLinkWord+"\",\n"

    return string_ilword_port

def writeInputLinkPhiBinsPort(memoriesPerLayer):
    """
    # Processing module port assignment: InputRouter kNPhiBns/hPhBnWord port
    """
    phiBinWord = ""

    # Loop through the layers and write the number of memories as three bits to phiBinWord
    for layer in memoriesPerLayer:
        phiBinWord = '{0:03b}'.format(memoriesPerLayer[layer]) + phiBinWord
    
    phiBinWord = phiBinWord.zfill(12) # Pad with zeros so it contains 12 bits

    string_phibin_port = "      hPhBnWord_V => \""+phiBinWord+"\",\n"

    return string_phibin_port
