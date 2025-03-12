import subprocess
import os

def convert_images_to_png(file_stem):
    """
    Converts all emf and wmf images in our media folder to png images
    
    Args:
        media_folder (str): Path to the folder
    """
    
    if os.path.exists(f"{file_stem}/media") and os.listdir(f"{file_stem}/media"):
        for filename in os.listdir(f"{file_stem}/media"):
            if 'png' in filename.lower():
                print('png file')
            else:
                file_path = os.path.join(f"{file_stem}/media", filename)
                png_path = os.path.splitext(file_path)[0] + ".png"

                try:
                    command = [
                        f"inkscape",
                        f"{file_path}",
                        "--export-type=png",
                        f"--export-filename={png_path}",
                    ]
                    subprocess.run(command, check=True)
#                    with Image.open(file_path) as img:
#                        img.save(png_path, "PNG")
                    print(f"Converted: {filename} -> {os.path.basename(png_path)}")
                    os.remove(file_path)  # Remove the original EMF/WMF file
                except Exception as e:
                    print(f"Failed to convert {filename}: {e}")