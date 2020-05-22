#!/usr/bin/env python

import csv
import sys
import logging
from os import listdir
from os.path import isfile, join
import pprint
from fuzzysearch import find_near_matches

logging.basicConfig(stream=sys.stderr, level=logging.ERROR)
pp = pprint.PrettyPrinter()


#get list of all cleaned text files
def get_cep_txt_filepaths():
    text_dir_path = './cep_txt/'
    text_filepaths = [join(text_dir_path, f) for f in listdir(text_dir_path) if isfile(join(text_dir_path, f))]
    return text_filepaths


#check if cep structure csv is reading correctly, return lines with issues
def cep_structure_questions(filepath):
    questions = []
    cep_structure = open(filepath, 'r')
    with cep_structure:
        reader = csv.reader(cep_structure)
        #log if CSV has errors
        line_number = 0  # for debugging purposes
        for row in reader:
            #for incremementing so we can report what line number of CSV error
            line_number += 1
            #does the CSV have the section, question structure?
            if(len(row) != 2):
                logging.info("line %d has an issue", line_number)
            else:
                questions.append(row)
    return questions


def fuzzy_parse_ceps(questions):
    ceps_parsed = {}
    q_not_found_count = {}
    for filepath in get_cep_txt_filepaths():
        ceps_parsed[filepath] = {}
        # if filepath == './cep_txt_clean/X391.txt':
        school_cep = open(filepath, 'r')
        with school_cep:
            data = school_cep.read()
            num_qs
            qs_found = 0
            #retrieve question matches
            question_matches = []
            for q_number, section_and_question in enumerate(questions):
                #initializing here even though I'm populating below
                ceps_parsed[filepath][q_number] = []
                #break out section and question
                section = section_and_question[0]
                question = section_and_question[1]
                #does this section exist?
                if data.find(section) != -1:
                    num_qs += 1
                    #using fuzzysearch
                    max_distance = 1  # Lehvenstein distance will increase if we can't initially find the question
                    for i in range(0, 10):
                        #match current q
                        find_near_matches(question, data, max_l_dist=max_distance)
                        #did we find anything?
                        if len(match_current_q) > 0:
                            #yup, increment count for logging and save away match
                            qs_found += 1
                            question_matches.append(match_current_q[0])
                            break
                        else:
                            max_distance += i  # we didn't find anything so we increase max Levhenstein distance
                    #if we're here, we didn't find the question
                    if question in q_not_found_count:
                        q_not_found_count[question] += 1
                    else:
                        q_not_found_count[question] = 1
                        # logging if we didn't find total number of questions
            if(qs_found == num_qs):
                logging.info(f'found all qs in {filepath}')
            else:
                logging.warning(f'found {qs_found} of {num_qs} in {filepath}')
            #retrieve all answers (in between questions)
            for m, match in enumerate(question_matches):
                question = match.matched
                answer_start = match.end + 1
                next_match = question_matches[m+1]
                answer_end = next_match.start - 1
                answer = data[answer_start:answer_end]
                ceps_parsed[filepath][m] = [question, answer]
    return ceps_parsed


def parse_ceps(questions):
    ceps_parsed = []
    q_not_found_count = {}
    for filepath in get_cep_txt_filepaths():
        # ceps_parsed[filepath] = {}
        # if filepath == './cep_txt_clean/X391.txt':
        school_cep = open(filepath, 'r')
        with school_cep:
            data = school_cep.read()
            num_qs = 0
            qs_found = 0
            #get lowest indices of questions
            for q_number, section_and_question in enumerate(questions):
                # separate section and question
                section = section_and_question[0]
                question = section_and_question[1]
                # check if question section in data
                if data.find(section) != -1:
                    #initialize dict to capture cep, qn, q, and a set
                    current_cep_q_a = {}
                    current_cep_q_a['dbn'] = filepath[-8:-4]
                    current_cep_q_a['number'] = q_number
                    current_cep_q_a['question'] = question
                    num_qs += 1
                    # find current q lowest index
                    q_lowest_index = data.find(question)
                    # find next q lowest index
                    next_q_lowest_index = data.find(questions[q_number+1][1]) if q_number < (len(questions)-1) else len(data)
                    # set answer lowest index if q found
                    a_lowest_index = q_lowest_index + len(question) if q_lowest_index != -1 else -1
                    # set answer highest index if next q found
                    a_highest_index = next_q_lowest_index - 1 if next_q_lowest_index != -1 else -1
                    # if q and a's found, save to parser indices else log error
                    if a_lowest_index != -1:
                        qs_found += 1
                        # save the question number, question, answer lowest index, and answer highest index
                        answer = data[a_lowest_index:a_highest_index]
                        current_cep_q_a['answer'] = answer
                    else:
                        if question in q_not_found_count:
                            q_not_found_count[question] += 1
                        else:
                            q_not_found_count[question] = 1
                ceps_parsed.append(current_cep_q_a)
            # logging if we didn't find total number of questions
            if(qs_found == num_qs):
                logging.info(f'found all qs in {filepath}')
            else:
                logging.warning(f'found {qs_found} of {num_qs} in {filepath}')
    #for debugging parse process
    for k, v in q_not_found_count.items():
        if v > 1000 and v < 1579:
            print(k)
            print("----")
    return ceps_parsed


cep_structure_filepath = './cep1819-structure.csv'
#check if issues, get questions
questions = cep_structure_questions(cep_structure_filepath)
#can we find the question in every txt file? if not log which question and which text file
ceps_parsed = parse_ceps(questions)
#lots of data to output, let's choose one question for now
one_record_per_school = []
for record in ceps_parsed:
    if record['number'] == 57:
        one_record_per_school.append(record)
#now let's write this one record per school for illustrative purposes
fields = ["dbn", "number", "question", "answer"]
filename = "standard_ceps_pip.csv"
with open(filename, 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fields)
    writer.writeheader()
    writer.writerows(one_record_per_school)
#fuzzysearch_answers_from_ceps(cep_structure_filepath)


