## CEP Analysis

1. Downloaded all NYC Department of Education school's Comprehensive Education Plan(CEPs) from the iPlan Portal. All public schools except charter schools, which are still considered public because they receive public funding, are required to submit CEPs annually. 1,579 schools filed plans for the 2018-19 school year.

2. Converted all PDFs to text files with PDFMiner's pdf2txt.py tool.

3. Removed newlines, leading spaces/tabs, and trailing spaces and tabs as it was hampering building the CSV of CEP questions - i.e. When copy-pasting the questions asked of schools into the cep1819-structure.csv file, I encountered unexpected newline characters that would result in the CSV being improperly read by Python and subsequently would make extracting answers to questions impossible.

4. Built a CSV of CEP text questions with their section headers to parse the short answer data from the clean text files.

## ToDo List

1. Remove page headers and page numbers from clean text files
2. Build a text file of CEP specific "stop text", text that can be safely stripped out of question-answer CSV
3. Build a CSV for the CEP short answer data with structure - district-borough-number, question, answer
4. Extract tabular CSV data [tabula-py](https://github.com/chezou/tabula-py)
4. Topic analysis (Discovering and Visualizing Topics in Texts)