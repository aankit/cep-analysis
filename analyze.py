from PyPDF4 import PdfFileReader


def extract_information(pdf_path):
    with open(pdf_path, 'rb') as f:
        pdf = PdfFileReader(f)
        information = pdf.getDocumentInfo()
        number_of_pages = pdf.getNumPages()

    txt = f"""
    Information about {pdf_path}:

    Author: {information.author}
    Creator: {information.creator}
    Producer: {information.producer}
    Subject: {information.subject}
    Title: {information.title}
    Number of pages: {number_of_pages}
    """
    # print(txt)
    return information


def extract_page_text(pdf_path, page):
    with open(pdf_path, 'rb') as f:
        pdf = PdfFileReader(f)
        pageObj = pdf.getPage(page)
        txt = pageObj.extractText()
    return txt


def write_text_to_file(t, f):
    text_file = open(f, "w")
    n = text_file.write(t)
    text_file.close()

page = extract_page_text("./cep_M033.pdf", 4)
print(page)
length = write_text_to_file(page, './temp.txt')
lines = page.splitlines()
# for line in lines:
#     print(line)
#     print("---")