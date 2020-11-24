## CEP Analysis

Annually all NYC Department of Education schools, except for charters, bring together a team of folks to write Comprehensive Education Plans that describe their programming, staffing, budgeting, compliance, etc. in a range of different areas important to their superintendents and the city. These plans are made public as PDFs by the DOE - [learn more here](https://www.schools.nyc.gov/get-involved/families/school-leadership-team/comprehensive-education-plans). The `overview-of-the-educational-planning-process.pdf ` PDF has the process schools followed for 2019-20 CEPs (though they didn't post them publicly on the date indicated).

The time, effort, and specificity of the data in these plans have led me to believe it should be open (machine-readable) so it can be analyzed and used in analyses by researchers and practioners and potentially be made legible for current and prospective teachers, school leaders, parents, and anyone else that is impacted by our public schools.

## Requirements

Spin up a virtualenv and install requirements.

`pip install -r requirements.txt`

## Files

* `scripts/` has bash scripts for downloading, converting and cleaning text files
* `input/` contains files used as inputs to queries or parsing - i.e. list of terms to lookup, Robin Hood portfolio schools, standard CEP questions for 2018-19.
* `parse.py` has functions used to validate input files and parse CEP text files
* `query.py` where I've been writing (or trying to write) a function for each query we made into the CEPs during summer 2020. 
* `output/` is where the various output data files live.

## 

## CEP Analysis

1. Downloaded all NYC Department of Education school's Comprehensive Education Plan(CEPs) from the iPlan Portal. All public schools except charter schools, which are still considered public because they receive public funding, are required to submit CEPs annually. 1,579 schools filed plans for the 2018-19 school year.

2. Converted all PDFs to text files with PDFMiner's pdf2txt.py tool. Tested a number of tools include PyPDF2 and 4, converting PDFs to documents using LibreOffice, parsing to lxml with pdfquery package, and poking at tabular data with Tabula. pdf2txt.py converted all text (or so I believe) and was least expensive. 

3. Updated cleaning script to remove newlines, leading spaces and tabs, trailing spaces and tabs, CEP title, footers, and formfeed character. This has been an iterative process (see 5).

4. Built a CSV of CEP text questions with their section headers to parse the short answer data from the clean text files.

5. First pass at analyzing parsing patterns. A few questions are not being found in all, a few in many, and a few others in just some. Going back to cleaning script before dealing with edge cases.

6. Sorted CEPs into directories for the five formats used (with counts):
    * CEP: 1,167
    * SCEP: 239
    * Renewal SCEP: 50
    * CEP-CS: 102
    * Rise CEP: 21

7. Focused on the "standard" CEP format (the largest group above). Parser using Python String.find() is working with 80-90% accuracy (very much esimated).

8. I researched, tested and also implemented a [fuzzysearch](https://github.com/taleinat/fuzzysearch) parser function that uses Levenshtein distance. Fuzzysearch was able to find questions that were mangled when converted to text from PDF when higher Levenshtein distances were used. Not using as main parser yet, but will test and make the switch if it gets me closer to 100% than String.find().


## ToDo List

1. Analyze parse patterns to learn about CEPs and to find opportunities to sanitize, engineer, organize data.
1. Build a text file of CEP specific "stop text", text that can be safely stripped out of question-answer CSV (may not be necessary)
1. General NLP text pre-processing as described [here](https://medium.com/@datamonsters/text-preprocessing-in-python-steps-tools-and-examples-bf025f872908) also in [this awesome Google Sheet of tools](https://docs.google.com/spreadsheets/d/1-9rMhfcmxFv2V2Q5ZWn1FfLDZZYsuwb1eoSp9CiEEOg/edit#gid=1112515333)
1. Build a CSV for the CEP short answer data with structure - district-borough-number, question, answer
1. Do I need to parse Qs and As for the CEP or can I use NLP to skip this step and start to look for interesting patterns?
1. Extract tabular CSV data [tabula-py](https://github.com/chezou/tabula-py)
1. Topic analysis (Discovering and Visualizing Topics in Texts)


