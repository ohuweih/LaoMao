import os
import argparse
import logging
import formatting
import imageConverter
import xlsxConverter
import pandoc

# Configure logging
logging.basicConfig(level=logging.INFO,
                    handlers=[logging.FileHandler("my_log_file.log", mode='w', encoding='utf-8'),
                              logging.StreamHandler()])
        
def process_content(content, output_file):
    logging.info("Removing certain patterns in asciidoc file")
    content = formatting.remove_text_by_patterns(content)

    logging.info("changing all image links to .png")
    content = formatting.replace_image_suffix_to_png(content)

    logging.info("Escaping double angle brackets")
    content = formatting.escape_double_angle_brackets(content)

    logging.info("Styling note boxes")
    content = formatting.recolor_notes(content)

    logging.info("Adding anchors to bibliography")
    keys, content = formatting.add_anchors_to_bibliography(content)

    logging.info("Connecting in-document references to bibliography")
    content = formatting.add_links_to_bibliography(content, keys)

    logging.info("Fixing image captions")
    content = formatting.use_block_tag_for_img_and_move_caption_ahead(content)

    logging.info("Escaping square brackets")
    content = formatting.escape_source_square_brackets(content)

    logging.info("Removing bad ++ patters")
    content = formatting.remove_bad_plus_syntax(content)
    
    logging.info("fixing image file paths")
    content = formatting.fix_image_file_path(content, output_file)

    logging.info("Adding Marks for review")
    content = formatting.add_review_marker_for_images(content)

    return content


def write_output(output_file, content):
    logging.info(f"Writing fixed content to the output file: {output_file}")
    with open(output_file, 'w', encoding="utf-8") as file:
        file.write(content)


def fix_asciidoc(input_file, output_file):
    #directory = pathlib.Path(input_file).parent

    logging.info("Read the initial asciidoc file...")
    with open(input_file, 'r', encoding="utf-8") as file:
        content = file.read()

    content = process_content(content, output_file)
    write_output(f"{output_file}/{output_file}.adoc", content)
    os.remove(input_file) 




def main():
    '''
    Main fuction will take two arguments (input_file and output_file) and run a docx to asciidoc conversion of the file, put all media in to its own folder "/media/media", edit the asciidoc file to change all .emf strings to .png strings and convert all emf images to png images"
    
    '''
    ### TODO Remove parser and add a gui file selection ###
    parser = argparse.ArgumentParser(description="convert docx to adoc, including image support")
    parser.add_argument("-i", "--input", required=True, nargs="+", help="Docx to convert")

    args = parser.parse_args()
    
    for input in args.input:
        file_dir = os.path.dirname(input)
        file_name = os.path.basename(input)
        file_stem = os.path.splitext(file_name)[0]

        print(f"Processing: {input}")


        if ".docx" in input:
            media_folder = f"{file_stem}/extracted_media/"
            pandoc.run_pandoc(media_folder, input, f"{file_stem}")
            fix_asciidoc(f"{file_stem}/{file_stem}_no_format.adoc", f"{file_stem}")
            imageConverter.convert_images_to_png(media_folder)
        elif ".xlsx" in input:
            image_output_dir = f"{file_stem}/extracted_images/"
            xlsxConverter.convert_xlsx_to_adoc_with_images(input, f"{file_stem}", image_output_dir)
        else:
            print("File not supported: Expected a docx or xlsx file")
        print(f"Completed: {input}\n")

if __name__ == "__main__":
    main()
