#!/usr/bin/python3

import csv

cep_structure = open('cep1819-structure.csv', 'r')

with cep_structure:

    reader = csv.reader(cep_structure)

    for row in reader:
        print(row)
        print(len(row))
        # section = row[0]
        # question = row[1]

        # print(section)
        # print(question)
