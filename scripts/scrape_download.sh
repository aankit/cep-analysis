#!/usr/local/bin/bash

source config.sh

mkdir "${project_path}/pdfs/"
for year in ${Years[@]}; do
    mkdir "${project_path}/pdfs/${year}"
    cd "${project_path}/pdfs/${year}"
    for borough in ${Boroughs[@]}; do
        for num in {001..999}; do
            bn=${borough}${num}
            url="${url_stem}${year}/cep_${bn}.pdf"
            curl_status=`curl --silent --connect-timeout 5 --output /dev/null "${url}" -I -w "%{http_code}\n"`
            if [ $curl_status -eq "200" ]; then
                FILE="${project_path}/pdfs/${year}/$bn.pdf"
                if test -f "$FILE"; then 
                    echo "$FILE exists"
                else
                    echo "saving to ${project_path}/pdfs/${year}/$bn.pdf"
                    curl $url -o "${project_path}/pdfs/${year}/$bn.pdf"
                fi
            else
                echo "${bn} CEP for ${year} not found"
            fi
        done
    done
done