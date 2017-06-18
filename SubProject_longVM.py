#!/usr/bin/env python

import argparse

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
    goodseedings=[]

seedings = goodseedings if args.seedings is None else args.seedings
print seedings

if not set(seedings).issubset(goodseedings):
    print 'Required seedings are not all possible in this detector region'
    print 'available seedings are :', goodseedings
    exit(1)

print 'Will read', args.input
fi = open(args.input,"r")
fo = open(args.output,"w")

for line in fi:

    if len(line.split(' > '))!=3:
        continue
    
    proc = line.split(' > ')[1]

    # check processing module first
    # seeding
    match_proc = False
    for seeding in seedings:
        seed1 = seeding[0:2]
        seed2 = seeding[2:4]
        # VMRouterTE
        if 'VMRTE' in proc:
            if seed1 in proc or seed2 in proc:
                match_proc = True
                break
        # VMRouterME, ProjectionTransceiver, MatchTransceiver
        if 'VMRME' in proc or 'PT' in proc or 'MT' in proc:
            if seed1 not in proc and seed2 not in proc:
                match_proc = True
                break
        # TrackletEngine
        if 'TE' in proc:
            if '_'+seed1 in proc and '_'+seed2 in proc:
                match_proc = True
                break
        # TrackletCalculator, ProjectionRouter, MatchEngine, MatchCalculator,
        # FitTrack
        if 'TC' in proc or 'PR' in proc or 'ME' in proc or 'MC' in proc or 'FT' in proc:
            if seeding in proc:
                match_proc = True
                break
        # PurgeDuplicate
        if 'PD' in proc:
            match_proc = True
            
    if not match_proc:
        continue

    # region
    if args.region in ['L','D']: # not hybrid
        if 'PHIQ' in proc or 'PHIW' in proc or 'PHIX' in proc or 'PHIY' in proc:
            continue
    # VMRTE, VMME, TE, PR, ME, MC, MT
    if 'VMR' in proc or 'TE' in proc or 'PR' in proc or 'ME' in proc or 'MC' in proc or 'MT' in proc:
        if args.region=='L' and '_D' in proc:  # barrel only
            continue
        if args.region=='D' and '_L' in proc:  # disk only
            continue
            
    if 'PT' in proc:
        if args.region=='L' and 'D5' in proc:
            continue
        if args.region=='D':
            if 'L1' in proc or 'L2' in proc:
                continue

            
    # now pick relevant memories
    inputmems = line.split(' > ')[0].split()
    outputmems = line.split(' > ')[2].split()
    
    inputmems_new = []
    outputmems_new = []

    for im in inputmems:
        veto_mem = False
        # check seeding
        if 'TPROJ' in im or 'FM' in im or 'TF' in im or 'CT' in im:    
            mseed = im.split('_')[1][0:4]
            if mseed not in seedings:
                veto_mem = True
        if veto_mem:
            continue
        
        # check region
        if 'TPROJ' in im or 'FM' in im:
            target = im.split('_')[2][0:2]
            if args.region not in target:
                veto_mem = True
        if veto_mem:
            continue
        
        inputmems_new.append(im)


    for om in outputmems:
        veto_mem = False
        # check seeding
        if 'TPROJ' in om or 'FM' in om or 'TF' in om or 'CT' in om:    
            mseed = om.split('_')[1][0:4]
            if mseed not in seedings:
                veto_mem = True
        if veto_mem:
            continue
        
        # check region
        if 'TPROJ' in om or 'FM' in om:
            target = om.split('_')[2][0:2]
            if args.region not in target:
                veto_mem = True
        if veto_mem:
            continue
        
        outputmems_new.append(om)

    # write to output
    for imn in inputmems_new:
        fo.write(imn+" ")
    fo.write("> "+proc+" >")
    for omn in outputmems_new:
        fo.write(" "+omn)
    fo.write("\n")

print 'Output ', args.output
