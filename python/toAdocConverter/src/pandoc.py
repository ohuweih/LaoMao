import os
import subprocess 

def run_pandoc(media_folder, input_file, output_file): 
    """ 
    Run a Windows shell command and save the output to a file. 
    
        Args: command (str): The shell command to run. 
        output_file (str): Path to the file where output will be saved. 
    """ 

#    pandoc_path = shutil.which("pandoc") or os.path.join(os.getcwd(), "pandoc")

#    if not os.path.exists(pandoc_path):
#        print("Pandoc executable not found. Ensure Pandoc is installed and available in the system PATH.")
#        return
    
    try:
        if not os.path.exists(media_folder): 
            os.makedirs(media_folder)
        command = [
            "pandoc",  # Use the found Pandoc executable
            "-f", "docx",
            "-t", "asciidoc",
            "--default-image-extension", ".png",
            "--extract-media", media_folder,
            "-o", f"{output_file}/{output_file}_no_format.adoc",
            input_file
        ]
        subprocess.run(command, check=True) 
        print(f"Command executed successfully. Output saved to {output_file}") 

    except subprocess.CalledProcessError as e: 
        print(f"Failed to execute command: {e}") 