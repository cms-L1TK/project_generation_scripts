#!/usr/bin/env python

import math

fi = open("memorymodules.dat","r")

memorymodules=[]
memorycounts=[0,0,0,0,0,0,0,0,0,0,0]

for line in fi :
    splitline=line.split(" ")
    print "Line:",splitline
    lenold=len(memorymodules)
    if (splitline[0]=="InputLink:") :
        memorymodules.append([1,splitline[1]])
    if (splitline[0]=="StubsByLayer:") :
        memorymodules.append([2,splitline[1]])
    if (splitline[0]=="StubsByDisk:") :
        memorymodules.append([2,splitline[1]])
    if (splitline[0]=="AllStubs:" or splitline[0]=="VMStubsTE:" or splitline[0]=="VMStubsME:") :        
        basename=splitline[1].split("n")[0]
        number=0
        if (len(splitline[1].split("n"))>1) :
            number=splitline[1].split("n")[1]
        found=False
        for x in memorymodules :
            if (basename==x[1]) :
                found=True
                if (number>x[2]) :
                    x[2]=number
        if (not found) :
            memorymodules.append([3,basename,number])
    if (splitline[0]=="StubPairs:") :
        memorymodules.append([4,splitline[1]])
    if (splitline[0]=="TrackletParameters:") :
        memorymodules.append([5,splitline[1]])
    if (splitline[0]=="TrackletProjections:") :
        if "From" not in splitline[1] :
            memorymodules.append([5,splitline[1]])
        else :
            memorymodules.append([6,splitline[1]])
    if (splitline[0]=="AllProj:") :
        memorymodules.append([7,splitline[1]])
    if (splitline[0]=="VMProjections:") :
        memorymodules.append([7,splitline[1]])
    if (splitline[0]=="CandidateMatch:") :
        memorymodules.append([8,splitline[1]])
    if (splitline[0]=="FullMatch:") :
        if "From" not in splitline[1] :
            basename=splitline[1].split("n")[0]
            number=0
            if (len(splitline[1].split("n"))>1) :
                number=splitline[1].split("n")[1]
            found=False
            for x in memorymodules :
                if (basename==x[1]) :
                    found=True
                    if (number>x[2]) :
                        x[2]=number
            if (not found) :
                memorymodules.append([9,basename,number])
        else :
            basename=splitline[1].split("n")[0]
            number=0
            if (len(splitline[1].split("n"))>1) :
                number=splitline[1].split("n")[1]
            found=False
            for x in memorymodules :
                if (basename==x[1]) :
                    found=True
                    if (number>x[2]) :
                        x[2]=number
            if (not found) :
                memorymodules.append([10,basename,number])
    if (splitline[0]=="TrackFit:") :
        memorymodules.append([11,splitline[1]])

    if (lenold != len(memorymodules)) :    
        memorycounts[memorymodules[len(memorymodules)-1][0]-1]+=1

for x in memorymodules :
    print x

print memorycounts



fi = open("processingmodules.dat","r")

processingmodules=[]
processingcounts=[0,0,0,0,0,0,0,0,0,0]

for line in fi :
    splitline=line.split(" ")
    print "Line:",splitline
    lenold=len(processingmodules)
    if (splitline[0]=="LayerRouter:") :
        processingmodules.append([1,splitline[1]])
    if (splitline[0]=="DiskRouter:") :
        processingmodules.append([1,splitline[1]])
    if (splitline[0]=="VMRouter:") :
        processingmodules.append([2,splitline[1]])
    if (splitline[0]=="TrackletEngine:") :
        processingmodules.append([3,splitline[1]])
    if (splitline[0]=="TrackletCalculator:") :
        processingmodules.append([4,splitline[1]])
    if (splitline[0]=="ProjectionTransceiver:") :
        processingmodules.append([5,splitline[1]])
    if (splitline[0]=="ProjectionRouter:") :
        processingmodules.append([6,splitline[1]])
    if (splitline[0]=="MatchEngine:") :
        processingmodules.append([7,splitline[1]])
    if (splitline[0]=="MatchCalculator:") :
        processingmodules.append([8,splitline[1]])
    if (splitline[0]=="MatchTransceiver:") :
        processingmodules.append([9,splitline[1]])
    if (splitline[0]=="FitTrack:") :
        processingmodules.append([10,splitline[1]])

    if (lenold != len(processingmodules)) :    
        processingcounts[processingmodules[len(processingmodules)-1][0]-1]+=1

for x in processingmodules :
    print "processingmodules : ",x

print processingcounts

xmemories=[0.005,0.065,0.145,0.26,0.37,0.495,0.60,0.72,0.82,0.90,0.975]
dxmemories=[0.015,0.02,0.03,0.05,0.05,0.05,0.05,0.045,0.03,0.025,0.025]
memories=[0,0,0,0,0,0,0,0,0,0,0]

fo = open("diagram.dat","w")

for module in memorymodules :
    num=memories[module[0]-1]
    memories[module[0]-1]+=1
    y=(0.5+num)/(memorycounts[module[0]-1])
    x=xmemories[module[0]-1]
    dx=dxmemories[module[0]-1]
    module.append([x,y,x+dx,y])
    fo.write("Memory "+module[1])
    fo.write(" "+str(x)+" "+str(y)+" "+str(x+dx)+" "+str(y)+"\n")
    print module


xprocessing=[0.03,0.10,0.20,0.32,0.44,0.56,0.67,0.78,0.865,0.945]
dxprocessing=[0.02,0.03,0.05,0.03,0.03,0.025,0.04,0.025,0.02,0.02]
processing=[0,0,0,0,0,0,0,0,0,0]

for module in processingmodules :
    num=processing[module[0]-1]
    processing[module[0]-1]+=1
    y=(0.5+num)/(processingcounts[module[0]-1])
    x=xprocessing[module[0]-1]
    dx=dxprocessing[module[0]-1]
    module.append([x,y,x+dx,y])
    fo.write("Process "+module[1].split("\n")[0])
    fo.write(" "+str(x)+" "+str(y)+" "+str(x+dx)+" "+str(y)+"\n")
    print module

fi = open("wires.dat","r")
for line in fi :
    memory=line.split(" ")[0]
    if (memory[len(memory)-2]=="n" or memory[len(memory)-3]=="n") :
        memory=memory.split("n")[0]
    inprocess=line.split("input=> ")[1].split(" ")[0].split(".")[0]    
    outprocess=line.split("output=> ")[1].split("\n")[0].split(".")[0]

    print memory+" in: "+inprocess+" out: "+outprocess

    #Find the memory module
    memmodule=[]
    for mem in memorymodules :
        if (mem[1]==memory) :
            memmodule=mem
    if (memmodule==[]) :
        print "Could not find memorymodule: ",memory
        print "Will terminate"
        exit()

    last=len(memmodule)-1
        
    #Find the input processing module    
    if (inprocess!="") :
        procmodule=[]        
        for proc in processingmodules :
            #print "Comparing ",proc[1].split("\n")[0]," - ",inprocess
            if (proc[1].split("\n")[0]==inprocess) :
                procmodule=proc
        if (procmodule==[]) :
            print "Could not find in processingmodule: ",inprocess
            print "Will terminate"
            exit()
        print "memmodule[0], procmodule[0] : ", memmodule[0],procmodule[0]    
        if (memmodule[0]==procmodule[0]+1 or memmodule[0]==procmodule[0]) :
            fo.write("Line "+str(procmodule[2][2])+" "+str(procmodule[2][3]))
            fo.write(" "+str(memmodule[last][0])+" "+str(memmodule[last][1])+"\n")
        

    #Find the output processing module    
    if (outprocess!="") :    
        procmodule=[]        
        for proc in processingmodules :
            #print "Comparing ",proc[1].split("\n")[0]," - ",outprocess
            if (proc[1].split("\n")[0]==outprocess) :
                procmodule=proc
        if (procmodule==[]) :
            print "Could not find outprocessingmodule: ",outprocess
            print "Will terminate"
            exit()
        if (memmodule[0]==procmodule[0] or memmodule[0]==procmodule[0]-1) :
            fo.write("Line "+str(procmodule[2][0])+" "+str(procmodule[2][1]))
            fo.write(" "+str(memmodule[last][2])+" "+str(memmodule[last][3])+"\n")
