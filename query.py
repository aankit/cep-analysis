from parse import parse_ceps
import csv


#return records with term count as key and count as value
def count_search_term(records, term, case_senstive=False):
    for record in records:
        if term not in record.keys():
            record[term] = 0
        if case_senstive:
            matches = re.findall(rf'{term}', record['answer'])
        else:
            matches = re.findall(rf'{term}', record['answer'], re.IGNORECASE)
        for match in matches:
            record[term] += 1
    return records


def main():
    cep_structure_filepath = './cep1819-structure-clean.csv'
    cep_text_filepaths = './cep_txt_utf'
    records = parse_ceps(cep_text_filepaths, cep_structure_filepath)
    cs_terms = ['ELA']
    ci_terms = ['math', 'code', 'computer', 'tech', 'literacy', 'blended literacy', 'computational thinking', 'science']
    for term in ci_terms:
        records = count_search_term(records, term)
    for term in cs_terms:
        records = count_search_term(records, term, True)
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

    filename = "portfolio-schools_search-terms.csv"
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
    # qs_parsed = find_q_indices(questions)

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    pp = pprint.PrettyPrinter()
    main()