#!/usr/bin/env python

from parse import parse_ceps, parse_ceps_by_term
import csv
import re
from fuzzysearch import find_near_matches
import pprint
import itertools

pp = pprint.PrettyPrinter()


#add term as a key and count as value to each record
def add_count_term_to_record(records, term, case_senstive=False):
    for record in records:
        if term not in record.keys():
            record[term] = 0
        if case_senstive:
            matches = re.findall(rf"{term}", record['answer'])
        else:
            matches = re.findall(rf"{term}", record['answer'], re.IGNORECASE)
        for match in matches:
            record[term] += 1
    return records


def create_new_record_each_term(records, term, case_senstive=False):
    excerpt_range = 30
    term_records = []
    for record in records:
        if case_senstive:
            matches = re.finditer(rf'{term}', record['answer'])
        else:
            matches = re.finditer(rf'{term}', record['answer'], re.IGNORECASE)
        for match in matches:
            new_record = record
            new_record['term'] = match.group()
            excerpt_start = 0 if (match.start() - excerpt_range) < 0 else match.start()-excerpt_range
            excerpt_end = len(record['answer']) if (match.end()+excerpt_range) > len(record['answer']) else match.end()+excerpt_range
            excerpt = record['answer'][excerpt_start:excerpt_end]
            new_record['excerpt'] = excerpt
            term_records.append(new_record)
    return term_records


def find_term_locations(record, term, case_senstive=False, excerpt_range=15):
    if case_senstive:
        matches = re.finditer(rf'{term}', record['answer'])
    else:
        matches = re.finditer(rf'{term}', record['answer'], re.IGNORECASE)
    term_locations = []
    for match in matches:
        term_location = {}
        term_location['term'] = match.group()
        term_location['term_index'] = match.start()
        term_location['term_end_index'] = match.end()
        excerpt_start = 0 if term_location['term_index'] - excerpt_range < 0 else term_location['term_index'] - excerpt_range
        excerpt_end = len(record['answer']) if term_location['term_end_index'] + excerpt_range > len(record['answer']) else term_location['term_index'] + excerpt_range
        term_location['excerpt'] = record["answer"][excerpt_start:excerpt_end]
        term_location['bn'] = record['bn']
        term_location['section'] = record['section']
        term_location['question'] = record['question']
        term_locations.append(term_location)
    return term_locations


def query1(records, ci_terms, cs_terms, rh_schools):
    for term in ci_terms:
        records = add_count_term_to_record(records, term)
    for term in cs_terms:
        records = add_count_term_to_record(records, term, True)
    filename = "portfolio-schools_term-counts.csv"
    #build field names based on what was searched for
    fieldnames = ['bn', 'section', 'question', 'answer']
    for term in ci_terms:
        fieldnames.append(term)
    for term in cs_terms:
        fieldnames.append(term)
    to_write = []
    for record in records:
        record_to_write = {}
        if record['bn'] in rh_schools:
            for fieldname in fieldnames:
                record_to_write[fieldname] = record[fieldname]
            to_write.append(record_to_write)
    with open(filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='|')
        writer.writeheader()
        writer.writerows(to_write)


def query2(records, terms, school_filter):
    #a list of dictionaries with term, bn, section, question, excerpt
    all_term_locations = []
    for term in terms:
        for record in records:
            if record['bn'] in school_filter:
                one_term_locations = find_term_locations(record, term, True, 50)
                all_term_locations.extend(one_term_locations)
    filename = "portfolio-schools_terms-locations_(case_senstive).csv"
    #build field names based on what was searched for
    fieldnames = ['term', 'bn', 'section', 'question', 'excerpt']
    to_write = []
    for term_location in all_term_locations:
        record_to_write = {}
        for fieldname in fieldnames:
            record_to_write[fieldname] = term_location[fieldname]
        to_write.append(record_to_write)
    with open(filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='|')
        writer.writeheader()
        writer.writerows(to_write)


def query3(records, cs_terms, rh_schools):
    for term in cs_terms:
        records = add_count_term_to_record(records, term, True)
    filename = "portfolio-schools_blended-literacy-terms.csv"
    #build field names based on what was searched for
    fieldnames = ['bn']
    for term in cs_terms:
        fieldnames.append(term)
    to_write = []
    for school in rh_schools:
        school_dict = {}
        school_dict['bn'] = school
        for record in records:
            if record['bn'] == school:
                for term in cs_terms:
                    if term in school_dict.keys():
                        school_dict[term] += record[term]
                    else:
                        school_dict[term] = record[term]
        to_write.append(school_dict)
    with open(filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='|')
        writer.writeheader()
        writer.writerows(to_write)


def query4(excerpts, term_combinations, rh_schools):
    records = []
    for first, second in term_combinations:
        record = {}
        record["Intervention 1"] = first
        record["Intervention 2"] = second
        record["Num_Schools"] = 0
        for school in rh_schools:
            print(f"finding pairs in {school}")
            school_excerpts = [e for e in excerpts if e["bn"] == school]
            first_found = 0
            second_found = 0
            for excerpt in school_excerpts:
                if excerpt["term"] == first:
                    first_found += 1
                if excerpt["term"] == second:
                    second_found += 1
                if first_found > 0 and second_found > 0:
                    record["Num_Schools"] += 1
                    print("pair found")
                    break
        records.append(record)
    filename = "portfolio-schools_intervention_pairs.csv"
    #build field names based on what was searched for
    fieldnames = ["Intervention 1", "Intervention 2", "Num_Schools"]
    with open(filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='|')
        writer.writeheader()
        writer.writerows(records)


def raw_data_write(records, fieldnames, filename):
    to_write = []
    for record in records:
        row = {}
        for fieldname in fieldnames:
            row[fieldname] = record[fieldname]
        to_write.append(row)
    with open(filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='|')
        writer.writeheader()
        writer.writerows(to_write)


def main():
    cep_structure_filepath = './terms.csv'
    cep_text_filepaths = './txt/2018-19/'
    #parsing needs to happen once and be stored in a database, this will be database connection in future
    #records = parse_ceps(cep_text_filepaths, cep_structure_filepath)
    terms, excerpts = parse_ceps_by_term(cep_text_filepaths, cep_structure_filepath)
    term_combinations = list(itertools.combinations(terms, 2))
    # cs_terms = ['ELA', 'CS', 'Go Math', 'EngageNYC', 'NYC Performance Series', 'Harcourt Science', 'Amplify']
    cs_terms = ['Accelerated Reader 360',
                'Amplify',
                'Pearson',
                'BrainPOP',
                'CommonLit',
                'Core Knowledge',
                'Cortex',
                'Discovery Ed Tech Book',
                'EL Education',
                'Eureka Math',
                'Flocabulary',
                'FOSS',
                'Freckle',
                'GoFormative',
                'GoMath',
                'Google Classroom',
                'Great Minds Wit and Wisdom',
                'IDO',
                'Illuminate',
                'Imagine Learning',
                'INET',
                'iPuzzle',
                'iReady',
                'IXL',
                'Jump Math',
                'Kahoot',
                'Khan Academy',
                'LearnZillion',
                'Lexia',
                'Mathletics ',
                'MobyMax',
                'myON',
                'NearPod',
                'NewsELA',
                'Next Generation Learning Standards',
                'Passports',
                'Pathblazers',
                'Picture Perfect Science',
                'Quill',
                'Quizlet',
                'RazKids',
                'Read180',
                'Reading AZ',
                'Readorium',
                'ReadWorks',
                'ReadyGen',
                'ReflexMath',
                'REWARDS',
                'Rosetta Stone',
                'Sanford Harmony',
                'Schoology',
                'Splash Math',
                'STAR reading',
                'Starfalls',
                'Summit',
                'Tableau',
                'TC Reading and Writing Project',
                'The Writing Revolution (TWR)',
                'ThinkCERCA',
                'Versal',
                'Writing City',
                'Zearn']
    rh_schools = ['K516',
                  'X086',
                  'Q013',
                  'Q306',
                  'X359',
                  'M182',
                  'M083',
                  'Q330',
                  'Q014',
                  'Q019',
                  'X566',
                  'Q226',
                  'K392',
                  'X076',
                  'X481',
                  'K007',
                  'K013',
                  'K065',
                  'K089',
                  'K108',
                  'K149',
                  'K158',
                  'K190',
                  'K202',
                  'K213',
                  'K224',
                  'K273',
                  'K290',
                  'K306',
                  'K325',
                  'K328',
                  'K345',
                  'K346',
                  'K557',
                  'K677',
                  'X020',
                  'Q319',
                  'X178',
                  'X043',
                  'K375',
                  'K414',
                  'M175',
                  'K005',
                  'Q031',
                  'M015',
                  'M096',
                  'K041',
                  'K172',
                  'K557',
                  'K026',
                  'Q076',
                  'R010',
                  'M188',
                  'K401']
    raw_data_write(excerpts, ["bn", "term", "excerpt"], "term_pairs_excerpts.csv")
    query4(excerpts, term_combinations, rh_schools)


if __name__ == '__main__':
    main()
