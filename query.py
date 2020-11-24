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


def schools_term_counts(records, ci_terms, cs_terms, rh_schools):
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


def school_term_excerpts(records, terms, school_filter):
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


def schools_terms_counts(records, cs_terms, rh_schools):
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


def school_terms_pairs(excerpts, term_combinations, rh_schools):
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
    years = ['2009-10', '2010-11', '2011-12', '2012-13', '2013-14', '2014-15', '2015-16', '2016-17', '2017-18', '2018-19']
    cep_structure_filepath = './input/curriculum-terms.csv'
    for year in years:
        output_file = f'output/curriculum_lookup_historical/{year}.csv'
        cep_text_filepaths = f'./txt/{year}/'
        print(output_file)
        #parsing needs to happen once and be stored in a database, this will be database connection in future
        #records = parse_ceps(cep_text_filepaths, cep_structure_filepath)
        terms, excerpts = parse_ceps_by_term(cep_text_filepaths, cep_structure_filepath)
        # term_combinations = list(itertools.combinations(terms, 2))
        raw_data_write(excerpts, ["bn", "term", "excerpt"], output_file)


if __name__ == '__main__':
    main()
