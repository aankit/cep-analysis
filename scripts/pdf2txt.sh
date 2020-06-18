#!/usr/local/bin/bash

source config.sh

for year in ${Years[@]}; do
    save_location="${project_path}/txt/${year}"
    mkdir $save_location
    cd $save_location
    for file in $project_path/pdfs/$year/*; do
        filestem=$(basename "$file" | cut -f 1 -d '.')
        txtfile="${save_location}/${filestem}.txt"
        if test -f "$txtfile"; then
            echo "${file} exists"
        else
            echo "converting ${file} to ${txtfile}"
            pdf2txt.py -o $txtfile $file
        fi
    done
done

# for file in ../pdfs/*
# do
#     filename=$(echo $file | cut -d'/' -f 3)
#     filestem=$(echo $filename | cut -d'.' -f 1)
#     txtfilename="./txt/${filestem}.txt"
#     echo "saving to $txtfilename"
#     # pdf2txt.py -o $txtfilename $file
# done