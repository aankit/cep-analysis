#!/bin/bash

for file in ./pdfs/*
do
    filename=$(echo $file | cut -d'/' -f 3)
    filestem=$(echo $filename | cut -d'.' -f 1)
    txtfilename="./txt/${filestem}.txt"
    filesize=`wc -c $file | awk '{print $1}'`
    if [[ $filesize -lt 1300 ]]
    then 
        echo "removing $txtfilename"
        rm $txtfilename
        echo "removing $file"
        rm $file
    fi
done