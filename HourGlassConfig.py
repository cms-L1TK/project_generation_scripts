#!/usr/bin/env python

import math
import sys

NSector = 9
rcrit = 55.0

rinvmax=0.0057

#If true it will use a MatchProcessor to replace PRs, MEs, MC
combined=False 

two_pi=8*math.atan(1.0)

rlayers = [25.0 , 37.0 , 50.0, 68.0, 80.0, 110.0 ]

rmaxdisk=110.0

rpsmax = 67.0

zdisks = [131.2, 155.0, 185.34, 221.62, 265.0 ]

nallstubslayers = [ 8, 4, 4, 4, 4, 4 ]

nvmtelayers = [4, 8, 4, 8, 4, 8 ]

nallprojlayers = [ 8, 4, 4, 4, 4, 4 ]

nvmmelayers = [4, 8, 8, 8, 8, 8 ]

nallstubsdisks = [4, 4, 4, 4, 4 ]

nvmtedisks = [4, 4, 4, 4, 4 ]

nallprojdisks = [ 4, 4, 4, 4, 4 ]

nvmmedisks = [8, 4, 4, 4, 4 ]

#for seeding in L1D1 L2D1
nallstubsoverlaplayers = [ 8, 4] 
nvmteoverlaplayers = [2, 2]

nallstubsoverlapdisks = [4] 
nvmteoverlapdisks = [4]


def phiRange():

    phicrit=math.asin(0.5*rinvmax*rcrit)

    phimax=0.0
    
    for r in rlayers :
        dphi=math.fabs(math.asin(0.5*rinvmax*r)-phicrit)
        if dphi>phimax :
            phimax=dphi
    
    return two_pi/NSector+2*phimax


phirange=phiRange()

print "phi ranage : ",phirange

def split(a, n):
    k, m = divmod(len(a), n)
    return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in xrange(n))

def letter(i) :
    if i==1 :
        return "A"
    if i==2 :
        return "B"
    if i==3 :
        return "C"
    if i==4 :
        return "D"
    if i==5 :
        return "E"
    if i==6 :
        return "F"
    if i==7 :
        return "G"
    if i==8 :
        return "H"
    if i==9 :
        return "I"
    if i==10 :
        return "J"
    if i==11 :
        return "K"
    if i==12 :
        return "L"
    if i==13 :
        return "M"
    if i==14 :
        return "N"
    if i==15 :
        return "O"
    return "letter can not handle input = "+str(i)


def letteroverlap(i) :
    if i==1 :
        return "X"
    if i==2 :
        return "Y"
    if i==3 :
        return "Z"
    if i==4 :
        return "W"
    if i==5 :
        return "Q"
    if i==6 :
        return "R"
    if i==7 :
        return "S"
    if i==8 :
        return "T"
    return "letteroverlap can not handle input = "+str(i)

def rinv(ilayer,phiinner,phiouter) :
    return 2*math.sin(phiinner-phiouter)/(rlayers[ilayer-1]-rlayers[ilayer])

def rinvdisk(idisk,phiinner,phiouter) :
    return 2*math.sin(phiinner-phiouter)/(rpsmax*(zdisks[idisk-1]-zdisks[idisk])/zdisks[idisk-1])

def validtepair(ilayer,ivminner,ivmouter) :

    dphiinner=phirange/nallstubslayers[ilayer-1]/nvmtelayers[ilayer-1]
    dphiouter=phirange/nallstubslayers[ilayer]/nvmtelayers[ilayer]

    phiinner1=dphiinner*ivminner
    phiinner2=phiinner1+dphiinner
    
    phiouter1=dphiouter*ivmouter
    phiouter2=phiouter1+dphiouter

    rinv11=rinv(ilayer,phiinner1,phiouter1)
    rinv12=rinv(ilayer,phiinner1,phiouter2)
    rinv21=rinv(ilayer,phiinner2,phiouter1)
    rinv22=rinv(ilayer,phiinner2,phiouter2)
    
    #print rinv11,rinv12,rinv21,rinv22

    if rinv11>rinvmax and rinv12>rinvmax and rinv21>rinvmax and rinv22>rinvmax :
        return False

    if rinv11<-rinvmax and rinv12<-rinvmax and rinv21<-rinvmax and rinv22<-rinvmax :
        return False
    
    return True

def validtepairdisk(idisk,ivminner,ivmouter) :

    dphiinner=phirange/nallstubsdisks[idisk-1]/nvmtedisks[idisk-1]
    dphiouter=phirange/nallstubsdisks[idisk]/nvmtedisks[idisk]

    phiinner1=dphiinner*ivminner
    phiinner2=phiinner1+dphiinner
    
    phiouter1=dphiouter*ivmouter
    phiouter2=phiouter1+dphiouter

    rinv11=rinvdisk(idisk,phiinner1,phiouter1)
    rinv12=rinvdisk(idisk,phiinner1,phiouter2)
    rinv21=rinvdisk(idisk,phiinner2,phiouter1)
    rinv22=rinvdisk(idisk,phiinner2,phiouter2)
    
    #print rinv11,rinv12,rinv21,rinv22

    if rinv11>rinvmax and rinv12>rinvmax and rinv21>rinvmax and rinv22>rinvmax :
        return False

    if rinv11<-rinvmax and rinv12<-rinvmax and rinv21<-rinvmax and rinv22<-rinvmax :
        return False
    
    return True


def validtepairoverlap(ilayer,ivminner,ivmouter) :

    dphiinner=phirange/nallstubsoverlaplayers[ilayer-1]/nvmteoverlaplayers[ilayer-1]
    dphiouter=phirange/nallstubsoverlapdisks[0]/nvmteoverlapdisks[0]

    phiinner1=dphiinner*ivminner
    phiinner2=phiinner1+dphiinner
    
    phiouter1=dphiouter*ivmouter
    phiouter2=phiouter1+dphiouter

    rinv11=rinv(ilayer,phiinner1,phiouter1)
    rinv12=rinv(ilayer,phiinner1,phiouter2)
    rinv21=rinv(ilayer,phiinner2,phiouter1)
    rinv22=rinv(ilayer,phiinner2,phiouter2)
    
    #print rinv11,rinv12,rinv21,rinv22

    if rinv11>rinvmax and rinv12>rinvmax and rinv21>rinvmax and rinv22>rinvmax :
        return False

    if rinv11<-rinvmax and rinv12<-rinvmax and rinv21<-rinvmax and rinv22<-rinvmax :
        return False
    
    return True



def phiproj(ilayer,phi,rinv,projlayer) :

    dphi=math.asin(0.5*rlayers[projlayer-1]*rinv)-math.asin(0.5*rlayers[ilayer-1]*rinv)

    return phi+dphi;


def phiprojdisk(idisk,phi,rinv,projdisk) :

    rproj=min(rmaxdisk,rpsmax*zdisks[projdisk-1]/zdisks[idisk-1])
    
    dphi=math.asin(0.5*rproj*rinv)-math.asin(0.5*rpsmax*rinv)

    return phi+dphi;

def phiprojdisktolayer(idisk,phi,rinv,projlayer) :

    dphi=math.asin(0.5*rlayers[projlayer-1]*rinv)-math.asin(0.5*rmaxdisk*rinv)

    return phi+dphi;

def phiprojlayertodisk(ilayer,phi,rinv,projdisk) :

    dphi=math.asin(0.5*rmaxdisk*rinv)-math.asin(0.5*rlayers[ilayer-1]*rinv)

    return phi+dphi;

    

def phiprojrange(ilayer, projlayer, splist) :

    projrange=[]
    
    for spname in splist :
        ivminner=int(spname.split("PHI")[1].split("_")[0][1:])
        ivmouter=int(spname.split("PHI")[2][1:])
        #print projlayer, spname, spname.split("PHI"),ivminner,ivmouter

        dphiinner=phirange/nallstubslayers[ilayer-1]/nvmtelayers[ilayer-1]
        dphiouter=phirange/nallstubslayers[ilayer]/nvmtelayers[ilayer]

        phiinner1=dphiinner*ivminner
        phiinner2=phiinner1+dphiinner
    
        phiouter1=dphiouter*ivmouter
        phiouter2=phiouter1+dphiouter

        rinv11=rinv(ilayer,phiinner1,phiouter1)
        rinv12=rinv(ilayer,phiinner1,phiouter2)
        rinv21=rinv(ilayer,phiinner2,phiouter1)
        rinv22=rinv(ilayer,phiinner2,phiouter2)

        minrinv=rinv11
        maxrinv=rinv11

        if rinv12<minrinv :
            minrinv=rinv12
        if rinv12>maxrinv :
            maxrinv=rinv12
            
        if rinv21<minrinv :
            minrinv=rinv21
        if rinv21>maxrinv :
            maxrinv=rinv21

        if rinv22<minrinv :
            minrinv=rinv22
        if rinv22>maxrinv :
            maxrinv=rinv22

        if minrinv<-rinvmax :
            minrinv=-rinvmax

        if maxrinv>rinvmax :
            maxrinv=rinvmax

        if minrinv>rinvmax :
            minrinv=rinvmax

            
        phiminproj1=phiproj(ilayer,phiinner1,minrinv,projlayer)
        phiminproj2=phiproj(ilayer+1,phiouter1,minrinv,projlayer)

        phimin=min(phiminproj1,phiminproj2)-0.02
        
        phimaxproj1=phiproj(ilayer,phiinner2,maxrinv,projlayer)
        phimaxproj2=phiproj(ilayer+1,phiouter2,maxrinv,projlayer)

        phimax=max(phimaxproj1,phimaxproj2)+0.02

        if len(projrange)==0 :
            projrange=[phimin,phimax]
        else :
            projrange[0]=min(projrange[0],phimin)
            projrange[1]=max(projrange[1],phimax)


    return projrange


def phiprojrangedisk(idisk, projdisk, splist) :

    projrange=[]
    
    for spname in splist :
        ivminner=int(spname.split("PHI")[1].split("_")[0][1:])
        ivmouter=int(spname.split("PHI")[2][1:])
        #print projlayer, spname, spname.split("PHI"),ivminner,ivmouter

        dphiinner=phirange/nallstubsdisks[idisk-1]/nvmtedisks[idisk-1]
        dphiouter=phirange/nallstubsdisks[idisk]/nvmtedisks[idisk]

        phiinner1=dphiinner*ivminner
        phiinner2=phiinner1+dphiinner
    
        phiouter1=dphiouter*ivmouter
        phiouter2=phiouter1+dphiouter

        rinv11=rinvdisk(idisk,phiinner1,phiouter1)
        rinv12=rinvdisk(idisk,phiinner1,phiouter2)
        rinv21=rinvdisk(idisk,phiinner2,phiouter1)
        rinv22=rinvdisk(idisk,phiinner2,phiouter2)

        minrinv=rinv11
        maxrinv=rinv11

        if rinv12<minrinv :
            minrinv=rinv12
        if rinv12>maxrinv :
            maxrinv=rinv12
            
        if rinv21<minrinv :
            minrinv=rinv21
        if rinv21>maxrinv :
            maxrinv=rinv21

        if rinv22<minrinv :
            minrinv=rinv22
        if rinv22>maxrinv :
            maxrinv=rinv22

        if minrinv<-rinvmax :
            minrinv=-rinvmax

        if maxrinv>rinvmax :
            maxrinv=rinvmax

        phiminproj1=phiprojdisk(idisk,phiinner1,minrinv,projdisk)
        phiminproj2=phiprojdisk(idisk+1,phiouter1,minrinv,projdisk)

        phimin=min(phiminproj1,phiminproj2)
        
        phimaxproj1=phiprojdisk(idisk,phiinner2,maxrinv,projdisk)
        phimaxproj2=phiprojdisk(idisk+1,phiouter2,maxrinv,projdisk)

        phimax=max(phimaxproj1,phimaxproj2)

        if len(projrange)==0 :
            projrange=[phimin,phimax]
        else :
            projrange[0]=min(projrange[0],phimin)
            projrange[1]=max(projrange[1],phimax)


    return projrange

def phiprojrangedisktolayer(idisk,projlayer,splist) :

    projrange=[]
    
    for spname in splist :
        ivminner=int(spname.split("PHI")[1].split("_")[0][1:])
        ivmouter=int(spname.split("PHI")[2][1:])
        #print projlayer, spname, spname.split("PHI"),ivminner,ivmouter

        dphiinner=phirange/nallstubsdisks[idisk-1]/nvmtedisks[idisk-1]
        dphiouter=phirange/nallstubsdisks[idisk]/nvmtedisks[idisk]

        phiinner1=dphiinner*ivminner
        phiinner2=phiinner1+dphiinner
    
        phiouter1=dphiouter*ivmouter
        phiouter2=phiouter1+dphiouter

        rinv11=rinvdisk(idisk,phiinner1,phiouter1)
        rinv12=rinvdisk(idisk,phiinner1,phiouter2)
        rinv21=rinvdisk(idisk,phiinner2,phiouter1)
        rinv22=rinvdisk(idisk,phiinner2,phiouter2)

        minrinv=rinv11
        maxrinv=rinv11

        if rinv12<minrinv :
            minrinv=rinv12
        if rinv12>maxrinv :
            maxrinv=rinv12
            
        if rinv21<minrinv :
            minrinv=rinv21
        if rinv21>maxrinv :
            maxrinv=rinv21

        if rinv22<minrinv :
            minrinv=rinv22
        if rinv22>maxrinv :
            maxrinv=rinv22

        if minrinv<-rinvmax :
            minrinv=-rinvmax

        if maxrinv>rinvmax :
            maxrinv=rinvmax

        phiminproj1=phiprojdisktolayer(idisk,phiinner1,minrinv,projlayer)
        phiminproj2=phiprojdisktolayer(idisk+1,phiouter1,minrinv,projlayer)

        phimin=min(phiminproj1,phiminproj2)
        
        phimaxproj1=phiprojdisktolayer(idisk,phiinner2,maxrinv,projlayer)
        phimaxproj2=phiprojdisktolayer(idisk+1,phiouter2,maxrinv,projlayer)

        phimax=max(phimaxproj1,phimaxproj2)

        if len(projrange)==0 :
            projrange=[phimin,phimax]
        else :
            projrange[0]=min(projrange[0],phimin)
            projrange[1]=max(projrange[1],phimax)


    return projrange


def phiprojrangelayertodisk(ilayer,projdisk,splist) :

    projrange=[]
    
    for spname in splist :
        ivminner=int(spname.split("PHI")[1].split("_")[0][1:])
        ivmouter=int(spname.split("PHI")[2][1:])
        #print projlayer, spname, spname.split("PHI"),ivminner,ivmouter

        dphiinner=phirange/nallstubslayers[ilayer-1]/nvmtelayers[ilayer-1]
        dphiouter=phirange/nallstubslayers[ilayer]/nvmtelayers[ilayer]

        phiinner1=dphiinner*ivminner
        phiinner2=phiinner1+dphiinner
    
        phiouter1=dphiouter*ivmouter
        phiouter2=phiouter1+dphiouter

        rinv11=rinv(ilayer,phiinner1,phiouter1)
        rinv12=rinv(ilayer,phiinner1,phiouter2)
        rinv21=rinv(ilayer,phiinner2,phiouter1)
        rinv22=rinv(ilayer,phiinner2,phiouter2)

        minrinv=rinv11
        maxrinv=rinv11

        if rinv12<minrinv :
            minrinv=rinv12
        if rinv12>maxrinv :
            maxrinv=rinv12
            
        if rinv21<minrinv :
            minrinv=rinv21
        if rinv21>maxrinv :
            maxrinv=rinv21

        if rinv22<minrinv :
            minrinv=rinv22
        if rinv22>maxrinv :
            maxrinv=rinv22

        if minrinv<-rinvmax :
            minrinv=-rinvmax

        if maxrinv>rinvmax :
            maxrinv=rinvmax

        if minrinv>maxrinv :
            minrinv=maxrinv

        if maxrinv<minrinv :
            maxrinv=minrinv

        #print minrinv, maxrinv
            
        phiminproj1=phiprojlayertodisk(ilayer,phiinner1,minrinv,projdisk)
        phiminproj2=phiprojlayertodisk(ilayer+1,phiouter1,minrinv,projdisk)

        phimin=min(phiminproj1,phiminproj2)
        
        phimaxproj1=phiprojlayertodisk(ilayer,phiinner2,maxrinv,projdisk)
        phimaxproj2=phiprojlayertodisk(ilayer+1,phiouter2,maxrinv,projdisk)

        phimax=max(phimaxproj1,phimaxproj2)

        if len(projrange)==0 :
            projrange=[phimin,phimax]
        else :
            projrange[0]=min(projrange[0],phimin)
            projrange[1]=max(projrange[1],phimax)


    return projrange

def phiprojrangeoverlaplayertodisk(ilayer,projdisk,splist) :

    projrange=[]
    
    for spname in splist :
        ivminner=int(spname.split("PHI")[1].split("_")[0][1:])
        ivmouter=int(spname.split("PHI")[2][1:])
        #print projlayer, spname, spname.split("PHI"),ivminner,ivmouter

        dphiinner=phirange/nallstubslayers[ilayer-1]/nvmtelayers[ilayer-1]
        dphiouter=phirange/nallstubsdisks[0]/nvmtedisks[0]

        phiinner1=dphiinner*ivminner
        phiinner2=phiinner1+dphiinner
    
        phiouter1=dphiouter*ivmouter
        phiouter2=phiouter1+dphiouter

        rinv11=rinv(ilayer,phiinner1,phiouter1)
        rinv12=rinv(ilayer,phiinner1,phiouter2)
        rinv21=rinv(ilayer,phiinner2,phiouter1)
        rinv22=rinv(ilayer,phiinner2,phiouter2)

        minrinv=rinv11
        maxrinv=rinv11

        if rinv12<minrinv :
            minrinv=rinv12
        if rinv12>maxrinv :
            maxrinv=rinv12
            
        if rinv21<minrinv :
            minrinv=rinv21
        if rinv21>maxrinv :
            maxrinv=rinv21

        if rinv22<minrinv :
            minrinv=rinv22
        if rinv22>maxrinv :
            maxrinv=rinv22

        if minrinv<-rinvmax :
            minrinv=-rinvmax

        if maxrinv>rinvmax :
            maxrinv=rinvmax

        if minrinv>maxrinv :
            minrinv=maxrinv

        if maxrinv<minrinv :
            maxrinv=minrinv

        #print minrinv, maxrinv
            
        phiminproj1=phiprojlayertodisk(ilayer,phiinner1,minrinv,projdisk)
        phiminproj2=phiprojlayertodisk(ilayer+1,phiouter1,minrinv,projdisk)

        phimin=min(phiminproj1,phiminproj2)
        
        phimaxproj1=phiprojlayertodisk(ilayer,phiinner2,maxrinv,projdisk)
        phimaxproj2=phiprojlayertodisk(ilayer+1,phiouter2,maxrinv,projdisk)

        phimax=max(phimaxproj1,phimaxproj2)

        if len(projrange)==0 :
            projrange=[phimin,phimax]
        else :
            projrange[0]=min(projrange[0],phimin)
            projrange[1]=max(projrange[1],phimax)


    return projrange

def readUnusedProj() :
    fi = open("unusedproj.txt","r")

    unusedproj=[]

    for line in fi:
        unusedproj.append(line.split('\n')[0])

    return unusedproj

def findInputLinks(dtcphirange) :

    fi = open(dtcphirange,"r")

    ilinks=[]
    
    for line in fi:
        dtcname=line.split()[0]
        layerdisk=int(line.split()[1])
        phimin=float(line.split()[2])
        phimax=float(line.split()[3])
        #print "Line: ",dtcname,layerdisk,phimin,phimax
        phimin1=phimin-two_pi/9.0+0.5*phirange
        phimax1=phimax-two_pi/9.0+0.5*phirange
        phimin2=phimin+0.5*phirange
        phimax2=phimax+0.5*phirange

        #print "phimin1, phimax1 : ",phimin1,phimax1
        
        if layerdisk<7 :
            layer=layerdisk
            #print "layer : ",layer
            nallstubs=nallstubslayers[layer-1]
            dphi=phirange/nallstubs
            for iallstub in range(0,nallstubs) :
                phiminallstub=iallstub*dphi
                phimaxallstub=phiminallstub+dphi
                #print "Allstub phimin,max :",phiminallstub,phimaxallstub
                if layer==3 :
                    print "dtcname iallstub phiminallstub phimaxallstub :",dtcname,iallstub,phiminallstub,phimaxallstub
                    print "phimin1 phimax1 :",phimin1,phimax1
                    print "phimin2 phimax2 :",phimin2,phimax2
                if (phiminallstub<phimax1 and phimaxallstub>phimin1) or (phiminallstub<phimax2 and phimaxallstub>phimin2) :
                    if iallstub<nallstubs/2 :
                        il="IL_L"+str(layer)+"PHI"+letter(iallstub+1)+"_"+dtcname+"_A"
                        if layer==3 :
                            print "Add to",il
                        ilinks.append(il)
                        #print "Inputlink : ",il
                    if iallstub>=nallstubs/2 :
                        il="IL_L"+str(layer)+"PHI"+letter(iallstub+1)+"_"+dtcname+"_B"
                        if layer==3 :
                            print "Add to",il
                        ilinks.append(il)
                        #print "Inputlink : ",il
        else :
            disk=layerdisk-6
            #print "layerdisk disk : ",layerdisk,disk
            nallstubs=nallstubsdisks[disk-1]
            dphi=phirange/nallstubs
            for iallstub in range(0,nallstubs) :
                phiminallstub=iallstub*dphi
                phimaxallstub=phiminallstub+dphi
                #print "Allstub phimin,max :",phiminallstub,phimaxallstub
                if (phiminallstub<phimax1 and phimaxallstub>phimin1) or (phiminallstub<phimax2 and phimaxallstub>phimin2 :) :
                    if iallstub<nallstubs/2 :
                        il="IL_D"+str(disk)+"PHI"+letter(iallstub+1)+"_"+dtcname+"_A"
                        ilinks.append(il)
                        #print "Inputlink : ",il
                    if iallstub>=nallstubs/2 :
                        il="IL_D"+str(disk)+"PHI"+letter(iallstub+1)+"_"+dtcname+"_B"
                        ilinks.append(il)
                        #print "Inputlink : ",il

    return ilinks

inputlinks=findInputLinks("dtcphirange.txt")

print "Inputlinks :",len(inputlinks),inputlinks

unusedproj=readUnusedProj()

print "Unusedproj :",unusedproj


fp = open("wires.input.hourglass","w")

#
# Do the VM routers for the TE in the layers
#

for ilayer in range(1,7) :
    print "layer =",ilayer,"allstub memories",nallstubslayers[ilayer-1]
    fp.write("\n")
    fp.write("#\n")
    fp.write("# VMRouters for the TEs in layer "+str(ilayer)+" \n")
    fp.write("#\n")
    for iallstubmem in range(1,nallstubslayers[ilayer-1]+1) :
        allstubsmemname="L"+str(ilayer)+"PHI"+letter(iallstubmem)
        for il in inputlinks :
            if allstubsmemname in il :
                fp.write(il+" ")
        fp.write("> VMR_L"+str(ilayer)+"PHI"+letter(iallstubmem)+" > ")
        fp.write("AS_L"+str(ilayer)+"PHI"+letter(iallstubmem))
        for ivm in range(1,nvmmelayers[ilayer-1]+1) :
            fp.write(" VMSME_L"+str(ilayer)+"PHI"+letter(iallstubmem)+str((iallstubmem-1)*nvmmelayers[ilayer-1]+ivm))
        for ivm in range(1,nvmtelayers[ilayer-1]+1) :
            fp.write(" VMSTE_L"+str(ilayer)+"PHI"+letter(iallstubmem)+str((iallstubmem-1)*nvmtelayers[ilayer-1]+ivm))
        if ilayer in range(1,3) :
            for ivm in range(1,nvmteoverlaplayers[ilayer-1]+1) :
                fp.write(" VMSTE_L"+str(ilayer)+"PHI"+letteroverlap(iallstubmem)+str((iallstubmem-1)*nvmteoverlaplayers[ilayer-1]+ivm))
        
        fp.write("\n\n")

#
# Do the VM routers for the TE in the overlap layers
#

#for ilayer in range(1,3) :
#    print "layer =",ilayer,"allstub memories",nallstubslayers[ilayer-1]
#    fp.write("\n")
#    fp.write("#\n")
#    fp.write("# VMRouters for the TEs in overlap layer "+str(ilayer)+" \n")
#    fp.write("#\n")
#    for iallstubmem in range(1,nallstubsoverlaplayers[ilayer-1]+1) :
#        allstubsmemname="L"+str(ilayer)+"PHI"+letter(iallstubmem)
#        for il in inputlinks :
#            if allstubsmemname in il :
#                fp.write(il+" ")
#        fp.write("> VMRTE_L"+str(ilayer)+"PHI"+letteroverlap(iallstubmem)+" > "#)
#        fp.write("AS_L"+str(ilayer)+"PHI"+letteroverlap(iallstubmem))
#        for ivm in range(1,nvmteoverlaplayers[ilayer-1]+1) :
#            fp.write(" VMSTE_L"+str(ilayer)+"PHI"+letteroverlap(iallstubmem)+str((iallstubmem-1)*nvmteoverlaplayers[ilayer-1]+ivm))
#        fp.write("\n\n")



#
# Do the VM routers for the TE in the disks
#

for idisk in range(1,6) :
    print "disk =",idisk,"allstub memories",nallstubsdisks[idisk-1]
    fp.write("\n")
    fp.write("#\n")
    fp.write("# VMRouters for the TEs in disk "+str(idisk)+" \n")
    fp.write("#\n")
    for iallstubmem in range(1,nallstubsdisks[idisk-1]+1) :
        allstubsmemname="D"+str(idisk)+"PHI"+letter(iallstubmem)
        for il in inputlinks :
            if allstubsmemname in il :
                fp.write(il+" ")
        fp.write("> VMR_D"+str(idisk)+"PHI"+letter(iallstubmem)+" > ")
        fp.write("AS_D"+str(idisk)+"PHI"+letter(iallstubmem))
        for ivm in range(1,nvmmedisks[idisk-1]+1) :
            fp.write(" VMSME_D"+str(idisk)+"PHI"+letter(iallstubmem)+str((iallstubmem-1)*nvmmedisks[idisk-1]+ivm))
        if idisk in range(1,5) :
            for ivm in range(1,nvmtedisks[idisk-1]+1) :
                fp.write(" VMSTE_D"+str(idisk)+"PHI"+letter(iallstubmem)+str((iallstubmem-1)*nvmtedisks[idisk-1]+ivm))
        if idisk in range(1,2) :
            for ivm in range(1,nvmteoverlapdisks[idisk-1]+1) :
                fp.write(" VMSTE_D"+str(idisk)+"PHI"+letteroverlap(iallstubmem)+str((iallstubmem-1)*nvmteoverlapdisks[idisk-1]+ivm))
        fp.write("\n\n")


#
# Do the VM routers for the TE in the overlap disks
#

#for idisk in range(1,2) :
#    print "disk =",idisk,"allstub memories overlap ",nallstubsoverlapdisks[idisk-1]
#    fp.write("\n")
#    fp.write("#\n")
#    fp.write("# VMRouters for the TEs in overlap disk "+str(idisk)+" \n")
#    fp.write("#\n")
#    for iallstubmem in range(1,nallstubsoverlapdisks[idisk-1]+1) :
#        allstubsmemname="D"+str(idisk)+"PHI"+letter(iallstubmem)
#        for il in inputlinks :
#            if allstubsmemname in il :
#                fp.write(il+" ")
#        fp.write("> VMRTE_D"+str(idisk)+"PHI"+letteroverlap(iallstubmem)+" > ")
#        fp.write("AS_D"+str(idisk)+"PHI"+letteroverlap(iallstubmem))
#        for ivm in range(1,nvmteoverlapdisks[idisk-1]+1) :
#            fp.write(" VMSTE_D"+str(idisk)+"PHI"+letteroverlap(iallstubmem)+str((iallstubmem-1)*nvmteoverlapdisks[idisk-1]+ivm))
#        fp.write("\n\n")



#
# Do the VM routers for the ME in the layers
#

#for ilayer in range(1,7) :
#    print "layer =",ilayer,"allproj memories",nallprojlayers[ilayer-1]
#    fp.write("\n")
#    fp.write("#\n")
#    fp.write("# VMRouters for the MEs in layer "+str(ilayer)+" \n")
#    fp.write("#\n")
#    for iallprojmem in range(1,nallprojlayers[ilayer-1]+1) :
#        allstubsmemname="L"+str(ilayer)+"PHI"+letter(iallprojmem)
#        for il in inputlinks :
#            if allstubsmemname in il :
#                fp.write(il+" ")
#        fp.write("> VMRME_L"+str(ilayer)+"PHI"+letter(iallprojmem)+" > ")
#        fp.write("\n\n")


#
# Do the VM routers for the ME in the disks
#

#for idisk in range(1,6) :
#    print "disk =",idisk,"allproj memories",nallprojdisks[idisk-1]
#    fp.write("\n")
#    fp.write("#\n")
#    fp.write("# VMRouters for the MEs in disk "+str(idisk)+" \n")
#    fp.write("#\n")
#    for iallprojmem in range(1,nallprojdisks[idisk-1]+1) :
#        allstubsmemname="D"+str(idisk)+"PHI"+letter(iallprojmem)
#        for il in inputlinks :
#            if allstubsmemname in il :
#                fp.write(il+" ")
#        fp.write("> VMRME_D"+str(idisk)+"PHI"+letter(iallprojmem)+" > ")
#        fp.write("AS_D"+str(idisk)+"PHI"+letter(iallprojmem))
#        for ivm in range(1,nvmmedisks[idisk-1]+1) :
#            fp.write(" VMSME_D"+str(idisk)+"PHI"+letter(iallprojmem)+str((iallprojmem-1)*nvmmedisks[idisk-1]+ivm))
#        fp.write("\n\n")




#
# Do the TE for the layers
#

SP_list=[]

for ilayer in (1,3,5) :
    fp.write("\n")
    fp.write("#\n")
    fp.write("# Tracklet Engines for seeding layer "+str(ilayer)+" \n")
    fp.write("#\n")
    print "layer = ",ilayer
    for ivminner in range(1,nallstubslayers[ilayer-1]*nvmtelayers[ilayer-1]+1) :
        for ivmouter in range(1,nallstubslayers[ilayer]*nvmtelayers[ilayer]+1) :
            if validtepair(ilayer,ivminner,ivmouter) :
                fp.write("VMSTE_L"+str(ilayer)+"PHI"+letter((ivminner-1)/nvmtelayers[ilayer-1]+1)+str(ivminner))
                fp.write(" VMSTE_L"+str(ilayer+1)+"PHI"+letter((ivmouter-1)/nvmtelayers[ilayer]+1)+str(ivmouter))
                fp.write(" > TE_L"+str(ilayer)+"PHI"+letter((ivminner-1)/nvmtelayers[ilayer-1]+1)+str(ivminner))
                fp.write("_L"+str(ilayer+1)+"PHI"+letter((ivmouter-1)/nvmtelayers[ilayer]+1)+str(ivmouter))
                sp_name="SP_L"+str(ilayer)+"PHI"+letter((ivminner-1)/nvmtelayers[ilayer-1]+1)+str(ivminner)+"_L"+str(ilayer+1)+"PHI"+letter((ivmouter-1)/nvmtelayers[ilayer]+1)+str(ivmouter)
                fp.write(" > "+sp_name)
                fp.write("\n\n")
                SP_list.append(sp_name)


#
# Do the TE for the disks
#

for idisk in (1,3) :
    fp.write("\n")
    fp.write("#\n")
    fp.write("# Tracklet Engines for seeding disk "+str(idisk)+" \n")
    fp.write("#\n")
    print "disk = ",idisk
    for ivminner in range(1,nallstubsdisks[idisk-1]*nvmtedisks[idisk-1]+1) :
        for ivmouter in range(1,nallstubsdisks[idisk]*nvmtedisks[idisk]+1) :
            if validtepairdisk(idisk,ivminner,ivmouter) :
                fp.write("VMSTE_D"+str(idisk)+"PHI"+letter((ivminner-1)/nvmtedisks[idisk-1]+1)+str(ivminner))
                fp.write(" VMSTE_D"+str(idisk+1)+"PHI"+letter((ivmouter-1)/nvmtedisks[idisk]+1)+str(ivmouter))
                fp.write(" > TE_D"+str(idisk)+"PHI"+letter((ivminner-1)/nvmtedisks[idisk-1]+1)+str(ivminner))
                fp.write("_D"+str(idisk+1)+"PHI"+letter((ivmouter-1)/nvmtedisks[idisk]+1)+str(ivmouter))
                sp_name="SP_D"+str(idisk)+"PHI"+letter((ivminner-1)/nvmtedisks[idisk-1]+1)+str(ivminner)+"_D"+str(idisk+1)+"PHI"+letter((ivmouter-1)/nvmtedisks[idisk]+1)+str(ivmouter)
                fp.write(" > "+sp_name)
                fp.write("\n\n")
                SP_list.append(sp_name)



#
# Do the TE for the overlap
#

for ilayer in (1,2) :
    fp.write("\n")
    fp.write("#\n")
    fp.write("# Tracklet Engines for overlap seeding layer "+str(ilayer)+" \n")
    fp.write("#\n")
    print "layer = ",ilayer
    for ivminner in range(1,nallstubsoverlaplayers[ilayer-1]*nvmteoverlaplayers[ilayer-1]+1) :
        for ivmouter in range(1,nallstubsoverlapdisks[0]*nvmteoverlapdisks[0]+1) :
            if validtepairoverlap(ilayer,ivminner,ivmouter) :
                fp.write("VMSTE_L"+str(ilayer)+"PHI"+letteroverlap((ivminner-1)/nvmteoverlaplayers[ilayer-1]+1)+str(ivminner))
                fp.write(" VMSTE_D"+str(1)+"PHI"+letteroverlap((ivmouter-1)/nvmteoverlapdisks[0]+1)+str(ivmouter))
                fp.write(" > TE_L"+str(ilayer)+"PHI"+letteroverlap((ivminner-1)/nvmteoverlaplayers[ilayer-1]+1)+str(ivminner))
                fp.write("_D"+str(1)+"PHI"+letteroverlap((ivmouter-1)/nvmteoverlapdisks[0]+1)+str(ivmouter))
                sp_name="SP_L"+str(ilayer)+"PHI"+letteroverlap((ivminner-1)/nvmteoverlaplayers[ilayer-1]+1)+str(ivminner)+"_D"+str(1)+"PHI"+letteroverlap((ivmouter-1)/nvmteoverlapdisks[0]+1)+str(ivmouter)
                fp.write(" > "+sp_name)
                fp.write("\n\n")
                SP_list.append(sp_name)


                
                
#
# Do the TC for the layers
#

TPROJ_list=[]
TPAR_list=[]
                
for ilayer in (1,3,5) :
    fp.write("\n")
    fp.write("#\n")
    fp.write("# Tracklet Calculators for seeding layer "+str(ilayer)+" \n")
    fp.write("#\n")

    sp_layer=[]
    for sp_name in SP_list :
        if "_L"+str(ilayer) in sp_name and "_L"+str(ilayer+1) in sp_name :
            #print ilayer,sp_name
            sp_layer.append(sp_name)

    tcs=12
    if ilayer==3 :
        tcs=8
    if ilayer==5 :
        tcs=4

    sp_per_tc=split(sp_layer,tcs)
    
    tc_count=0
    for sps in  sp_per_tc :
        print len(sps), sps
        for sp_name in sps :
            fp.write(sp_name+" ")
        tc_count+=1
        #print sp_name, sp_name.split("PHI")
        fp.write("AS_L"+str(ilayer)+"PHI"+sp_name[8]+" AS_L"+str(ilayer+1)+"PHI"+sp_name.split("PHI")[2][0])  #PHI regions are hacks!
        tpar_name="TPAR_L"+str(ilayer)+"L"+str(ilayer+1)+letter(tc_count)
        fp.write(" > TC_L"+str(ilayer)+"L"+str(ilayer+1)+letter(tc_count)+" > "+tpar_name)
        TPAR_list.append(tpar_name)
        for projlayer in range(1,7) :
            if projlayer!=ilayer and projlayer!=ilayer+1 :
                projrange=phiprojrange(ilayer,projlayer,sps)
                for iallproj in range(1,nallprojlayers[projlayer-1]+1) :
                    phiprojmin=phirange/nallprojlayers[projlayer-1]*(iallproj-1)
                    phiprojmax=phirange/nallprojlayers[projlayer-1]*iallproj
                    if projrange[0]<phiprojmax and projrange[1]>phiprojmin :
                        proj_name="TPROJ_L"+str(ilayer)+"L"+str(ilayer+1)+letter(tc_count)+"_L"+str(projlayer)+"PHI"+letter(iallproj)
                        if proj_name not in unusedproj :
                            fp.write(" "+proj_name)
                            TPROJ_list.append(proj_name)
        projdisks=[]
        if ilayer<5 :
            projdisks.append(1)
            projdisks.append(2)
        if ilayer==1 :
            projdisks.append(3)
            projdisks.append(4)
            projdisks.append(5)
        for projdisk in projdisks :
            projrange=phiprojrangelayertodisk(ilayer,projdisk,sps)
            for iallproj in range(1,nallprojdisks[projdisk-1]+1) :
                phiprojmin=phirange/nallprojdisks[projdisk-1]*(iallproj-1)
                phiprojmax=phirange/nallprojdisks[projdisk-1]*iallproj
                if projrange[0]<phiprojmax and projrange[1]>phiprojmin :
                    proj_name="TPROJ_L"+str(ilayer)+"L"+str(ilayer+1)+letter(tc_count)+"_D"+str(projdisk)+"PHI"+letter(iallproj)
                    if proj_name not in unusedproj :
                        fp.write(" "+proj_name)
                        TPROJ_list.append(proj_name)
        fp.write("\n\n")


#
# Do the TC for the disks
#

                
for idisk in (1,3) :
    fp.write("\n")
    fp.write("#\n")
    fp.write("# Tracklet Calculators for seeding diks "+str(idisk)+" \n")
    fp.write("#\n")

    sp_disk=[]
    for sp_name in SP_list :
        if "_D"+str(idisk) in sp_name and "_D"+str(idisk+1) in sp_name :
            #print idisk,sp_name
            sp_disk.append(sp_name)

    tcs=6
    if idisk==3 :
        tcs=2

    sp_per_tc=split(sp_disk,tcs)
    
    tc_count=0
    for sps in  sp_per_tc :
        #print len(sps), sps
        for sp_name in sps :
            fp.write(sp_name+" ")
        tc_count+=1
        #print sp_name, sp_name.split("PHI")
        fp.write("AS_D"+str(idisk)+"PHI"+sp_name[8]+" AS_D"+str(idisk+1)+"PHI"+sp_name.split("PHI")[2][0])  #PHI regions are hacks!
        tpar_name="TPAR_D"+str(idisk)+"D"+str(idisk+1)+letter(tc_count)
        fp.write(" > TC_D"+str(idisk)+"D"+str(idisk+1)+letter(tc_count)+" > "+tpar_name)
        TPAR_list.append(tpar_name)
        for projdisk in range(1,6) :
            if projdisk!=idisk and projdisk!=idisk+1 :
                projrange=phiprojrangedisk(idisk,projdisk,sps)
                for iallproj in range(1,nallprojdisks[projdisk-1]+1) :
                    print "looking for projection to disk iallproj",projdisk,iallproj
                    phiprojmin=phirange/nallprojdisks[projdisk-1]*(iallproj-1)
                    phiprojmax=phirange/nallprojdisks[projdisk-1]*iallproj
                    if projrange[0]<phiprojmax and projrange[1]>phiprojmin :
                        proj_name="TPROJ_D"+str(idisk)+"D"+str(idisk+1)+letter(tc_count)+"_D"+str(projdisk)+"PHI"+letter(iallproj)
                        if proj_name not in unusedproj :
                            fp.write(" "+proj_name)
                            TPROJ_list.append(proj_name)
        projlayers=[]
        projlayers.append(1)
        if idisk==1 :
            projlayers.append(2)
        for projlayer in projlayers :
            projrange=phiprojrangedisktolayer(idisk,projlayer,sps)
            for iallproj in range(1,nallprojlayers[projlayer-1]+1) :
                phiprojmin=phirange/nallprojlayers[projlayer-1]*(iallproj-1)
                phiprojmax=phirange/nallprojlayers[projlayer-1]*iallproj
                if projrange[0]<phiprojmax and projrange[1]>phiprojmin :
                    proj_name="TPROJ_D"+str(idisk)+"D"+str(idisk+1)+letter(tc_count)+"_L"+str(projlayer)+"PHI"+letter(iallproj)
                    if proj_name not in unusedproj :
                        fp.write(" "+proj_name)
                        TPROJ_list.append(proj_name)
        fp.write("\n\n")


#for idisk in (1,3) :
#    fp.write("\n")
#    fp.write("#\n")
#    fp.write("# Tracklet Calculators for seeding disk "+str(idisk)+" \n")
#    fp.write("#\n")
#    print "disk = ",idisk
#    tc_count=0
#    for iallstubmeminner in range(1,nallstubsdisks[idisk-1]+1) :
#        innername="D"+str(idisk)+"PHI"+letter(iallstubmeminner)
#        for iallstubmemouter in range(1,nallstubsdisks[idisk]+1) :
#            outername="D"+str(idisk+1)+"PHI"+letter(iallstubmemouter)
#            valid=False
#            splist=[]
#            for sp_name in SP_list :
#                if innername in sp_name and outername in sp_name :
#                    valid=True
#                    splist.append(sp_name)
#                    fp.write(sp_name+" ")
#            if valid :
#                tc_count+=1
#                fp.write("AS_"+innername+" AS_"+outername)
#                tpar_name="TPAR_D"+str(idisk)+"D"+str(idisk+1)+letter(tc_count)
#                fp.write(" > TC_D"+str(idisk)+"D"+str(idisk+1)+letter(tc_count)+" > "+tpar_name)
#                TPAR_list.append(tpar_name)
#                for projdisk in range(1,6) :
#                    if projdisk!=idisk and projdisk!=idisk+1 :
#                        projrange=phiprojrangedisk(idisk,projdisk,splist)
#                        print idisk, iallstubmeminner,projdisk,projrange
#                        for iallproj in range(1,nallprojdisks[projdisk-1]+1) :
#                            phiprojmin=phirange/nallprojdisks[projdisk-1]*(iallproj-1)
#                            phiprojmax=phirange/nallprojdisks[projdisk-1]*iallproj
#                            if projrange[0]<phiprojmax and projrange[1]>phiprojmin :
#                                proj_name="TPROJ_D"+str(idisk)+"D"+str(idisk+1)+letter(tc_count)+"_D"+str(projdisk)+"PHI"+letter(iallproj)
#                                if proj_name not in unusedproj :
#                                    fp.write(" "+proj_name)
#                                    TPROJ_list.append(proj_name)
#                projlayers=[]
#                projlayers.append(1)
#                if idisk==1 :
#                    projlayers.append(2)
#                for projlayer in projlayers :
#                    projrange=phiprojrangedisktolayer(idisk,projlayer,splist)
#                    for iallproj in range(1,nallprojlayers[projlayer-1]+1) :
#                        phiprojmin=phirange/nallprojlayers[projlayer-1]*(iallproj-1)
#                        phiprojmax=phirange/nallprojlayers[projlayer-1]*iallproj
#                        if projrange[0]<phiprojmax and projrange[1]>phiprojmin :
#                            proj_name="TPROJ_D"+str(idisk)+"D"+str(idisk+1)+letter(tc_count)+"_L"+str(projlayer)+"PHI"+letter(iallproj)
#                            if proj_name not in unusedproj :
#                                fp.write(" "+proj_name)
#                                TPROJ_list.append(proj_name)
#        fp.write("\n\n")


#
# Do the TC for the overlap
#


                
for ilayer in (1,2) :
    fp.write("\n")
    fp.write("#\n")
    fp.write("# Tracklet Calculators for seeding in overlap layer "+str(ilayer)+" \n")
    fp.write("#\n")

    sp_layer=[]
    for sp_name in SP_list :
        if "_L"+str(ilayer) in sp_name and "_D1" in sp_name :
            #print ilayer,sp_name
            sp_layer.append(sp_name)

    tcs=6
    if ilayer==2 :
        tcs=2

    sp_per_tc=split(sp_layer,tcs)
    
    tc_count=0
    for sps in  sp_per_tc :
        #print len(sps), sps
        for sp_name in sps :
            fp.write(sp_name+" ")
        tc_count+=1
        reg1=sp_name[8]
        if reg1=="X" :
            reg1="A"
        if reg1=="Y" :
            reg1="B"
        if reg1=="Z" :
            reg1="C"
        if reg1=="W" :
            reg1="D"
        if reg1=="Q" :
            reg1="E"
        if reg1=="R" :
            reg1="F"
        if reg1=="S" :
            reg1="G"
        if reg1=="T" :
            reg1="H"
        reg2=sp_name.split("PHI")[2][0]
        if reg2=="X" :
            reg2="A"
        if reg2=="Y" :
            reg2="B"
        if reg2=="Z" :
            reg2="C"
        if reg2=="W" :
            reg2="D"
        if reg2=="Q" :
            reg2="E"
        if reg2=="R" :
            reg2="F"
        if reg2=="S" :
            reg2="G"
        if reg2=="T" :
            reg2="H"
        fp.write("AS_L"+str(ilayer)+"PHI"+reg1+" AS_D1PHI"+reg2)  #PHI regions are hacks!
        tpar_name="TPAR_L"+str(ilayer)+"D1"+letter(tc_count)
        fp.write(" > TC_L"+str(ilayer)+"D1"+letter(tc_count)+" > "+tpar_name)
        TPAR_list.append(tpar_name)
        if ilayer==2 :
            for projlayer in range(1,2) :
                projrange=phiprojrange(ilayer,projlayer,sps)
                #print ilayer, iallstubmeminner,projlayer,projrange
                for iallproj in range(1,nallprojlayers[projlayer-1]+1) :
                    phiprojmin=phirange/nallprojlayers[projlayer-1]*(iallproj-1)
                    phiprojmax=phirange/nallprojlayers[projlayer-1]*iallproj
                    if projrange[0]<phiprojmax and projrange[1]>phiprojmin :
                        proj_name="TPROJ_L"+str(ilayer)+"D"+str(1)+letter(tc_count)+"_L"+str(projlayer)+"PHI"+letter(iallproj)
                        if proj_name not in unusedproj :
                            fp.write(" "+proj_name)
                            TPROJ_list.append(proj_name)
        projdisks=[2,3,4,5]
        for projdisk in projdisks :
            projrange=phiprojrangeoverlaplayertodisk(ilayer,projdisk,sps)
            for iallproj in range(1,nallprojdisks[projdisk-1]+1) :
                phiprojmin=phirange/nallprojdisks[projdisk-1]*(iallproj-1)
                phiprojmax=phirange/nallprojdisks[projdisk-1]*iallproj
                if ilayer==1 :
                    print letter(tc_count),projrange, phiprojmin, phiprojmax, letter(iallproj)
                if projrange[0]<phiprojmax and projrange[1]>phiprojmin :
                    proj_name="TPROJ_L"+str(ilayer)+"D"+str(1)+letter(tc_count)+"_D"+str(projdisk)+"PHI"+letter(iallproj)
                    if proj_name not in unusedproj :
                        fp.write(" "+proj_name)
                        TPROJ_list.append(proj_name)
        fp.write("\n\n")


FM_list=[]
CM_list=[]


if combined :

    for ilayer in range(1,7) :
        print "layer =",ilayer,"allstub memories",nallprojlayers[ilayer-1]
        fp.write("\n")
        fp.write("#\n")
        fp.write("# PROJRouters+MatchEngines+MatchCalculator in layer "+str(ilayer)+" \n")
        fp.write("#\n")
        for iallprojmem in range(1,nallprojlayers[ilayer-1]+1) :
            projmemname="L"+str(ilayer)+"PHI"+letter(iallprojmem)
            for proj_name in TPROJ_list :
                if projmemname in proj_name :
                    fp.write(proj_name+" ")
            fp.write("AS_L"+str(ilayer)+"PHI"+letter(iallprojmem))
            for ivm in range(1,nallprojlayers[ilayer-1]*nvmmelayers[ilayer-1]+1) :
                phiregion=1+(ivm-1)/nvmmelayers[ilayer-1]
                if phiregion!=iallprojmem :
                    continue
                fp.write(" VMSME_L"+str(ilayer)+"PHI"+letter(phiregion)+str(ivm))

            fp.write(" > MP_L"+str(ilayer)+"PHI"+letter(iallprojmem)+" > ")
            fm_name="FM_L1L2_L"+str(ilayer)+"PHI"+letter(iallprojmem)
            if ilayer!=1 and ilayer!=2 :
                fp.write(fm_name+" ")
                FM_list.append(fm_name)
            fm_name="FM_L3L4_L"+str(ilayer)+"PHI"+letter(iallprojmem)
            if ilayer!=3 and ilayer!=4 :
                fp.write(fm_name+" ")
                FM_list.append(fm_name)
            fm_name="FM_L5L6_L"+str(ilayer)+"PHI"+letter(iallprojmem)
            if ilayer!=5 and ilayer!=6 :
                fp.write(fm_name+" ")
                FM_list.append(fm_name)
            fm_name="FM_D1D2_L"+str(ilayer)+"PHI"+letter(iallprojmem)
            if ilayer==1 or ilayer==2 :
                fp.write(fm_name+" ")
                FM_list.append(fm_name)
            fm_name="FM_D3D4_L"+str(ilayer)+"PHI"+letter(iallprojmem)
            if ilayer==1 :
                fp.write(fm_name+" ")
                FM_list.append(fm_name)
            fm_name="FM_L2D1_L"+str(ilayer)+"PHI"+letter(iallprojmem)
            if ilayer==1 :
                fp.write(fm_name+" ")
                FM_list.append(fm_name)
            fp.write("\n\n")

    for idisk in range(1,6) :
        print "disk =",idisk,"allstub memories",nallprojdisks[idisk-1]
        fp.write("\n")
        fp.write("#\n")
        fp.write("# PROJRouters+MatchEngine+MatchCalculator in disk "+str(idisk)+" \n")
        fp.write("#\n")
        for iallprojmem in range(1,nallprojdisks[idisk-1]+1) :
            projmemname="D"+str(idisk)+"PHI"+letter(iallprojmem)
            for proj_name in TPROJ_list :
                if projmemname in proj_name :
                    fp.write(proj_name+" ")
            fp.write("AS_D"+str(idisk)+"PHI"+letter(iallprojmem))
            for ivm in range(1,nallprojdisks[idisk-1]*nvmmedisks[idisk-1]+1) :
                phiregion=1+(ivm-1)/nvmmedisks[idisk-1]
                if phiregion!=iallprojmem :
                    continue
                fp.write(" VMSME_D"+str(idisk)+"PHI"+letter(phiregion)+str(ivm))
            fp.write(" > MP_D"+str(idisk)+"PHI"+letter(iallprojmem)+" > ")
            fm_name="FM_D1D2_D"+str(idisk)+"PHI"+letter(iallprojmem)
            if idisk!=1 and idisk!=2 :
                fp.write(fm_name+" ")
                FM_list.append(fm_name)
            fm_name="FM_D3D4_D"+str(idisk)+"PHI"+letter(iallprojmem)
            if idisk!=3 and idisk!=4 :
                fp.write(fm_name+" ")
                FM_list.append(fm_name)
            fm_name="FM_L1L2_D"+str(idisk)+"PHI"+letter(iallprojmem)
            if idisk!=5 :
                fp.write(fm_name+" ")
                FM_list.append(fm_name)
            fm_name="FM_L3L4_D"+str(idisk)+"PHI"+letter(iallprojmem)
            if idisk==1 or idisk==2 :
                fp.write(fm_name+" ")
                FM_list.append(fm_name)
            fm_name="FM_L1D1_D"+str(idisk)+"PHI"+letter(iallprojmem)
            if idisk!=1 :
                fp.write(fm_name+" ")
                FM_list.append(fm_name)
            fm_name="FM_L2D1_D"+str(idisk)+"PHI"+letter(iallprojmem)
            if idisk!=1 and idisk!=5 :
                fp.write(fm_name+" ")
                FM_list.append(fm_name)

            fp.write("\n\n")

            
    
else :
                
    #
    # Do the PROJRouters for the layers
    #

    for ilayer in range(1,7) :
        print "layer =",ilayer,"allstub memories",nallprojlayers[ilayer-1]
        fp.write("\n")
        fp.write("#\n")
        fp.write("# PROJRouters for the MEs in layer "+str(ilayer)+" \n")
        fp.write("#\n")
        for iallprojmem in range(1,nallprojlayers[ilayer-1]+1) :
            projmemname="L"+str(ilayer)+"PHI"+letter(iallprojmem)
            for proj_name in TPROJ_list :
                if projmemname in proj_name :
                    fp.write(proj_name+" ")
            fp.write("> PR_L"+str(ilayer)+"PHI"+letter(iallprojmem)+" > AP_L"+str(ilayer)+"PHI"+letter(iallprojmem))
            for ivm in range(1,nvmmelayers[ilayer-1]+1) :
                fp.write(" VMPROJ_L"+str(ilayer)+"PHI"+letter(iallprojmem)+str((iallprojmem-1)*nvmmelayers[ilayer-1]+ivm))
            fp.write("\n\n")


    #
    # Do the PROJRouters for the disks
    #

    for idisk in range(1,6) :
        print "disk =",idisk,"allstub memories",nallprojdisks[idisk-1]
        fp.write("\n")
        fp.write("#\n")
        fp.write("# PROJRouters for the MEs in disk "+str(idisk)+" \n")
        fp.write("#\n")
        for iallprojmem in range(1,nallprojdisks[idisk-1]+1) :
            projmemname="D"+str(idisk)+"PHI"+letter(iallprojmem)
            for proj_name in TPROJ_list :
                if projmemname in proj_name :
                    fp.write(proj_name+" ")
            fp.write("> PR_D"+str(idisk)+"PHI"+letter(iallprojmem)+" > AP_D"+str(idisk)+"PHI"+letter(iallprojmem))
            for ivm in range(1,nvmmedisks[idisk-1]+1) :
                fp.write(" VMPROJ_D"+str(idisk)+"PHI"+letter(iallprojmem)+str((iallprojmem-1)*nvmmedisks[idisk-1]+ivm))
            fp.write("\n\n")


    #
    # Do the ME for the layers
    #

    CM_list=[]

    for ilayer in range(1,7) :
        fp.write("\n")
        fp.write("#\n")
        fp.write("# Match Engines for layer "+str(ilayer)+" \n")
        fp.write("#\n")
        print "layer = ",ilayer
        for ivm in range(1,nallprojlayers[ilayer-1]*nvmmelayers[ilayer-1]+1) :
            fp.write("VMSME_L"+str(ilayer)+"PHI"+letter(1+(ivm-1)/nvmmelayers[ilayer-1])+str(ivm))
            fp.write(" VMPROJ_L"+str(ilayer)+"PHI"+letter(1+(ivm-1)/nvmmelayers[ilayer-1])+str(ivm)+" >")
            fp.write(" ME_L"+str(ilayer)+"PHI"+letter(1+(ivm-1)/nvmmelayers[ilayer-1])+str(ivm)+" > ")
            CM_name="CM_L"+str(ilayer)+"PHI"+letter(1+(ivm-1)/nvmmelayers[ilayer-1])+str(ivm)
            fp.write(CM_name)
            CM_list.append(CM_name)
            fp.write("\n\n")
 

    #
    # Do the ME for the disks
    #

    for idisk in range(1,6) :
        fp.write("\n")
        fp.write("#\n")
        fp.write("# Match Engines for disk "+str(idisk)+" \n")
        fp.write("#\n")
        print "disk = ",idisk
        for ivm in range(1,nallprojdisks[idisk-1]*nvmmedisks[idisk-1]+1) :
            fp.write("VMSME_D"+str(idisk)+"PHI"+letter(1+(ivm-1)/nvmmedisks[idisk-1])+str(ivm))
            fp.write(" VMPROJ_D"+str(idisk)+"PHI"+letter(1+(ivm-1)/nvmmedisks[idisk-1])+str(ivm)+" >")
            fp.write(" ME_D"+str(idisk)+"PHI"+letter(1+(ivm-1)/nvmmedisks[idisk-1])+str(ivm)+" > ")
            CM_name="CM_D"+str(idisk)+"PHI"+letter(1+(ivm-1)/nvmmedisks[idisk-1])+str(ivm)
            fp.write(CM_name)
            CM_list.append(CM_name)
            fp.write("\n\n")
 


    #
    # Do the MC for the layers
    #

    for ilayer in range(1,7) :
        fp.write("\n")
        fp.write("#\n")
        fp.write("# Match Calculator for layer "+str(ilayer)+" \n")
        fp.write("#\n")
        print "layer = ",ilayer
        for iproj in range(1,nallprojlayers[ilayer-1]+1) :
            for ivm in range(1,nvmmelayers[ilayer-1]+1) :
                fp.write("CM_L"+str(ilayer)+"PHI"+letter(iproj)+str((iproj-1)*nvmmelayers[ilayer-1]+ivm)+" ")
            fp.write("AP_L"+str(ilayer)+"PHI"+letter(iproj)+" ")
            fp.write("AS_L"+str(ilayer)+"PHI"+letter(iproj)+" > ")
            fp.write("MC_L"+str(ilayer)+"PHI"+letter(iproj)+" > ")
            fm_name="FM_L1L2_L"+str(ilayer)+"PHI"+letter(iproj)
            if ilayer!=1 and ilayer!=2 :
                fp.write(fm_name+" ")
                FM_list.append(fm_name)
            fm_name="FM_L3L4_L"+str(ilayer)+"PHI"+letter(iproj)
            if ilayer!=3 and ilayer!=4 :
                fp.write(fm_name+" ")
                FM_list.append(fm_name)
            fm_name="FM_L5L6_L"+str(ilayer)+"PHI"+letter(iproj)
            if ilayer!=5 and ilayer!=6 :
                fp.write(fm_name+" ")
                FM_list.append(fm_name)
            fm_name="FM_D1D2_L"+str(ilayer)+"PHI"+letter(iproj)
            if ilayer==1 or ilayer==2 :
                fp.write(fm_name+" ")
                FM_list.append(fm_name)
            fm_name="FM_D3D4_L"+str(ilayer)+"PHI"+letter(iproj)
            if ilayer==1 :
                fp.write(fm_name+" ")
                FM_list.append(fm_name)
            fm_name="FM_L2D1_L"+str(ilayer)+"PHI"+letter(iproj)
            if ilayer==1 :
                fp.write(fm_name+" ")
                FM_list.append(fm_name)
            fp.write("\n\n")
        
    #
    # Do the MC for the disks
    #

    for idisk in range(1,6) :
        fp.write("\n")
        fp.write("#\n")
        fp.write("# Match Calculator for disk "+str(idisk)+" \n")
        fp.write("#\n")
        print "disk = ",idisk
        for iproj in range(1,nallprojdisks[idisk-1]+1) :
            for ivm in range(1,nvmmedisks[idisk-1]+1) :
                fp.write("CM_D"+str(idisk)+"PHI"+letter(iproj)+str((iproj-1)*nvmmedisks[idisk-1]+ivm)+" ")
            fp.write("AP_D"+str(idisk)+"PHI"+letter(iproj)+" ")
            fp.write("AS_D"+str(idisk)+"PHI"+letter(iproj)+" > ")
            fp.write("MC_D"+str(idisk)+"PHI"+letter(iproj)+" > ")
            fm_name="FM_D1D2_D"+str(idisk)+"PHI"+letter(iproj)
            if idisk!=1 and idisk!=2 :
                fp.write(fm_name+" ")
                FM_list.append(fm_name)
            fm_name="FM_D3D4_D"+str(idisk)+"PHI"+letter(iproj)
            if idisk!=3 and idisk!=4 :
                fp.write(fm_name+" ")
                FM_list.append(fm_name)
            fm_name="FM_L1L2_D"+str(idisk)+"PHI"+letter(iproj)
            if idisk!=5 :
                fp.write(fm_name+" ")
                FM_list.append(fm_name)
            fm_name="FM_L3L4_D"+str(idisk)+"PHI"+letter(iproj)
            if idisk==1 or idisk==2 :
                fp.write(fm_name+" ")
                FM_list.append(fm_name)
            fm_name="FM_L1D1_D"+str(idisk)+"PHI"+letter(iproj)
            if idisk!=1 :
                fp.write(fm_name+" ")
                FM_list.append(fm_name)
            fm_name="FM_L2D1_D"+str(idisk)+"PHI"+letter(iproj)
            if idisk!=1 and idisk!=5 :
                fp.write(fm_name+" ")
                FM_list.append(fm_name)

            fp.write("\n\n")
        
        
#
# Do the Track Fits for the layers
#

                
for ilayer in (1,3,5) :
    fp.write("\n")
    fp.write("#\n")
    fp.write("# Tracklet Fit for seeding layer "+str(ilayer)+" \n")
    fp.write("#\n")
    fitname="L1L2"
    if ilayer==3 :
        fitname="L3L4"
    if ilayer==5 :
        fitname="L5L6"
        
    for fm_name in FM_list :
        if fitname in fm_name :
            fp.write(fm_name+" ")
    for tpar_name in TPAR_list :
        if fitname in tpar_name :
            fp.write(tpar_name+" ")
    fp.write(" > FT_"+fitname+" > TF_"+fitname)
    fp.write("\n\n")


#
# Do the Track Fits for the disks
#

                
for idisk in (1,3) :
    fp.write("\n")
    fp.write("#\n")
    fp.write("# Tracklet Fit for seeding disk "+str(idisk)+" \n")
    fp.write("#\n")
    fitname="D1D2"
    if idisk==3 :
        fitname="D3D4"
        
    for fm_name in FM_list :
        if fitname in fm_name :
            fp.write(fm_name+" ")
    for tpar_name in TPAR_list :
        if fitname in tpar_name :
            fp.write(tpar_name+" ")
    fp.write(" > FT_"+fitname+" > TF_"+fitname)
    fp.write("\n\n")


#
# Do the Track Fits for the overlap
#

                
for ilayer in (1,2) :
    fp.write("\n")
    fp.write("#\n")
    fp.write("# Tracklet Fit for overlap seeding layer "+str(ilayer)+" \n")
    fp.write("#\n")
    fitname="L1D1"
    if ilayer==2 :
        fitname="L2D1"
        
    for fm_name in FM_list :
        if fitname in fm_name :
            fp.write(fm_name+" ")
    for tpar_name in TPAR_list :
        if fitname in tpar_name :
            fp.write(tpar_name+" ")
    fp.write(" > FT_"+fitname+" > TF_"+fitname)
    fp.write("\n\n")

    
    
fp.write("TF_L1L2 TF_L3L4 TF_L5L6 TF_D1D2 TF_D3D4 TF_L1D1 TF_L2D1 > PD > CT_L1L2 CT_L3L4 CT_L5L6 CT_D1D2 CT_D3D4 CT_L1D1 CT_L2D1")    
fp.write("\n\n")

print "=========================Summary========================================"
print "StubPair    ",len(SP_list)
print "TPAR        ",len(TPAR_list)
print "TPROJ       ",len(TPROJ_list)
print "Cand. Match ",len(CM_list)
print "Full Match  ",len(FM_list)
