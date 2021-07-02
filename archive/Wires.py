#!/usr/bin/env python

#########################################################################
# Reads file wires.input.hourglassExtended (made by HourGlassConfig.py)
# and writes wires.dat, memorymodules.dat, processingmodules.dat
# & processingmodules_input.dat (never used).
#
# wires.input.hourglassextended: all input & output memories connected to each processing block.
#
# processingmodules_inputs.dat: no. input memories connected to each proc block.
# processingmodules.dat: list of all proc blocks. 
# memorymodules.dat: list of all input memories, with "n5" etc. appended to name to distinguish multiple copies of a given memory (required to avoid conflicts if it is read by multiple proc blocks).
# wires.dat: For each copy of each memory, indicate proc block that gives it its input/output, indicating also which pin name (after ".") on this proc block is used. 
#
#
# Detailed description in README.md.
#
# The code below is organised in 3 sections:
#   cfg params, python functions, python main routine.
#
#########################################################################

import math
import sys
import collections

if (len(sys.argv) != 2 ) :
    print "Usage: Wires.py wires.input"
    exit(1)

print 'Will read input file', sys.argv[1]
 
#Build the geometry for layers

inputmemorymodules = []
outputmemorymodules = []
processingmodules = []


#=== FUNCTION DEFINITIONS. (MAIN ROUTINE MUCH FURTHER DOWN).

# Calculate & print to screen block & distributed RAM requirements.
# (Input Args: nmem=no. of memories of given type)
# (Output Args: shortmem & longmem are no. of 18b & 36b BRAM in entire chain, and nbits are bits of DRAM). 

def printsum(memname,nmem,numem,nmemslots,memwidth,memdepth,nbx,shortmem,umem,nbits):
    # BRAM memory available only in multiples of 18 bits.
    # N.B. Fragile code! Hard-wired assumptions about possible memory width.

    if nmem==0 and numem==0 :
        return (shortmem,umem,nbits)
    #used to count 18 bit memories used by DRAM
    n18bits=1+(memwidth-1)/18
    
    #used to coutn #18k bit BRAMs
    n18kbits=1+(memwidth-1)/36

    Nbits=memwidth*nmemslots*nbx*1e-3 # Required bits of dist. RAM.

    if nmemslots==0 :
        Nbits=nmem*memwidth*memdepth*nbx*1e-3
        
    # Hard-wired assumption about which memories use distributed or block RAM.
    dram=1
    bram=1
    if "Input" in memname :
        dram=0
    if "All Stubs" in memname :
        dram=0
    if "TE" in memname :
        dram=0
    if "ME" in memname :
        dram=0
    if "Stub Pair" in memname :
        bram=0
    if "Stub Triplet" in memname :
        bram=0
    if "TPROJ" in memname :
        bram=0
    if "TPAR" in memname :
        dram=0
    if "All Proj" in memname :
        dram=0
    if "VM Proj" in memname :
        bram=0
    if "Cand. Match" in memname :
        bram=0
    if "Full Match" in memname :
        dram=0
    if "Track Fit" in memname :
        bram=0
    if "Clean Track" in memname :
        bram=0

    Nbits*=dram
        
    print memname,"{:4.0f}".format(nmem),"{:10.0f}".format(memwidth),"{:7.0f}".format(memdepth),"{:5.0f}".format(nbx),"{:14.3f}".format(Nbits),"{:10.0f}".format(bram*nmem*n18kbits),"{:10.0f}".format(numem)

    nbits+=Nbits

    shortmem+=bram*nmem*n18kbits

    umem+=numem
    
    return (shortmem,umem,nbits)

# Get unique identifier (used to identify track fit input pin) for stub layer corresponding to memory.

def matchin(proc,mem):
    if "FT_L1L2" in proc:
        if "L3" in mem[8:10]:
            return "1"
        if "L4" in mem[8:10]:
            return "2"
        if "L5" in mem[8:10]:
            return "3"
        if "L6" in mem[8:10]:
            return "4"
        if "D1" in mem[8:10] or "F1" in mem[8:10] or "B1" in mem[8:10]:
            return "4"
        if "D2" in mem[8:10] or "F2" in mem[8:10] or "B2" in mem[8:10]:
            return "3"
        if "D3" in mem[8:10] or "F3" in mem[8:10] or "B3" in mem[8:10]:
            return "2"
        if "D4" in mem[8:10] or "F4" in mem[8:10] or "B4" in mem[8:10]:
            return "1"
    if "FT_L2L3D1" in proc:
        if "L1" in mem[8:10]:
            return "1"
        if "L4" in mem[8:10]:
            return "2"
        if "F2" in mem[8:10] or "B2" in mem[8:10] or "D2" in mem[8:10]:
            return "4"
        if "F3" in mem[8:10] or "B3" in mem[8:10] or "D3" in mem[8:10]:
            return "3"
        if "F4" in mem[8:10] or "B4" in mem[8:10] or "D4" in mem[8:10]:
            return "2"
    if "FT_L2L3" in proc:
        if "L1" in mem[8:10]:
            return "1"
        if "D4" in mem[8:10] or "F4" in mem[8:10] or "B4" in mem[8:10]:
            return "1"
        if "L4" in mem[8:10]:
            return "2"
        if "D3" in mem[8:10] or "F3" in mem[8:10] or "B3" in mem[8:10]:
            return "2"
        if "L5" in mem[8:10]:
            return "3"
        if "F2" in mem[8:10] or "B2" in mem[8:10] or "D2" in mem[8:10]:
            return "3"
        if "F1" in mem[8:10] or "B1" in mem[8:10] or "D1" in mem[8:10]:
            return "4"
    if "FT_L3L4L2" in proc:
        if "L1" in mem[8:10]:
            return "1"
        if "L5" in mem[8:10]:
            return "2"
        if "L6" in mem[8:10]:
            return "3"
        if "F1" in mem[8:10] or "B1" in mem[8:10] or "D1" in mem[8:10]:
            return "4"
        if "F2" in mem[8:10] or "B2" in mem[8:10] or "D2" in mem[8:10]:
            return "3"
        if "F3" in mem[8:10] or "B3" in mem[8:10] or "D3" in mem[8:10]:
            return "2"
    if "FT_L3L4" in proc:
        if "L1" in mem[8:10]:
            return "1"
        if "L2" in mem[8:10]:
            return "2"
        if "L5" in mem[8:10]:
            return "3"
        if "L6" in mem[8:10]:
            return "4"
        if "F1" in mem[8:10] or "B1" in mem[8:10] or "D1" in mem[8:10]:
            return "4"
        if "F2" in mem[8:10] or "B2" in mem[8:10] or "D2" in mem[8:10]:
            return "3"
    if "FT_L5L6" in proc:
        if "L1" in mem[8:10]:
            return "1"
        if "L2" in mem[8:10]:
            return "2"
        if "L3" in mem[8:10]:
            return "3"
        if "L4" in mem[8:10]:
            return "4"
    if "FT_L5L6L4" in proc:
        if "L1" in mem[8:10]:
            return "1"
        if "L2" in mem[8:10]:
            return "2"
        if "L3" in mem[8:10]:
            return "3"
        if "L4" in mem[8:10]:
            return "4"
    if "FT_D1D2L2" in proc:
        if "L1" in mem[8:10]:
            return "1"
        if "D3" in mem[8:10]:
            return "2"
        if "D4" in mem[8:10]:
            return "3"
        if "D5" in mem[8:10]:
            return "4"
        if "L3" in mem[8:10]:
            return "4"
    if "FT_D1D2" in proc:
        if "L1" in mem[8:10]:
            return "1"
        if "D3" in mem[8:10]:
            return "2"
        if "D4" in mem[8:10]:
            return "3"
        if "D5" in mem[8:10]:
            return "4"
        if "L2" in mem[8:10]:
            return "4"
    if "FT_B1B2" in proc:
        if "L1" in mem[8:10]:
            return "1"
        if "B3" in mem[8:10]:
            return "2"
        if "B4" in mem[8:10]:
            return "3"
        if "B5" in mem[8:10]:
            return "4"
        if "L2" in mem[8:10]:
            return "4"
    if "FT_D3D4" in proc:
        if "L1" in mem[8:10]:
            return "1"
        if "D1" in mem[8:10]:
            return "2"
        if "D2" in mem[8:10]:
            return "3"
        if "D5" in mem[8:10]:
            return "4"
        if "L2" in mem[8:10]:
            return "4"
    if "FT_F3F4" in proc:
        if "L1" in mem[8:10]:
            return "1"
        if "F1" in mem[8:10]:
            return "2"
        if "F2" in mem[8:10]:
            return "3"
        if "F5" in mem[8:10]:
            return "4"
        if "L2" in mem[8:10]:
            return "4"
    if "FT_B3B4" in proc:
        if "L1" in mem[8:10]:
            return "1"
        if "B1" in mem[8:10]:
            return "2"
        if "B2" in mem[8:10]:
            return "3"
        if "B5" in mem[8:10]:
            return "4"
        if "L2" in mem[8:10]:
            return "4"
    if "FT_F1L" in proc:
        if "F2" in mem[8:10]:
            return "1"
        if "F3" in mem[8:10]:
            return "2"
        if "F4" in mem[8:10]:
            return "3"
        if "F5" in mem[8:10]:
            return "4"
    if "FT_D1L1" in proc or "FT_L1D1" in proc :
        if "D2" in mem[8:10]:
            return "1"
        if "D3" in mem[8:10]:
            return "2"
        if "D4" in mem[8:10]:
            return "3"
        if "D5" in mem[8:10]:
            return "4"
    if "FT_D1L2" in proc or "FT_L2D1" in proc :
        if "L1" in mem[8:10]:
            return "1"
        if "D2" in mem[8:10]:
            return "2"
        if "D3" in mem[8:10]:
            return "3"
        if "D4" in mem[8:10] or "D1" in mem[8:10]:
            return "4"
    if "FT_B1L" in proc:
        if "B2" in mem[8:10]:
            return "1"
        if "B3" in mem[8:10]:
            return "2"
        if "B4" in mem[8:10]:
            return "3"
        if "B5" in mem[8:10]:
            return "4"
            
    print "Unknown in matchin : ",proc,mem,mem[8:10]
    return "0"

#=== FUNCTION DEFS FINISHED. NOW BACK INSIDE MAIN.

projsize={}

fprojsize = open("TPROJ_Size.txt","r")
for line in fprojsize :
    name=line.split()[0]
    size=int(line.split()[1])
    #print name,size
    projsize[name]=size

# Read input file giving all input & output memories connected to each individual processing block 
fi = open(sys.argv[1],"r")

lines = []

fp1 = open("processingmodules_inputs.dat","w") # File to contain number of input memories connected to each proc block.

for line in fi:
    if line[0]=="#" :
        continue
    if not ">" in line:
        continue
    substr = line.split(">")
    lines.append(line)
    if len(substr) != 3 :
        print "Line should have two '>' :",line
    # Get all input & output memories connected to a given proc block.
    inputmems = substr[0].split() 
    processing = substr[1] # algo step block
    outputmems = substr[2].split()
    fp1.write(processing+" has "+str(len(inputmems))+" inputs\n")
    # Store all input & outpyt memories & proc blocks, (multiple times for memories used by more than one proc block).
    for mems in inputmems :
        inputmemorymodules.append(mems)
    for mems in outputmems :
        outputmemorymodules.append(mems)
    processingmodules.append(processing)
print "Number of processing modules : ",len(processingmodules)
print "Number of input memories     : ",len(inputmemorymodules)
print "Number of output memories    : ",len(outputmemorymodules)

# Sanity check: All proc modules must have unique names to avoid confusion. Output memories should have unique names, since otherwise several proc modules will write to same memory (conflict). Input memories may not have unique names at this point, since HourGlassConfig.py doesn't clone memories if read by multiple proc modules. This will be fixed by Wires.py.
#if (len(inputmemorymodules) != len(set(inputmemorymodules))):
#    print "WARNING: Input memory module names are not unique"
if (len(outputmemorymodules) != len(set(outputmemorymodules))):
    print "WARNING: Output memory module names are not unique"
if (len(processingmodules) != len(set(processingmodules))):
    print "WARNING: Processing module names are not unique"

fp2 = open("processingmodules.dat","w") # File to contain list of all proc blocks.

# Sanity check: All input memories must also written as output memories, except for IL_ memory whose writing from DTC inputs is not modelled here.
for mem in inputmemorymodules :
    if not mem in outputmemorymodules :
        if "IL_" not in mem :
            print "Warning: ",mem," is not in outputmemorymodules"

# Sanity check: All output memories must be used as input memories, except for final memory in chain CT_.
for mem in outputmemorymodules :
    if not mem in inputmemorymodules :
        if "CT_" not in mem :
            print "Warning: ",mem," is not in inputmemorymodules"
        if "CT_" in mem:
            inputmemorymodules.append(mem) # Bodge as memorymodules.dat assumes inputmemorymodules contains all memories, not just input ones ...

VMR_nmod=0
TP_nmod=0
MP_nmod=0
FT_nmod=0
PD_nmod=0
            
# Write to file algo step and name of all processing blocks implementing that algo step.
for proc in processingmodules :
    proc=proc.strip()
    if "VMR_" in proc:
        fp2.write("VMRouter: "+proc+"\n")
        VMR_nmod+=1
    if "VMRTE_" in proc:
        fp2.write("VMRouterTE: "+proc+"\n") # Not used!
    if "VMRME_" in proc:
        fp2.write("VMRouterME: "+proc+"\n") # Not used!
    if "TE_" in proc:
        if "VMRTE_" not in proc:
            fp2.write("TrackletEngine: "+proc+"\n")
    if "TED_" in proc:
        fp2.write("TrackletEngineDisplaced: "+proc+"\n")
    if "TRE_" in proc:
        fp2.write("TripletEngine: "+proc+"\n")
    if "TC_" in proc:
        fp2.write("TrackletCalculator: "+proc+"\n")
    if "TP_" in proc:
        fp2.write("TrackletProcessor: "+proc+"\n")
        TP_nmod+=1
    if "TCD_" in proc:
        fp2.write("TrackletCalculatorDisplaced: "+proc+"\n")
    if "PR_" in proc:
        fp2.write("ProjectionRouter: "+proc+"\n")
    if "PRD_" in proc:
        fp2.write("ProjectionDiskRouter: "+proc+"\n")
    if "PT_" in proc:
        fp2.write("ProjectionTransceiver: "+proc+"\n")
    if "ME_" in proc:
        if "VMRME_" not in proc:
            fp2.write("MatchEngine: "+proc+"\n")
    if "MC_L" in proc:
        fp2.write("MatchCalculator: "+proc+"\n")
    if "MC_D" in proc:
        fp2.write("DiskMatchCalculator: "+proc+"\n")
    if "MP_" in proc:
        fp2.write("MatchProcessor: "+proc+"\n")
        MP_nmod+=1
    if "MT_" in proc:
        fp2.write("MatchTransceiver: "+proc+"\n")
    if "FT_" in proc:
        fp2.write("FitTrack: "+proc+"\n")
        FT_nmod+=1
    if "PD" in proc:
        fp2.write("PurgeDuplicate: "+proc+"\n")
        PD_nmod+=1

print "Module Type             #mod"
print "VMRouter             ","{:4.0f}".format(VMR_nmod)
print "TrackletProcessor    ","{:4.0f}".format(TP_nmod)
print "MatchProcessor       ","{:4.0f}".format(MP_nmod)
print "FitTrack             ","{:4.0f}".format(FT_nmod)
print "PurgeDuplicate       ","{:4.0f}".format(PD_nmod)


        
fp3 = open("memorymodules.dat","w") # File listing all input memories, with "n5" etc. appended to name to distinguish multiple copies of a given memory (required to avoid conflicts if it is read by multiple proc blocks).

inputmemcount=collections.OrderedDict() # Map (that remembers order elements entered) of all input memories and number of times each is used (= copies created).

shortmem=0
umem=0

IL_mem=0
SL_mem=0
SD_mem=0
AS_mem=0
VMSTEInner_mem=0
VMSTEOuter_mem=0
VMSME_mem=0
VMSTE_mem=0
SP_mem=0
SPD_mem=0
ST_mem=0
TPROJ_mem=0
TPROJ_umem=0
TPROJ_memslots=0
TPAR_mem=0
TPAR_umem=0
AP_mem=0
AP_umem=0
VMPROJ_mem=0
CM_mem=0
FM_mem=0
TF_mem=0
CT_mem=0


# Loop on input memories (which each appear multiple times if read by several proc blocks)
# N.B. HourGlassConfig.py ensures that no memory is written by more than one proc block.

# Loop over map of all input memories and number of copies of each required.

for mem in inputmemorymodules : 
    # Incremement "inputmemcount" map indicating no. of times each memory used.
    inputmemcount[mem] = inputmemcount.get(mem,0) + 1
    count = inputmemcount[mem]
    # If given memory used by multiple proc blocks, will need multiple copies of it to avoid conflicts.
    # String "n" distinguishes these.
    n=""
    if inputmemorymodules.count(mem)>1 :
        n="n"+str(count)
    if inputmemorymodules.count(mem) == 1 :
        if "AS_" in mem or "VMSTE_" in mem or "VMSME_" in mem:
            n="n1"
    found=False
    # Hard-wired [36] etc. indicate required memory bit width. Should match https://twiki.cern.ch/twiki/bin/view/CMS/HybridDataFormat but doesn't!? FIX! Should also match args of printsum() below.
    if "IL_" in mem:
        fp3.write("InputLink: "+mem+n+" [36]\n") # a.k.a. InputStub
        IL_mem+=1
        found=True
    if "SL" in mem:   
        fp3.write("StubsByLayer: "+mem+n+" [36]\n") # Not used!
        SL_mem+=1
        found=True
    if "SD" in mem:  
        fp3.write("StubsByDisk: "+mem+n+" [36]\n") # Not used!
        SD_mem+=1
        found=True
    if "AS_" in mem:
        fp3.write("AllStubs: "+mem+n+" [42]\n")
        AS_mem+=1
        found=True
    if "VMSTE_" in mem:
        fp3.write("VMStubsTE: "+mem+n+" [18]\n")
        VMSTEInner_mem+=0.5
        VMSTEOuter_mem+=0.5
        found=True
    if "VMSME_" in mem:
        fp3.write("VMStubsME: "+mem+n+" [18]\n")
        VMSME_mem+=1
        found=True
    if "SP_" in mem:
        fp3.write("StubPairs: "+mem+n+" [12]\n")
        SP_mem+=1
        found=True
    if "SPD_" in mem:
        fp3.write("StubPairsDisplaced: "+mem+n+" [12]\n")
        SPD_mem+=1
        found=True
    if "ST_" in mem:
        fp3.write("StubTriplets: "+mem+n+" [18]\n")
        ST_mem+=1
        found=True
    if "TPROJ_" in mem:
        fp3.write("TrackletProjections: "+mem+n+" [54]\n")
        found=True
        if mem in projsize :
            size=projsize[mem]
            #print mem,size
        TPROJ_mem+=1
        if size<24 :
            if size<8 :
                TPROJ_memslots+=8
            else:
                TPROJ_memslots+=24
        else :
            TPROJ_umem+=1
    if "TPAR_" in mem:
        fp3.write("TrackletParameters: "+mem+n+" [56]\n")
        TPAR_mem+=1
        found=True
    if "AP_" in mem:
        fp3.write("AllProj: "+mem+n+" [56]\n")
        AP_mem+=1
        found=True
    if "VMPROJ_" in mem:
        fp3.write("VMProjections: "+mem+n+" [13]\n")
        VMPROJ_mem+=1
        found=True
    if "CM_" in mem:
        fp3.write("CandidateMatch: "+mem+n+" [12]\n")
        CM_mem+=1
        found=True
    if "FM_" in mem:
        fp3.write("FullMatch: "+mem+n+" [36]\n")
        FM_mem+=1
        found=True
    if "TF_" in mem:
        fp3.write("TrackFit: "+mem+n+" [126]\n")
        TF_mem+=1
        found=True
    if "CT_" in mem:
        fp3.write("CleanTrack: "+mem+n+" [126]\n")
        CT_mem+=1
        found=True
    if not found :
        print "Did not print memorymodule : ",mem

# Print to screen a summary of memory use.
print "Memory type           #mems  bits wide   depth   #BX   DRAM (kbits)  #18k BRAM   #UtraRAM"


nbits=0

# N.B. hard-wired memory width, depth & #bx numbers here, but only used for memory use summary.
# FIX: Depths here are less than 18*(240MHz/40MHz)=108 assumed by C++, so would increase truncation.


(shortmem,umem,nbits)=printsum("Input Link          ",IL_mem,0,0,36,48,2,shortmem,umem,nbits)

(shortmem,umem,nbits)=printsum("All Stubs           ",AS_mem,0,0,36,128,4,shortmem,umem,nbits)

if SP_mem>0 :
    (shortmem,umem,nbits)=printsum("VM Stubs (TEIn)     ",VMSTEInner_mem,0,0,24,32,2,shortmem,umem,nbits)

if SP_mem==0 :
    VMSTEOuter_mem=42*4
    VMSME_mem=48*4

(shortmem,umem,nbits)=printsum("VM Stubs (TEOut)    ",VMSTEOuter_mem,0,0,18,128,2,shortmem,umem,nbits)

(shortmem,umem,nbits)=printsum("VM Stubs (ME)       ",VMSME_mem,0,0,18,128,8,shortmem,umem,nbits)
 
(shortmem,umem,nbits)=printsum("Stub Pair Displaced ",SPD_mem,0,0,12,16,2,shortmem,umem,nbits)

(shortmem,umem,nbits)=printsum("Stub Pair           ",SP_mem,0,0,14,32,2,shortmem,umem,nbits)

(shortmem,umem,nbits)=printsum("Stub Triplet        ",ST_mem,0,0,18,32,2,shortmem,umem,nbits)

(shortmem,umem,nbits)=printsum("TPROJ               ",TPROJ_mem,TPROJ_umem,TPROJ_memslots,72,64,2,shortmem,umem,nbits)

(shortmem,umem,nbits)=printsum("TPAR                ",TPAR_mem,TPAR_umem,0,72,64,8,shortmem,umem,nbits)

(shortmem,umem,nbits)=printsum("All Projection      ",AP_mem,AP_umem,0,64,64,4,shortmem,umem,nbits)

(shortmem,umem,nbits)=printsum("VM Projection       ",VMPROJ_mem,0,0,13,16,2,shortmem,umem,nbits)

(shortmem,umem,nbits)=printsum("Cand. Match         ",CM_mem,0,0,12,32,2,shortmem,umem,nbits)

(shortmem,umem,nbits)=printsum("Full Match          ",FM_mem,0,0,36,32,2,shortmem,umem,nbits)

(shortmem,umem,nbits)=printsum("Track Fit           ",TF_mem,0,0,122,64,2,shortmem,umem,nbits)

(shortmem,umem,nbits)=printsum("Clean Track         ",CT_mem,0,0,122,64,2,shortmem,umem,nbits)

print "Number of 18 bit memories   :",shortmem
print "Number of UltraRAM memories :",umem
#print "BRAM Megabits required using 18/36 bit memories:",shortmem*0.018
print "DRAM Megabits of memories used (x1.5):",nbits*1.5e-3

fp4 = open("wires.dat","w") # File listing for each copy of each memory, the proc block that gives it its input/output, indicating also which pin name (after ".") on this proc block is used.
  
tcin={}
trein={}
tcdin={}
prin={}
cmin={}
fmin2={}
ftin={}
tfin={}
mtout={}
ctout={}
 
# N.B. HourGlassConfig.py ensures that no output memory is written by > 1 proc module, to avoid conflicts. However, it doesn't ensure that no input memory is read by > 1 proc module, so this must be fixed by Wires.py. It does this here by cloning the memories if they are read by > 1 proc module, (appending an "n1", "n2" etc. to their name to identify each clone); and then using several output pins of the proc module that writes to this memory, with each pin writing to one clone of the memory. Furthermore, as wires.input.hourglassExtended indicates that each proc block reads/writes several memories, and a different pin of proc block must be used for each, this script names pins (after (".") in the module name).

memreadprocpairs=[]

for line in lines :
    substrs = line.split(">")
    for mem in substrs[0].split() :
        tmp=(mem.strip(),substrs[1].strip())
        memreadprocpairs.append(tmp)

memcount={}        

# Loop over map of all input memories and number of copies of each required.        
for memreadprocpair in memreadprocpairs :

    #print memreadprocpair
    mem=memreadprocpair[0]
    readproc=memreadprocpair[1]

    if mem in memcount :
        memcount[mem]+=1
    else :
        memcount[mem]=1

    count=memcount[mem]

    n=""
    if "AS_" in mem or "VMSTE_" in mem or "VMSME_" in mem:
        n="n"+str(count)

    fp4.write(mem+n+" input=> ")    

    # now we need to search for an proc module that fills this memory
    for line in lines: # Loop through file wires.input.hourglassExtended . (in_mem > proc > out_mem)
        substr = line.split(">")
        if mem in substr[2].split() : # Match with one of input memories of this proc block.
            proc=substr[1].strip()
            fp4.write(proc)
            # Where proc block reads > 1 memory, name input pin used after ".", with name based on memory it reads from.
            if "VMRTE" in mem:  # Not used!
                if "_L1" in mem:
                    fp4.write(".stuboutL1")
                if "_L2" in mem:
                    fp4.write(".stuboutL2")
                if "_L3" in mem:
                    fp4.write(".stuboutL3")
                if "_L4" in mem:
                    fp4.write(".stuboutL4")
                if "_L5" in mem:
                    fp4.write(".stuboutL5")
                if "_L6" in mem:
                    fp4.write(".stuboutL6")
            if "SD" in mem:  # Not used!
                if "_F1" in mem or "_B1" in mem:
                    fp4.write(".stuboutD1")
                if "_F2" in mem or "_B2" in mem:
                    fp4.write(".stuboutD2")
                if "_F3" in mem or "_B3" in mem:
                    fp4.write(".stuboutD3")
                if "_F4" in mem or "_B4" in mem:
                    fp4.write(".stuboutD4")
                if "_F5" in mem or "_B5" in mem:
                    fp4.write(".stuboutD5")
            if "VMSTE_" in mem:
                if "hourglass" in sys.argv[1] :
                    fp4.write(".vmstubout"+mem[8:(len(mem))]+n+" ")
                else :
                    fp4.write(".vmstubout"+mem[11:(len(mem))]+n+" ")
            if "VMSME_" in mem:
                fp4.write(".vmstubout"+mem[8:(len(mem))]+n+" ")
            if "AS_" in mem:
                fp4.write(".allstubout"+n+" ")
            if "SP_" in mem: # Only 1 memory written per TE proc block (hard-wired assumption). 
                fp4.write(".stubpairout")
            if "SPD_" in mem:
                fp4.write(".stubpairout")
            if "ST_" in mem:  # Not used!
                fp4.write(".stubtripout")
            if "TPROJ_" in mem:
                if ("PT_" in proc) :  # Not used!
                    fp4.write(".projout"+mem[13:17])
                else : 
                    if ("TPROJ_ToM" in mem) :  # Not used!
                        fp4.write(".projoutToMinus_"+mem[23:]) 
                    else : 
                        if ("TPROJ_ToP" in mem) :   # Not used!
                            fp4.write(".projoutToPlus_"+mem[22:]) 
                        else :
                            fp4.write(".projout"+mem[12:])
            if "VMPROJ_" in mem:
                if "hourglass" in sys.argv[1]:
                    fp4.write(".vmprojout"+mem[9:]+n+" ")
                else :   # Not used!
                    fp4.write(".vmprojout"+mem[14:]+n+" ")
            if "AP_" in mem:
                fp4.write(".allprojout"+n+" ")
            if "CM_" in mem:
                fp4.write(".matchout ")
            if "FM_" in mem:
                if "_ToMinus" in mem:  # Not used!
                    fp4.write(".matchoutminus")
                else:
                    if "_ToPlus" in mem:  # Not used!
                        fp4.write(".matchoutplus")
                    else:
                        mtout[proc] = mtout.get(proc,0) + 1
                        fp4.write(".matchout"+str(mtout[proc])+" ")
            if "TF_" in mem:
                fp4.write(".trackout")
            if "CT_" in mem:
                ctout[proc] = ctout.get(proc,0) + 1
                fp4.write(".trackout"+str(ctout[proc])+" ")
            if "TPAR_" in mem:
                fp4.write(".trackpar")

    # now we need to print the proc module that reads this memory
    fp4.write(" output=> ")
    proc=readproc
    fp4.write(proc)
    if "IL" in mem  and not "PHIL" in mem:
        fp4.write(".stubin")
    if "SL" in mem:  # Not used!
        if "SL1_" in mem :
            fp4.write(".stubinLink1")
        if "SL2_" in mem :
            fp4.write(".stubinLink2")
        if "SL3_" in mem :
            fp4.write(".stubinLink3")
    if "SD" in mem:  # Not used!
        if "SD1_" in mem :
             fp4.write(".stubinLink1")
        if "SD2_" in mem :
            fp4.write(".stubinLink2")
        if "SD3_" in mem :
            fp4.write(".stubinLink3")
    if "VMSTE_" in mem:
    # Each TE block has two (three) input pins (indicated by ".") taking stubs forming seed. 
        if "hourglass" in sys.argv[1]:
            if "TE_" in proc or "TP_" in proc : # Prompt tracking
                # Hard-wired coding of whether input memory has innner/outer stub in seed.
                if ( ("_D1" in mem and not ("TE_L1" in proc or "TE_L2" in proc or "TP_L1" in proc or "TP_L2" in proc)) or ("_L2" in mem and not ("TE_L1" in proc or "TP_L1" in proc)) or "_L1" in mem or ("_L3" in mem and not ("TE_L2" in proc or "TP_L2" in proc)) or "_L5" in mem or "_D3" in mem ) :
                    fp4.write(".innervmstubin")
                else :
                    fp4.write(".outervmstubin")
            elif "TED_" in proc: # Displaced tracking
                if ("_L3" in mem and not "TED_L2" in proc) or ("_L5" in mem) or ("_L2" in mem) or ("_D1" in mem):
                    fp4.write(".firstvmstubin")
                else:
                    fp4.write(".secondvmstubin")
            elif "TRE_" in proc: # 3rd layer of displaced track seeding
                fp4.write(".thirdvmstubin")
            else:
                print "UNKNOWN CONSUMER OF VMSTE! ", line
        else :  # Not used!
            if ( ("_L1" in mem and not "TE_D1" in proc and not "TE_B1" in proc) or "_L3" in mem or "_L5" in mem or "_D1" in mem or "_D3" in mem or "_B1" in mem or "_B3" in mem ) :
                fp4.write(".innervmstubin")
            else :
                fp4.write(".outervmstubin")                        
    if "VMSME_" in mem:
        fp4.write(".vmstubin")
    if "AS_" in mem:
        if ("MC_" in proc or "MP_" in proc) :
            fp4.write(".allstubin")
        else :
            # Each TC block has two (three) input pins (indicated by ".") taking stubs forming seed.
            if "TC_" in proc or "TP_" in proc:
                if ( "_L1" in mem or "_L3" in mem or "_L5" in mem or "_F1" in mem or "_F3" in mem ) :  
                    fp4.write(".innerallstubin")
                else :
                    fp4.write(".outerallstubin")
            elif "TCD_L3" in proc:
                if "_L3" in mem:
                    fp4.write(".firstallstubin")
                elif "_L4" in mem:
                    fp4.write(".secondallstubin")
                else:
                    fp4.write(".thirdallstubin")
            elif "TCD_L5" in proc:
                if "_L4" in mem:
                    fp4.write(".thirdallstubin")
                elif "_L5" in mem:
                    fp4.write(".firstallstubin")
                else:
                    fp4.write(".secondallstubin")
            elif "TCD_L2" in proc:
                if "_D1" in mem:
                    fp4.write(".thirdallstubin")
                elif "_L2" in mem:
                    fp4.write(".firstallstubin")
                else:
                    fp4.write(".secondallstubin")
            elif "TCD_D1" in proc:
                if "_L2" in mem:
                    fp4.write(".thirdallstubin")
                elif "_D1" in mem:
                    fp4.write(".firstallstubin")
                else:
                    fp4.write(".secondallstubin")
            else:
                print "UNKNOWN CONSUMER OF AS_ ",line                            
    if "SP_" in mem:
        # Count times this TC proc block reads a SP memory, since each memory must be read on separate input pin. 
        tcin[proc] = tcin.get(proc,0) + 1
        fp4.write(".stubpair"+str(tcin[proc])+"in") # Label input pin of TC proc block.
    if "SPD_" in mem:
        trein[proc] = trein.get(proc,0) + 1
        fp4.write(".stubpair"+str(trein[proc])+"in")
    if "ST_" in mem:  # Not used!
        ii1=0
        for f in tcdin :
            if f[0]==proc :
                f[1]+=1
                ii1=f[1]
            if ii1==0:
                tcdin.append([proc,1])
                ii1=1
            fp4.write(".stubtriplet"+str(ii1)+"in")
    if "TPROJ_" in mem:
        if ("PT_" in proc or "MP_" in proc) :
            fp4.write(".projin")
        else:
            prin[proc] = prin.get(proc,0) + 1
            fp4.write(".proj"+str(prin[proc])+"in")
    if "VMPROJ_" in mem:
        fp4.write(".vmprojin")
    if "AP_" in mem:
        fp4.write(".allprojin")
    if "CM_" in mem:
        cmin[proc] = cmin.get(proc,0) + 1
        fp4.write(".match"+str(cmin[proc])+"in")
    if "TF_" in mem:
        tfin[proc] = tfin.get(proc,0) + 1
        fp4.write(".trackin"+str(tfin[proc]))
    if "FM_" in mem:
        if "MT_" in proc : # Not used
            fmin2[proc] = fmin2.get(proc,0) + 1
            fp4.write(".proj"+str(fmin2[proc])+"in")
        else:
            # Track fitter has one input pin for stubs from each layer
            # FIX! This was for Tracklet. Hybrid instead has one input pin for each Pt range.
            num=matchin(proc,mem) # Get unique ID for layer number of this memory.
            fmin2[proc+num] = fmin2.get(proc+num,0) + 1
            fp4.write(".fullmatch"+num+"in"+str(fmin2[proc+num]))
    if "TPAR_" in mem:
        ftin[proc] = ftin.get(proc,0) + 1
        fp4.write(".tpar"+str(ftin[proc])+"in")
                  
    fp4.write("\n")

#special case as last processing step
for line in lines:
    if "FT_L1L2" in line :
        fp4.write("CT_L1L2 input=> PD.trackout1 output=>\n")
    if "FT_L3L4" in line :
        fp4.write("CT_L3L4 input=> PD.trackout2 output=>\n")
    if "FT_L5L6" in line :
        fp4.write("CT_L5L6 input=> PD.trackout3 output=>\n")
    if "FT_D1D2" in line :
        fp4.write("CT_D1D2 input=> PD.trackout4 output=>\n")
    if "FT_D3D4" in line :
        fp4.write("CT_D3D4 input=> PD.trackout5 output=>\n")
    if "FT_L1D1" in line :
        fp4.write("CT_L1D1 input=> PD.trackout6 output=>\n")
    if "FT_L2D1" in line :
        fp4.write("CT_L2D1 input=> PD.trackout7 output=>\n")
    if "FT_L2L3" in line :
        fp4.write("CT_L2L3 input=> PD.trackout8 output=>\n")

    
fp4.close()
