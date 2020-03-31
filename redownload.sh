#!/bin/bash

url="https://www.nycenet.edu/documents/oaosi/cep/2018-19/cep_"

for file in ./pdfs/*
do
    filesize=`wc -c $file | awk '{print $1}'`
    if [[ $filesize -lt 1300 ]]
    then 
        filename=$(echo $file | cut -d'/' -f 3)
        url="${url}${filename}"
        echo "saving to ./retry_pdfs/$filename"
        curl $url -o "./retry_pdfs/$bn.pdf"  
    fi
done