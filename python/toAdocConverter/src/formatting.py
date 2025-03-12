import re
import logging

def normalize_spaces(content):
    return content.replace("\xa0", " ")

def escape_double_angle_brackets(content):
    pattern = r"<<(.*?)>>"
    return re.sub(pattern, r"\<<\1>>", content)


def recolor_notes(content):
    notes_patterns = [
        re.compile(r'(?<!foot)(?<!\[)Note:.*'),
        re.compile(r'Note\s+\d+.*'),
        re.compile(r'EXAMPLE\s+\d+:.*'),
        re.compile(r'Please note:.*')
    ]

    matches = set()
    for pattern in notes_patterns:
        matches.update(re.findall(pattern, content))

    # Iterate over the matches and modify the figure tags
    for match in matches:
        content = content.replace(match, f'\n====\n{match.strip()}\n====\n')

    return content


def remove_lines(content, start_line, end_line):
    lines = content.splitlines()
    lines_to_keep = lines[:start_line - 1] + lines[end_line:]
    return '\n'.join(lines_to_keep)


def remove_text_by_patterns(content):
    regular_exp_list = [
        r'Table of Contents\n\n(.*?)(?=\n\n==)',
        r'\[#_Toc\d* \.anchor]####Table \d*\:?\s?',
        r'\[#_Ref\d* \.anchor]####Table \d*\:?\s?',
        r'\[\#_Ref\d* \.anchor\](?:\#{2,4})',
        r'\[\#_Toc\d* \.anchor\](?:\#{2,4})',
        r'\{empty\}'
    ]

    for regex in regular_exp_list:
        # Remove occurrences of the specified regular expression
        content = re.sub(regex, '', content)
    return content


def use_block_tag_for_img_and_move_caption_ahead(content):
    # Define the callback function
    def replacement(match):
        # Use block figure tag
        figure_tag: str = match[1]
        figure_tag = figure_tag.replace("image:", "image::")

        # remove "Figure+num" as it will be automatically done in AsciiDoc
        caption: str = match[2]
        caption = re.sub(r'^Figure \d*:?', '', caption)

        # Move the caption to the beginning of the figure tag
        modified_figure_tag = f'.{caption.strip()}\n{figure_tag}\n'

        return modified_figure_tag

    # Define the regular expression pattern to match figure tags with specific captions
    pattern = r'(image:\S+\[.*?\])\s+?\n?\n?(Figure.*?\n)'

    # Replace the original figure tags with the modified ones
    new_content = re.sub(pattern, replacement, content)
    return new_content


def escape_source_square_brackets(content):
    pattern = r"\[(SOURCE:.*?)\]"
    return re.sub(pattern, r"&#91;\1&#93;", content)


def find_bibliography_section(content):
    # Find the position of "== Bibliography"
    bibliography_pos = content.find("== Bibliography")
    if bibliography_pos == -1:
        logging.warning("Bibliography section not found")
        return None
    return bibliography_pos


def add_anchors_to_bibliography(content):
    bibliography_pos = find_bibliography_section(content)
    if bibliography_pos is None:
        return {}, content

    # Extract the substring starting from the position of "== Bibliography"
    bibliography_text = content[bibliography_pos:]
    biblio_pattern = re.compile(r'^\[(\d+)\](.+)', re.MULTILINE)

    matches = {key: val for key, val in biblio_pattern.findall(bibliography_text)}

    for biblio_tag_num, biblio_tag_text in matches.items():
        anchor = f'[#bib{biblio_tag_num}]'
        modified_text = f'{anchor}\n[{biblio_tag_num}]{biblio_tag_text}'
        bibliography_text = bibliography_text.replace(f'[{biblio_tag_num}]{biblio_tag_text}', modified_text)

    content = content[:bibliography_pos] + bibliography_text
    return matches.keys(), content


def add_links_to_bibliography(content, keys):
    for key in keys:
        in_link_patterns = r'(?<!\[#bib{key}\]\n)\[{key}\]'
        in_link_patterns = in_link_patterns.format(key=key)
        content = re.sub(in_link_patterns, f'link:#bib{key}[[{key}\]]', content)
    return content


def remove_bad_plus_syntax(content):
    pattern = r"\++"
    return re.sub(pattern, '', content)

def replace_image_suffix_to_png(content):
    pattern = ".wmf"
    content = re.sub(pattern, '.png', content)
    pattern = ".emf"
    content = re.sub(pattern, '.png', content)
    return content

def fix_image_file_path(content, output_file):
    pattern = f"{output_file}/media/"
    content = re.sub(pattern, f'../_images/{output_file}/media/', content)
    return content

def removing_unnamed_columns(content):
    pattern = r"^|\bUnnamed: \d+\s*"
    content = re.sub(pattern, '', content)
    pattern2 = r"\^\|\|"
    content = re.sub(pattern2, '', content)
    pattern3 = r"\^\|"
    content = re.sub(pattern3, '', content)
    return content


def removing_nan_columns(content):
    pattern = "NaN"
    content = re.sub(pattern, '', content)
    pattern2 = "nan"
    content = re.sub(pattern2, '', content)
    return content

def add_review_marker_for_images(content):
    pattern = r"(image::)"
    review_marker = "**======================PLEASE REVIEW HERE======================**\n\n"
    pattern2 = r"(image:)"
    content = re.sub(pattern, rf"{review_marker}\1", content)
    content = re.sub(pattern2, rf"{review_marker}\1", content)
    return content

def remove_table_of_contents(content):
    pattern = r'(?s)^== Table of Contents\s*.*?(?=^==\s*\S)'
    content = re.sub(pattern, '', content, flags=re.MULTILINE | re.IGNORECASE)
    pattern2 = r'(?s)^\*Table of Contents\*\s*.*?(?=^==\s*\S)'
    content = re.sub(pattern2, '____\n\n', content, flags=re.MULTILINE | re.IGNORECASE)
    pattern3 = '____'
    content = re.sub(pattern3, '', content)
    return content

def fix_overview_header(content):
    pattern = r'(^==)\s+Document Overview'
    content = re.sub(pattern, r'\1 Document Overview', content, flags=re.MULTILINE | re.IGNORECASE)
    pattern2 = r'^\s*==\s*$'
    content = re.sub(pattern2, '', content, flags=re.MULTILINE)
    return content

def resize_tables(content):
#    pattern = r'\[width=[^\],]+,\s*cols="[^"]+",\s*options="header",?\]'
#    content = re.sub(pattern, '[%autowidth.stretch,options="header"]', content)
    return content

import re

def fix_table_headers(content):
    table_pattern = r"(\[.*?(?:,)?\s*options=[\"']?headers?[\"']?,?.*?\]\n)?\|===\n((?:\|[^\n]+\n)+)\|===\n"

    def check_columns(match):
        attributes = match.group(1) or ""
        table_body = match.group(2)
        rows = table_body.strip().split("\n")
        column_counts = [row.count("|") for row in rows]

        if all(count == 1 for count in column_counts):
            cleaned_attributes = re.sub(r'(,?\s*options=["\']?headers?["\']?,?)', '', attributes).strip()
            
            # Ensure proper syntax remains
            cleaned_attributes = re.sub(r'\[\s*,', '[', cleaned_attributes)  # Fix leading comma issue
            cleaned_attributes = re.sub(r',\s*\]', ']', cleaned_attributes)  # Fix trailing comma issue
            cleaned_attributes = cleaned_attributes.replace("[]", "")  # Remove empty brackets
            
            return f"{cleaned_attributes}\n|===\n{table_body}\n|===\n" if cleaned_attributes else f"|===\n{table_body}\n|===\n"
        else:
            return f"{attributes}|===\n{table_body}\n|===\n"

    content = re.sub(table_pattern, check_columns, content, flags=re.MULTILINE)
    return content


def fix_broken_list(content):
    pattern = r"(^\* {blank})\n([^\n]+)"
    content = re.sub(pattern, r"\1\2", content, flags=re.MULTILINE)
    return content