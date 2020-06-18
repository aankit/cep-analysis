from parse import cep_structure_questions
from parse import parse_ceps
import csv
import re

cep_structure_filepath = './cep1819-structure.csv'
#check if issues, get questions
questions = cep_structure_questions(cep_structure_filepath)
#can we find the question in every txt file? if not log which question and which text file
ceps_parsed = parse_ceps(questions)
#lots of data to output, let's choose one question for now
query_results = []
for record in ceps_parsed:
    if record['dbn'] == "X086":
        if 'answer' in record.keys():
            if re.search(r'ELA', record['answer']):
                query_results.append(record)
#now let's write this one record per school for illustrative purposes
fields = ["dbn", "number", "question", "answer"]
filename = "X086-ELA.csv"
with open(filename, 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fields)
    writer.writeheader()
    writer.writerows(query_results)
#fuzzysearch_answers_from_ceps(cep_structure_filepath)