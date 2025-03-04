from pdfminer.high_level import extract_text
import panflute as pf


def load_pdf_as_text(input):
    text = extract_text(input)
    return text


def convert_text_to_asciidoc(text, output_file):
    doc = pf.convert_text(text, input_format='markdown', output_format='asciidoc')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(doc)
