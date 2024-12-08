from builtins import range
from TrackletGraph import MemModule, ProcModule, MemTypeInfoByKey
def getVMStubNCopy(memmod):

    mem = memmod.inst;
    if "VMSTE" in mem:
        proc = memmod.downstreams[0].inst;
        if "L1L2" in proc:
            return 5;
        if "L2L3" in proc:
            return 2;
        if "L3L4" in proc:
            return 5;
        if "L5L6" in proc:
            return 3;
        if "D1D2" in proc:
            return 3;
        if "D3D4" in proc:
            return 2;
        if "L1D1" in proc:
            return 3;
        if "L2D1" in proc:
            return 2;
        return "Error no match for "+proc
    elif "VMSME" in mem:
        if "L1" in mem:
            return 4;
        if "L2" in mem:
            return 4;
        if "L3" in mem:
            return 4;
        if "L4" in mem:
            return 4;
        if "L5" in mem:
            return 4;
        if "L6" in mem:
            return 4;
        if "D1" in mem:
            return 4;
        if "D2" in mem:
            return 4;
        if "D3" in mem:
            return 4;
        if "D4" in mem:
            return 4;
        if "D5" in mem:
            return 4;
        return "Error no match for "+mem
    else:
        return "Wrong memory module:"+mem

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

def writeTBMemoryReadInstance(mtypeB, memDict, bxbitwidth, is_initial, is_binned, split):
    """
    # VHDL test-bench
    # Reads memory text files
    """
    str_len = 22 # length of string for formatting purposes

    string_mem = ""

    memList = memDict[mtypeB]

    for memMod in memList :

        mem = memMod.inst

        if split == 2 and "in" not in mem:
            continue
    
        if "DL" in mtypeB and "AS" not in mtypeB: # Special case for DTC links that reads from FIFOs
            string_mem += "    read" + mem + " : entity work.FileReaderFIFO\n"
            string_mem += "  generic map (\n"
            memtmp = mem.replace("twoS","2S")
            string_mem += "      FILE_NAME".ljust(str_len) + "=> FILE_IN_"+mtypeB+"&\""+ memtmp + "\"&inputFileNameEnding,\n"
            string_mem += "      DELAY".ljust(str_len) + "=> " + mtypeB.split("_")[0] + "_DELAY*MAX_ENTRIES,\n"
            string_mem += "      FIFO_WIDTH".ljust(str_len) + "=> " + mtypeB.split("_")[1] + ",\n"
            string_mem += "      DEBUG".ljust(str_len) + "=> true,\n"
            string_mem += "      FILE_NAME_DEBUG".ljust(str_len) + "=> FILE_OUT_DL_debug&\""+ memtmp + "\"&debugFileNameEnding\n"
            string_mem += "    )\n"
            string_mem += "    port map (\n"
            string_mem += "      CLK".ljust(str_len) + "=> CLK,\n"
            string_mem += "      READ_EN".ljust(str_len) + "=> " + mem + "_link_read,\n"
            string_mem += "      DATA".ljust(str_len) + "=> " + mem + "_link_AV_dout,\n"
            string_mem += "      START".ljust(str_len) + "=> " + ("START_" + mem + ",\n" if is_initial else "open,\n")
            string_mem += "      EMPTY_NEG".ljust(str_len) + "=> " + mem + "_link_empty_neg\n"
        else:             # Standard case for BRAM 
            string_mem += "    read" + mem + " : entity work.FileReader\n"
            string_mem += "  generic map (\n"
            #FIXME Hack for reading the AS input memories
            memtmp = mem.replace("in","n1")
            if "MPAR" in mem :
                memtmp = memtmp.replace("n1","")
            #    memtmp = "T"+mem[1:10]
            string_mem += "      FILE_NAME".ljust(str_len) + "=> FILE_IN_" + mtypeB+"&\""+ memtmp + "\"&inputFileNameEnding,\n"
            string_mem += "      DELAY".ljust(str_len) + "=> " + mtypeB.split("_")[0] + "_DELAY*MAX_ENTRIES,\n"
            string_mem += "      RAM_WIDTH".ljust(str_len) + "=> " + mtypeB.split("_")[1] + ",\n"
            string_mem += "      NUM_PAGES".ljust(str_len) + "=> " + str(2**bxbitwidth) + ",\n"
            if "MPROJ" in mem:
                string_mem += "      PAGE_LENGTH".ljust(str_len) + "=> 64,\n"
            if "MPAR" in mem or "MPROJ" in mem:
                string_mem += "      NUM_TPAGES".ljust(str_len) + "=> 4,\n"
            if "MPAR" in mem :
                string_mem += "      NUM_BINS".ljust(str_len) + "=> 4,\n"
            else:
                string_mem += "      NUM_BINS".ljust(str_len) + "=> 8,\n" if is_binned else "" # FIX ME 16 for MEDISK
            string_mem += "      DEBUG".ljust(str_len) + "=> true,\n"
            string_mem += "      FILE_NAME_DEBUG".ljust(str_len) + "=> FILE_OUT_" + mtypeB+"&\""+ mem + "_debug\"&debugFileNameEnding\n"
            string_mem += "    )\n"
            string_mem += "    port map (\n"
            string_mem += "      CLK".ljust(str_len) + "=> CLK,\n"
            string_mem += "      ADDR".ljust(str_len) + "=> " + mem + "_writeaddr,\n"
            string_mem += "      DATA".ljust(str_len) + "=> " + mem + "_din,\n"
            string_mem += "      START".ljust(str_len) + "=> START_" + mem + ",\n" if is_initial else "      START => open,\n"
            string_mem += "      WRITE_EN".ljust(str_len) + "=> " + mem + "_wea\n"

        string_mem += "    );\n"

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

        if memInfo.isFIFO: 
            tName = "t_"+mtypeB+"_1b"
            ss += "  subtype "+tName+" is std_logic;\n"
            tName = "t_"+mtypeB+"_DATA"
            ss += "  subtype "+tName+" is std_logic_vector("+str(bitwidth-1)+" downto 0);\n"
        else:

            if memInfo.is_binned:
                ncopy = 4
                if memInfo.downstream_mtype_short == "TP" :
                    ncopy = 5
                tName = "t_"+mtypeB+"_1b"
                ss += "  subtype "+tName+" is std_logic;\n" 
                tName = "t_"+mtypeB+"_A1b"
                ss += "  subtype "+tName+" is std_logic_vector("+str(ncopy-1)+" downto 0);\n" 
                tName = "t_"+mtypeB+"_ADDR"
                ss += "  subtype "+tName+" is std_logic_vector("+str(9+memInfo.bxbitwidth)+" downto 0);\n" 
                tName = "t_"+mtypeB+"_ADDRDISK"
                ss += "  subtype "+tName+" is std_logic_vector("+str(10+memInfo.bxbitwidth)+" downto 0);\n" 
                tName = "t_"+mtypeB+"_AADDR"
                ss += "  subtype "+tName+" is t_arr"+str(ncopy)+"_"+str(10+memInfo.bxbitwidth)+"b;\n"
                tName = "t_"+mtypeB+"_AADDRDISK"
                ss += "  subtype "+tName+" is t_arr"+str(ncopy)+"_"+str(11+memInfo.bxbitwidth)+"b;\n"
                tName = "t_"+mtypeB+"_DATA"
                ss += "  subtype "+tName+" is std_logic_vector("+str(bitwidth-1)+" downto 0);\n"  
                tName = "t_"+mtypeB+"_ADATA"
                ss += "  subtype "+tName+" is t_arr"+str(ncopy)+"_"+str(bitwidth)+"b;\n"  
            else:
                tName = "t_"+mtypeB+"_1b"
                ss += "  subtype "+tName+" is std_logic;\n"
                if "MPAR" in mtypeB:
                    tName = "t_"+mtypeB+"_ADDR"
                    ss += "  subtype "+tName+" is std_logic_vector("+str(8+memInfo.bxbitwidth)+" downto 0);\n" 
                elif "MPROJ" in mtypeB:
                    tName = "t_"+mtypeB+"_ADDR"
                    ss += "  subtype "+tName+" is std_logic_vector("+str(7+memInfo.bxbitwidth)+" downto 0);\n" 
                else:
                    tName = "t_"+mtypeB+"_ADDR"
                    ss += "  subtype "+tName+" is std_logic_vector("+str(6+memInfo.bxbitwidth)+" downto 0);\n" 
                tName = "t_"+mtypeB+"_DATA"
                ss += "  subtype "+tName+" is std_logic_vector("+str(bitwidth-1)+" downto 0);\n" 


            if memInfo.is_binned:
                varStr = "_64_4b"
            else:
                if "MPROJ" in tName:
                    varStr = "_6b"
                else:
                    varStr = "_7b"
            if "MPROJ" in tName:
                tName = "t_"+mtypeB+"_MASK"
                ss += "  subtype "+tName+" is t_arr"+str(num_pages)+"_4b;\n"
            tName = "t_"+mtypeB+"_NENT"
            if memInfo.is_binned:
                ss += "  subtype "+tName+" is std_logic_vector(63 downto 0);\n"
                tName = "t_"+mtypeB+"_NENTADDR"
                nentaddrbits = "3"
                ss += "  subtype "+tName+" is std_logic_vector("+nentaddrbits+" downto 0);\n"
                tName = "t_"+mtypeB+"_NENTADDRDISK"
                nentaddrbits = "4"
                ss += "  subtype "+tName+" is std_logic_vector("+nentaddrbits+" downto 0);\n"
            else:
                #FIXME
                tpages = 1
                if "MPROJ" in tName or "MPAR" in tName:
                    tpages = 4
                ss += "  subtype "+tName+" is t_arr"+str(num_pages*tpages)+varStr+";\n"
            if memInfo.is_binned:
                varStr = "_64_1b"
                tName = "t_"+mtypeB+"_MASK"
                ss += "  subtype "+tName+" is t_arr"+str(num_pages)+varStr+";\n"
                tName = "t_"+mtypeB+"_MASK_"+str(num_pages)
                ss += "  subtype "+tName+" is std_logic_vector("+str(num_pages)+"*64-1 downto 0);\n"
                varStr = "_128_1b"
                tName = "t_"+mtypeB+"_MASKDISK"
                ss += "  subtype "+tName+" is t_arr"+str(num_pages)+varStr+";\n"
                tName = "t_"+mtypeB+"_MASKDISK_"+str(num_pages)
                ss += "  subtype "+tName+" is std_logic_vector("+str(num_pages)+"*128-1 downto 0);\n"
                vmstubwidth = memInfo.bitwidth
                if "VMSTE" in mtypeB:
                    ss += "  subtype "+tName+"_2 is std_logic_vector(2*64-1 downto 0);\n" 
                    tName = "t_"+mtypeB+"_DATA"
                    ss += "  subtype "+tName+"_2 is std_logic_vector(2*"+str(vmstubwidth)+"-1 downto 0);\n" 
                    ss += "  subtype "+tName+"_3 is std_logic_vector(3*"+str(vmstubwidth)+"-1 downto 0);\n" 
                    ss += "  subtype "+tName+"_4 is std_logic_vector(4*"+str(vmstubwidth)+"-1 downto 0);\n" 
                    ss += "  subtype "+tName+"_5 is std_logic_vector(5*"+str(vmstubwidth)+"-1 downto 0);\n" 
                if "VMSME" in mtypeB:
                    ss += "  subtype "+tName+"_4 is std_logic_vector(4*64-1 downto 0);\n" 
                    tName = "t_"+mtypeB+"_DATA"
                    ss += "  subtype "+tName+"_2 is std_logic_vector(2*"+str(vmstubwidth)+"-1 downto 0);\n" 
                    ss += "  subtype "+tName+"_3 is std_logic_vector(3*"+str(vmstubwidth)+"-1 downto 0);\n" 
                    ss += "  subtype "+tName+"_4 is std_logic_vector(4*"+str(vmstubwidth)+"-1 downto 0);\n" 
                    
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

def writeTopLevelMemoryType(mtypeB, memList, memInfo, extraports, delay = 0, split = False, MPARdict = 0):
    """
    # Declaration of memories of type "mtype" (e.g. TPROJ) & associated wires
    # Inputs:
    #   mTypeB  = memory type & its bits width (TPROJ_58 etc.)
    #   memList = list of memories of given type & bit width
    #   memInfo = Info about each memory type (in MemTypeInfoByKey class)
    """

    wirelist = ""
    mem_str = ""
    mtype = mtypeB.split("_")[0]
    bitwidth = mtypeB.split("_")[1]

    # Assume all memories of given type have same bxbitwidth.
    bxbitwidth =  memInfo.bxbitwidth
    num_pages = 2**bxbitwidth

    interface = int(memInfo.is_final) - int(memInfo.is_initial)

    first_merge_streamer = True

    for memmod in memList:

        nmem = 0

        mem=memmod.inst

        disk = ""
        if memInfo.is_binned:
            nmem = getVMStubNCopy(memmod)
            if "VMSME_D" in mem:
                disk="DISK"

        if interface == 1:
            assert memInfo.upstream_mtype_short != ""
            sync_signal = memmod.upstreams[0].inst+"_done"
        else:
            assert memInfo.downstream_mtype_short != ""
            sync_signal = memmod.downstreams[0].inst+"_start"

        parameterlist = ""
        portlist = ""
        delay_parameterlist = ""
        delay_parameterlist_0 = ""
        delay2_parameterlist = ""
        delay_portlist_0 = ""
        delay_portlist = ""
        delay2_portlist = ""
        #FIXME
        if "MPAR" in mem and not "in" in mem:
            interface = 0
            extraports = False
        if "AS" in mem and not "in" in mem and split == 2:
            interface = 0
            extraports = False
        merge_parameterlist = ""
        merge_portlist = ""
        # Write wires
        if delay > 0:
            if not memInfo.is_binned:
                wirelist += "  signal "+mem+"_bx                   : "
                wirelist += "std_logic_vector(2 downto 0);\n"
            wirelist += "  signal "+mem+"_start                   : "
            wirelist += "std_logic;\n"
            wirelist += "  signal "+mem+"_wea_delay_0          : "
            wirelist += "t_"+mtypeB+"_1b;\n"
            wirelist += "  signal "+mem+"_writeaddr_delay_0   : "
            wirelist += "t_"+mtypeB+"_ADDR"+disk+";\n"
            wirelist += "  signal "+mem+"_din_delay_0         : "
            wirelist += "t_"+mtypeB+"_DATA;\n"
            wirelist += "  signal "+mem+"_wea_delay          : "
            wirelist += "t_"+mtypeB+"_1b;\n"
            wirelist += "  signal "+mem+"_writeaddr_delay   : "
            wirelist += "t_"+mtypeB+"_ADDR"+disk+";\n"
            wirelist += "  signal "+mem+"_din_delay         : "
            wirelist += "t_"+mtypeB+"_DATA;\n"
            if (interface != -1 and not extraports) or (split == 1 and "TPAR" in mem):
                if "TPAR" in mem:
                    wirelist += "  signal "+mem+"_dummy   : std_logic_vector(1 downto 0);\n"
                wirelist += "  signal "+mem+"_wea          : "
                wirelist += "t_"+mtypeB+"_1b;\n"
                wirelist += "  signal "+mem+"_writeaddr   : "
                wirelist += "t_"+mtypeB+"_ADDR"+disk+";\n"
                wirelist += "  signal "+mem+"_din         : "
                wirelist += "t_"+mtypeB+"_DATA;\n"
        if not (interface == 1 and not split == 1):
            if memInfo.is_binned :
                wirelist += "  signal "+mem+"_A_enb         : "
                wirelist += "t_"+mtypeB+"_A1b;\n"
                wirelist += "  signal "+mem+"_AV_readaddr   : "
                wirelist += "t_"+mtypeB+"_AADDR"+disk+";\n"
                wirelist += "  signal "+mem+"_AV_dout       : "
                wirelist += "t_"+mtypeB+"_ADATA;\n"
            else:
                wirelist += "  signal "+mem+"_enb          : "
                wirelist += "t_"+mtypeB+"_1b := '1';\n" #FIXME send a read enable from merge module
                wirelist += "  signal "+mem+"_V_readaddr    : "
                wirelist += "t_"+mtypeB+"_ADDR"+disk+";\n"
                wirelist += "  signal "+mem+"_V_dout        : "
                wirelist += "t_"+mtypeB+"_DATA;\n"
                #FIXME this is a hack
                if "MPAR" in mem and "in" in mem :
                    wirelist += "  signal "+mem+"_V_tpar        : "
                    wirelist += "t_"+mtypeB+"_DATA;\n"
                    wirelist += "  signal "+mem+"_valid        : "
                    wirelist += "STD_LOGIC;\n"
                    wirelist += "  signal "+mem+"_trackletindex        : "
                    wirelist += "STD_LOGIC_VECTOR(8 downto 0);\n"
                    wirelist += "  signal "+mem+"_AV_dout_nent        : "
                    wirelist += "t_arr_7b(0 to 31);\n"
                #FIXME this is a hack
                if "AS" in mem and "in" in mem :
                    wirelist += "  signal "+mem+"_V_as        : "
                    wirelist += "t_"+mtypeB+"_DATA;\n"
                    wirelist += "  signal "+mem+"_valid        : "
                    wirelist += "STD_LOGIC;\n"
                    wirelist += "  signal "+mem+"_index        : "
                    wirelist += "STD_LOGIC_VECTOR(31 downto 0);\n"
            if memInfo.has_numEntries_out or (split == 1 and "AS" in mem):
                if memInfo.is_binned:
                    disk=""
                    if "VMSME_D" in mem:
                        disk="DISK"
                    wirelist += "  signal "+mem+"_AV_dout_mask : "
                    wirelist += "t_"+mtypeB+"_MASK"+disk+"; -- (#page)(#bin)\n"
                    wirelist += "  signal "+mem+"_enb_nent         : "
                    wirelist += "t_"+mtypeB+"_1b;\n"
                    wirelist += "  signal "+mem+"_V_addr_nent   : "
                    wirelist += "t_"+mtypeB+"_NENTADDR"+disk+";\n"
                    wirelist += "  signal "+mem+"_AV_dout_nent : "
                    wirelist += "t_"+mtypeB+"_NENT; -- (#page)(#bin)\n"
                    wirelist += "  signal "+mem+"_V_datatmp : "
                    wirelist += "t_"+mtypeB+"_DATA_"+str(nmem)+";\n"
                    wirelist += "  signal "+mem+"_V_masktmp : "
                    wirelist += "t_"+mtypeB+"_MASK"+disk+"_"+str(num_pages)+";\n"
                else:
                    wirelist += "  signal "+mem+"_AV_dout_nent  : "
                    wirelist += "t_"+mtypeB+"_NENT; -- (#page)\n"
                    if "MPROJ" in mem:
                        wirelist += "  signal "+mem+"_AV_dout_mask  : "
                        wirelist += "t_"+mtypeB+"_MASK;\n"
        else :
            if memInfo.is_binned:
                disk=""
                if "VMSME_D" in mem:
                    disk="DISK"
                wirelist += "  signal "+mem+"_V_datatmp : "
                wirelist += "t_"+mtypeB+"_DATA_"+str(nmem)+";\n"
                wirelist += "  signal "+mem+"_V_masktmp : "
                wirelist += "t_"+mtypeB+"_MASK"+disk+"_"+str(num_pages)+";\n"

        # Write parameters
        parameterlist += "        RAM_WIDTH       => "+bitwidth+",\n"
        parameterlist += "        NUM_PAGES       => "+str(num_pages)+",\n"
        if "MPROJ" in mem:
            parameterlist += "        PAGE_LENGTH       => 64,\n"
        if "MPROJ" in mem or "MPAR" in mem:
            parameterlist += "        NUM_TPAGES       => 4,\n"
        parameterlist += "        INIT_FILE       => \"\",\n"
        parameterlist += "        INIT_HEX        => true,\n"
        parameterlist += "        RAM_PERFORMANCE => \"HIGH_PERFORMANCE\",\n"
        parameterlist += "        NAME            => \""+mem+"\",\n"
        if delay > 0:
            delay2_parameterlist +="        DELAY           => " + str(delay*2) +",\n"
            delay_parameterlist +="        DELAY           => " + str(delay) +",\n"
            delay_parameterlist_0 +="        DELAY           => " + str(delay+1) +",\n"
            #enable to use non-default delay value
            if "MPROJ" in mem:
                #special case for the merged projections
                delay_parameterlist +="        PAGE_LENGTH       => 64,\n"
                delay_parameterlist_0 +="        PAGE_LENGTH       => 64,\n"
            if "MPAR" in mem or "MPROJ" in mem:
                #special case for the merged memories
                delay_parameterlist +="        NUM_PAGES       => "+str(4*num_pages)+",\n"
                delay_parameterlist_0 +="        NUM_PAGES       => "+str(4*num_pages)+",\n"
            else:
                delay_parameterlist +="        NUM_PAGES       => "+str(num_pages)+",\n"
                delay_parameterlist_0 +="        NUM_PAGES       => "+str(num_pages)+",\n"
            if memInfo.is_binned:
                disk=""
                if "VMSME_D" in mem:
                    disk = "*2"
                delay_parameterlist +="        RAM_DEPTH       => "+str(num_pages)+disk+"*PAGE_LENGTH_CM,\n"
                delay_parameterlist_0 +="        RAM_DEPTH       => "+str(num_pages)+disk+"*PAGE_LENGTH_CM,\n"
            delay_parameterlist +="        RAM_WIDTH       => "+bitwidth+",\n"
            delay_parameterlist_0 +="        RAM_WIDTH       => "+bitwidth+",\n"

        ncopy = getVMStubNCopy(memmod);


        if "VMSTE_" in mem: 
            parameterlist += "        ADDR_WIDTH      => 4,\n"
            parameterlist += "        NUM_PHI_BINS    => 8,\n"
            parameterlist += "        NUM_RZ_BINS     => 8,\n"
            parameterlist += "        NUM_COPY        => "+str(ncopy)+"\n"
        if "VMSME_L" in mem: # VMSME memories have 16 bins in the disks
            parameterlist += "        ADDR_WIDTH      => 4,\n"
            parameterlist += "        NUM_PHI_BINS    => 8,\n"
            parameterlist += "        NUM_RZ_BINS     => 8,\n"
            parameterlist += "        NUM_COPY        => "+str(ncopy)+"\n"
        if "VMSME_D" in mem: # VMSME memories have 16 bins in the disks
            parameterlist += "        ADDR_WIDTH      => 4,\n"
            parameterlist += "        NUM_PHI_BINS    => 8,\n"
            parameterlist += "        NUM_RZ_BINS     => 16,\n"
            parameterlist += "        NUM_COPY        => "+str(ncopy)+"\n"
        if "TPAR" in mem:
            parameterlist += "        MEM_TYPE        => \"ultra\",\n"

            #FIXME implement delay for disks
        # Write ports
        portlist += "        clka      => clk,\n"
        if delay > 0:
            portlist += "        wea       => "+mem+"_wea_delay,\n"
            portlist += "        addra     => "+mem+"_writeaddr_delay,\n"
            portlist += "        dina      => "+mem+"_din_delay,\n"
        else:
            portlist += "        wea       => "+mem+"_wea,\n"
            portlist += "        addra     => "+mem+"_writeaddr,\n"
            portlist += "        dina      => "+mem+"_din,\n"
        if delay > 0:
            delay2_portlist += "        clk      => clk,\n"
            delay2_portlist += "        reset    => reset,\n"
            #FIXME
            if not "in" in mem :
                if ("VMSMER" in memmod.upstreams[0].mtype_short() or "PC" in memmod.upstreams[0].mtype_short()) and split == 2:
                    delay2_portlist += "        done   => PC_done,\n"
                    delay2_portlist += "        bx_out   => PC_bx_out,\n"
                else:
                    delay2_portlist += "        done   => "+memmod.upstreams[0].mtype_short()+"_done,\n"
                    delay2_portlist += "        bx_out   => "+memmod.upstreams[0].mtype_short()+"_bx_out,\n"
            delay2_portlist += "        bx       => "+mem+"_bx,\n"
            delay2_portlist += "        start    => "+mem+"_start,\n"
            delay_portlist_0 += "        clk      => clk,\n"
            delay_portlist_0 += "        wea       => "+mem+"_wea,\n"
            delay_portlist_0 += "        addra     => "+mem+"_writeaddr,\n"
            delay_portlist_0 += "        dina      => "+mem+"_din,\n"
            delay_portlist_0 += "        wea_out       => "+mem+"_wea_delay_0,\n"
            delay_portlist_0 += "        addra_out     => "+mem+"_writeaddr_delay_0,\n"
            delay_portlist_0 += "        dina_out      => "+mem+"_din_delay_0,\n"
            delay_portlist += "        clk      => clk,\n"
            delay_portlist += "        wea       => "+mem+"_wea_delay_0,\n"
            delay_portlist += "        addra     => "+mem+"_writeaddr_delay_0,\n"
            delay_portlist += "        dina      => "+mem+"_din_delay_0,\n"
            delay_portlist += "        wea_out       => "+mem+"_wea_delay,\n"
            delay_portlist += "        addra_out     => "+mem+"_writeaddr_delay,\n"
            delay_portlist += "        dina_out      => "+mem+"_din_delay,\n"
        # add merge_stream modules if split and TPAR or AS
        if "TPAR" in mem and split == 1:
            addrwidth = 10
            ramwidth = memInfo.bitwidth
            numpages = 8
            seed = mem.split("_")[1][:-1]
            iTC = mem.split("_")[1][-1]
            for PCGroup in MPARdict[seed]:
                if iTC == PCGroup[0]:
                    numInputs = len(PCGroup)
                    merge_parameterlist += "        RAM_WIDTH => "+str(ramwidth)+",\n"
                    merge_parameterlist += "        NUM_PAGES => "+str(numpages)+",\n"
                    merge_parameterlist += "        NUM_INPUTS => "+str(numInputs)+",\n"
                    merge_parameterlist += "        NUM_EXTRA_BITS => 2,\n"
                    merge_portlist += "        bx_in => TP_bx_out,\n"
                    merge_portlist += "        bx_in_vld => TP_bx_out_vld,\n"
                    merge_portlist += "        rst => '0',\n"
                    merge_portlist += "        clk => clk,\n"
                    merge_portlist += "        enb_arr => open,\n"
                    #This will make output for first stream_merge module (is there a less hacky way?)
                    if first_merge_streamer: 
                      merge_portlist += "        bx_out => TP_bx_out_merged,\n"
                      first_merge_streamer = False
                    else:
                      merge_portlist += "        bx_out => open,\n"
                    merge_portlist += "        merged_dout => MPAR_"+seed+PCGroup+"_stream_V_dout,\n"
                    for i in range(4):  merge_portlist += "        din"+str(i)+"=>TPAR_"+seed+PCGroup[i%numInputs]+"_V_dout,\n"
                    for i in range(4):  merge_portlist += "        nent"+str(i)+"=>TPAR_"+seed+PCGroup[i%numInputs]+"_AV_dout_nent,\n"
                    for i in range(numInputs):  merge_portlist += "        addr_arr("+str(((i+1)*addrwidth)-1)+" downto "+ str(i*addrwidth)+ ")=>TPAR_"+seed+PCGroup[i%numInputs]+"_V_readaddr,\n"
                    mem_str += "    MERGE_STREAM_TPAR"+seed+PCGroup+" : entity work.tf_merge_streamer\n"
                    mem_str += "      generic map (\n"+merge_parameterlist.rstrip(",\n")+"\n      )\n"
                    mem_str += "      port map (\n"+merge_portlist.rstrip(",\n")+"\n      );\n\n"

        elif "AS" in mem and "n1" in mem and split == 1:
            addrwidth = 10
            ramwidth = memInfo.bitwidth
            numpages = 8
            numInputs = 1
            merge_parameterlist += "        RAM_WIDTH => "+str(ramwidth)+",\n"
            merge_parameterlist += "        NUM_PAGES => "+str(numpages)+",\n"
            merge_parameterlist += "        NUM_INPUTS => "+str(numInputs)+",\n"
            merge_parameterlist += "        NUM_EXTRA_BITS => 0,\n"
            merge_portlist += "        bx_in => TP_bx_out,\n"
            merge_portlist += "        bx_in_vld => TP_bx_out_vld,\n"
            merge_portlist += "        rst => '0',\n"
            merge_portlist += "        clk => clk,\n"
            merge_portlist += "        enb_arr => open,\n"
            merge_portlist += "        bx_out => open,\n"
            merge_portlist += "        merged_dout => "+mem+"_stream_V_dout,\n"
            for i in range(4):  merge_portlist += "        din"+str(i)+"=>" +mem+"_V_dout,\n"
            for i in range(4):  merge_portlist += "        nent"+str(i)+"=>" +mem+"_AV_dout_nent,\n"
            for i in range(numInputs):  merge_portlist += "        addr_arr("+str(((i+1)*addrwidth)-1)+" downto "+ str(i*addrwidth)+ ")=>"+mem+"_V_readaddr,\n"
            mem_str += "    STREAM_"+mem+" : entity work.tf_merge_streamer\n"
            mem_str += "      generic map (\n"+merge_parameterlist.rstrip(",\n")+"\n      )\n"
            mem_str += "      port map (\n"+merge_portlist.rstrip(",\n")+"\n      );\n\n"
        portlist += "        clkb      => clk,\n"
        portlist += "        rstb      => '0',\n"
        portlist += "        regceb    => '1',\n"
        if not memInfo.is_binned :
            portlist += "        enb       => "+mem+"_enb,\n"
            portlist += "        addrb     => "+mem+"_V_readaddr,\n"
            portlist += "        doutb     => "+mem+"_V_dout,\n"
        if ("AS" in mem or "MPAR" in mem) and "in" in mem:
            portlist += "        sync_nent => PC_start,\n"
        elif "MPAR" in mem and "in" not in mem:
            portlist += "        sync_nent => "+mem+"_start,\n"
        elif "AS" in mem and "n1" in mem and split == 1:
            portlist += "        sync_nent => TP_L1L2A_start,\n"
        elif "TPAR" in mem and split == 1:
            portlist += "        sync_nent => TP_done,\n" 
        else:
            portlist += "        sync_nent => "+sync_signal+",\n"
        if memmod.has_numEntries_out or ("n1" in mem and split == 1):
            if memList[0].is_binned:
                ncopy = getVMStubNCopy(memmod);
                portlist += "        enb       => ("
                for i in reversed(range(0, ncopy)) : 
                    if i != 0 :
                        portlist += mem+"_A_enb("+str(i)+"),"
                    else:
                        portlist += mem+"_A_enb("+str(i)+")),\n"
                portlist += "        addrb     => ("
                for i in reversed(range(0, ncopy)) : 
                    if i !=0 :
                        portlist += mem+"_AV_readaddr("+str(i)+"),"
                    else:
                        portlist += mem+"_AV_readaddr("+str(i)+")),\n"
                portlist += "        doutb     => "+mem+"_V_datatmp,\n"
                portlist += "        enb_nent  => "+mem+"_enb_nent,\n"
                portlist += "        addr_nent  => "+mem+"_V_addr_nent,\n"
                portlist += "        dout_nent  => "+mem+"_AV_dout_nent,\n"
                portlist += "        mask_o    => "+mem+"_V_masktmp,\n"
            else:
                portlist += "        nent_o    => "+mem+"_AV_dout_nent,\n"
                if "MPROJ" in mem:
                    portlist += "        mask_o    => "+mem+"_AV_dout_mask,\n"
        else:
            portlist += "        nent_o    => open,\n"

        if memList[0].is_binned:
            vmstubwidth = str(memInfo.bitwidth)
            nbx = 2**bxbitwidth
            ncopy = getVMStubNCopy(memmod) 
            mem_str += "    "+mem+"_dataformat : entity work.vmstub"+vmstubwidth+"dout"+str(ncopy)+"\n"
            module =  memList[0].downstreams[0].inst[0:3]
            mem_str += "      port map (\n"
            mem_str += "        datain => "+mem+"_V_datatmp,\n"
            for i in range(0, ncopy) : 
                if i < ncopy-1 :
                    mem_str += "        dataout"+str(i)+" => "+mem+"_AV_dout("+str(i)+"),\n"
                else:
                    mem_str += "        dataout"+str(i)+" => "+mem+"_AV_dout("+str(i)+")\n"
            mem_str += "      );\n\n"
            disk = ""
            if "VMSME_D" in mem:
                disk = "DISK"
            mem_str += "    "+mem+"_maskformat : entity work.vmstub"+str(nbx)+"mask"+disk+"\n"
            mem_str += "      port map (\n"
            mem_str += "        datain => "+mem+"_V_masktmp,\n"
            for i in range(0, nbx) :
                if i < nbx-1 :
                    mem_str += "        dataout"+str(i)+" => "+mem+"_AV_dout_mask("+str(i)+"),\n"
                else:
                    mem_str += "        dataout"+str(i)+" => "+mem+"_AV_dout_mask("+str(i)+")\n"
            mem_str += "      );\n\n"
            mem_str += "    "+mem+" : entity work.tf_mem_bin\n"
        else:
            if "MPROJ" in mem:
                mem_str += "    "+mem+" : entity work.tf_mem_tproj\n"
            elif  "MPAR" in mem:
                mem_str += "    "+mem+" : entity work.tf_mem_tpar\n"
            else:
                mem_str += "    "+mem+" : entity work.tf_mem\n"        
        mem_str += "      generic map (\n"+parameterlist.rstrip(",\n")+"\n      )\n"
        mem_str += "      port map (\n"+portlist.rstrip(",\n")+"\n      );\n\n"
        if delay > 0:
            if not memInfo.is_binned and not "in" in mem and not "AS_" in mem:
                mem_str += "    "+mem+"_BX_GEN : entity work.CreateStartSignal\n"
                mem_str += "      generic map (\n"+delay2_parameterlist.rstrip(",\n")+"\n      )\n"
                mem_str += "      port map (\n"+delay2_portlist.rstrip(",\n")+"\n      );\n\n"
            mem_str += "    "+mem+"_DELAY : entity work.tf_pipe_delay\n"        
            mem_str += "      generic map (\n"+delay_parameterlist.rstrip(",\n")+"\n      )\n"
            mem_str += "      port map (\n"+delay_portlist.rstrip(",\n")+"\n      );\n\n"
            mem_str += "    "+mem+"_DELAY0 : entity work.tf_pipe_delay\n"        
            mem_str += "      generic map (\n"+delay_parameterlist_0.rstrip(",\n")+"\n      )\n"
            mem_str += "      port map (\n"+delay_portlist_0.rstrip(",\n")+"\n      );\n\n"

    return wirelist,mem_str

def writeControlSignals_interface(initial_proc, final_procs, notfinal_procs, delay = 0, split = 0):
    """
    # Top-level interface: control signals
    """
    
    final_proc_short = final_procs[0].split("_")[0]
    string_ctrl_signals = ""
    string_ctrl_signals += "    clk        : in std_logic;\n"
    string_ctrl_signals += "    reset      : in std_logic;\n"
    string_ctrl_signals += "    "+initial_proc+"_start  : in std_logic;\n"
    string_ctrl_signals += "    "+initial_proc+"_bx_in : in std_logic_vector(2 downto 0);\n"
    if split == 1:
        string_ctrl_signals += "    TP_bx_out_merged : out std_logic_vector(2 downto 0);\n"
    if split == 2:
        string_ctrl_signals += "    "+initial_proc+"_bx_out : out std_logic_vector(2 downto 0);\n"
        string_ctrl_signals += "    "+initial_proc+"_bx_out_vld : out std_logic;\n"
        string_ctrl_signals += "    "+initial_proc+"_done : out std_logic;\n"

    string_ctrl_signals += "    "+final_proc_short+"_bx_out : out std_logic_vector(2 downto 0);\n"
    string_ctrl_signals += "    "+final_proc_short+"_bx_out_vld : out std_logic;\n"
    string_ctrl_signals += "    "+final_proc_short+"_done   : out std_logic;\n"
    if final_proc_short == "TB":
      for final_proc in final_procs:
        string_ctrl_signals += "    "+final_proc+"_last_track   : out std_logic;\n"
        string_ctrl_signals += "    "+final_proc+"_last_track_vld   : out std_logic;\n"
    # Extra output ports if debug info must be sent to test-bench.
    for mid_proc in notfinal_procs:
        #Hack should probably not need the if statement here...
        if mid_proc != "PC" :
            string_ctrl_signals += "    "+mid_proc+"_bx_out : out std_logic_vector(2 downto 0);\n"
            string_ctrl_signals += "    "+mid_proc+"_bx_out_vld : out std_logic;\n"
            string_ctrl_signals += "    "+mid_proc+"_done   : out std_logic;\n"

    return string_ctrl_signals

def writeMemoryLHSPorts_interface(memList, mtypeB, extraports=False,split = 0):
    """
    # Top-level interface: input memories' ports.
    """

    if (extraports):
        direction = "out" # carry debug info to test-bench
    else:
        direction = "in"

    string_input_mems = ""

    for memMod in memList:

        mem = memMod.inst

        disk = ""
        if memMod.is_binned :
            if "VMSME_D" in mem:
                disk = "DISK"

        #FIXME special cases
    
        if "MPAR" in mem:
            if "in" not in mem:
                continue
        if "AS" in mem:
            if "in" not in mem and split == 2:
                continue
                
        string_input_mems += "    "+mem+"_wea        : "+direction+" t_"+mtypeB+"_1b;\n"
        string_input_mems += "    "+mem+"_writeaddr : "+direction+" t_"+mtypeB+"_ADDR"+disk+";\n"
        string_input_mems += "    "+mem+"_din       : "+direction+" t_"+mtypeB+"_DATA;\n"

    return string_input_mems

def writeDTCLinkLHSPorts_interface(mtypeB, memDict):
    """
    # Top-level interface: input DTC link ports.
    """

    string_input_mems = ""
    
    memList = memDict[mtypeB]
    for memMod in memList :

        mem = memMod.inst

        string_input_mems += "    "+mem+"_link_AV_dout       : in t_"+mtypeB+"_DATA;\n"
        string_input_mems += "    "+mem+"_link_empty_neg     : in t_"+mtypeB+"_1b;\n"
        string_input_mems += "    "+mem+"_link_read          : out t_"+mtypeB+"_1b;\n"

    return string_input_mems
def writeMemoryRHSPorts_interface(mtypeB, memInfo, memDict, split, MPARdict = 0):
    """
    # Top-level interface: output memories' ports.
    # Inputs:
    #   mTypeB  = memory type & its bits width (TPROJ_58 etc.)
    #   memInfo = Info about each memory type (in MemTypeInfoByKey class)
    """

    # Assume all memories of given type have same bxbitwidth.
    bxbitwidth =  memInfo.bxbitwidth
    memList = memDict[mtypeB]
    string_output_mems = ""
    for memMod in memList:

      mem = memMod.inst

      disk=""
      if "VMSME_D" in mem:
          disk="DISK"

      if "VMSME" in mtypeB:
          string_output_mems += "    "+mem+"_A_enb          : in t_"+mtypeB+"_A1b;\n"
          string_output_mems += "    "+mem+"_AV_readaddr    : in t_"+mtypeB+"_AADDR"+disk+";\n"
          string_output_mems += "    "+mem+"_AV_dout        : out t_"+mtypeB+"_ADATA;\n"
          string_output_mems += "    "+mem+"_AV_dout_mask        : out t_"+mtypeB+"_MASK"+disk+";\n"
          string_output_mems += "    "+mem+"_enb_nent        : out t_"+mtypeB+"_1b;\n"
          string_output_mems += "    "+mem+"_V_addr_nent        : out t_"+mtypeB+"_NENTADDR"+disk+";\n"
          string_output_mems += "    "+mem+"_AV_dout_nent       : out t_"+mtypeB+"_NENT;\n"
      elif "AS" in mtypeB and split: #AS/TPAR at interface need to go through merging module
          string_output_mems += "    "+mem+"_stream_V_dout : out std_logic_vector("+str(memMod.bitwidth)+" downto 0);\n"
      elif "TPAR" in mtypeB and split == 1:
          seed = mem.split("_")[1][:-1]
          itc = mem.split("_")[1][-1]
          for PCGroup in MPARdict[seed]:
              if itc == PCGroup[0]:
                  string_output_mems += "    MPAR_"+seed+PCGroup+"_stream_V_dout : out std_logic_vector("+str(memMod.bitwidth+2)+" downto 0);\n"
      else:
          string_output_mems += "    "+mem+"_enb          : in t_"+mtypeB+"_1b;\n"
          string_output_mems += "    "+mem+"_V_readaddr    : in t_"+mtypeB+"_ADDR;\n"
          string_output_mems += "    "+mem+"_V_dout        : out t_"+mtypeB+"_DATA;\n"
          if memInfo.has_numEntries_out:
              num_pages = 2**bxbitwidth
              if memInfo.is_binned:
                  string_output_mems += "    "+mem+"_AV_dout_nent : "
                  string_output_mems += "out t_"+mtypeB+"_NENT;\n"
                  string_output_mems += "    "+mem+"_AV_dout_mask : "
                  string_output_mems += "out t_"+mtypeB+"_MASK;\n"
              else:
                  string_output_mems += "    "+mem+"_AV_dout_nent  : "
                  string_output_mems += "out t_"+mtypeB+"_NENT;\n"

    return string_output_mems

def writeTrackStreamRHSPorts_interface(mtypeB, memDict):
    """
    # Top-level interface: output track stream ports.
    # Inputs:
    #   mTypeB  = memory type & its bits width (TPROJ_58 etc.)
    """
    string_output_mems = ""

    memList = memDict[mtypeB]

    for memMod in memList :
        
        mem = memMod.inst

        string_output_mems += "    "+mem+"_stream_AV_din       : out t_"+mtypeB+"_DATA;\n"
        string_output_mems += "    "+mem+"_stream_A_full_neg   : in t_"+mtypeB+"_1b;\n"
        string_output_mems += "    "+mem+"_stream_A_write      : out t_"+mtypeB+"_1b;\n"

    return string_output_mems

def writeTBConstants(memDict, memInfoDict, procs, emData_dir, sector, split):
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
    string_constants += "  constant DEBUG".ljust(str_len) + ": boolean := False;      --! Debug off/on\n"
 
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

                #FIXME - hack for fpga2 project
                if split == 2:
                    mem_delay = 0

                string_constants += ("  constant " + memInfo.mtype_short + "_DELAY").ljust(str_len) + ": integer := " + str(mem_delay) + ";          --! Number of BX delays\n"
                string_input_tmp += ("  constant FILE_IN_" + mtypeB).ljust(str_len) + ": string := memPrintsDir&\"" + mem_dir + "/" + mem_file_start + "_\";\n"
                if "VMSME_16" == mtypeB:
                    string_input_tmp += ("  constant FILE_IN_VMSME_17").ljust(str_len) + ": string := memPrintsDir&\"" + mem_dir + "/" + mem_file_start + "_\";\n"
                string_debug_tmp += ("  constant FILE_OUT_" + memInfo.mtype_short + "_debug").ljust(str_len) + ": string := dataOutDir;\n"
                #FIXME hack
                string_output_tmp += ("  constant FILE_OUT_" + mtypeB).ljust(str_len) + ": string := dataOutDir;\n"
                if "VMSME_16" == mtypeB:
                    string_output_tmp += ("  constant FILE_OUT_VMSME_17").ljust(str_len) + ": string := dataOutDir;\n"
        else:
            string_output_tmp += ("  constant FILE_OUT_" + mtypeB).ljust(str_len) + ": string := dataOutDir;\n"

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

def writeTBControlSignals(memDict, memInfoDict, initial_proc, final_procs, notfinal_procs, split = False, MPARdict = 0):

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
    string_ctrl_signals += ("  signal "+final_procs[-1].mtype_short()+"_bx_out").ljust(str_len)+": std_logic_vector(2 downto 0) := (others => '1');\n"
    string_ctrl_signals += ("  signal "+final_procs[-1].mtype_short()+"_bx_out_vld").ljust(str_len)+": std_logic := '0';\n"
    string_ctrl_signals += ("  signal "+final_procs[-1].mtype_short()+"_done").ljust(str_len)+": std_logic := '0';\n"
    if final_procs[-1].mtype_short().startswith("TB"):
        for final_proc in final_procs:
            string_ctrl_signals += ("  signal "+final_proc.inst+"_last_track").ljust(str_len)+": std_logic := '0';\n"
            string_ctrl_signals += ("  signal "+final_proc.inst+"_last_track_vld").ljust(str_len)+": std_logic := '0';\n"

    first_mem = "" # The first memory of the chain
    found_first_mem = False

    # Loop over all memory types
    string_ctrl_signals += "\n  -- Signals matching ports of top-level VHDL\n"
    for mtypeB in memDict:
        if split == 1 and ("TPROJ" in mtypeB or "VMSME" in mtypeB):
          continue 
        memInfo = memInfoDict[mtypeB]

        if initial_proc in memInfo.downstream_mtype_short and not found_first_mem:
            first_mem = mtypeB
            found_first_mem = True

        if "DL" in mtypeB and "AS" not in mtypeB: # Special case for DTCLink as it has a FIFO read interface
            memList = memDict[mtypeB]

            for memMod in memList :
                mem = memMod.inst
                string_ctrl_signals += ("  signal "+mem+"_link_read").ljust(str_len)+": "
                string_ctrl_signals += ("t_"+mtypeB+"_1b").ljust(str_len2)+":= '0';\n"
                string_ctrl_signals += ("  signal "+mem+"_link_empty_neg").ljust(str_len)+": "
                string_ctrl_signals += ("t_"+mtypeB+"_1b").ljust(str_len2)+":= '0';\n"
                string_ctrl_signals += ("  signal "+mem+"_link_AV_dout").ljust(str_len)+": "
                string_ctrl_signals += ("t_"+mtypeB+"_DATA").ljust(str_len2)+":= (others => '0');\n"
        elif memInfo.isFIFO: # Special case for FIFO write
            memList = memDict[mtypeB]

            for memMod in memList :
                mem = memMod.inst
                string_ctrl_signals += ("  signal "+mem+"_stream_A_write").ljust(str_len)+": "
                string_ctrl_signals += ("t_"+mtypeB+"_1b").ljust(str_len2)+":= '0';\n"
                string_ctrl_signals += ("  signal "+mem+"_stream_A_full_neg").ljust(str_len)+": "
                string_ctrl_signals += ("t_"+mtypeB+"_1b").ljust(str_len2)+":= '0';\n"
                string_ctrl_signals += ("  signal "+mem+"_stream_AV_din").ljust(str_len)+": "
                string_ctrl_signals += ("t_"+mtypeB+"_DATA").ljust(str_len2)+":= (others => '0');\n"

        elif memInfo.is_final: # RAM read interface
            memList = memDict[mtypeB]

            for memMod in memList :
                mem = memMod.inst

                # Add nentries signal if last memory of the chain
                if memInfo.is_binned: #FIXME including both read and write signals
                    disk = ""
                    if "VMSME_D" in mem:
                        disk = "DISK"
                    string_ctrl_signals += ("  signal "+mem+"_wea").ljust(str_len)+": "
                    string_ctrl_signals += ("t_"+mtypeB+"_1b").ljust(str_len2)+":= '0';\n"
                    string_ctrl_signals += ("  signal "+mem+"_writeaddr").ljust(str_len)+": "
                    string_ctrl_signals += ("t_"+mtypeB+"_ADDR"+disk).ljust(str_len2)+":= (others => '0');\n"
                    string_ctrl_signals += ("  signal "+mem+"_din").ljust(str_len)+": "
                    string_ctrl_signals += ("t_"+mtypeB+"_DATA").ljust(str_len2)+":= (others => '0');\n"
                    string_ctrl_signals += ("  signal "+mem+"_enb").ljust(str_len)+": "
                    string_ctrl_signals += ("t_"+mtypeB+"_A1b").ljust(str_len2)+":= (others => '0');\n"
                    string_ctrl_signals += ("  signal "+mem+"_readaddr").ljust(str_len)+": "
                    string_ctrl_signals += ("t_"+mtypeB+"_AADDR"+disk).ljust(str_len2)+":= (others => (others => '0'));\n"
                    string_ctrl_signals += ("  signal "+mem+"_dout").ljust(str_len)+": "
                    string_ctrl_signals += ("t_"+mtypeB+"_ADATA").ljust(str_len2)+":= (others => (others => '0'));\n"
                    string_ctrl_signals += ("  signal "+mem+"_AAV_dout_nent").ljust(str_len)+": "
                    string_ctrl_signals += ("t_"+mtypeB+"_NENT").ljust(str_len2)+":= (others => '0'); -- (#page)(#bin)\n"
                    string_ctrl_signals += ("  signal "+mem+"_AV_dout_mask").ljust(str_len)+": "
                    string_ctrl_signals += ("t_"+mtypeB+"_MASK").ljust(str_len2)+":= (others => (others => '0')); -- (#page)(#bin)\n"
                elif split == 1 and "TPAR" in mem:
                    seed = mem.split("_")[1][:-1]
                    itc = mem.split("_")[1][-1]
                    for PCGroup in MPARdict[seed]:
                        if PCGroup[0] == itc:
                            string_ctrl_signals +="  signal MPAR_"+seed+PCGroup +"_stream_V_dout: std_logic_vector("+str(memMod.bitwidth+2)+" downto 0) := (others=> '0') ;\n"
                else:
                    string_ctrl_signals += ("  signal "+mem+"_enb").ljust(str_len)+": "
                    string_ctrl_signals += ("t_"+mtypeB+"_1b").ljust(str_len2)+":= '0';\n"
                    string_ctrl_signals += ("  signal "+mem+"_readaddr").ljust(str_len)+": "
                    string_ctrl_signals += ("t_"+mtypeB+"_ADDR").ljust(str_len2)+":= (others => '0');\n"
                    string_ctrl_signals += ("  signal "+mem+"_dout").ljust(str_len)+": "
                    string_ctrl_signals += ("t_"+mtypeB+"_DATA").ljust(str_len2)+":= (others => '0');\n"
                    string_ctrl_signals += ("  signal "+mem+"_AV_dout_nent").ljust(str_len)+": "
                    string_ctrl_signals += ("t_"+mtypeB+"_NENT").ljust(str_len2)+":= (others => (others => '0')); -- (#page)\n"
        else: # RAM write interface
            memList = memDict[mtypeB]

            for memMod in memList :
                mem = memMod.inst

                disk = ""
                if memMod.is_binned:
                    if "VMSME_D" in mem:
                        disk = "DISK"
                if "AS" in mem and "n1" in mem and split == 1:
                    string_ctrl_signals += "  signal "+mem+"_stream_V_dout : std_logic_vector("+str(memMod.bitwidth)+" downto 0) := (others => '0');\n"
                    continue
                string_ctrl_signals += ("  signal "+mem+"_wea").ljust(str_len)+": "
                string_ctrl_signals += ("t_"+mtypeB+"_1b").ljust(str_len2)+":= '0';\n"
                string_ctrl_signals += ("  signal "+mem+"_writeaddr").ljust(str_len)+": "
                string_ctrl_signals += ("t_"+mtypeB+"_ADDR"+disk).ljust(str_len2)+":= (others => '0');\n"
                string_ctrl_signals += ("  signal "+mem+"_din").ljust(str_len)+": "
                string_ctrl_signals += ("t_"+mtypeB+"_DATA").ljust(str_len2)+":= (others => '0');\n"


    if "DL" in first_mem:
        string_ctrl_signals += "\n  -- Indicates that reading of DL of first event has started.\n"
        string_ctrl_signals += "  signal START_FIRST_LINK : std_logic := '0';\n"
    else:
        string_ctrl_signals += "\n  -- Indicates that writing of the initial memories of the first event has started.\n"
        string_ctrl_signals += "  signal START_FIRST_WRITE : std_logic := '0';\n"

    memList = memDict[first_mem]

    for memMod in memList :
        mem = memMod.inst
        string_ctrl_signals += "  signal START_" + mem + " : t_" + first_mem + "_1b" + " := '0';\n"

    string_ctrl_signals += "\n"

    return string_ctrl_signals

def writeFWBlockInstance(topfunc, memDict, memInfoDict, initial_proc, final_procs, notfinal_procs = [], split = False, MPARdict = 0):

    """
    # VHDL test bench: write the instantiation of the top level SectorProcessor FW
    # Inputs:
    #   topfunc:        name of the top module
    #   memDict:        dictionary of memories organised by type 
    #                   & no. of bits (TPROJ_58 etc.)
    #   memInfoDict:    dictionary of info (MemTypeInfoByKey) about each memory type.
    #   initial_proc:   name of the first processing module of the chain
    #   final_procs:    names of the last processing modules of the chain
    #   notfinal_procs: a set of the names of processing modules not at the end of the chain
    """
    str_len = 35 # length of string for formatting purposes

    string_fwblock_inst =  "  sectorProcFull : if INST_TOP_TF = 1 generate\n" if notfinal_procs or final_procs[-1].mtype_short() == initial_proc else "  sectorProc : if INST_TOP_TF = 0 generate\n"
    string_fwblock_inst += "  begin\n"
    string_fwblock_inst += "    uut : entity work." + topfunc + "\n"
    string_fwblock_inst += "      port map(\n"
    string_fwblock_inst += "        clk".ljust(str_len) + "=> clk,\n"
    string_fwblock_inst += "        reset".ljust(str_len) + "=> reset,\n"
    string_fwblock_inst += ("        " + initial_proc + "_start").ljust(str_len) + "=> " + initial_proc + "_start,\n"
    string_fwblock_inst += ("        " + initial_proc + "_bx_in").ljust(str_len) + "=> " + initial_proc + "_bx_in,\n"
    string_fwblock_inst += ("        " + final_procs[-1].mtype_short() + "_bx_out").ljust(str_len) + "=> " + final_procs[-1].mtype_short() + "_bx_out,\n"
    string_fwblock_inst += ("        " + final_procs[-1].mtype_short() + "_bx_out_vld").ljust(str_len) + "=> " + final_procs[-1].mtype_short() + "_bx_out_vld,\n"
    string_fwblock_inst += ("        " + final_procs[-1].mtype_short() + "_done").ljust(str_len) + "=> " + final_procs[-1].mtype_short() + "_done,\n"
    if final_procs[-1].mtype_short().startswith("TB"):
        for final_proc in final_procs :
            string_fwblock_inst += ("        " + final_proc.inst + "_last_track").ljust(str_len) + "=> " + final_proc.inst + "_last_track,\n"
            string_fwblock_inst += ("        " + final_proc.inst + "_last_track_vld").ljust(str_len) + "=> " + final_proc.inst + "_last_track_vld,\n"

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
        if split == 1 and ("VMSME" in mtypeB or "TPROJ" in mtypeB):
          continue
        memInfo = memInfoDict[mtypeB]
        memList = memDict[mtypeB]
        for memMod in memList:
            mem = memMod.inst
            if memInfo.is_initial:
                if "DL" in mtypeB and "AS" not in mtypeB: # Special case for DTCLink as it has FIFO input
                    string_input += ("        "+mem+"_link_AV_dout").ljust(str_len) + "=> "+mem+"_link_AV_dout,\n"
                    string_input += ("        "+mem+"_link_empty_neg").ljust(str_len) + "=> "+mem+"_link_empty_neg,\n"
                    string_input += ("        "+mem+"_link_read").ljust(str_len) + "=> "+mem+"_link_read,\n"
                else:
                    if ("MPAR" in mem or "AS" in mem) and not "in" in mem:
                        continue
                    string_input += ("        "+mem+"_wea").ljust(str_len) + "=> "+mem+"_wea,\n"
                    string_input += ("        "+mem+"_writeaddr").ljust(str_len) + "=> "+mem+"_writeaddr,\n"
                    string_input += ("        "+mem+"_din").ljust(str_len) + "=> "+mem+"_din,\n"
            elif memInfo.isFIFO: # Special case FIFO output
                string_tmp = ("        "+mem+"_stream_AV_din").ljust(str_len) + "=> "+mem+"_stream_AV_din,\n"
                string_tmp += ("        "+mem+"_stream_A_full_neg").ljust(str_len) + "=> "+mem+"_stream_A_full_neg,\n"
                string_tmp += ("        "+mem+"_stream_A_write").ljust(str_len) + "=> "+mem+"_stream_A_write,\n"
                if memInfo.is_final:
                    string_output += string_tmp
                else:
                    string_debug  += string_tmp
            elif memInfo.is_final:
                if memInfo.is_binned:
                    string_debug += ("        "+mem+"_wea").ljust(str_len) + "=> "+mem+"_wea,\n"
                    string_debug += ("        "+mem+"_writeaddr").ljust(str_len) + "=> "+mem+"_writeaddr,\n"
                    string_debug += ("        "+mem+"_din").ljust(str_len) + "=> "+mem+"_din,\n"
                    string_output += ("        "+mem+"_A_enb").ljust(str_len) + "=> "+mem+"_enb,\n"
                    string_output += ("        "+mem+"_AV_readaddr").ljust(str_len) + "=> "+mem+"_readaddr,\n"
                    string_output += ("        "+mem+"_AV_dout").ljust(str_len) + "=> "+mem+"_dout,\n"
                    string_output += ("        "+mem+"_AV_dout_mask").ljust(str_len) + "=> open,\n" #FIXME
                    string_output += ("        "+mem+"_enb_nent").ljust(str_len) + "=> open,\n"
                    string_output += ("        "+mem+"_V_addr_nent").ljust(str_len) + "=> open,\n"
                    string_output += ("        "+mem+"_AV_dout_nent").ljust(str_len) + "=> open,\n"
                elif ("TPAR" in mem) and split == 1:
                    seed = mem.split("_")[1][:-1]
                    itc = mem.split("_")[1][-1]
                    for PCGroup in  MPARdict[seed]:
                        if PCGroup[0] == itc:
                            string_output += ("        MPAR_"+seed+PCGroup+"_stream_V_dout").ljust(str_len) + "=> MPAR_"+seed+PCGroup+"_stream_V_dout,\n"
                else:
                    string_output += ("        "+mem+"_enb").ljust(str_len) + "=> "+mem+"_enb,\n"
                    string_output += ("        "+mem+"_V_readaddr").ljust(str_len) + "=> "+mem+"_readaddr,\n"
                    string_output += ("        "+mem+"_V_dout").ljust(str_len) + "=> "+mem+"_dout,\n"
                    string_output += ("        "+mem+"_AV_dout_nent").ljust(str_len) + "=> "+mem+"_AV_dout_nent,\n"
            elif split ==1 and ("AS" in mtypeB and "n1" in mem):
                    string_output += ("        "+mem+"_stream_V_dout").ljust(str_len) + "=> "+mem+"_stream_V_dout,\n"
            else:
                string_debug += ("        "+mem+"_wea").ljust(str_len) + "=> "+mem+"_wea,\n"
                string_debug += ("        "+mem+"_writeaddr").ljust(str_len) + "=> "+mem+"_writeaddr,\n"
                string_debug += ("        "+mem+"_din").ljust(str_len) + "=> "+mem+"_din,\n"

    string_fwblock_inst += "        -- Input data\n"
    string_fwblock_inst += string_input
    if notfinal_procs:
        string_fwblock_inst += "        -- Debug output data\n"
        string_fwblock_inst += string_debug
    string_fwblock_inst += "        -- Output data\n"
    string_fwblock_inst += string_output[:-2]+"\n" # Remove the last comma
    
    string_fwblock_inst += "      );\n"
    string_fwblock_inst += "  end generate sectorProcFull;\n\n" if notfinal_procs or final_procs[-1].mtype_short() == initial_proc else "  end generate sectorProc;\n\n"

    return string_fwblock_inst

def writeTBMemoryWriteInstance(mtypeB, memList, proc, proc_up, bxbitwidth, is_binned, is_cm, split):
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

    string_mem = ""

    for memMod in memList:
        mem = memMod.inst
        if ("AS" in mem and "n1" in mem and split == 1):
            #FIXME rewrite this to be a separate function
            width = memMod.bitwidth + 1
            str_len = 16 # length of string for formatting purposes
            string_mem += "    write"+mem+" : entity work.FileWriterFIFO\n"
            string_mem += "    generic map (\n"
            string_mem += "      FILE_NAME".ljust(str_len)+"=> FILE_OUT_"+mtypeB+"&\""+mem+"\"&outputFileNameEnding,\n"
            string_mem += "      FIFO_WIDTH".ljust(str_len)+"=> " + str(width) + "\n"
            string_mem += "    )\n"
            string_mem += "    port map (\n"
            string_mem += "      CLK".ljust(str_len)+"=> CLK,\n"
            string_mem += "      DONE".ljust(str_len)+"=> TP_DONE,\n"
            string_mem += "      WRITE_EN".ljust(str_len)+"=> ("+mem+"_stream_V_dout(" + str(width - 1) + ")),\n"
            string_mem += "      FULL_NEG".ljust(str_len)+'=> open,\n'
            string_mem += "      DATA".ljust(str_len)+"=> "+mem+"_stream_V_dout\n"
            string_mem += "    );\n"
            continue

        string_mem += "      write"+mem+" : entity work.FileWriter\n"
        string_mem += "      generic map (\n"
        string_mem += "        FILE_NAME".ljust(str_len)+"=> FILE_OUT_"+mtypeB+"&\""+mem+"\"&outputFileNameEnding,\n"
        string_mem += "        RAM_WIDTH".ljust(str_len)+"=> " + mtypeB.split("_")[1] + ",\n"
        if is_cm and is_binned :
            if "VMSME_D" in mem:
                string_mem += "        PAGE_LENGTH".ljust(str_len)+"=> 2048,\n"
            else:
                string_mem += "        PAGE_LENGTH".ljust(str_len)+"=> 1024,\n"
        if "MPROJ" in mem :
            string_mem += "        NUM_TPAGES".ljust(str_len)+"=> 4,\n"
            string_mem += "        PAGE_LENGTH".ljust(str_len)+"=> 64,\n"
        string_mem += "        NUM_PAGES".ljust(str_len)+"=> " + str(2**bxbitwidth) + "\n"
        string_mem += "      )\n"
        string_mem += "      port map (\n"
        string_mem += "        CLK".ljust(str_len)+"=> CLK,\n"
        string_mem += "        ADDR".ljust(str_len)+"=> "+mem+"_writeaddr,\n"
        string_mem += "        DATA".ljust(str_len)+"=> "+mem+"_din,\n"
        string_mem += "        WRITE_EN".ljust(str_len)+"=> "+mem+"_wea,\n"
        if proc == "VMSMER" :
            string_mem += "        START".ljust(str_len)+"=> PC_START,\n"
        else:
            string_mem += "        START".ljust(str_len)+"=> "+(proc+"_START,\n" if not proc_up else proc_up+"_DONE,\n")
        string_mem += "        DONE".ljust(str_len)+"=> "+proc+"_DONE\n"
        string_mem += "      );\n"
    
    return string_mem

def writeTBMemoryWriteRAMInstance(mtypeB, memDict, proc, bxbitwidth, is_binned, split, MPARdict = 0):
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

    memList = memDict[mtypeB]

    for memMod in memList:

        mem = memMod.inst

        if (("TPAR" in mem) or ("AS" in mem and "n1" in mem)) and split == 1: #FIXME FPGA1 hack
            width = 0
            if "TPAR" in mem:
              width= memMod.bitwidth + 3
              seed = mem.split("_")[1][:-1]
              itc = mem.split("_")[1][-1]
              for PCGroup in MPARdict[seed]:
                  if PCGroup[0] != itc: continue
                  mem = "MPAR_" + seed + PCGroup
            else:
              width= memMod.bitwidth + 1
            if "MPAR" not in mem: continue #FIXME also not good
            str_len = 16 # length of string for formatting purposes
            string_mem += "    write"+mem+" : entity work.FileWriterFIFO\n"
            string_mem += "    generic map (\n"
            string_mem += "      FILE_NAME".ljust(str_len)+"=> FILE_OUT_"+mtypeB+"&\""+mem+"\"&outputFileNameEnding,\n"
            string_mem += "      FIFO_WIDTH".ljust(str_len)+"=> " + str(width) + "\n"
            string_mem += "    )\n"
            string_mem += "    port map (\n"
            string_mem += "      CLK".ljust(str_len)+"=> CLK,\n"
            string_mem += "      DONE".ljust(str_len)+"=> TP_DONE,\n"
            string_mem += "      WRITE_EN".ljust(str_len)+"=> ("+mem+"_stream_V_dout(" + str(width - 1) + ")),\n"
            string_mem += "      FULL_NEG".ljust(str_len)+'=> open,\n'
            string_mem += "      DATA".ljust(str_len)+"=> "+mem+"_stream_V_dout\n"
            string_mem += "    );\n"
            continue
        string_mem += "    write"+mem+" : entity work.FileWriterFromRAM" + ("Binned\n" if is_binned else "\n")
        string_mem += "    generic map (\n"
        string_mem += "      FILE_NAME".ljust(str_len)+"=> FILE_OUT_"+mtypeB+"&\""+mem+"\"&outputFileNameEnding,\n"
        string_mem += "      RAM_WIDTH".ljust(str_len)+"=> " + mtypeB.split("_")[1] + ",\n"
        string_mem += "      NUM_PAGES".ljust(str_len)+"=> " + str(2**bxbitwidth) + "\n"
        string_mem += "    )\n"
        string_mem += "    port map (\n"
        string_mem += "      CLK".ljust(str_len)+"=> CLK,\n"
        string_mem += "      ADDR".ljust(str_len)+"=> "+mem+"_readaddr,\n"
        string_mem += "      DATA".ljust(str_len)+"=> "+mem+"_dout,\n"
        string_mem += "      READ_EN".ljust(str_len)+"=> "+mem+"_enb,\n"
        if "VMSME" not in mem: #FIXME
          string_mem += "      NENT_ARR".ljust(str_len)+"=> "+mem+"_A" + ("A" if is_binned else "") + "V_dout_nent,\n"
        else:
          string_mem += "      NENT_ARR".ljust(str_len)+"=> open,\n"
        string_mem += "      DONE".ljust(str_len)+"=> "+proc+"_DONE\n"
        string_mem += "    );\n"

    return string_mem 


def writeTBMemoryWriteFIFOInstance(mtypeB, memDict, proc):
    """
    # VHDL test bench: write the loop that writes the input to all FIFO memories to text files
    # Inputs:
    #   mtypeB:     the name of the memory type, including the number of bits (e.g. TPROJ_58)
    #   proc:       the processing module that writes to this memory.
    """

    memList = memDict[mtypeB]

    string_mem = ""

    memWidth = int(mtypeB.split("_")[-1])

    for memMod in memList:
        mem = memMod.inst

        str_len = 16 # length of string for formatting purposes
        string_mem += "    write"+mem+" : entity work.FileWriterFIFO\n"
        string_mem += "    generic map (\n"
        string_mem += "      FILE_NAME".ljust(str_len)+"=> FILE_OUT_"+mtypeB+"&\""+mem+"\"&outputFileNameEnding,\n"
        string_mem += "      FIFO_WIDTH".ljust(str_len)+"=> " + mtypeB.split("_")[1] + "\n"
        string_mem += "    )\n"
        string_mem += "    port map (\n"
        string_mem += "      CLK".ljust(str_len)+"=> CLK,\n"
        string_mem += "      DONE".ljust(str_len)+"=> "+proc+"_DONE,\n"
        string_mem += "      WRITE_EN".ljust(str_len)+"=> ("+mem+"_stream_A_write and "+mem+"_stream_AV_din(" + str(memWidth - 1) + ")),\n"
        string_mem += "      FULL_NEG".ljust(str_len)+"=> "+mem+"_stream_A_full_neg,\n"
        string_mem += "      DATA".ljust(str_len)+"=> "+mem+"_stream_AV_din\n"
        string_mem += "    );\n"

    return string_mem 

def writeProcCombination(module, str_ctrl_func, str_ports):
    """
    # Instantiation of processing module within top-level.
    # FIXME needs fixing to include template parameters for generic proc module writing
    """
    module_str = ""

    if "PC_" in module.inst:
        module_str += "  " + module.inst + "_mem_reader : entity work.mem_reader\n"
        module_str += "    generic map (\n"
        module_str += "      RAM_WIDTH    => " + str(module.upstreams[0].bitwidth) + ",\n"
        module_str += "      NUM_TPAGES    => 4,\n"
        module_str += "      NAME    => \""+module.inst+"_mem_reader\"\n"
        module_str += "    )\n"
        module_str += "    port map (\n"
        module_str += "      clk    => clk,\n"
        module_str += "      bx    => PC_bx_in,\n"
        module_str += "      start => PC_start,\n"
        module_str += "      enb   => MPAR_"+module.inst[3:]+"in_enb,\n"
        module_str += "      addra => MPAR_"+module.inst[3:]+"in_V_readaddr,\n"
        module_str += "      din   => MPAR_"+module.inst[3:]+"in_V_dout,\n"
        module_str += "      dout  => MPAR_"+module.inst[3:]+"in_V_tpar,\n"
        module_str += "      valid  => MPAR_"+module.inst[3:]+"in_valid,\n"
        module_str += "      index  => MPAR_"+module.inst[3:]+"in_trackletindex,\n"
        module_str += "      nent  => MPAR_"+module.inst[3:]+"in_AV_dout_nent\n"
        module_str += "    );\n\n"

    if "VMSMER_" in module.inst:
        module_str += "  " + module.inst + "_mem_reader : entity work.mem_reader\n"
        module_str += "    generic map (\n"
        module_str += "      RAM_WIDTH    => " + str(module.upstreams[0].bitwidth) + ",\n"
        module_str += "      NAME    => \""+module.inst+"_mem_reader\"\n"
        module_str += "    )\n"
        module_str += "    port map (\n"
        module_str += "      clk    => clk,\n"
        module_str += "      bx    => PC_bx_in,\n"
        module_str += "      start => PC_start,\n"
        module_str += "      enb   => AS_"+module.inst[7:]+"in_enb,\n"
        module_str += "      addra => AS_"+module.inst[7:]+"in_V_readaddr,\n"
        module_str += "      din   => AS_"+module.inst[7:]+"in_V_dout,\n"
        module_str += "      dout  => AS_"+module.inst[7:]+"in_V_as,\n"
        module_str += "      valid  => AS_"+module.inst[7:]+"in_valid,\n"
        module_str += "      index  => AS_"+module.inst[7:]+"in_index(6 downto 0),\n"
        module_str += "      nent  => AS_"+module.inst[7:]+"in_AV_dout_nent\n"
        module_str += "    );\n\n"

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

def writeStartSwitchAndInternalBX(module,mem,extraports=False, delay = 0, first_of_type=False):
    """
    # Top-level: control (start/done) & Bx signals for use by given module
    # Inputs: processing module & memory that is upstream of it.
    """
    first_proc = (mem is None)
    mtype = module.inst
    mtype_up = None

    # First write the LATCH module that emulates the 108 clock delay for the
    # processing of the stubs in the PC and VMSMER
    #

    int_ctrl_wire = ""
    int_ctrl_func = ""


    if "PC_" in mtype and first_of_type :

        int_ctrl_func +=  "  LATCH_PC_VMSMER: entity work.CreateStartSignal\n"
        startsignal_parameter_list = "        DELAY           => " + str(110) +",\n"
        int_ctrl_func += "      generic map (\n"+startsignal_parameter_list.rstrip(",\n")+"\n      )\n"

        int_ctrl_func += "    port map (\n"
        int_ctrl_func += "      clk   => clk,\n"
        int_ctrl_func += "      reset => reset,\n"
        int_ctrl_func += "      done  => PC_start,\n"
        int_ctrl_func += "      bx_out => PC_bx_in,\n"
        int_ctrl_func += "      bx => PC_bx_out,\n"
        int_ctrl_func += "      start => PC_done\n"
        int_ctrl_func += "  );\n\n"

    if first_proc:
        mtype_up = module.mtype_short()
    else:
        mtype_up = mem.upstreams[0].mtype_short()

    if not first_proc and not extraports:
        int_ctrl_wire += "  signal "+mtype_up+"_done : std_logic := '0';\n"
        int_ctrl_wire += "  signal "+mtype_up+"_bx_out : std_logic_vector(2 downto 0);\n"
        int_ctrl_wire += "  signal "+mtype_up+"_bx_out_vld : std_logic;\n"
    int_ctrl_wire += "  signal "+mtype+"_bx_in : std_logic_vector(2 downto 0);\n"
    int_ctrl_wire += "  signal "+mtype+"_start : std_logic := '0';\n"
    int_ctrl_func +=  "  LATCH_"+mtype+": entity work.CreateStartSignal\n"
    if delay > 0:
      startsignal_parameter_list = "        DELAY           => " + str(delay*2) +",\n"
      int_ctrl_func += "      generic map (\n"+startsignal_parameter_list.rstrip(",\n")+"\n      )\n"

    int_ctrl_func += "    port map (\n"
    int_ctrl_func += "      clk   => clk,\n"
    int_ctrl_func += "      reset => reset,\n"
    if "MP_" in mtype :
        int_ctrl_func += "      done  => PC_done,\n"
        int_ctrl_func += "      bx_out => PC_bx_out,\n"
    else:
        if first_proc:
            if mtype_up == "VMSMER":
                mtype_up = "PC"
            int_ctrl_func += "      done  => "+mtype_up+"_start,\n"
            int_ctrl_func += "      bx_out => "+mtype_up+"_bx_in,\n"
        else:
            int_ctrl_func += "      done  => "+mtype_up+"_done,\n"
            int_ctrl_func += "      bx_out => "+mtype_up+"_bx_out,\n"
    int_ctrl_func += "      bx => "+mtype+"_bx_in,\n"
    int_ctrl_func += "      start => "+mtype+"_start\n"
    int_ctrl_func += "  );\n\n"

    return int_ctrl_wire,int_ctrl_func

def writeProcControlSignalPorts(module,first_of_type):
    """
    # Processing module port assignment: control signals
    """
    string_ctrl_ports = ""
    string_ctrl_ports += "      ap_clk   => clk,\n"
    string_ctrl_ports += "      ap_rst   => reset,\n"
    #FIXME Special case as the PC_start is use also for VMSMER
    if (module.mtype_short()=="PC") :
        string_ctrl_ports += "      ap_start => "+module.inst+"_start,\n"
    if (module.mtype_short()!="PC" and module.mtype_short()!="VMSMER") :
        string_ctrl_ports += "      ap_start => "+module.inst+"_start,\n"
        string_ctrl_ports += "      ap_idle  => open,\n"
        string_ctrl_ports += "      ap_ready => open,\n"
        if first_of_type:
            string_ctrl_ports += "      ap_done  => "+module.mtype_short()+"_done,\n"
        else:
            string_ctrl_ports += "      ap_done  => open,\n"

    return string_ctrl_ports

def writeProcBXPort(modName,isInput,isInitial,first_of_type,delay):
    """
    # Processing module port assignment: BX ports
    """
    bx_str = ""
    #FIXME
    if "PC_" in modName and not isInput:
        bx_str += "      bx_V          => "+modName+"_bx_in,\n"        
    if "VMSMER_" in modName and not isInput:
        bx_str += "      bx_V          => PC_bx_in,\n"        
    if isInput and isInitial:
        bx_str += "      bx_V          => "+modName+"_bx_in,\n"
    elif isInput and not isInitial:
        bx_str += "      bx_V          => "+modName+"_bx_in,\n"
    elif not isInput:
        if delay==0:
            bx_str += "      bx_o_V        => "+modName+"_bx_out,\n"
            bx_str += "      bx_o_V_ap_vld => "+modName+"_bx_out_vld,\n"
        else:
            if first_of_type and not ("VMSMER" in modName or "PC" in modName):
                bx_str += "      bx_o_V        => "+modName.split("_")[0]+"_bx_out,\n"
                if ("TB_" in modName) or ("TP_" in modName):
                  bx_str += "      bx_o_V_ap_vld => "+modName.split("_")[0]+"_bx_out_vld,\n"
                else:
                  bx_str += "      bx_o_V_ap_vld => open,\n"
    return bx_str

def writeProcMemoryLHSPorts(argname,mem,split = False):
    """
    # Processing module port assignment: outputs to memories
    """

    string_mem_ports = ""
    if ("TPROJ" in mem.inst) and split == 1: #set TPROJ and VMSME to open for a split-FPGA project
          string_mem_ports += "      "+argname+"_dataarray_data_V_ce0       => open,\n"
          string_mem_ports += "      "+argname+"_dataarray_data_V_we0       => open,\n"
          string_mem_ports += "      "+argname+"_dataarray_data_V_address0  => open,\n"
          string_mem_ports += "      "+argname+"_dataarray_data_V_d0        => open,\n"
    elif ("VMSME" in mem.inst and split == 1):
        string_mem_ports += "      "+argname+"_dataarray_0_data_V_ce0       => open,\n"
        string_mem_ports += "      "+argname+"_dataarray_0_data_V_we0       => open,\n"
        string_mem_ports += "      "+argname+"_dataarray_0_data_V_address0  => open,\n"
        string_mem_ports += "      "+argname+"_dataarray_0_data_V_d0        => open,\n"
    elif "memoriesTEO" in argname or "memoryME" in argname :
        string_mem_ports += "      "+argname+"_dataarray_0_data_V_ce0       => open,\n"
        string_mem_ports += "      "+argname+"_dataarray_0_data_V_we0       => "
        string_mem_ports += mem.mtype_short() + "_" + mem.var()+"_wea,\n"
        string_mem_ports += "      "+argname+"_dataarray_0_data_V_address0  => "
        string_mem_ports += mem.mtype_short() + "_" + mem.var()+"_writeaddr,\n"
        string_mem_ports += "      "+argname+"_dataarray_0_data_V_d0        => "
        string_mem_ports += mem.mtype_short() + "_" + mem.var()+"_din,\n"
    else:
        string_mem_ports += "      "+argname+"_dataarray_data_V_ce0       => open,\n"
        string_mem_ports += "      "+argname+"_dataarray_data_V_we0       => "
        string_mem_ports += mem.mtype_short() + "_" + mem.var()+"_wea,\n"
        if "TPAR" in mem.inst and split == 1 : #FIXME TPAR addr from TP should be 10 bits
            string_mem_ports += "      "+argname+"_dataarray_data_V_address0(9 downto 0)  => "
            string_mem_ports += mem.mtype_short() + "_" + mem.var()+"_writeaddr,\n"
            string_mem_ports += "      "+argname+"_dataarray_data_V_address0(11 downto 10)  => "
            string_mem_ports += mem.mtype_short() + "_" + mem.var()+"_dummy,\n"
        else:
            string_mem_ports += "      "+argname+"_dataarray_data_V_address0  => "
            string_mem_ports += mem.mtype_short() + "_" + mem.var()+"_writeaddr,\n"
        string_mem_ports += "      "+argname+"_dataarray_data_V_d0        => "
        string_mem_ports += mem.mtype_short() + "_" + mem.var()+"_din,\n"


    return string_mem_ports

def writeProcMemoryRHSPorts(argname,mem,portindex=0, split = 0):
    """
    # Processing module port assignment: inputs from memories
    """
    string_mem_ports = ""
    if (mem.mtype == "VMStubsTEOuter" or mem.mtype == "VMStubsME"):
        ncopy = getVMStubNCopy(mem)
        for instance in range(0,ncopy):
            string_mem_ports += "      "+argname+"_dataarray_"+str(instance)+"_data_V_ce"+str(portindex)+"       => "
            string_mem_ports += mem.mtype_short() + "_" + mem.var()+"_A_enb("+str(instance)+"),\n"
            string_mem_ports += "      "+argname+"_dataarray_"+str(instance)+"_data_V_address"+str(portindex)+"  => "
            string_mem_ports += mem.mtype_short() + "_" + mem.var()+"_AV_readaddr("+str(instance)+"),\n"
            string_mem_ports += "      "+argname+"_dataarray_"+str(instance)+"_data_V_q"+str(portindex)+"        => "
            string_mem_ports += mem.mtype_short() + "_" + mem.var()+"_AV_dout("+str(instance)+"),\n"
    elif (mem.mtype == "TrackletParameters" and "in" in mem.var()) :
        #FIXME - this is a hack as this is not a memory type..
          string_mem_ports += "      valid        => "
          string_mem_ports += mem.mtype_short()+"_"+mem.var()+"_valid,\n"
          string_mem_ports += "      trackletindex_V        => "
          string_mem_ports += mem.mtype_short()+"_"+mem.var()+"_trackletindex,\n"
          string_mem_ports += "      "+argname+"_data_V        => "
          string_mem_ports += mem.mtype_short()+"_"+mem.var()+"_V_tpar,\n"
    elif (mem.mtype == "AllStubs" and "in" in mem.var()) :
        #FIXME - this is a hack as this is not a memory type..
          string_mem_ports += "      valid        => "
          string_mem_ports += mem.mtype_short()+"_"+mem.var()+"_valid,\n"
          string_mem_ports += "      index        => "
          string_mem_ports += mem.mtype_short()+"_"+mem.var()+"_index,\n"
          string_mem_ports += "      "+argname+"_data_V        => "
          string_mem_ports += mem.mtype_short()+"_"+mem.var()+"_V_as,\n"
    else:
        string_mem_ports = ""
        string_mem_ports += "      "+argname+"_dataarray_data_V_ce"+str(portindex)+"       => "
        string_mem_ports += mem.mtype_short()+"_"+mem.var()+"_enb,\n"
        string_mem_ports += "      "+argname+"_dataarray_data_V_address"+str(portindex)+"  => "
        string_mem_ports += mem.mtype_short()+"_"+mem.var()+"_V_readaddr,\n"
        string_mem_ports += "      "+argname+"_dataarray_data_V_q"+str(portindex)+"        => "
        string_mem_ports += mem.mtype_short()+"_"+mem.var()+"_V_dout,\n"

    if (mem.has_numEntries_out and portindex == 0):
        if mem.is_binned:
            string_mem_ports += "      "+argname+"_nentries_V_ce0 => "+mem.mtype_short()+"_"+mem.var()+"_enb_nent,\n"
            string_mem_ports += "      "+argname+"_nentries_V_address0 => "+mem.mtype_short()+"_"+mem.var()+"_V_addr_nent,\n"
            string_mem_ports += "      "+argname+"_nentries_V_q0 => "+mem.mtype_short()+"_"+mem.var()+"_AV_dout_nent,\n"
            for i in range(0,2**mem.bxbitwidth):
                nrz = 8
                if mem.var()[0] == "D"  and split == 2:
                    nrz = 16
                for j in range(0,nrz):
                    string_mem_ports += "      "+argname+"_binmask8_"+str(i)+"_V_"+str(j)+"     => ("
                    for k in range(0,8):
                        if k != 0 :
                            string_mem_ports += ", "
                        string_mem_ports += mem.mtype_short()+"_"+mem.var()+"_AV_dout_mask("+str(i)+")("+str((j+1)*8-k-1)+")"
                    string_mem_ports += "),\n"
        else:
            tpage = 1
            if "MPROJ" in mem.mtype_short() :
                tpage = 4
                for i in range(0,2**mem.bxbitwidth):
                    string_mem_ports += "      "+argname+"_mask_"+str(i)+"_V                   => "
                    string_mem_ports += mem.mtype_short()+"_"+mem.var()+"_AV_dout_mask("+str(i)+"),\n"
            for i in range(0,tpage*(2**mem.bxbitwidth)):
                #FIXME - hack...
                if "MPAR" in mem.mtype_short() :
                    continue
                if "AS" in mem.mtype_short() and "in" in mem.var():
                    continue
                string_mem_ports += "      "+argname+"_nentries_"+str(i)+"_V               => "
                string_mem_ports += mem.mtype_short()+"_"+mem.var()+"_AV_dout_nent("+str(i)+"),\n"

    return string_mem_ports

def writeLastTrackPorts(ftName, is_open):
    string_last_track_port = "      done        => "
    if is_open:
        string_last_track_port += "open,\n"
    else:
        string_last_track_port += ftName+"_last_track,\n"
        string_last_track_port += "      done_ap_vld => "+ftName+"_last_track_vld,\n"

    return string_last_track_port

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
    depth = 0
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
    string_mem_ports += mem.inst+"_link_AV_dout,\n"
    string_mem_ports += "      "+argname+"_V_empty_n  => "
    string_mem_ports += mem.inst+"_link_empty_neg,\n"
    string_mem_ports += "      "+argname+"_V_read     => "
    string_mem_ports += mem.inst+"_link_read,\n"
    return string_mem_ports

def writeProcTrackStreamLHSPorts(argname,mem):
    """
    # Processing module port assignment: output track streams
    """
    string_mem_ports = ""
    string_mem_ports += "      "+argname+"_V_din       => "
    string_mem_ports += mem.inst+"_stream_AV_din,\n"
    string_mem_ports += "      "+argname+"_V_full_n    => "
    string_mem_ports += mem.inst+"_stream_A_full_neg,\n"
    string_mem_ports += "      "+argname+"_V_write     => "
    string_mem_ports += mem.inst+"_stream_A_write,\n"
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
