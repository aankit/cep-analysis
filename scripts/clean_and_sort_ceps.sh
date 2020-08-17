#!/usr/local/bin/bash

source config.sh

for file in $project_path/txt/2018-19/*
do
    filename=$(basename "$file")
    echo "cleaning ${filename}"
    # sed alpha line strips down to alphanumeric, maybe unicode? should have documented where I found it
    stripped=$(sed 's/[^[:alpha:];\ -@]//g' < $file | \
            sed -n -e ":a" -e "$ s/\n//gp;N;b a" | \
            sed -e 's/ \{2,\}/ /g' | \
            sed 's/^[ \t]*//;s/[ \t]*$//'  | \
            sed 's/2018-19\ CEP\ [[:digit:]]//g' | \
            tr -d '\f\')

    if echo "$stripped" | grep -q "2018-19 COMPREHENSIVE EDUCATIONAL PLAN (CEP) DBN: (i.e. 01M001):";
    then
        echo "found CEP"
        echo "$stripped" | sed 's/2018-19 COMPREHENSIVE EDUCATIONAL PLAN (CEP) DBN: (i.e. 01M001)://g' > $project_path/cep_txt_utf/$filename
    elif echo "$stripped" | grep -q "2018-19 SCHOOL COMPREHENSIVE EDUCATIONAL PLAN (SCEP) DBN: (i.e. 01M001):";
    then
        echo "found SCEP"
        echo "$stripped" | sed 's/2018-19 SCHOOL COMPREHENSIVE EDUCATIONAL PLAN (SCEP) DBN: (i.e. 01M001)://g' > $project_path/scep_txt_utf/$filename
    elif echo "$stripped" | grep -q "2018-19 RENEWAL SCHOOL COMPREHENSIVE EDUCATIONAL PLAN (RSCEP) DBN: (i.e. 01M001):";
    then    
        echo "found RSCEP"
        echo "$stripped" | sed 's/2018-19 RENEWAL SCHOOL COMPREHENSIVE EDUCATIONAL PLAN (RSCEP) DBN: (i.e. 01M001)://g' > $project_path/rscep_txt_utf/$filename
    elif echo "$stripped" | grep -q "2018-19 COMPREHENSIVE EDUCATIONAL PLAN (CEP-CS) DBN: (i.e. 01M001):";
    then
        echo "found CEP-CS"
        echo "$stripped" | sed 's/2018-19 COMPREHENSIVE EDUCATIONAL PLAN (CEP-CS) DBN: (i.e. 01M001)://g' > $project_path/cep_cs_txt_utf/$filename
    elif echo "$stripped" | grep -q "2018-19 RISE SCHOOL COMPREHENSIVE EDUCATIONAL PLAN (R-CEP) DBN: (i.e. 01M001):";
        then
        echo "found RISE CEP"
        echo "$stripped" | sed 's/2018-19 RISE SCHOOL COMPREHENSIVE EDUCATIONAL PLAN (R-CEP) DBN: (i.e. 01M001)://g' > $project_path/rise_cep_txt_utf/$filename
    else
        echo "uncategorized CEP"
        echo "$stripped" > ./uncat_cep_txt/$filename
    fi

done