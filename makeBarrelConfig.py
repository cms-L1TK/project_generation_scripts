#!/usr/bin/env python

import argparse

# Parse options
parser = argparse.ArgumentParser(description="Make a barrel-only configuration of the track finder.")
parser.add_argument("-w", "--wires", type=str, default="wires.dat", help="Reference wires.dat file (from full config)")
parser.add_argument("-p", "--process", type=str, default="processingmodules.dat", help="Reference processingmodules.dat file (from full config)")
parser.add_argument("-m", "--memories", type=str, default="memorymodules.dat", help="Reference memorymodules.dat file (from full config)")
args = parser.parse_args()

# First extract all the modules and wires for a barrel-only project
fin = open(args.wires)
outputWires = []
processingModules = []
memoryModules = []
dtcs = {}
for line in fin:
    splitLine = line.split()
    assert(len(splitLine) == 4 or len(splitLine) == 5)

    memName = splitLine[0]

    inputModule = None
    outputModule = None
    if len(splitLine) == 5:
        inputModule = splitLine[2].split(".")[0]
        outputModule = splitLine[4].split(".")[0]
    else:
        if splitLine[-1] == "output=>": # output track memory
            inputModule = splitLine[2].split(".")[0]
        else: # input link
            outputModule = splitLine[-1].split(".")[0]

    # Count the number of barrel-only InputRouters for each DTC and continue if
    # this line is not barrel-only
    dtc = None
    if inputModule is not None and inputModule.startswith("IR_"):
        assert(memName.startswith("IL_"))
        dtc = inputModule[3:]
        if dtc not in dtcs:
            dtcs[dtc] = 0
        dtcs[dtc] += 1
    if "_D" in line or "L1D1" in line or "L2D1" in line:
        if dtc is not None:
            dtcs[dtc] -= 1
        continue

    outputWires.append(line)
    memoryModules.append(memName)
    if inputModule is not None:
        processingModules.append(inputModule)
    if outputModule is not None:
        processingModules.append(outputModule)
fin.close()

# Next extract the processing module labels from the existing file
fin = open(args.process)
processLabels = {}
for line in fin:
    splitLine = line.split()
    assert(len(splitLine) == 2)

    prefix = splitLine[1].split("_")[0]
    processLabels[prefix] = splitLine[0]
fin.close()

# Then extract the memory module labels and sizes from the existing file
fin = open(args.memories)
memoryLabels = {}
memorySizes = {}
for line in fin:
    splitLine = line.split()
    assert(len(splitLine) == 3)

    prefix = splitLine[1].split("_")[0]
    memoryLabels[prefix] = splitLine[0]
    memorySizes[prefix] = splitLine[2]
fin.close()

# Write the barrel-only wires file
fout = open("barrel_wires.dat", "w")
for line in outputWires:
    output = True
    for dtc in dtcs:
        if dtcs[dtc] == 0 and dtc in line:
            output = False
            break
    if not output:
        continue
    fout.write(line)
fout.close()

# Write the barrel-only processing modules file
fout = open("barrel_processingmodules.dat", "w")
for p in sorted(set(processingModules)):
    output = True
    for dtc in dtcs:
        if dtcs[dtc] == 0 and dtc in p:
            output = False
            break
    if not output:
        continue
    prefix = p.split("_")[0]
    fout.write(processLabels[prefix] + " " + p + "\n")
fout.close()

# Write the barrel-only memory modules file
fout = open("barrel_memorymodules.dat", "w")
for m in sorted(set(memoryModules)):
    output = True
    for dtc in dtcs:
        if dtcs[dtc] == 0 and dtc in m:
            output = False
            break
    if not output:
        continue
    prefix = m.split("_")[0]
    fout.write(memoryLabels[prefix] + " " + m + " " + memorySizes[prefix] + "\n")
fout.close()
