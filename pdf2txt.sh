#!/bin/bash

for file in ./pdfs/*
do
    filename=$(echo $file | cut -d'/' -f 3)
    filestem=$(echo $filename | cut -d'.' -f 1)
    txtfilename="./txt/${filestem}.txt"
    echo "saving to $txtfilename"
    pdf2txt.py -o $txtfilename $file
done