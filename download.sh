#!/bin/bash

while IFS=, read -r dbn rh_school bn url tot_enrollment num_female num_black num_hispanic
do
    echo "saving to ./pdfs/$bn.pdf"
    curl $url -o "./pdfs/$bn.pdf"  
done < cep-dashboard.csv