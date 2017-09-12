#!/usr/bin/env python

import argparse
import proj_dict as pdict

goodseedings=['L1L2','L3L4','L5L6','D1D2','D3D4','D1L1','D1L2']

parser = argparse.ArgumentParser(description='Generate sub-project for long VM')
parser.add_argument('-r','--region', type=str, choices=['L','D','H','A'],
                    default='A',
                    help='Detector regions : L - Layer only; D - Disk only; H - Hybrid; A - Entire tracker')
parser.add_argument('-s','--seedings',nargs='+',type=str, choices=goodseedings,
                    help='seeding pairs')
parser.add_argument('-i','--input', type=str, default='wires.input.longVM_sector',
                    help='input file')
parser.add_argument('-o','--output', type=str, default='wires.reduced',
                    help='output name')

args = parser.parse_args()

# check if seedings are allowed in specified tracker region
if args.region=='L':
    goodseedings=['L1L2','L3L4','L5L6']
elif args.region=='D':
    goodseedings=['D1D2','D3D4']
elif args.region=='H':
    # TODO: hybrid seeding, seeding in barrel(disk) projecting to disk(layer)
    goodseedings=['D1L1', 'D1L2']

seeds = goodseedings if args.seedings is None else args.seedings
print seeds

if not set(seeds).issubset(goodseedings):
    print 'Required seedings are not all possible in this detector region'
    print 'available seedings are :', goodseedings
    exit(0)

# dictionary that stores lists of possible projections for a given seeding
proj_dict = {} 
if args.region == 'L':
    proj_dict = pdict.proj_dict_L
elif args.region == 'D':
    proj_dict = pdict.proj_dict_D
elif args.region == 'H':
    proj_dict = pdict.proj_dict_H
else:
    proj_dict = pdict.proj_dict

# match processing modules by seedings and possible projection layers/disks
def match_proc(proc, seedings, region):
    if region in ['L','D']: # not hybrid
        if 'PHIQ' in proc or 'PHIW' in proc or 'PHIX' in proc or 'PHIY' in proc:
            return False
    
    for seeding in seedings:
        seed1 = seeding[0:2]
        seed2 = seeding[2:4]
        projections = proj_dict[seeding]
        
        # VMRouterTE
        if 'VMRTE' in proc:
            if seed1 in proc or seed2 in proc:
                return True
        # VMRouterME
        elif 'VMRME' in proc:
            if proc.split('_')[-1][0:2] in projections:
                return True
        # TrackletEngine
        elif 'TE' in proc:
            if '_'+seed1 in proc and '_'+seed2 in proc:
                return True
        # TrackletCalculator
        elif 'TC' in proc:
            if seeding in proc:
                return True
        # ProjectionTransceiver
        elif 'PT' in proc:
            for proj in projections:
                if proj in proc:
                    return True
        # ProjectionRouter, MatchEngine, MatchCalculator
        elif 'PR' in proc or 'ME' in proc or 'MC' in proc:
            if seeding in proc and proc.split('_')[-1][0:2] in projections:
                return True
        # MatchTransceiver
        elif 'MT' in proc:
            for proj in projections:
                if proj in proc:
                    return True
        # FitTrack
        elif 'FT' in proc:
            if seeding in proc:
                return True
        # PurgeDuplicate
        elif 'PD' in proc:
            return True
        else:
            print 'WARNING : ', proc, ' not specified!!'
            exit(1)
            
    return False

# veto processing modules based on allowed projection layers/disks
def veto_proc(proc, seedings):
    for seeding in seedings:
        if 'PR' in proc or 'ME' in proc or 'MC' in proc:
            if proc.split('_')[-1][0:2] in proj_dict[seeding]:
                return False
        else:
            return False
    
    return True

# match memory modules by seedings and possible projection layers/disks
def match_mem(mem, seedings, region):
    if region in ['L','D']: # not hybrid
        if 'PHIQ' in mem or 'PHIW' in mem or 'PHIX' in mem or 'PHIY' in mem:
            return False
    
    for seeding in seedings:
        seed1 = seeding[0:2]
        seed2 = seeding[2:4]
        projections = proj_dict[seeding]

        if 'VMSTE' in mem:
            if seed1 in mem or seed2 in mem:
                return True
        elif 'VMSME' in mem:
            if mem.split('_')[-1][0:2] in projections:
                return True
        elif 'SP' in mem:
            if '_'+seed1 in mem and '_'+seed2 in mem:
                return True
        elif 'TPROJ' in mem or 'FM' in mem or 'CM' in mem:
            if seeding in mem.split('_')[1]:
                for proj in projections:
                    if proj in mem.split('_')[2]:
                        return True
        elif 'TF' in mem or 'CT' in mem:
            if seeding in mem.split('_')[1]:
                return True
        else:
            return True
            
    return False    

# veto memory modules based on allowed projection layers/disks
def veto_mem(mem, seedings):
    for seeding in seedings:
        seed1 = seeding[0:2]
        seed2 = seeding[2:4]
        projections = proj_dict[seeding]

        if 'TPROJ' in mem:
            for proj in projections:
                if proj in mem.split('_')[-1]:
                    return False
            
    return True


print 'Will read', args.input
fi = open(args.input,"r")
fo = open(args.output,"w")

vmproj = []
tproj_pt = []

for line in fi:

    if len(line.split(' > '))!=3:
        continue
    
    proc = line.split(' > ')[1].split()[0]
    inputmems = line.split(' > ')[0].split()
    outputmems = line.split(' > ')[2].split()

    inputmems_new = []
    outputmems_new = []
    
    if 'VMR' in proc or 'TE' in proc: # VMRouterTE, VMRouterME, TrackletEngine
        if match_proc(proc, seeds, args.region) :
            inputmems_new = inputmems
            outputmems_new = outputmems
    elif 'TC' in proc: # TrackletCalculator
        if match_proc(proc, seeds, args.region):
            inputmems_new = inputmems
            for mem in outputmems:
                if 'TPROJ' not in mem:
                    outputmems_new.append(mem)
                else:  # TPROJ memory
                    if match_mem(mem, seeds, args.region):
                        outputmems_new.append(mem)                      
    elif 'PT' in proc: # ProjectionTransceiver
        if match_proc(proc, seeds, args.region):
            # TPROJ memories
            for mem in inputmems:
                if match_mem(mem, seeds, args.region):
                    inputmems_new.append(mem)                
            for mem in outputmems:
                if match_mem(mem, seeds, args.region):
                    outputmems_new.append(mem)
                    tproj_pt.append(mem)
            if len(outputmems_new)==0: # if empty
                # some projections from different seedings are merged
                for mem in outputmems:
                    if not veto_mem(mem, seeds):
                        outputmems_new.append(mem)
                        tproj_pt.append(mem)
            assert len(outputmems_new)>0
    elif 'PR' in proc: # ProjectionRouter
        # do not match by seeding since PR handles mixture of seeding pairs
        if not veto_proc(proc, seeds):
            for mem in inputmems: # TPROJ
                if 'FromPlus' in mem or 'FromMinus' in mem:
                    if mem in tproj_pt:
                        inputmems_new.append(mem)
                else:
                    if match_mem(mem, seeds, args.region):
                        inputmems_new.append(mem)
            if len(inputmems_new) > 0:
                for mem in outputmems:
                    outputmems_new.append(mem) # AP, VMPROJ
                    # keep track of vmproj in case of mixed seeding
                    if 'VMPROJ' in mem:
                        vmproj.append(mem)
    elif 'ME' in proc: # MatchEngine
        # do not match by seeding since ME handles mixture of seeding pairs
        if not veto_proc(proc, seeds):
            assert len(inputmems)==2
            if inputmems[1] in vmproj:
                inputmems_new = inputmems
                outputmems_new = outputmems
    elif 'MC' in proc: # MatchCalculator
        ToNeighborFM = []
        # do not match by seeding since MC handles mixture of seeding pairs
        if not veto_proc(proc, seeds):
            for mem in outputmems: # FM
                if match_mem(mem, seeds, args.region):
                    outputmems_new.append(mem)
                if '_ToPlus' in mem or '_ToMinus' in mem:
                    ToNeighborFM.append(mem)
                    
            if len(outputmems_new)>0:
                inputmems_new = inputmems
                
            # add ToPlus and ToMinus memories if not added yet
            addedNeighbors = False
            for newmem in outputmems_new:
                if '_ToPlus' in newmem or '_ToMinus' in newmem:
                    addedNeighbors = True
                    break
            if not addedNeighbors and len(outputmems_new)>0:
                outputmems_new += ToNeighborFM
                    
    elif 'MT' in proc: # MatchTransceiver
        if match_proc(proc, seeds, args.region):
            for mem in outputmems:
                if match_mem(mem, seeds, args.region):
                    outputmems_new.append(mem)
            inputmems_new = inputmems
    elif 'FT' in proc: # FitTrack
        if match_proc(proc, seeds, args.region):
            for mem in inputmems:
                if 'FM' not in mem:
                    inputmems_new.append(mem)
                else:
                    if match_mem(mem, seeds,args.region):
                        inputmems_new.append(mem)
            outputmems_new = outputmems
    elif 'PD' in proc: # PurgeDuplicate
        for mem in inputmems:
            if match_mem(mem, seeds, args.region):
                inputmems_new.append(mem)
        for mem in outputmems:
            if match_mem(mem, seeds, args.region):
                outputmems_new.append(mem)           
        
    # write to output
    # check if new input and output memories are empty
    if len(inputmems_new)==0 or len(outputmems_new)==0:
        continue

    for imn in inputmems_new:
        fo.write(imn+" ")
    fo.write("> "+proc+" >")
    for omn in outputmems_new:
        fo.write(" "+omn)
    fo.write("\n")

print 'Output ', args.output

