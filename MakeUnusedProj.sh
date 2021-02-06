#!/usr/bin/bash

####################################################################
# Update file unusedproj.dat (which is used by HourGlassConfig.py).
#
# This file lists the TPROJ memories that emulation indicates never
# contain data, so should be pruned from wiring map.
# 
#
# Before using this, checkout firmware repo, so it can be found in
# ../firmware-hls/
####################################################################

DATA="../firmware-hls/emData"
FILEOUT="unusedproj.txt"

if [ ! -f ${DATA}/download.sh ]
then
    echo "ERROR: ${DATA} not found. Please checkout firmware-hls repo."
    exit 1
fi

if [ ! -d ${DATA}/MemPrints/ ]
then
    echo "Downloading .txt files with BRAM test data into ${DATA}"
    echo "(takes a few minutes)"
    pushd $DATA
    ./download.sh
    popd
fi     

if [ -f $FILEOUT ]
then
    rm $FILEOUT
fi
    
for f in ${DATA}/MemPrints/TrackletProjections/*.dat
do
    # Count lines in file not containing event header.
    NUM_DATA_LINES=`\grep -v Event $f | wc -l`
    if [ $NUM_DATA_LINES == 0 ]
    then
	# Select ID of this memory from part of file name.
	TPROJ_ID=`echo $f | cut -d _ -f 2-4`
	echo $TPROJ_ID >> $FILEOUT
    fi
done

echo "File $FILEOUT written."
