
import pymupdf
from docx import Document


def extract_pdf_text(file_path):

    text = ""

    pdf = pymupdf.open(file_path)

    for page_number, page in enumerate(pdf):

        page_text = page.get_text()

        text += f"\n[PAGE {page_number + 1}]\n"
        text += page_text

    pdf.close()

    return text


def extract_docx_text(file_path):

    document = Document(file_path)

    text = ""

    for paragraph in document.paragraphs:

        text += paragraph.text + "\n"

    return text
