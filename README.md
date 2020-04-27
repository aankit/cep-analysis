## What is this?

Annually all NYC Department of Education schools, except for charters, bring together a team of folks to write Comprehensive Education Plans that describe their programming, staffing, budgeting, compliance, etc. in a range of different areas important to their superintendents and the city. These plans are made public as PDFs by the DOE - [learn more here](https://www.schools.nyc.gov/get-involved/families/school-leadership-team/comprehensive-education-plans).

The time, effort, and specificity of the data in these plans have led me to believe it should be open (machine-readable) so it can be analyzed and used in analyses by researchers and practioners and potentially be made legible for current and prospective teachers, school leaders, parents, and anyone else that is impacted by our public schools.

## CEP Analysis

1. Downloaded all NYC Department of Education school's Comprehensive Education Plan(CEPs) from the iPlan Portal. All public schools except charter schools, which are still considered public because they receive public funding, are required to submit CEPs annually. 1,579 schools filed plans for the 2018-19 school year.

2. Converted all PDFs to text files with PDFMiner's pdf2txt.py tool. Tested a number of tools include PyPDF2 and 4, converting PDFs to documents using LibreOffice, parsing to lxml with pdfquery package, and poking at tabular data with Tabula. pdf2txt.py converted all text (or so I believe) and was least expensive. 

3. Updated cleaning script to remove newlines, leading spaces and tabs, trailing spaces and tabs, CEP title, footers, and formfeed character. This has been an iterative process (see 5).

4. Built a CSV of CEP text questions with their section headers to parse the short answer data from the clean text files.

5. First pass at analyzing parsing patterns. A few questions are not being found in all, a few in many, and a few others in just some. Going back to cleaning script before dealing with edge cases.

## ToDo List

1. Analyze parse patterns for other text cleaning
2. Build a text file of CEP specific "stop text", text that can be safely stripped out of question-answer CSV
3. Build a CSV for the CEP short answer data with structure - district-borough-number, question, answer
4. Extract tabular CSV data [tabula-py](https://github.com/chezou/tabula-py)
5. Topic analysis (Discovering and Visualizing Topics in Texts)


