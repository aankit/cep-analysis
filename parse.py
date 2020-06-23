#!/usr/bin/env python

import csv
import sys
import logging
from os import listdir
from os.path import isfile, join
import pprint
from fuzzysearch import find_near_matches
import re


#get list of all cleaned text files
def get_cep_txt_filepaths(text_dir_path):
    text_filepaths = [join(text_dir_path, f) for f in listdir(text_dir_path) if isfile(join(text_dir_path, f))]
    return text_filepaths


#check if cep structure csv is reading correctly, return lines with issues
def cep_structure_intake(filepath):
    structure = []
    cep_structure = open(filepath, 'r', encoding='utf-8')
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
                structure.append(row)
    return structure


def fuzzysearch(query, data):
    match_current_q = None
    for max_distance in range(1, 8):
        #match current q
        match_current_q = find_near_matches(query, data, max_l_dist=max_distance)
        #did we find anything?
        if len(match_current_q) > 0:
            break
        else:
            match_current_q = None
    return match_current_q


def find_section_indices(cep_text_file_paths, structure):
    records = []
    for filepath in get_cep_txt_filepaths(cep_text_file_paths):
        school_cep = open(filepath, 'r')
        with school_cep:
            data = school_cep.read()
            school_records = []
            starting_index = 0
            for index, section_and_question in enumerate(structure):
                # separate section and question
                section = section_and_question[0]
                question = section_and_question[1]
                section_index = data.find(section, starting_index)
                if section_index != -1:
                    starting_index = section_index
                    cep_record = {}
                    cep_record['bn'] = filepath[-8:-4]
                    cep_record['structure_index'] = index
                    cep_record['section'] = section
                    cep_record['section_index'] = section_index
                    school_records.append(cep_record)
                else:
                    print(f'{section} not found')
                    # pass
            for i, record in enumerate(school_records):
                current_section_index = record['section_index']
                look_ahead = 1
                next_section_index = None
                while next_section_index is None:
                    if i+look_ahead >= len(school_records)-1:
                        next_section_index = len(data) - 1
                    else:
                        next_section_index = school_records[i+look_ahead]['section_index']
                        if current_section_index == next_section_index:
                            look_ahead += 1
                            next_section_index = None
                        else:
                            next_section_index = school_records[i+look_ahead]['section_index']
                record['section_end_index'] = next_section_index - 1
                records.append(record)
    return records


def find_question_indices(cep_text_file_paths, sections, structure):
    records = []
    num_schools = 1
    for filepath in get_cep_txt_filepaths(cep_text_file_paths):
        school_cep = open(filepath, 'r')
        bn = filepath[-8:-4]
        print(f'{num_schools}: {bn}')
        with school_cep:
            data = school_cep.read()
            #let's grab our sections data record about this CEP
            school_section_records = [record for record in sections if record['bn'] == bn]
            qf = 0
            tq = 0
            for record in school_section_records:
                tq += 1
                question = structure[record['structure_index']][1]
                section = structure[record['structure_index']][0]
                section_data = data[record['section_index']:record['section_end_index']]
                question_index = section_data.find(question)
                if question_index == -1:
                    print("using fuzzy")
                    fuzzy_match = fuzzysearch(question, section_data)
                    if fuzzy_match is not None:
                        if len(fuzzy_match) > 1:
                            print(section)
                            print(question)
                            print(fuzzy_match)
                            raise Exception("too many matches found")  # comment out in future
                        else:
                            qf += 1
                            question_index = fuzzy_match[0].start
                            question_end_index = fuzzy_match[0].end
                    else:
                        print(f'{section} : {question} not found')
                else:
                    qf += 1
                    question_end_index = question_index + len(question)
                #if we have a question that falls within current section, then let's remember the question indices
                record['question_index'] = record['section_index'] + question_index
                record['question_end_index'] = record['section_index'] + question_end_index
                record['question'] = question
                records.append(record)
            print(f'{qf} out of {tq}')
            num_schools += 1
    return records


def find_answer_indices(cep_text_file_paths, questions):
    records = []
    for filepath in get_cep_txt_filepaths(cep_text_file_paths):
        school_cep = open(filepath, 'r')
        bn = filepath[-8:-4]
        with school_cep:
            data = school_cep.read()
            #let's grab our sections data record about this CEP
            school_records = [record for record in questions if record['bn'] == bn]
            for i, record in enumerate(school_records):
                #the answer begins after the question ends, altho some qs have extra help text that we'll figure out later
                answer_index = record['question_end_index'] + 1
                #the answer either ends at the next question if q in same section or next section if different section
                if i == len(school_records)-1:
                    answer_end_index = record['section_end_index']
                else:
                    if record['section_index'] == school_records[i+1]['section_index']:
                        answer_end_index = school_records[i+1]['question_index'] - 1
                    else:
                        answer_end_index = record['section_end_index']
                record['answer_index'] = answer_index
                record['answer_end_index'] = answer_end_index
                record['answer'] = data[answer_index:answer_end_index]
                records.append(record)
    return records


#return records with term count as key and count as value
def count_search_term(cep_text_file_paths, records, term, case_senstive=False):
    for filepath in get_cep_txt_filepaths(cep_text_file_paths):
        counter = "|"
        print(f'searching {term} {counter}')
        school_cep = open(filepath, 'r')
        bn = filepath[-8:-4]
        with school_cep:
            data = school_cep.read()
            #let's grab our sections data record about this CEP
            for record in records:
                if record['bn'] == bn:
                    if case_senstive:
                        matches = re.findall(rf'{term}', record['answer'])
                    else:
                        matches = re.findall(rf'{term}', record['answer'], re.IGNORECASE)
                    for match in matches:
                        if term in record.keys():
                            record[term] += 1
                        else:
                            record[term] = 1
        counter += "|"
    return records


def test():
    cep_structure_filepath = './cep1819-structure-clean.csv'
    cep_text_file_paths = './cep_txt_utf'
    #check if issues, get questions
    structure = cep_structure_intake(cep_structure_filepath)
    #start parsing the text files, starting broad and getting more granular
    sections = find_section_indices(cep_text_file_paths, structure)
    questions = find_question_indices(cep_text_file_paths, sections, structure)
    records = find_answer_indices(cep_text_file_paths, questions)
    cs_terms = ['ELA']
    ci_terms = ['math', 'code', 'computer', 'tech', 'literacy', 'blended literacy', 'computational thinking', 'science', 'grades served']
    for term in ci_terms:
        records = count_search_term(cep_text_file_paths, records, term)
    #answers
    for record in records:
        if record['bn'] == 'X086' and 'math' in record.keys():
            pp.pprint(record)
    # qs_parsed = find_q_indices(questions)

logging.basicConfig(stream=sys.stderr, level=logging.ERROR)
pp = pprint.PrettyPrinter()
test()
