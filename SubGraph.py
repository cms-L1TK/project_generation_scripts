#!/usr/bin/env python3

import math
import sys

if (len(sys.argv) != 2 ) :
    print("Usage: SubGraph.py <proc. module>")
    print(len(sys.argv))
    print(sys.argv[0])
    print(sys.argv[1])
    exit(1)

print('Will read wires.dat')
 
#Build the geometry for layers

inputmemorymodules = []
outputmemorymodules = []

fi = open("wires.dat","r")

for line in fi:
    if not sys.argv[1] in line:
        continue
    substr = line.split("=>")
    if len(substr) != 3 :
        print(substr)
    subsubstr=substr[0].split()
    if sys.argv[1] in substr[1]:
        inputmemorymodules.append(subsubstr[0])
    if sys.argv[1] in substr[2]:
        outputmemorymodules.append(subsubstr[0])

fp = open("subgraph.dat","w")

fp.write(sys.argv[1]+"\n");

for mem in inputmemorymodules :
    fp.write("out "+mem+"\n");

for mem in outputmemorymodules :
    fp.write("in "+mem+"\n");

