#!/usr/local/bin/bash

project_path="/Users/Aankit/Documents/CEP"
declare -a Boroughs=("K" "M" "Q" "R" "X")
declare -a Years=("2009-10" "2010-11" "2011-12" "2012-13" "2013-14" "2014-15" "2015-16" "2016-17" "2017-18" "2018-19")
url_stem="https://www.nycenet.edu/documents/oaosi/cep/"
yes=0
no=0

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

echo "${yes} CEPs found"
echo "${no} not found or not schools"