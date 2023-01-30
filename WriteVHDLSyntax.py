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
    string_preamble = "--! Standard library\n"
    string_preamble += "library ieee;\n"
    string_preamble += "--! Standard package\n"
    string_preamble += "use ieee.std_logic_1164.all;\n"
    string_preamble += "--! Signed/unsigned calculations\n"
    string_preamble += "use ieee.numeric_std.all;\n"
    string_preamble += "--! Math real\n"
    string_preamble += "use ieee.math_real.all;\n"
    string_preamble += "--! TextIO\n"
    string_preamble += "use ieee.std_logic_textio.all;\n"
    string_preamble += "--! Standard functions\n"
    string_preamble += "library std;\n"
    string_preamble += "--! Standard TextIO functions\n"
    string_preamble += "use std.textio.all;\n"

    string_preamble += "\n--! Xilinx library\n"
    string_preamble += "library unisim;\n"
    string_preamble += "--! Xilinx package\n"
    string_preamble += "use unisim.vcomponents.all;\n"

    string_preamble += "\n--! User packages\n"
    string_preamble += "use work.tf_pkg.all;\n"
    string_preamble += "use work.memUtil_pkg.all;\n\n"

    return string_preamble

def writeTopModuleOpener(topmodule_name):
    string_topmod_opener = "entity "+topmodule_name+" is\n  port(\n"
    return string_topmod_opener

def writeTBOpener(topfunc):
    string_tb_opener = "--! @brief TB\n"
    string_tb_opener += "entity " + topfunc + " is\n"
    string_tb_opener += "end " + topfunc + ";\n\n"
    string_tb_opener += "--! @brief TB\n"
    string_tb_opener += "architecture behaviour of "+ topfunc +" is\n\n"
    return string_tb_opener

def writeTopModuleEntityCloser(topmodule_name):
    string_closer = "end "+topmodule_name+";\n\n"
    string_closer += "architecture rtl of "+topmodule_name+" is\n\n"
    return string_closer

def writeTBEntityBegin():
    string_begin = "begin\n\n"
    string_begin += "--! @brief Make clock ---------------------------------------\n"
    string_begin += "  clk <= not clk after CLK_PERIOD/2;\n\n"
    return string_begin

def writeTopModuleCloser():
    string_closer = "\n\nend rtl;\n"
    return string_closer

def writeTBModuleCloser():
    string_closer = "\nend behaviour;\n"
    return string_closer

def writeTBMemoryStimulusProcess(initial_proc):
    """
    # VHDL test-bench
    # Stimulates reading and process start
    """

    string_mem = "  procStart : process(CLK)\n"
    string_mem += "    -- Process to start first module in chain & generate its BX counter input.\n"
    string_mem += "    -- Also releases reset flag.\n"
    string_mem += "    constant CLK_RESET : natural := 5; -- Any low number OK.\n"
    string_mem += "    variable CLK_COUNT : natural := 1;\n" if "IR" not in initial_proc else "    variable CLK_COUNT : natural := MAX_ENTRIES - CLK_RESET;\n"
    string_mem += "    variable EVENT_COUNT : integer := -1;\n"
    string_mem += "    variable v_line : line; -- Line for debug\n"
    string_mem += "  begin\n\n"
    string_mem += "    if START_FIRST_" + ("WRITE" if "IR" not in initial_proc else "LINK") + " = '1' then\n"
    string_mem += "      if rising_edge(CLK) then\n"
    string_mem += "        if (CLK_COUNT < MAX_ENTRIES) then\n"
    string_mem += "          CLK_COUNT := CLK_COUNT + 1;\n"
    string_mem += "        else\n"
    string_mem += "          CLK_COUNT := 1;\n"
    string_mem += "          EVENT_COUNT := EVENT_COUNT + 1;\n\n"
    string_mem += "          -- " + initial_proc + " should start one TM period after time when first event starting being \n" if "IR" not in initial_proc else ""
    string_mem += "          -- written to first memory in chain, as it takes this long to write full event.\n" if "IR" not in initial_proc else ""
    string_mem += "          " + initial_proc + "_START <= '1';\n"
    string_mem += "          " + initial_proc + "_BX_IN <= std_logic_vector(to_unsigned(EVENT_COUNT, " + initial_proc + "_BX_IN'length));\n\n"
    string_mem += "          write(v_line, string'(\"=== Processing event \")); write(v_line,EVENT_COUNT); write(v_line, string'(\" at SIM time \")); write(v_line, NOW); writeline(output, v_line);\n"
    string_mem += "        end if;\n"
    string_mem += "        -- Releae\n"
    string_mem += "        if (CLK_COUNT = " + ("CLK_RESET" if "IR" not in initial_proc else "MAX_ENTRIES") + ") then \n"
    string_mem += "          RESET <= '0';\n"
    string_mem += "        end if;\n"
    string_mem += "      end if;\n"
    string_mem += "    end if;\n"
    string_mem += "  end process procStart;\n\n"

    return string_mem

def writeTBMemoryReadInstance(mtypeB, bxbitwidth, is_initial, is_binned):
    """
    # VHDL test-bench
    # Reads memory text files
    """
    str_len = 22 # length of string for formatting purposes

    string_mem = ""
    string_mem += "  " + mtypeB + "_loop : for var in enum_" + mtypeB + " generate\n"
    string_mem += "  begin\n"
    
    if "DL" in mtypeB: # Special case for DTC links that reads from FIFOs
        string_mem += "    read" + mtypeB + " : entity work.FileReaderFIFO\n"
        string_mem += "  generic map (\n"
        string_mem += "      FILE_NAME".ljust(str_len) + "=> FILE_IN_" + mtypeB.split("_")[0] + "&memory_enum_to_string(var)&inputFileNameEnding,\n"
        string_mem += "      DELAY".ljust(str_len) + "=> " + mtypeB.split("_")[0] + "_DELAY*MAX_ENTRIES,\n"
        string_mem += "      FIFO_WIDTH".ljust(str_len) + "=> " + mtypeB.split("_")[1] + ",\n"
        string_mem += "      DEBUG".ljust(str_len) + "=> true,\n"
        string_mem += "      FILE_NAME_DEBUG".ljust(str_len) + "=> FILE_OUT_" + mtypeB.split("_")[0] + "_debug&memory_enum_to_string(var)&debugFileNameEnding\n"
        string_mem += "    )\n"
        string_mem += "    port map (\n"
        string_mem += "      CLK".ljust(str_len) + "=> CLK,\n"
        string_mem += "      READ_EN".ljust(str_len) + "=> " + mtypeB + "_link_read(var),\n"
        string_mem += "      DATA".ljust(str_len) + "=> " + mtypeB + "_link_AV_dout(var),\n"
        string_mem += "      START".ljust(str_len) + "=> " + ("START_" + mtypeB.split("_")[0] + "(var),\n" if is_initial else "open,\n")
        string_mem += "      EMPTY_NEG".ljust(str_len) + "=> " + mtypeB + "_link_empty_neg(var)\n"
    else:             # Standard case for BRAM 
        string_mem += "    read" + mtypeB + " : entity work.FileReader\n"
        string_mem += "  generic map (\n"
        string_mem += "      FILE_NAME".ljust(str_len) + "=> FILE_IN_" + mtypeB.split("_")[0] + "&memory_enum_to_string(var)&inputFileNameEnding,\n"
        string_mem += "      DELAY".ljust(str_len) + "=> " + mtypeB.split("_")[0] + "_DELAY*MAX_ENTRIES,\n"
        string_mem += "      RAM_WIDTH".ljust(str_len) + "=> " + mtypeB.split("_")[1] + ",\n"
        string_mem += "      NUM_PAGES".ljust(str_len) + "=> " + str(2**bxbitwidth) + ",\n"
        string_mem += "      NUM_BINS".ljust(str_len) + "=> 8,\n" if is_binned else "" # FIX ME 16 for MEDISK
        string_mem += "      DEBUG".ljust(str_len) + "=> true,\n"
        string_mem += "      FILE_NAME_DEBUG".ljust(str_len) + "=> FILE_OUT_" + mtypeB.split("_")[0] + "_debug&memory_enum_to_string(var)&debugFileNameEnding\n"
        string_mem += "    )\n"
        string_mem += "    port map (\n"
        string_mem += "      CLK".ljust(str_len) + "=> CLK,\n"
        string_mem += "      ADDR".ljust(str_len) + "=> " + mtypeB + "_mem_AV_writeaddr(var),\n"
        string_mem += "      DATA".ljust(str_len) + "=> " + mtypeB + "_mem_AV_din(var),\n"
        string_mem += "      START".ljust(str_len) + "=> START_" + mtypeB.split("_")[0] + "(var),\n" if is_initial else "      START => open,\n"
        string_mem += "      WRITE_EN".ljust(str_len) + "=> " + mtypeB + "_mem_A_wea(var)\n"

    string_mem += "    );\n"
    string_mem += "  end generate " + mtypeB + "_loop;\n\n"

    return string_mem

def writeMemoryUtil(memDict, memInfoDict):
    """
    # Produce VHDL package with utilities for memories that are specific
    # to current chain.
    # Inputs:
    #   memDict = dictionary of memories organised by type 
    #             & no. of bits (TPROJ_58 etc.)
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

        combined = False

        if memInfo.is_binned:
            combined =  memInfo.downstream_mtype_short in ("TP", "MP")

        # address and nentries types not needed for DTC links or output track
        # streams
        if memInfo.isFIFO: 
            arrName = "t_arr_"+mtypeB+"_1b"
            ss += "  type "+arrName+" is array("+enumName+") of std_logic;\n"
            arrName = "t_arr_"+mtypeB+"_DATA"
            ss += "  type "+arrName+" is array("+enumName+") of std_logic_vector("+str(bitwidth-1)+" downto 0);\n"
        else:

            if combined:
                ncopy = 4
                if memInfo.downstream_mtype_short == "TP" :
                    ncopy = 5
                arrName = "t_arr_"+mtypeB+"_1b"
                ss += "  type "+arrName+" is array("+enumName+") of std_logic;\n" 
                arrName = "t_arr_"+mtypeB+"_A1b"
                ss += "  type "+arrName+" is array("+enumName+") of std_logic_vector("+str(ncopy-1)+" downto 0);\n" 
                arrName = "t_arr_"+mtypeB+"_ADDR"
                ss += "  type "+arrName+" is array("+enumName+") of std_logic_vector("+str(9+memInfo.bxbitwidth)+" downto 0);\n" 
                arrName = "t_arr_"+mtypeB+"_AADDR"
                ss += "  type "+arrName+" is array("+enumName+") of t_arr"+str(ncopy)+"_"+str(10+memInfo.bxbitwidth)+"b;\n"
                arrName = "t_arr_"+mtypeB+"_DATA"
                ss += "  type "+arrName+" is array("+enumName+") of std_logic_vector("+str(bitwidth-1)+" downto 0);\n"  
                arrName = "t_arr_"+mtypeB+"_ADATA"
                ss += "  type "+arrName+" is array("+enumName+") of t_arr"+str(ncopy)+"_"+str(bitwidth)+"b;\n"  
            else:
                arrName = "t_arr_"+mtypeB+"_1b"
                ss += "  type "+arrName+" is array("+enumName+") of std_logic;\n" 
                arrName = "t_arr_"+mtypeB+"_ADDR"
                ss += "  type "+arrName+" is array("+enumName+") of std_logic_vector("+str(6+memInfo.bxbitwidth)+" downto 0);\n" 
                arrName = "t_arr_"+mtypeB+"_DATA"
                ss += "  type "+arrName+" is array("+enumName+") of std_logic_vector("+str(bitwidth-1)+" downto 0);\n" 

            if memInfo.is_binned:
                if memInfo.downstream_mtype_short in ("TP", "MP") :
                    varStr = "_64_4b"
                else:
                    varStr = "_8_5b"
            else:
                varStr = "_7b"
            arrName = "t_arr_"+mtypeB+"_NENT"
            if combined:
              if  "VMSME" in arrName :
                ss += "  type "+arrName+" is array("+enumName+") of std_logic_vector(31 downto 0);\n"
                arrName = "t_arr_"+mtypeB+"_NENTADDR"
                ss += "  type "+arrName+" is array("+enumName+") of std_logic_vector(4 downto 0);\n"
              else:
                ss += "  type "+arrName+" is array("+enumName+") of t_arr"+str(num_pages)+varStr+";\n"
            else:
              ss += "  type "+arrName+" is array("+enumName+") of t_arr"+str(num_pages)+varStr+";\n"
            if memInfo.is_binned:
                if memInfo.downstream_mtype_short in ("TP", "MP") :
                    varStr = "_64_1b"
                    arrName = "t_arr_"+mtypeB+"_MASK"
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
            newvar = mem.var()
            # Bodge explained in TrackletGraph::Node()
            if (mem.inst.startswith("DL_twoS")):
                newvar = newvar.replace("twoS","2S")
            ss += "       when "+mem.var()+" => return \""+newvar+"\";\n"
        ss += "    end case;\n"
        ss += "    return \"No conversion found.\";\n"
        ss += "  end memory_enum_to_string;\n\n"

    ss += "end package body memUtil_pkg;\n"

    return ss;

def writeTopLevelMemoryType(mtypeB, memList, memInfo, extraports):
    """
    # Declaration of memories of type "mtype" (e.g. TPROJ) & associated wires
    # Inputs:
    #   mTypeB  = memory type & its bits width (TPROJ_58 etc.)
    #   memList = list of memories of given type & bit width
    #   memInfo = Info about each memory type (in MemTypeInfoByKey class)
    """

    combined = False
    nmem = 0

    if memInfo.is_binned:
        combined =  memInfo.downstream_mtype_short in ("TP", "MP")
        if memInfo.downstream_mtype_short == "TP" :
            nmem =  5
        if memInfo.downstream_mtype_short == "MP" :
            nmem =  4

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
        if combined :
            wirelist += "  signal "+mtypeB+"_mem_AA_enb         : "
            wirelist += "t_arr_"+mtypeB+"_A1b;\n"
            wirelist += "  signal "+mtypeB+"_mem_AAV_readaddr   : "
            wirelist += "t_arr_"+mtypeB+"_AADDR;\n"
            wirelist += "  signal "+mtypeB+"_mem_AAV_dout       : "
            wirelist += "t_arr_"+mtypeB+"_ADATA;\n" 
        else:
            wirelist += "  signal "+mtypeB+"_mem_A_enb          : "
            wirelist += "t_arr_"+mtypeB+"_1b;\n"
            wirelist += "  signal "+mtypeB+"_mem_AV_readaddr    : "
            wirelist += "t_arr_"+mtypeB+"_ADDR;\n"
            wirelist += "  signal "+mtypeB+"_mem_AV_dout        : "
            wirelist += "t_arr_"+mtypeB+"_DATA;\n" 

        if memInfo.has_numEntries_out:
            if memInfo.is_binned:
                if combined:
                    wirelist += "  signal "+mtypeB+"_mem_AAV_dout_mask : "
                    wirelist += "t_arr_"+mtypeB+"_MASK; -- (#page)(#bin)\n"  
                    if "VMSTE" in mtypeB :
                        wirelist += "  signal "+mtypeB+"_mem_AAAV_dout_nent : "
                        wirelist += "t_arr_"+mtypeB+"_NENT; -- (#page)(#bin)\n"
                    else:
                        wirelist += "  signal "+mtypeB+"_mem_A_enb_nentA : "
                        wirelist += "t_arr_"+mtypeB+"_1b;\n"
                        wirelist += "  signal "+mtypeB+"_mem_A_enb_nentB : "
                        wirelist += "t_arr_"+mtypeB+"_1b;\n"
                        wirelist += "  signal "+mtypeB+"_mem_AV_addr_nentA : "
                        wirelist += "t_arr_"+mtypeB+"_NENTADDR;\n"
                        wirelist += "  signal "+mtypeB+"_mem_AV_addr_nentB : "
                        wirelist += "t_arr_"+mtypeB+"_NENTADDR;\n"
                        wirelist += "  signal "+mtypeB+"_mem_AV_dout_nentA : "
                        wirelist += "t_arr_"+mtypeB+"_NENT;\n"
                        wirelist += "  signal "+mtypeB+"_mem_AV_dout_nentB : "
                        wirelist += "t_arr_"+mtypeB+"_NENT;\n"
                else:
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
    parameterlist += "        NAME            => \""+mtypeB+"_\"&memory_enum_to_string(var)\n"

    if "VMSME_D" in memList[0].inst: # VMSME memories have 16 bins in the disks
        parameterlist += "        NUM_MEM_BINS    => 16,\n"
        parameterlist += "        NUM_ENTRIES_PER_MEM_BINS => 8,\n"

    # Write ports
    portlist += "        clka      => clk,\n"
    if combined :
        portlist += "        wea       => "+mtypeB+"_mem_A_wea(var),\n"
        portlist += "        addra     => "+mtypeB+"_mem_AV_writeaddr(var),\n"
        portlist += "        dina      => "+mtypeB+"_mem_AV_din(var),\n"
    else:
        portlist += "        wea       => "+mtypeB+"_mem_A_wea(var),\n"
        portlist += "        addra     => "+mtypeB+"_mem_AV_writeaddr(var),\n"
        portlist += "        dina      => "+mtypeB+"_mem_AV_din(var),\n"
    portlist += "        clkb      => clk,\n"
    portlist += "        rstb      => '0',\n"
    portlist += "        regceb    => '1',\n"
    if combined :
        for inst in range(0,nmem) :
            portlist += "        enb"+str(inst)+"       => "+mtypeB+"_mem_AA_enb(var)("+str(inst)+"),\n"
            portlist += "        addrb"+str(inst)+"     => "+mtypeB+"_mem_AAV_readaddr(var)("+str(inst)+"),\n"
            portlist += "        doutb"+str(inst)+"     => "+mtypeB+"_mem_AAV_dout(var)("+str(inst)+"),\n"
    else:
        portlist += "        enb       => "+mtypeB+"_mem_A_enb(var),\n"
        portlist += "        addrb     => "+mtypeB+"_mem_AV_readaddr(var),\n"
        portlist += "        doutb     => "+mtypeB+"_mem_AV_dout(var),\n"
    portlist += "        sync_nent => "+sync_signal+",\n"

    if memList[0].has_numEntries_out:
        if memList[0].is_binned:
            if combined:
                portlist += "        mask_o    => "+mtypeB+"_mem_AAV_dout_mask(var),\n"
                if "VMSTE" in mtypeB :
                    portlist += "        nent_o    => "+mtypeB+"_mem_AAAV_dout_nent(var),\n"
                else:
                    portlist += "        enb_nentA  => "+mtypeB+"_mem_A_enb_nentA(var),\n"
                    portlist += "        enb_nentB  => "+mtypeB+"_mem_A_enb_nentB(var),\n"
                    portlist += "        addr_nentA  => "+mtypeB+"_mem_AV_addr_nentA(var),\n"
                    portlist += "        addr_nentB  => "+mtypeB+"_mem_AV_addr_nentB(var),\n"
                    portlist += "        dout_nentA    => "+mtypeB+"_mem_AV_dout_nentA(var),\n"
                    portlist += "        dout_nentB    => "+mtypeB+"_mem_AV_dout_nentB(var),\n"
            else:
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
        module =  memList[0].downstreams[0].inst[0:3]
        if module == "TP_" :
            mem_str += "    "+mtypeB+" : entity work.tf_mem_bin_cm5\n"
        elif module == "MP_" :
            mem_str += "    "+mtypeB+" : entity work.tf_mem_bin_cm4_new\n"
        else:
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
    #   mTypeB  = memory type & its bits width (TPROJ_58 etc.)
    #   memInfo = Info about each memory type (in MemTypeInfoByKey class)
    """

    combined = (memInfo.downstream_mtype_short in ("TP", "MP"))

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
            if combined:
                string_output_mems += "    "+mtypeB+"_mem_AAV_dout_mask : "
                string_output_mems += "out t_arr_"+mtypeB+"_MASK;\n"
        else:
            string_output_mems += "    "+mtypeB+"_mem_AAV_dout_nent  : "
            string_output_mems += "out t_arr_"+mtypeB+"_NENT;\n" 

    return string_output_mems

def writeTrackStreamRHSPorts_interface(mtypeB):
    """
    # Top-level interface: output track stream ports.
    # Inputs:
    #   mTypeB  = memory type & its bits width (TPROJ_58 etc.)
    """
    string_output_mems = ""
    string_output_mems += "    "+mtypeB+"_stream_AV_din       : out t_arr_"+mtypeB+"_DATA;\n"
    string_output_mems += "    "+mtypeB+"_stream_A_full_neg   : in t_arr_"+mtypeB+"_1b;\n"
    string_output_mems += "    "+mtypeB+"_stream_A_write      : out t_arr_"+mtypeB+"_1b;\n"

    return string_output_mems

def writeTBConstants(memDict, memInfoDict, procs, emData_dir, sector):
    """
    # VHDL test-bench: write the constants used by the test-bench
    # Inputs:
    #   memDict:        dictionary of memories organised by type 
    #                   & no. of bits (TPROJ_58 etc.)
    #   memInfoDict:    dictionary of info (MemTypeInfoByKey) about each memory type.
    #   procs:          list of processes in the order that they are positioned in the chain
    #   emData_dir:     the directory for the emData/ folder
    #   sector:         the sector/nonant number
    """

    str_len = 32 # length of string for formatting purposes

    string_constants = ""
    string_constants += "  -- ########################### Constant Definitions ###########################\n"
    string_constants += "  -- ############ Please change the constants in this section ###################\n\n"
    string_constants += "  --=========================================================================\n"
    string_constants += "  -- Specify version of chain to run from TB:\n"
    string_constants += "  --    0 = SectorProcessor.vhd from python script.\n"
    string_constants += "  --    1 = SectorProcessorFull.vhd from python script (gives intermediate MemPrints).\n"
    string_constants += "  --    N.B. Change this also in makeProject.tcl !\n"
    string_constants += "  constant INST_TOP_TF".ljust(str_len) + ": integer := 1; \n"
    string_constants += "  --=========================================================================\n\n"
    string_constants += "  constant CLK_PERIOD".ljust(str_len) + ": time    := 4 ns;       --! 250 MHz\n"
    string_constants += "  constant DEBUG".ljust(str_len) + ": boolean := false;      --! Debug off/on\n"
 
    # Write delay and input/output file name signals
    string_input_tmp = "  -- File directories and the start of the file names that memories have in common\n"
    string_input_tmp += "  -- Input files\n"
    string_output_tmp = "  -- Output files\n"
    string_debug_tmp = "  -- Debug output files to check input was correctly read.\n"

    for mtypeB in memDict:
        memInfo = memInfoDict[mtypeB]
        if memInfo.is_initial:
            # Avoid duplicate constants, e.g. for VMSTE
            if memInfo.mtype_short not in string_input_tmp:
                mem_dir = memInfo.mtype_long.replace("AllStubs", "Stubs").replace("Inner", "").replace("Outer", "").replace("DTCLink", "InputStubs").replace("InputLink", "InputStubs").replace("FullMatch", "Matches").replace("AllProj", "TrackletProjections").replace("CandidateMatch", "Matches") # Directory name for the memory testvectors. FIX ME, make this prettier?!
                mem_file_start = memInfo.mtype_long.replace("ME", "").replace("TE","").replace("Inner", "").replace("Outer", "").replace("DTC", "").replace("InputLink", "InputStubs").replace("FullMatch", "FullMatches").replace("CandidateMatch", "CandidateMatches") # Testvector file name start. FIX ME, make this prettier?!
                mem_delay = procs.index(memInfo.downstream_mtype_short) # The delay in number of bx. The initial process of the chain will have 0 delay, the second have 1 bx delay etc.

                string_constants += ("  constant " + memInfo.mtype_short + "_DELAY").ljust(str_len) + ": integer := " + str(mem_delay) + ";          --! Number of BX delays\n"
                string_input_tmp += ("  constant FILE_IN_" + memInfo.mtype_short).ljust(str_len) + ": string := memPrintsDir&\"" + mem_dir + "/" + mem_file_start + "_" + memInfo.mtype_short + "_\";\n"
                string_debug_tmp += ("  constant FILE_OUT_" + memInfo.mtype_short + "_debug").ljust(str_len) + ": string := dataOutDir&\"" + memInfo.mtype_short + "_\";\n"
        else:
            string_output_tmp += ("  constant FILE_OUT_" + mtypeB).ljust(str_len) + ": string := dataOutDir&\"" + memInfo.mtype_short + "_\";\n"
    
    string_constants += "\n  -- Paths of data files specified relative to Vivado project's xsim directory.\n"
    string_constants += "  -- e.g. IntegrationTests/PRMEMC/script/Work/Work.sim/sim_1/behav/xsim/\n"
    string_constants += "  constant memPrintsDir".ljust(str_len) + ": string := \"" + emData_dir + "\";\n"
    string_constants += "  constant dataOutDir".ljust(str_len) + ": string := \"../../../../../dataOut/\";\n\n"

    string_constants += string_input_tmp
    string_constants += string_output_tmp
    string_constants += string_debug_tmp
    
    string_constants += "\n  -- File name endings\n"
    string_constants += "  constant inputFileNameEnding".ljust(str_len) + ": string := \"_" + sector + ".dat\"; -- " + sector + " specifies the nonant/sector the testvectors represent\n"
    string_constants += "  constant outputFileNameEnding".ljust(str_len) + ": string := \".txt\";\n"
    string_constants += "  constant debugFileNameEnding".ljust(str_len) + ": string := \".debug.txt\";\n\n"

    return string_constants

def writeTBControlSignals(memDict, memInfoDict, initial_proc, final_proc, notfinal_procs):
    """
    # VHDL test bench: write control signals
    # Inputs:
    #   memDict:        dictionary of memories organised by type 
    #                   & no. of bits (TPROJ_58 etc.)
    #   memInfoDict:    dictionary of info (MemTypeInfoByKey) about each memory type.
    #   initial_proc:   name of the first processing module of the chain
    #   final_proc:     name of the last processing module of the chain
    #   notfinal_procs: a set of the names of processing modules not at the end of the chain
    """

    str_len = 36 # length of string for formatting purposes
    str_len2 = 21

    string_ctrl_signals = "\n  -- ########################### Signals ###########################\n"
    string_ctrl_signals += "  -- ### UUT signals ###\n"
    string_ctrl_signals += "  signal clk".ljust(str_len)+": std_logic := '0';\n"
    string_ctrl_signals += "  signal reset".ljust(str_len)+": std_logic := '1';\n"
    string_ctrl_signals += ("  signal "+initial_proc+"_start").ljust(str_len)+": std_logic := '0';\n"
    string_ctrl_signals += ("  signal "+initial_proc+"_idle").ljust(str_len)+": std_logic := '0';\n"
    string_ctrl_signals += ("  signal "+initial_proc+"_ready").ljust(str_len)+": std_logic := '0';\n"
    string_ctrl_signals += ("  signal "+initial_proc+"_bx_in").ljust(str_len)+": std_logic_vector(2 downto 0) := (others => '1');\n"
    # Extra output ports if debug info must be sent to test-bench.
    for mid_proc in notfinal_procs:
        string_ctrl_signals += ("  signal "+mid_proc+"_bx_out").ljust(str_len)+": std_logic_vector(2 downto 0) := (others => '1');\n"
        string_ctrl_signals += ("  signal "+mid_proc+"_bx_out_vld").ljust(str_len)+": std_logic := '0';\n"
        string_ctrl_signals += ("  signal "+mid_proc+"_done").ljust(str_len)+": std_logic := '0';\n"
    string_ctrl_signals += ("  signal "+final_proc+"_bx_out").ljust(str_len)+": std_logic_vector(2 downto 0) := (others => '1');\n"
    string_ctrl_signals += ("  signal "+final_proc+"_bx_out_vld").ljust(str_len)+": std_logic := '0';\n"
    string_ctrl_signals += ("  signal "+final_proc+"_done").ljust(str_len)+": std_logic := '0';\n"

    first_mem = "" # The first memory of the chain
    found_first_mem = False

    # Loop over all memory types
    string_ctrl_signals += "\n  -- Signals matching ports of top-level VHDL\n"
    for mtypeB in memDict:
        
        memInfo = memInfoDict[mtypeB]
        combined = (memInfo.downstream_mtype_short in ("TP", "MP"))

        if initial_proc in memInfo.downstream_mtype_short and not found_first_mem:
            first_mem = mtypeB
            found_first_mem = True

        if "DL" in mtypeB: # Special case for DTCLink as it has a FIFO read interface
            string_ctrl_signals += ("  signal "+mtypeB+"_link_read").ljust(str_len)+": "
            string_ctrl_signals += ("t_arr_"+mtypeB+"_1b").ljust(str_len2)+":= (others => '0');\n"
            string_ctrl_signals += ("  signal "+mtypeB+"_link_empty_neg").ljust(str_len)+": "
            string_ctrl_signals += ("t_arr_"+mtypeB+"_1b").ljust(str_len2)+":= (others => '0');\n"
            string_ctrl_signals += ("  signal "+mtypeB+"_link_AV_dout").ljust(str_len)+": "
            string_ctrl_signals += ("t_arr_"+mtypeB+"_DATA").ljust(str_len2)+":= (others => (others => '0'));\n"
        elif memInfo.isFIFO: # Special case for FIFO write
            string_ctrl_signals += ("  signal "+mtypeB+"_stream_A_write").ljust(str_len)+": "
            string_ctrl_signals += ("t_arr_"+mtypeB+"_1b").ljust(str_len2)+":= (others => '0');\n"
            string_ctrl_signals += ("  signal "+mtypeB+"_stream_A_full_neg").ljust(str_len)+": "
            string_ctrl_signals += ("t_arr_"+mtypeB+"_1b").ljust(str_len2)+":= (others => '0');\n"
            string_ctrl_signals += ("  signal "+mtypeB+"_stream_AV_din").ljust(str_len)+": "
            string_ctrl_signals += ("t_arr_"+mtypeB+"_DATA").ljust(str_len2)+":= (others => (others => '0'));\n"

        elif memInfo.is_final: # RAM read interface
            string_ctrl_signals += ("  signal "+mtypeB+"_mem_A_enb").ljust(str_len)+": "
            string_ctrl_signals += ("t_arr_"+mtypeB+"_1b").ljust(str_len2)+":= (others => '0');\n"
            string_ctrl_signals += ("  signal "+mtypeB+"_mem_AV_readaddr").ljust(str_len)+": "
            string_ctrl_signals += ("t_arr_"+mtypeB+"_ADDR").ljust(str_len2)+":= (others => (others => '0'));\n"
            string_ctrl_signals += ("  signal "+mtypeB+"_mem_AV_dout").ljust(str_len)+": "
            string_ctrl_signals += ("t_arr_"+mtypeB+"_DATA").ljust(str_len2)+":= (others => (others => '0'));\n"
            # Add nentries signal if last memory of the chain
            if memInfo.is_binned:
                string_ctrl_signals += ("  signal "+mtypeB+"_mem_AAAV_dout_nent").ljust(str_len)+": "
                string_ctrl_signals += ("t_arr_"+mtypeB+"_NENT").ljust(str_len2)+":= (others => (others => (others => (others => '0')))); -- (#page)(#bin)\n"
                if combined:
                    string_ctrl_signals += ("  signal "+mtypeB+"_mem_AAV_dout_mask").ljust(str_len)+": "
                    string_ctrl_signals += ("t_arr_"+mtypeB+"_MASK").ljust(str_len2)+":= (others => (others => (others => '0'))); -- (#page)(#bin)\n"
            else:
                string_ctrl_signals += ("  signal "+mtypeB+"_mem_AAV_dout_nent").ljust(str_len)+": "
                string_ctrl_signals += ("t_arr_"+mtypeB+"_NENT").ljust(str_len2)+":= (others => (others => (others => '0'))); -- (#page)\n"
        else: # RAM write interface
            string_ctrl_signals += ("  signal "+mtypeB+"_mem_A_wea").ljust(str_len)+": "
            string_ctrl_signals += ("t_arr_"+mtypeB+"_1b").ljust(str_len2)+":= (others => '0');\n"
            string_ctrl_signals += ("  signal "+mtypeB+"_mem_AV_writeaddr").ljust(str_len)+": "
            string_ctrl_signals += ("t_arr_"+mtypeB+"_ADDR").ljust(str_len2)+":= (others => (others => '0'));\n"
            string_ctrl_signals += ("  signal "+mtypeB+"_mem_AV_din").ljust(str_len)+": "
            string_ctrl_signals += ("t_arr_"+mtypeB+"_DATA").ljust(str_len2)+":= (others => (others => '0'));\n"

    if "DL" in first_mem:
        string_ctrl_signals += "\n  -- Indicates that reading of DL of first event has started.\n"
        string_ctrl_signals += "  signal START_FIRST_LINK : std_logic := '0';\n"
    else:
        string_ctrl_signals += "\n  -- Indicates that writing of the initial memories of the first event has started.\n"
        string_ctrl_signals += "  signal START_FIRST_WRITE : std_logic := '0';\n"
    string_ctrl_signals += "  signal START_" + first_mem.split("_")[0] + " : t_arr_" + first_mem + "_1b" + " := (others => '0');\n\n"

    return string_ctrl_signals

def writeFWBlockInstance(topfunc, memDict, memInfoDict, initial_proc, final_proc, notfinal_procs = []):
    """
    # VHDL test bench: write the instantiation of the top level SectorProcessor FW
    # Inputs:
    #   topfunc:        name of the top module
    #   memDict:        dictionary of memories organised by type 
    #                   & no. of bits (TPROJ_58 etc.)
    #   memInfoDict:    dictionary of info (MemTypeInfoByKey) about each memory type.
    #   initial_proc:   name of the first processing module of the chain
    #   final_proc:     name of the last processing module of the chain
    #   notfinal_procs: a set of the names of processing modules not at the end of the chain
    """
    str_len = 35 # length of string for formatting purposes

    string_fwblock_inst =  "  sectorProcFull : if INST_TOP_TF = 1 generate\n" if notfinal_procs or final_proc == initial_proc else "  sectorProc : if INST_TOP_TF = 0 generate\n"
    string_fwblock_inst += "  begin\n"
    string_fwblock_inst += "    uut : entity work." + topfunc + "\n"
    string_fwblock_inst += "      port map(\n"
    string_fwblock_inst += "        clk".ljust(str_len) + "=> clk,\n"
    string_fwblock_inst += "        reset".ljust(str_len) + "=> reset,\n"
    string_fwblock_inst += ("        " + initial_proc + "_start").ljust(str_len) + "=> " + initial_proc + "_start,\n"
    string_fwblock_inst += ("        " + initial_proc + "_bx_in").ljust(str_len) + "=> " + initial_proc + "_bx_in,\n"
    string_fwblock_inst += ("        " + final_proc + "_bx_out").ljust(str_len) + "=> " + final_proc + "_bx_out,\n"
    string_fwblock_inst += ("        " + final_proc + "_bx_out_vld").ljust(str_len) + "=> " + final_proc + "_bx_out_vld,\n"
    string_fwblock_inst += ("        " + final_proc + "_done").ljust(str_len) + "=> " + final_proc + "_done,\n"

    # Add debug signals if considering intermediate memories
    if notfinal_procs:
        string_fwblock_inst += "        -- Debug control signals\n"
        for mid_proc in notfinal_procs:
            string_fwblock_inst += ("        " + mid_proc + "_bx_out").ljust(str_len) + "=> " + mid_proc + "_bx_out,\n"
            string_fwblock_inst += ("        " + mid_proc + "_bx_out_vld").ljust(str_len) + "=> " + mid_proc + "_bx_out_vld,\n"
            string_fwblock_inst += ("        " + mid_proc + "_done").ljust(str_len) + "=> " + mid_proc + "_done,\n"

    # Memory input/output/debug signals
    string_input = ""
    string_output = ""
    string_debug = ""

    for mtypeB in memDict:
        memInfo = memInfoDict[mtypeB]
        combined = (memInfo.downstream_mtype_short in ("TP", "MP"))
        if memInfo.is_initial:
            if "DL" in mtypeB: # Special case for DTCLink as it has FIFO input
                string_input += ("        "+mtypeB+"_link_AV_dout").ljust(str_len) + "=> "+mtypeB+"_link_AV_dout,\n"
                string_input += ("        "+mtypeB+"_link_empty_neg").ljust(str_len) + "=> "+mtypeB+"_link_empty_neg,\n"
                string_input += ("        "+mtypeB+"_link_read").ljust(str_len) + "=> "+mtypeB+"_link_read,\n"
            else:
                string_input += ("        "+mtypeB+"_mem_A_wea").ljust(str_len) + "=> "+mtypeB+"_mem_A_wea,\n"
                string_input += ("        "+mtypeB+"_mem_AV_writeaddr").ljust(str_len) + "=> "+mtypeB+"_mem_AV_writeaddr,\n"
                string_input += ("        "+mtypeB+"_mem_AV_din").ljust(str_len) + "=> "+mtypeB+"_mem_AV_din,\n"
        elif memInfo.isFIFO: # Special case FIFO output
            string_tmp = ("        "+mtypeB+"_stream_AV_din").ljust(str_len) + "=> "+mtypeB+"_stream_AV_din,\n"
            string_tmp += ("        "+mtypeB+"_stream_A_full_neg").ljust(str_len) + "=> "+mtypeB+"_stream_A_full_neg,\n"
            string_tmp += ("        "+mtypeB+"_stream_A_write").ljust(str_len) + "=> "+mtypeB+"_stream_A_write,\n"
            if memInfo.is_final:
                string_output += string_tmp
            else:
                string_debug  += string_tmp
        elif memInfo.is_final:
            string_output += ("        "+mtypeB+"_mem_A_enb").ljust(str_len) + "=> "+mtypeB+"_mem_A_enb,\n"
            string_output += ("        "+mtypeB+"_mem_AV_readaddr").ljust(str_len) + "=> "+mtypeB+"_mem_AV_readaddr,\n"
            string_output += ("        "+mtypeB+"_mem_AV_dout").ljust(str_len) + "=> "+mtypeB+"_mem_AV_dout,\n"
            if memInfo.is_binned:
                string_output += ("        "+mtypeB+"_mem_AAAV_dout_nent").ljust(str_len) + "=> "+mtypeB+"_mem_AAAV_dout_nent,\n"
                if combined:
                    string_output += ("        "+mtypeB+"_mem_AAV_dout_mask").ljust(str_len) + "=> "+mtypeB+"_mem_AAV_dout_mask,\n"
            else:
                string_output += ("        "+mtypeB+"_mem_AAV_dout_nent").ljust(str_len) + "=> "+mtypeB+"_mem_AAV_dout_nent,\n"
        else:
            string_debug += ("        "+mtypeB+"_mem_A_wea").ljust(str_len) + "=> "+mtypeB+"_mem_A_wea,\n"
            string_debug += ("        "+mtypeB+"_mem_AV_writeaddr").ljust(str_len) + "=> "+mtypeB+"_mem_AV_writeaddr,\n"
            string_debug += ("        "+mtypeB+"_mem_AV_din").ljust(str_len) + "=> "+mtypeB+"_mem_AV_din,\n"

    string_fwblock_inst += "        -- Input data\n"
    string_fwblock_inst += string_input
    if notfinal_procs:
        string_fwblock_inst += "        -- Debug output data\n"
        string_fwblock_inst += string_debug
    string_fwblock_inst += "        -- Output data\n"
    string_fwblock_inst += string_output[:-2]+"\n" # Remove the last comma
    
    string_fwblock_inst += "      );\n"
    string_fwblock_inst += "  end generate sectorProcFull;\n\n" if notfinal_procs or final_proc == initial_proc else "  end generate sectorProc;\n\n"

    return string_fwblock_inst

def writeTBMemoryWriteInstance(mtypeB, proc, proc_up, bxbitwidth, is_binned, is_cm):
    """
    # VHDL test bench: write the loop that writes the input to the intermediate RAM memories to text files
    # Inputs:
    #   mtypeB:     the name of the memory type, including the number of bits (e.g. TPROJ_58)
    #   proc:       the processing module that writes to this memory.
    #   proc_up:    the previous processing module (upstream). If proc is the initial module, then this is an empty string
    #   bxbitwidth: number of bits for the bunch-crossings. I.e. one page per bx.
    #   is_binned:  if the memory is binned or not.
    """

    str_len = 18 # length of string for formatting purposes

    string_mem = "    "+mtypeB+"_loop : for var in enum_"+mtypeB+" generate\n"
    string_mem += "    begin\n"
    string_mem += "      write"+mtypeB+" : entity work.FileWriter\n"
    string_mem += "      generic map (\n"
    string_mem += "        FILE_NAME".ljust(str_len)+"=> FILE_OUT_"+mtypeB+"&memory_enum_to_string(var)&outputFileNameEnding,\n"
    string_mem += "        RAM_WIDTH".ljust(str_len)+"=> " + mtypeB.split("_")[1] + ",\n"
    if is_cm and is_binned :
        string_mem += "        PAGE_LENGTH".ljust(str_len)+"=> 1024,\n"
    string_mem += "        NUM_PAGES".ljust(str_len)+"=> " + str(2**bxbitwidth) + "\n"
    string_mem += "      )\n"
    string_mem += "      port map (\n"
    string_mem += "        CLK".ljust(str_len)+"=> CLK,\n"
    string_mem += "        ADDR".ljust(str_len)+"=> "+mtypeB+"_mem_AV_writeaddr(var),\n"
    string_mem += "        DATA".ljust(str_len)+"=> "+mtypeB+"_mem_AV_din(var),\n"
    string_mem += "        WRITE_EN".ljust(str_len)+"=> "+mtypeB+"_mem_A_wea(var),\n"
    string_mem += "        START".ljust(str_len)+"=> "+(proc+"_START,\n" if not proc_up else proc_up+"_DONE,\n")
    string_mem += "        DONE".ljust(str_len)+"=> "+proc+"_DONE\n"
    string_mem += "      );\n"
    string_mem += "    end generate "+mtypeB+"_loop;\n\n"
    
    return string_mem

def writeTBMemoryWriteRAMInstance(mtypeB, proc, bxbitwidth, is_binned):
    """
    # VHDL test bench: write the loop that writes the output from the end-of-chain BRAM memories to text files
    # Inputs:
    #   mtypeB:     the name of the memory type, including the number of bits (e.g. TPROJ_58)
    #   proc:       the processing module that writes to this memory.
    #   bxbitwidth: number of bits for the bunch-crossings. I.e. one page per bx.
    #   is_binned:  if the memory is binned or not.
    """
    str_len = 16 # length of string for formatting purposes
    string_mem = ""

    # FIX ME change number of bins from default 8 to 16 for VMSME Disk memories
    string_mem += "  -- FIX ME change number of bins from default 8 to 16 for VMSME Disk memories!!!\n" if "VMSME" in mtypeB else ""

    string_mem += "  "+mtypeB+"_loop : for var in enum_"+mtypeB+" generate\n"
    string_mem += "  begin\n"
    string_mem += "    write"+mtypeB+" : entity work.FileWriterFromRAM" + ("Binned\n" if is_binned else "\n")
    string_mem += "    generic map (\n"
    string_mem += "      FILE_NAME".ljust(str_len)+"=> FILE_OUT_"+mtypeB+"&memory_enum_to_string(var)&outputFileNameEnding,\n"
    string_mem += "      RAM_WIDTH".ljust(str_len)+"=> " + mtypeB.split("_")[1] + ",\n"
    string_mem += "      NUM_PAGES".ljust(str_len)+"=> " + str(2**bxbitwidth) + "\n"
    string_mem += "    )\n"
    string_mem += "    port map (\n"
    string_mem += "      CLK".ljust(str_len)+"=> CLK,\n"
    string_mem += "      ADDR".ljust(str_len)+"=> "+mtypeB+"_mem_AV_readaddr(var),\n"
    string_mem += "      DATA".ljust(str_len)+"=> "+mtypeB+"_mem_AV_dout(var),\n"
    string_mem += "      READ_EN".ljust(str_len)+"=> "+mtypeB+"_mem_A_enb(var),\n"
    string_mem += "      NENT_ARR".ljust(str_len)+"=> "+mtypeB+"_mem_AA" + ("A" if is_binned else "") + "V_dout_nent(var),\n"
    string_mem += "      DONE".ljust(str_len)+"=> "+proc+"_DONE\n"
    string_mem += "    );\n"
    string_mem += "  end generate "+mtypeB+"_loop;\n\n"

    return string_mem 


def writeTBMemoryWriteFIFOInstance(mtypeB, proc, bxbitwidth):
    """
    # VHDL test bench: write the loop that writes the input to all FIFO memories to text files
    # Inputs:
    #   mtypeB:     the name of the memory type, including the number of bits (e.g. TPROJ_58)
    #   proc:       the processing module that writes to this memory.
    #   bxbitwidth: number of bits for the bunch-crossings. I.e. one page per bx.
    """
    str_len = 16 # length of string for formatting purposes
    string_mem = ""
    string_mem += "  "+mtypeB+"_loop : for var in enum_"+mtypeB+" generate\n"
    string_mem += "  begin\n"
    string_mem += "    write"+mtypeB+" : entity work.FileWriterFIFO\n"
    string_mem += "    generic map (\n"
    string_mem += "      FILE_NAME".ljust(str_len)+"=> FILE_OUT_"+mtypeB+"&memory_enum_to_string(var)&outputFileNameEnding,\n"
    string_mem += "      FIFO_WIDTH".ljust(str_len)+"=> " + mtypeB.split("_")[1] + "\n"
    string_mem += "    )\n"
    string_mem += "    port map (\n"
    string_mem += "      CLK".ljust(str_len)+"=> CLK,\n"
    string_mem += "      DONE".ljust(str_len)+"=> "+proc+"_DONE,\n"
    string_mem += "      WRITE_EN".ljust(str_len)+"=> "+mtypeB+"_stream_A_write(var),\n"
    string_mem += "      FULL_NEG".ljust(str_len)+"=> "+mtypeB+"_stream_A_full_neg(var),\n"
    string_mem += "      DATA".ljust(str_len)+"=> "+mtypeB+"_stream_AV_din(var)\n"
    string_mem += "    );\n"
    string_mem += "  end generate "+mtypeB+"_loop;\n\n"

    return string_mem 

def writeProcCombination(module, str_ctrl_func, str_ports):
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
    if "TE_" in lut.inst:
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

    int_ctrl_func =  "  LATCH_"+mtype+": entity work.CreateStartSignal\n"
    int_ctrl_func += "    port map (\n"
    int_ctrl_func += "      clk   => clk,\n"
    int_ctrl_func += "      reset => reset,\n"
    int_ctrl_func += "      done  => "+mtype+"_done,\n"
    int_ctrl_func += "      start => "+mtype_down+"_start\n"
    int_ctrl_func += "  );\n\n"

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

def writeProcMemoryLHSPorts(argname,mem,combined=False):
    """
    # Processing module port assignment: outputs to memories
    """
    string_mem_ports = ""
    if combined and ("memoriesTEO" in argname or "memoryME" in argname) :
        string_mem_ports += "      "+argname+"_dataarray_0_data_V_ce0       => open,\n"
        string_mem_ports += "      "+argname+"_dataarray_0_data_V_we0       => "
        string_mem_ports += mem.keyName()+"_mem_A_wea("+mem.var()+"),\n"
        string_mem_ports += "      "+argname+"_dataarray_0_data_V_address0  => "
        string_mem_ports += mem.keyName()+"_mem_AV_writeaddr("+mem.var()+"),\n"
        string_mem_ports += "      "+argname+"_dataarray_0_data_V_d0        => "
        string_mem_ports += mem.keyName()+"_mem_AV_din("+mem.var()+"),\n"
    else:
        string_mem_ports += "      "+argname+"_dataarray_data_V_ce0       => open,\n"
        string_mem_ports += "      "+argname+"_dataarray_data_V_we0       => "
        string_mem_ports += mem.keyName()+"_mem_A_wea("+mem.var()+"),\n"
        string_mem_ports += "      "+argname+"_dataarray_data_V_address0  => "
        string_mem_ports += mem.keyName()+"_mem_AV_writeaddr("+mem.var()+"),\n"
        string_mem_ports += "      "+argname+"_dataarray_data_V_d0        => "
        string_mem_ports += mem.keyName()+"_mem_AV_din("+mem.var()+"),\n"


    return string_mem_ports

def writeProcMemoryRHSPorts(argname,mem,portindex=0,combined=False):
    """
    # Processing module port assignment: inputs from memories
    """
    if combined and (mem.mtype == "VMStubsTEOuter" or mem.mtype == "VMStubsME"): #FIXME hack for combined modules
        string_mem_ports = ""
        nmem = 5
        if mem.mtype == "VMStubsME" :
            nmem = 4
        for instance in range(0,nmem):
            string_mem_ports += "      "+argname+"_dataarray_"+str(instance)+"_data_V_ce"+str(portindex)+"       => "
            string_mem_ports += mem.keyName()+"_mem_AA_enb("+mem.var()+")("+str(instance)+"),\n"
            string_mem_ports += "      "+argname+"_dataarray_"+str(instance)+"_data_V_address"+str(portindex)+"  => "
            string_mem_ports += mem.keyName()+"_mem_AAV_readaddr("+mem.var()+")("+str(instance)+"),\n"
            string_mem_ports += "      "+argname+"_dataarray_"+str(instance)+"_data_V_q"+str(portindex)+"        => "
            string_mem_ports += mem.keyName()+"_mem_AAV_dout("+mem.var()+")("+str(instance)+"),\n"
    else:
        string_mem_ports = ""
        string_mem_ports += "      "+argname+"_dataarray_data_V_ce"+str(portindex)+"       => "
        string_mem_ports += mem.keyName()+"_mem_A_enb("+mem.var()+"),\n"
        string_mem_ports += "      "+argname+"_dataarray_data_V_address"+str(portindex)+"  => "
        string_mem_ports += mem.keyName()+"_mem_AV_readaddr("+mem.var()+"),\n"
        string_mem_ports += "      "+argname+"_dataarray_data_V_q"+str(portindex)+"        => "
        string_mem_ports += mem.keyName()+"_mem_AV_dout("+mem.var()+"),\n"

    if mem.has_numEntries_out and portindex == 0:
        #First branch is for combined modules
        if combined:
            if mem.mtype == "VMStubsTEOuter" :
                for i in range(0,2**mem.bxbitwidth):
                    if mem.is_binned:
                        for j in range(0,8):
                            string_mem_ports += "      "+argname+"_binmask8_"+str(i)+"_V_"+str(j)+"     => ("
                            for k in range(0, 8) :
                                if k != 0 :
                                    string_mem_ports += ", "
                                string_mem_ports += mem.keyName()+"_mem_AAV_dout_mask("+mem.var()+")("+str(i)+")("+str(j+(7-k)*8)+")"
                            string_mem_ports += "),\n"
                        for j in range(0,8):
                            string_mem_ports += "      "+argname+"_nentries8_"+str(i)+"_V_"+str(j)+"     => ("
                            for k in range(0, 8) :
                                if k != 0 :
                                    string_mem_ports += ", "
                                string_mem_ports += mem.keyName()+"_mem_AAAV_dout_nent("+mem.var()+")("+str(i)+")("+str(j+(7-k)*8)+")"
                            string_mem_ports += "),\n"
                    else:
                        string_mem_ports += "      "+argname+"_nentries_"+str(i)+"_V               => "
                        string_mem_ports += mem.keyName()+"_mem_AAV_dout_nent("+mem.var()+")("+str(i)+"),\n"
            elif mem.mtype == "VMStubsME" :
                if mem.is_binned:
                    for i in range(0,2**mem.bxbitwidth):
                        for j in range(0,8):
                            string_mem_ports += "      "+argname+"_binmask8_"+str(i)+"_V_"+str(j)+"     => ("
                            for k in range(0, 8) :
                                if k != 0 :
                                    string_mem_ports += ", "
                                string_mem_ports += mem.keyName()+"_mem_AAV_dout_mask("+mem.var()+")("+str(i)+")("+str(j+(7-k)*8)+")"
                            string_mem_ports += "),\n"
                    string_mem_ports += "      "+argname+"_nentries8a_v_q0              => "+mem.keyName()+"_mem_AV_dout_nentA("+mem.var()+"),\n"
                    string_mem_ports += "      "+argname+"_nentries8a_v_address0        => "+mem.keyName()+"_mem_AV_addr_nentA("+mem.var()+"),\n"
                    string_mem_ports += "      "+argname+"_nentries8a_v_ce0             => "+mem.keyName()+"_mem_A_enb_nentA("+mem.var()+"),\n"
                    string_mem_ports += "      "+argname+"_nentries8b_v_q0              => "+mem.keyName()+"_mem_AV_dout_nentB("+mem.var()+"),\n"
                    string_mem_ports += "      "+argname+"_nentries8b_v_address0        => "+mem.keyName()+"_mem_AV_addr_nentB("+mem.var()+"),\n"
                    string_mem_ports += "      "+argname+"_nentries8b_v_ce0             => "+mem.keyName()+"_mem_A_enb_nentB("+mem.var()+"),\n"
                else:
                    for i in range(0,2**mem.bxbitwidth): 
                        string_mem_ports += "      "+argname+"_nentries_"+str(i)+"_V               => "
                        string_mem_ports += mem.keyName()+"_mem_AAV_dout_nent("+mem.var()+")("+str(i)+"),\n"
        else:
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

def writeLUTParameters(argname, lut, innerPS, outerPS):
    parameterlist = ""
    width = 0
    if "in" in argname:
        width = 1
        depth = 8 if innerPS else 9
        parameterlist += "      lut_file  => \"LUTs/"+lut.inst+"_stubptinnercut.tab\",\n"
    elif "out" in argname:
        width = 1
        depth = 8 if outerPS else 9
        parameterlist += "      lut_file  => \"LUTs/"+lut.inst+"_stubptoutercut.tab\",\n"
    parameterlist += "      lut_width => "+str(width)+",\n"
    parameterlist += "      lut_depth => "+str(2**depth)+"\n"
    
    return parameterlist

def writeLUTWires(argname, lut, innerPS, outerPS):
    wirelist = ""
    argname = argname.split("[")[0]
    depth = 0
    width = 0
    if "in" in argname:
        depth = 8 if innerPS else 9
        width = 1
    elif "out" in argname:
        depth = 8 if outerPS else 9
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
    # 32 bits per phibin word: 8 bits per layer, where each bit represent if a 
    # memories is used. First memory represents phi region A etc.
    """
    phiBinWord = ""

    # Loop through the layers and write the memories used as 8 bits to phiBinWord
    for layer in memoriesPerLayer:
        phiBinWord = memoriesPerLayer[layer] + phiBinWord
    
    phiBinWord = phiBinWord.zfill(32) # Pad with zeros so it contains 32 bits

    string_phibin_port = "      hPhBnWord_V => \""+phiBinWord+"\",\n"

    return string_phibin_port
