#!/bin/bash

for file in ./txt/*
do
    filename=$(echo $file | cut -d'/' -f 3)
    echo "cleaning ${filename}"
    sed -n -e ":a" -e "$ s/\n//gp;N;b a" < $file | \
    sed -e 's/ \{2,\}/ /g' | \
    sed 's/^[ \t]*//;s/[ \t]*$//'  | \
    sed 's/2018-19\ CEP\ [[:digit:]]//g' | \
    sed 's/2018-19 COMPREHENSIVE EDUCATIONAL PLAN (CEP) DBN: (i.e. 01M001)://g' | \
    tr -d '\f\' > ./cep_txt_clean/$filename
done