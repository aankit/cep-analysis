#!/bin/bash

for file in ./txt/*
do
    filename=$(echo $file | cut -d'/' -f 3)
    echo "cleaning ${filename}"
    stripped=$(sed -n -e ":a" -e "$ s/\n//gp;N;b a" < $file | \
            sed -e 's/ \{2,\}/ /g' | \
            sed 's/^[ \t]*//;s/[ \t]*$//'  | \
            sed 's/2018-19\ CEP\ [[:digit:]]//g' | \
            tr -d '\f\')

    if echo "$stripped" | grep -q "2018-19 COMPREHENSIVE EDUCATIONAL PLAN (CEP) DBN: (i.e. 01M001):";
    then
        echo "found CEP"
        echo "$stripped" | sed 's/2018-19 COMPREHENSIVE EDUCATIONAL PLAN (CEP) DBN: (i.e. 01M001)://g' > ./cep_txt/$filename
    elif echo "$stripped" | grep -q "2018-19 SCHOOL COMPREHENSIVE EDUCATIONAL PLAN (SCEP) DBN: (i.e. 01M001):";
    then
        echo "found SCEP"
        echo "$stripped" | sed 's/2018-19 SCHOOL COMPREHENSIVE EDUCATIONAL PLAN (SCEP) DBN: (i.e. 01M001)://g' > ./scep_txt/$filename
    elif echo "$stripped" | grep -q "2018-19 RENEWAL SCHOOL COMPREHENSIVE EDUCATIONAL PLAN (RSCEP) DBN: (i.e. 01M001):";
    then    
        echo "found RSCEP"
        echo "$stripped" | sed 's/2018-19 RENEWAL SCHOOL COMPREHENSIVE EDUCATIONAL PLAN (RSCEP) DBN: (i.e. 01M001)://g' > ./rscep_txt/$filename
    elif echo "$stripped" | grep -q "2018-19 COMPREHENSIVE EDUCATIONAL PLAN (CEP-CS) DBN: (i.e. 01M001):";
    then
        echo "found CEP-CS"
        echo "$stripped" | sed 's/2018-19 COMPREHENSIVE EDUCATIONAL PLAN (CEP-CS) DBN: (i.e. 01M001)://g' > ./cep_cs_txt/$filename
    elif echo "$stripped" | grep -q "2018-19 RISE SCHOOL COMPREHENSIVE EDUCATIONAL PLAN (R-CEP) DBN: (i.e. 01M001):";
        then
        echo "found RISE CEP"
        echo "$stripped" | sed 's/2018-19 RISE SCHOOL COMPREHENSIVE EDUCATIONAL PLAN (R-CEP) DBN: (i.e. 01M001)://g' > ./rise_cep_txt/$filename
    else
        echo "uncategorized CEP"
        echo "$stripped" > ./uncat_cep_txt/$filename
    fi

done