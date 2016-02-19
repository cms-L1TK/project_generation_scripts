#!/usr/bin/env python

import math
import sys

if (len(sys.argv) != 2 ) :
    print "Usage: SubProject.py wires.D3|D4|D3D4|D5D6"
    exit(1)

print 'Will process', sys.argv[1]

regions = []
vregions = []

if sys.argv[1]=="D5D6":
    regions = ["D5","D6"] 
    vregions = ["D1","D2","D3","D4","D7","D8","L1L2","F1L","_L1","_L2","_L3","_L4","_L5","_L6","_B1","_B2"]

if sys.argv[1]=="D3":
    regions = ["D3"] 
    vregions = ["D1","D2","D4","D5","D6","D7","D8","_F1","_F2","_F3","_F4","_F5"]

if sys.argv[1]=="D4":
    regions = ["D4"] 
    vregions = ["D1","D2","D3","D5","D6","D7","D8","_F1","_F2","_F3","_F4","_F5"]

if sys.argv[1]=="D3D4":
    regions = ["D3","D4"] 
    vregions = ["D1","D2","D5","D6","D7","D8","_F1","_F2","_F3","_F4","_F5","_B1","_B2","_B3","_B4","_B5"]


print 'Will read wires.input.fullsector and select ',regions
 

fi = open("wires.input.fullsector","r")

fo = open("wires.reduced","w")

for line in fi:
    match=False
    for region in regions:
        if region in line:
            match=True;
    if not match:
        continue
    substr=line.split()
    countgt=0
    inputmem=[]
    outputmem=[]
    cmd=""
    for str in substr:
        if str == ">" :
            countgt+=1
            continue
        if countgt==1 :
            cmd=str
            continue
        veto=False
        for vregion in vregions:
            if vregion in str:
                if not "SD" in str:
                    veto=True;
        if not veto:
            if countgt==0:
                inputmem.append(str)
            if countgt==2:
                outputmem.append(str)
                
    if len(inputmem)!=0:
        if len(outputmem)!=0:
            for str in inputmem:
                fo.write(str+" ")
            fo.write(" > "+cmd+" >")
            for str in outputmem:
                fo.write(" "+str)
            fo.write("\n")




