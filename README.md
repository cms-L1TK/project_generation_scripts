# Project Generation Scripts

Basic instructions to run the project generation for the Vivado HLS project with hourglass configuration

## Overview of code for producing wiring files.

(More technical details about the internal operation of the scripts can be found at end of this document).

The wiring files are no longer produced by python script. The original python wiring scripts, which can be found in archive/, are documented in archive/README.md.

Instead, the wiring files are now made by the L1 track C++ emulation code https://github.com/cms-L1TK/cmssw/ , after editing L1Trigger/TrackFindingTracklet/interface/Settings.h to set the configuration parameter: writeConfig_=true.

This produces three files, the latest version of which is in
https://github.com/cms-L1TK/firmware-hls in directory emData/ .

  *wires.dat*, *memorymodules.dat*, *processingmodules.dat* & 

  **DATA FORMAT**: The key output is *wires.dat*, where each line contains a single instance of a memory module and the proc modules that read/write to it, together with the I/O pins used. Clones are distinguished by "n1", "n2" etc. in the name. Pin names include "in" or "out" to distinguish read or write.

      Mem  input=> ProcModuleWrite.pinX  output=>ProcModuleRead.pinY

  Files *memorymodules.dat* & *processingmodules.dat* list all memories/proc modules, with each line containing a module instance name and its corresponding type, following the format

      ModuleType: ModuleInstance

  The names of the output memories are unique, such that none is written by > 1 proc module to avoid conflicts. If the code detects that a memory is read by > 1 proc module, it clones it to avoid conflicts. Furthermore, as each proc module connects to several memories, it names the input/output pins of the proc module used for each connection.
  
* Generate the top-level FW for L1 track chain.

  N.B. Currently CANNOT generate a full project since some processing steps are under construction.
  1) Checkout the project generation scripts: `git clone git@github.com:cms-L1TK/project_generation_scripts.git`
  1) Checkout L1Trk HLS code: `git clone https://github.com/cms-tracklet/firmware-hls`
  1) Download the wiring files: `cd firmware-hls/emData/ ; ./download.sh -t; cd ../..`
  1) Copy the wiring files to the project generation area: `cd project_generation_scripts/; cp ../firmware-hls/emData/LUTs/*.dat .`
  1) Ensure ROOT is in your PATH.
  1) Make top-level VHDL: `./generator_hdl.py (dirHLS)`, *dirHLS* is the location of the HLS code, which defaults to "../firmware-hls".

Example for PR-ME-MC chain: 
```
./generator_hdl.py --uut PR_L3PHIC -u 0 -d 2
```      
Example for TE-TC chain:
 ```     
./generator_hdl.py --uut TC_L1L2E -u 1 -d 0
```
Example for IR-VMR chain:
```
./generator_hdl.py --uut VMR_L2PHIA -u 1 -d 0
```
Example for "reduced" IR-VMR-TE-TC-PR-ME-MC-TB skinny chain
```
./makeReducedConfig.py
./generator_hdl.py --mut IR -u 0 -d 7 -w reduced_wires.dat -p reduced_processingmodules.dat -m reduced_memorymodules.dat
```
Example for barrel-only IR-VMR-TE-TC-PR-ME-MC-TB chain
```
./makeBarrelConfig.py
./generator_hdl.py --mut IR -u 0 -d 7 -w barrel_wires.dat -p barrel_processingmodules.dat -m barrel_memorymodules.dat
```

  Optional arguments include:
  
      -h, --help          For help & to see default option values
      -f, --topfunc       Top function name of generated FW
      -n, --projname      Project name
      -p, --procconfig    Name of the processing module configuration .dat file
      -m, --memconfig     Name of the memory module configuration .dat file
      -w, --wireconfig    Name of the wiring configuration .dat file
      --memprint_dir      Directory to search for memory printouts produced by the emulation
      --emData_dir        Directory into which the memory printout files are copied for the HLS project
      -ng, --no_graph     Disable making of wiring diagram. If disabled, then ROOT is not required.
      
 For generating a partial project:

 
      -r, --region        Detector region of the generated project.
      		              Choose from A(all), L(barrel), D(disk).
      --uut               Specify a unit under test, e.g. TC_L1L2E
      --mut		  Specify a module under test, e.g PR (Projection Routers)
      -x                  Give top-level VHDL extra output ports to carry
      			  debug info to test-bench corresponding to inputs
			  to all memory modules in chain.
      -u, --nupstream     The number of processing steps to be generated upstream of the UUT or MUT 
      -d, --ndownstream   The number of processing steps to be generated downstream of the UUT or MUT

  This script parses the three .dat files from the previous step and instantiates a *TrackletGraph* object (defined in TrackletGraph.py). The TrackletGraph object is a representation of the project configuration, containing all processing and memory objects as well as their inter-connections.

  The other part of this script takes the TrackletGraph object as input and writes out relevant files for the top level project.
  In order to generate correct and up-to-date functions for requested processing steps, the script parses the (templated) function definition of each step in the corresponding header file in L1Trk HLS repo (https://github.com/cms-tracklet/firmware-hls/tree/master/TrackletAlgorithm).

  The final product of this script includes a top-level VHDL module which instantiates all the relevant HLS IP cores and HDL memory modules, as well as an VHDL test bench, (which should ultimately read the memory printout files made by the C++ emulation). In the future, the script will generate a tcl script needed to generate the project.

 The script also makes a wiring diagram *TrackletProject.pdf* of the mem/proc modules in the VHDL.

### makeReducedConfig.py

This script takes an input wires.dat, modules.dat, and memories.dat file, and allows you to make a reduced summer chain configuration centered around one module (currently explicitly set to be one TC). The script takes the phi sector of the TC, and chooses phi sectors for the layers that line up with it, then recursively searches for TC inputs and outputs within those phi regions. It outputs a new set of wires, modules, and memories files including only these files.

By default the script will run starting with *TC_L1L2F*, and produced files called *reduced_wires.dat*, etc., but it can be modified with these options:
  
    -w, --wires         Reference wires.dat file (from full config)
    -p, --process       Reference processingmodules.dat file (from full config)
    -m, --memories      Reference memorymodules.dat file (from full config)
    -s, --sector        TC phi sector from which to create the reduced config. By default this is "F".
    -o, --output        Prefix to add to all output files
    -l, --layers        Select the layer pair to create seeds with. By default this is "L1L2". 
    -n, --noneg         Remove all negative eta modules from the config. Done by default.
    --graph/--no-graph  Enable/disable making of the diagram. If disabled (not default) ROOT is not required.

-----------------------------------------------------------------

## Scripts for plotting wiring diagram:

To (re)make the wiring diagram in root:

      root -l
      root[0] .L DrawTrackletProject.C
      root[1] DrawTrackletProject()

This processes file *diagram.dat*, which you can obtain from *generate_hdl.py* -- corresponds to subset of wiring pertaining to generated VHDL.

-----------------------------------------------------------------

## Python version and other dependencies
This code is compatible with python 3.  All new code should be compatible with python 3; since python 2 has ended support in 2020.

Some of the code also depends on ROOT and its python interface (last tested with version 6.10.00), though this can be disabled via the `--no-graph` option.

-----------------------------------------------------------------

## Technical details of scripts for producing wiring files.

N.B. The documentation below was written for the old python scripts, but is largely still relevant to the C++ version of them.

-- Configuration parameters:

Set at top of script. e.g. "nallstubslayers" sets number of coarse phi regions (each corresponding to an "AllStub" memory) each layer is divided into within a phi nonant. And "nvmtelayers" sets the number of Virtual Modules in phi per coarse phi region for each layer, for later used by TrackletEngine.

This writes FILE = wires.input.hourglassExtended . Documenting how each section of this is produced:

1) "Input Router" ("IL") 

Each sends stubs from one DTC (e.g. "PS10G_1") to 4-8 AllStub memories (labelled "PHIA-PHIH", each corresponding to a coarse phi division of nonant) in each layer ("L1-L6" or "D1-D5") the DTC reads.
It's output AllStub memories therefore have names such as "IL_L1PHIC_PS10G_1_A".

findInputLinks() reads a file "dtcphirange.txt" (written by C++ emulation), which has a line for each 
DTC indicating its name and the range of phi of stubs it reads. This is used to identify which DTCs
map on to which coarse phi regions. 

N.B. FILE contains no section listing the IL itself and its connections to the DTCs.

2) "VMRouters (VMR) for the TEs in the layers / disks"

e.g. IL_L1PHIC_PS10G_1_A IL_L1PHIC_PS10G_2_A IL_L1PHIC_neg_PS10G_1_A > VMR_L1PHIC > AS_L1PHIC VMSME_L1PHIC9 VMSME_L1PHIC10 VMSME_L1PHIC11 VMSME_L1PHIC12 VMSTE_L1PHIC9 VMSTE_L1PHIC10 VMSTE_L1PHIC11 VMSTE_L1PHIC12 VMSTE_L1PHIZ5 VMSTE_L1PHIZ6

Each VMR writes AllStub memories ("AS_") for a single coarse phi region (e.g. "PHIC"), merging data from all DTCs related to this phi region. It does so by merging data from the AllStub memories written by all ILs for this phi region. Above FILE line lists all IL AllStub Memories that feed (">") into a single VMR ("VMR_L1PHIC") that writes to the output AllStub memories ("AS_L1PHIC").

Each VMR also writes to Virtual Module memories ("VMS") to be used later by the Match Engine ("ME") or "Tracklet Engine ("TE"). e.g. In FILE word "VMSTE_L1PHIC9 - 12", we are writing to the 9th - 12th VM in L1. (Each coarse phi region in L1 currently has 4 VMs (cfg param "nvmtelayers"), so PHIC contains VMs 9-12).

3) "Tracklet Engines (TE) for seeding layer / disk"

Each TE reads one VM in two neighbouring layers, finds stub pairs and writes them to a StubPair ("SP") memory.

e.g. VMSTE_L1PHIB5 VMSTE_L2PHIA7 > TE_L1PHIB5_L2PHIA7 > SP_L1PHIB5_L2PHIA7

indicates VMs PHIB5 from L1 and PHIA7 from L2 are processed by TE with name corresponding to these VMs,
and written to corresponding SP memory.

validtepair*(...) checks of each VM pair would be consistent with a track of Pt > 2 GeV.

For displaced tracking, function validtedpair*(...) used instead, which requires the VM pair to be consistent with |d0| < 3cm for at least one of q/Pt = 1/2 or -1/2.

4) "Tracklet Calculators (TC) for seeding layer / disk"

e.g. SP_L1PHIB6_L2PHIA8 SP_L1PHIB7_L2PHIA5 SP_L1PHIB7_L2PHIA6 > TC_L1L2C > TPAR_L1L2XXC TPROJ_L1L2XXC_L3PHIA TPROJ_L1L2XXC_L3PHIB TPROJ_L1L2XXC_L4PHIA

Each TC reads several SP memories, each containing a pair of VMs of two seeding layers (L1 & L2 here). Several (set by "tcs") TCs are created for each layer pair, and the SP memories are distributed between them. In TC_L1L2C, "C" indicates that this is 3rd TC in the layer pair. (N.B. Completely unrelated to the coarse phi regions). The helix params are stored in memory TPAR_L1L2XXC, (with "XX" added to name of all TC output memories). The track projections to all other layers are stored in TPROJ_L1L2XXC_L3PHIA etc, where last part of name indicates layer number and coarse phi region of projection. (N.B. These coarse phi regions can differ from those of VMRs).

phiprojrange*(...) is used to determine phi projection in each layer, to identify which coarse phi regions are consistent with projection.

This step also stores the list of all TPAR & TPROJ memories in arrays TPROJ_list & TPAR_list.

5) "PROJRouters for the MEs in layer / disk"

TPROJ_L3L4XXA_L2PHIA TPROJ_L3L4XXB_L2PHIA TPROJ_L3L4XXC_L2PHIA > PR_L2PHIA > AP_L2PHIA VMPROJ_L2PHIA1 VMPROJ_L2PHIA2 

e.g. This merges all projections (e.g. TPROJ_L3L4XXB_L2PHIA, seed L3L4 extrapolated to coarse phi region A of L2 (L2PHIA) using the B'th tracklet calculator) that point to the same coarse phi region of the extrapolation layer from various seeding layers. This list of these is taken from array TPROJ_list, mentioned above. These are all processed by a single Projection Router algo. It writes intercept point of helix with coarse phi region to All Projection (AP) memory. And whenever intercept lies within a VM, (although code doesn't check this, only if intercept is consistent with coarse phi region), writes index of tracklet to  VM Projection (VMProj) memory for that VM.

6) "Match Engines for the layers / disks"

VMSME_L1PHIA1 VMPROJ_L1PHIA1 > ME_L1PHIA1 > CM_L1PHIA1

Checks consistency of stubs in VM with helix intercept. e.g. ME for VM A1 in L1 reads stubs from VM memory (VMS) and intercepts from projection memory (VMPROJ) for this VM. Matching (tracklet,stub) indices written to CandidateMatch (CM) memory.

7) "Match Calculator for layer / disk"

CM_L2PHIB9 CM_L2PHIB10 CM_L2PHIB11 > MC_L2PHIB > FM_L3L4XX_L2PHIB FM_L5L6XX_L2PHIB

More precise pairing of stubs & intercepts within a given coarse phi region "B" of a layer L2, using the Candidate Matches of all VMs in that region. Result written to Full Match (FM") memories, subdivided according to the seeding layer pairs (e.g. L3L4, where "XX means nothing") which can be extrapolated to the extrapolation layer.

8) "Tracklet Fit for seeding" 

FM_L5L6XX_L1PHIA FM_L5L6XX_L1PHIB FM_L5L6XX_L1PHIC > FT_L5L6XX > TF_L5L6XX

A fit algo is run for each seeding layer pair. It reads the matches (FM) of stubs to tracklets from each layer and all coarse phi regions.

