#!/usr/bin/python3

import csv
import sys
import logging
from os import listdir
from os.path import isfile, join
import pprint

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
pp = pprint.PrettyPrinter()


#get list of all cleaned text files
def get_cep_txt_filepaths():
    text_dir_path = './txt_clean/'
    text_filepaths = [join(text_dir_path, f) for f in listdir(text_dir_path) if isfile(join(text_dir_path, f))]
    return text_filepaths


def extract_answers_from_ceps(questions):
    num_qs = len(questions)
    cep_parser_indices = {}
    for filepath in get_cep_txt_filepaths():
        cep_parser_indices[filepath] = {}
        school_cep = open(filepath, 'r')
        with school_cep:
            data = school_cep.read()
            qs_found = 0
            #get lowest indices of questions
            for q_number, question in enumerate(questions):
                #find current q lowest index and set answer lowest index if q found
                q_lowest_index = data.find(question)
                a_lowest_index = q_lowest_index + len(question) if q_lowest_index != -1 else -1
                #find next q lowest index and set answer highest index if next q found
                next_q_lowest_index = data.find(questions[q_number+1]) if q_number < (len(questions)-1) else len(data)
                a_highest_index = next_q_lowest_index - 1 if next_q_lowest_index != -1 else -1
                #if q and a's found, save to parser indices else log error
                if a_lowest_index != -1 or a_highest_index != -1:
                    qs_found += 1
                    #save the question number, question, answer lowest index, and answer highest index
                    cep_parser_indices[filepath][q_number] = [question, a_lowest_index, a_highest_index]
                else:
                    logging.info(f'{q_number+1} is not found')
            #logging if we didn't find total number of questions
            if(qs_found < num_qs):
                logging.info(f'found {qs_found} of {num_qs} in {filepath}')
            #print the cep_parse_indices
    pp.pprint(cep_parser_indices['./txt_clean/X811.txt'])


#check if cep structure csv is reading correctly
def extract_questions_from_cep_structure(cep_structure):
    questions = []
    with cep_structure:
        reader = csv.reader(cep_structure)
        #log if CSV has errors
        line_number = 0  # for debugging purposes

        for row in reader:
            #for incremementing so we can report what line number of CSV error
            line_number += 1

            #does the CSV have the section, question structure?
            row_length = len(row)
            if(row_length != 2):
                logging.info("line %d has an issue", line_number)
            else:
                questions.append(row[1])
    return questions


cep_structure = open('cep1819-structure.csv', 'r')
#get the questions
questions = extract_questions_from_cep_structure(cep_structure)
#can we find the question in every txt file? if not log which question and which text file
extract_answers_from_ceps(questions)