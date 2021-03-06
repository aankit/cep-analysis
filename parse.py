#!/usr/bin/env python

import csv
import sys
import logging
from os import listdir
from os.path import isfile, join
from fuzzysearch import find_near_matches
import re

logging.basicConfig(filename='parse.log', filemode='w', level=logging.INFO)


def parse_ceps(cep_text_filepaths, cep_structure_filepath):
    #check if issues, get questions
    structure = structure_intake(cep_structure_filepath, 2)
    #start parsing the text files, starting broad and getting more granular
    sections = find_section_indices(cep_text_filepaths, structure)
    questions = find_question_indices(cep_text_filepaths, sections, structure)
    answers = find_answer_indices(cep_text_filepaths, questions)
    return answers


def parse_ceps_by_term(cep_text_filepaths, terms_filepath):
    #check if issues with terms
    structure = structure_intake(terms_filepath, 2)
    terms = []
    for row in structure:
        terms.append(row[0])
    excerpts = find_term_indices(cep_text_filepaths, structure)
    # excerpts = find_excerpt_indices(cep_text_filepaths, terms)
    return terms, excerpts


#get list of all cleaned text files
def get_cep_txt_filepaths(text_dir_path):
    text_filepaths = [join(text_dir_path, f) for f in listdir(text_dir_path) if not f.startswith('.') and isfile(join(text_dir_path, f))]
    return text_filepaths


#check if cep structure csv is reading correctly, return lines with issues
def structure_intake(filepath, expected_length, headers=False):
    structure = []
    cep_structure = open(filepath, 'r', encoding='utf-8')
    with cep_structure:
        reader = csv.reader(cep_structure)
        #log if CSV has errors
        line_number = 0  # for debugging purposes
        for row in reader:
            #for incremementing so we can report what line number of CSV error
            line_number += 1
            #if headers and first line, go to next iteration
            if headers and line_number == 1:
                continue
            #does the CSV have the section, question structure?
            if len(row) != expected_length:
                msg = f"line {line_number} has an issue."
                logging.info(msg)
            else:
                structure.append(row)
    return structure


def fuzzysearch(query, data, max_distance=8):
    match_current_q = None
    for distance in range(1, max_distance):
        #match current q
        match_current_q = find_near_matches(query, data, max_l_dist=distance)
        #did we find anything?
        if len(match_current_q) > 0:
            break
        else:
            match_current_q = None
    return match_current_q


def find_section_indices(cep_text_filepaths, structure):
    records = []
    for filepath in get_cep_txt_filepaths(cep_text_filepaths):
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
                    msg = f"{section} not found"
                    logging.info(msg)
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


def find_question_indices(cep_text_filepaths, sections, structure):
    records = []
    for filepath in get_cep_txt_filepaths(cep_text_filepaths):
        school_cep = open(filepath, 'r')
        bn = filepath[-8:-4]
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
                    fuzzy_match = fuzzysearch(question, section_data)
                    if fuzzy_match is not None:
                        if len(fuzzy_match) > 1:
                            msg = f"{question} found twice in {section}"
                            logging.info(msg)
                            raise Exception("too many matches found")  # comment out in future
                        else:
                            qf += 1
                            question_index = fuzzy_match[0].start
                            question_end_index = fuzzy_match[0].end
                    else:
                        msg = f"{section} : {question} not found"
                        logging.info(msg)
                else:
                    qf += 1
                    question_end_index = question_index + len(question)
                #if we have a question that falls within current section, then let's remember the question indices
                record['question_index'] = record['section_index'] + question_index
                record['question_end_index'] = record['section_index'] + question_end_index
                record['question'] = question
                records.append(record)
            msg = f"{bn}: {qf} out of {tq}"
            logging.info(msg)
    return records


def find_answer_indices(cep_text_filepaths, questions):
    records = []
    for filepath in get_cep_txt_filepaths(cep_text_filepaths):
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


def find_term_indices(cep_text_filepaths, structure):
    exact_matches_only = ["Fundations", "Zearn", "CodeX", "iReady", "i-Ready"]
    records = []
    half_excerpt_length = 50
    for filepath in get_cep_txt_filepaths(cep_text_filepaths):
        school_cep = open(filepath, 'r')
        bn = filepath[-8:-4]
        with school_cep:
            data = school_cep.read()
            for row in structure:
                term = row[0]
                #needs to be parameterized, right now manually referencing column with lookup term
                lookup_array = row[1].split(",") 
                for lookup in lookup_array:
                    matches = re.finditer(rf"{lookup}", data)
                    if not any(matches) and term not in exact_matches_only:
                        matches = fuzzysearch(f" {lookup} ", data, 2)
                    if matches:
                        for match in matches:
                            term_matches = {}
                            try:
                                start = match.start()
                            except:
                                start = match.start
                            try:
                                end = match.end()
                            except:
                                end = match.end
                            excerpt_start = start-half_excerpt_length if start > half_excerpt_length else 0
                            excerpt_end = end+half_excerpt_length if end+half_excerpt_length < len(data) else len(data)
                            term_matches["bn"] = bn
                            term_matches["term"] = term
                            term_matches["start"] = start
                            term_matches["end"] = end
                            term_matches["excerpt"] = data[excerpt_start:excerpt_end]
                            records.append(term_matches)
    return records
