#!/bin/bash

for file in ./txt/*
do
    filename=$(echo $file | cut -d'/' -f 3)
    echo "removing new lines from ${filename}"
    # tr -d '\n' < $file > ./txt_clean/$filename
    sed -n -e ":a" -e "$ s/\n//gp;N;b a" < $file | \
    sed -e 's/ \{2,\}/ /g' | \
    sed 's/^[ \t]*//;s/[ \t]*$//' > ./cep_txt_clean/$filename
done