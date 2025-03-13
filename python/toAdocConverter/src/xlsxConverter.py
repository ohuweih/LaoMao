import os
import pandas as pd
from zipfile import ZipFile
from xml.etree import ElementTree as ET

def extract_images_from_xlsx(input_file, image_output_dir):
    """ 
    Extracts images from an Excel file and saves them to a directory.
    """ 
    if not os.path.exists(image_output_dir): 
        os.makedirs(image_output_dir) 
    sheet_images = {} 

    with ZipFile(input_file, 'r') as archive:
        media_files = [f for f in archive.namelist() if f.startswith("xl/media/")]
        drawing_files = [f for f in archive.namelist() if f.startswith("xl/drawings/")]
        drawing_rels_files = [f for f in archive.namelist() if f.startswith("xl/drawings/_rels/")]
        worksheet_rels = [f for f in archive.namelist() if f.startswith("xl/worksheets/_rels/")]
        workbook_xml = archive.read("xl/workbook.xml")
        workbook_tree = ET.fromstring(workbook_xml)
        sheet_map = {}
        drawing_to_sheets = {}

        for sheet in workbook_tree.findall(".//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet"):
            sheet_id = sheet.attrib["sheetId"]
            sheet_name = sheet.attrib["name"]
            sheet_map[f"sheet{sheet_id}.xml"] = sheet_name

        for rel_path in worksheet_rels:
            internal_sheet_name = rel_path.replace("xl/worksheets/_rels/", "").replace(".xml.rels", ".xml")
            display_sheet_name = sheet_map.get(internal_sheet_name, f"Unknown_Sheet_{internal_sheet_name}")
            rels_xml = archive.read(rel_path)
            rels_tree = ET.fromstring(rels_xml)

            for rel in rels_tree.findall(".//{http://schemas.openxmlformats.org/package/2006/relationships}Relationship"):
                if "drawing" in rel.attrib["Type"]:
                    drawing_file = rel.attrib["Target"].replace("../", "xl/")
                    drawing_to_sheets.setdefault(drawing_file, []).append(display_sheet_name)

        for drawing_path in drawing_files:
            try:
                drawing_xml = archive.read(drawing_path)
                tree = ET.fromstring(drawing_xml)
                associated_sheets = drawing_to_sheets.get(drawing_path, [f"Unknown_Sheet_{drawing_path}"])

                drawing_rels_path = drawing_path.replace("xl/drawings/", "xl/drawings/_rels/") + ".rels"
                if drawing_rels_path not in archive.namelist():
                    continue  # Skip if the drawing relationships file doesn't exist
                
                drawing_rels_xml = archive.read(drawing_rels_path)
                drawing_rels_tree = ET.fromstring(drawing_rels_xml)
                rId_to_media = {
                    rel.attrib["Id"]: rel.attrib["Target"].replace("../", "xl/")
                    for rel in drawing_rels_tree.findall(".//{http://schemas.openxmlformats.org/package/2006/relationships}Relationship")
                    if "media" in rel.attrib["Target"]
                    }
                for tag in tree.findall(".//{http://schemas.openxmlformats.org/drawingml/2006/main}blip"):
                    img_rId = tag.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed"]
                    media_file = rId_to_media.get(img_rId)
                    if media_file:
                        img_name = os.path.basename(media_file)
                        img_output_path = os.path.join(image_output_dir, img_name)

                        with open(img_output_path, "wb") as img_file:
                            img_file.write(archive.read(media_file))
                            for sheet_name in associated_sheets:
                                sheet_images.setdefault(sheet_name, []).append(img_name)

            except Exception as e:
                print(f"Error processing drawing file {drawing_path}: {e}")

    return sheet_images

def convert_xlsx_to_adoc_with_images(input_file, output_file, image_output_dir): 
    """ 
    Converts an Excel file to AsciiDoc with cleaned data and extracted images.
    """ 
    try:
        images = extract_images_from_xlsx(input_file, image_output_dir) 
        excel_data = pd.ExcelFile(input_file)

        output_file = f"{output_file}/{output_file}_no_format.adoc"
        
        with open(output_file, 'w', encoding='utf-8') as adoc_file: 
            for sheet_name in excel_data.sheet_names:
                if "archive" in sheet_name.lower():
                    print(f"Skipping archived sheet: {sheet_name}")
                    continue
                
                adoc_file.write(f"# {sheet_name}\n\n")

                df = excel_data.parse(sheet_name, header=None)
                
                # Detect the correct header row dynamically
                first_non_empty_row = df.notna().any(axis=1).idxmax()
                
                # Re-load the sheet with detected header row
                df = pd.read_excel(input_file, sheet_name=sheet_name, header=first_non_empty_row)
                
                # Drop empty columns caused by merging
                non_empty_headers = df.columns.notna()
                df = df.loc[:, non_empty_headers | df.notna().any(axis=0)]
                
                # Fill down merged cell values for clarity
                df = df.fillna(method='ffill')

                # Convert to AsciiDoc table format
                adoc_file.write(f'[%autowidth.stretch,options="header"]\n|===\n')
                adoc_file.write("| " + " | ".join(df.columns.astype(str)) + "\n")
                for _, row in df.iterrows():
                    adoc_file.write("| " + " | ".join(map(str, row)) + "\n") 
                adoc_file.write("|===\n\n")

                # Handle images if they exist for this sheet
                if sheet_name in images:
                    for img_name in images[sheet_name]:
                        img_path = os.path.join(image_output_dir, f"{img_name}") 
                        adoc_file.write(f"image:../_images/{img_path}[{img_name}]\n\n") 

        print(f"Successfully converted {input_file} to {output_file} with fixes.") 
        return output_file

    except Exception as e: 
        print(f"Error occurred: {e}") 
        return None
   

def main():
    '''
    Main fuction will take two arguments (input_file) and run a docx to asciidoc conversion of the file, put all media in to its own folder "/media/media", edit the asciidoc file to change all .emf strings to .png strings and convert all emf images to png images"
    
    '''
    ### TODO Remove parser and add a gui file selection ###
    ### TODO remove output arg and derive everything from input ###
    parser = argparse.ArgumentParser(description="convert docx to adoc, including image support")
    parser.add_argument("-i", "--input", required=True, help="Docx to convert")

    args = parser.parse_args()

    file_dir = os.path.dirname(args.input)
    file_name = os.path.basename(args.input)
    file_stem = os.path.splitext(file_name)[0]

    image_output_dir = f"{file_stem}/extracted_images/" 
    convert_xlsx_to_adoc_with_images(args.input, file_stem, image_output_dir)

if __name__ == "__main__":
    main()