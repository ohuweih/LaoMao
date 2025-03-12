import pdfplumber
import panflute as pf
import os
import re
import pandas as pd
from io import StringIO


def load_pdf_as_text(input):
    text = ""
    with pdfplumber.open(input) as pdf:
        for page in pdf.pages:
            text += page.extract_text(layout=True) + "\n"
    return text

def initial_clean_asciidoc_after_pdf_conversion(text):
	# Remove sequences of 5+ consonants without spaces (likely gibberish)
    clean_text = re.sub(r'\b[b-df-hj-np-tv-z]{5,}\b', '', text)
	# Remove repeating characters like "Rreeppllaacceemmeenntt"
    clean_text = re.sub(r'(.)\1+', r'\1', text)
	# Fix broken words with excessive spacing
    clean_text = re.sub(r'([a-zA-Z])\s{2,}([a-zA-Z])', r'\1 \2', text)
    # Replace multiple spaces with a single space
    clean_text = re.sub(r' {2,}', ' ', text)
    # Remove newlines in the middle of sentences
    clean_text = re.sub(r'([a-zA-Z]),?\n([a-zA-Z])', r'\1 \2', text)
	# Fix lines that start with numbers (potentially part of tables)
    clean_text = re.sub(r'^\s*\d+\s+', '\n', text, flags=re.MULTILINE)
    return clean_text
     

def extract_tables(text):
	# Identify potential tables based on repetitive numbers and columns
    table_pattern = re.findall(r'(\d+.*\d+)', text)
    if table_pattern:
    	# Convert to DataFrame if table-like patterns are detected
        table_text = '\n'.join(table_pattern)
        df = pd.read_csv(StringIO(table_text), delimiter=r'\s+', header=None)
        return df.to_string(index=False)
    else:
        return text


def convert_text_to_asciidoc(text, output_dir, output_file):
    if not os.path.exists(output_dir): 
        os.makedirs(output_dir)
    clean_text = initial_clean_asciidoc_after_pdf_conversion(text)
#    text_with_extracted_tables = extract_tables(clean_text)
    doc = pf.convert_text(clean_text, input_format='markdown', output_format='asciidoc')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(doc)

